"""Single-worker CPU gameplay/analysis plates on the unchanged relations-v4 clock.

No import-time work, GPU, speech mutation or platform operations. Generated
pieces are silent. The caller owns final audio rebasing and delivery review.
"""
from pathlib import Path
import argparse, copy, hashlib, json, math, os, re, subprocess, sys, time
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

H=Path(__file__).resolve().parent; R=H.parents[3]; L=H/'local/game-plates'
LOADED_SOURCE=Path(__file__).read_bytes()
LOADED_CODE_SHA256=hashlib.sha256(LOADED_SOURCE).hexdigest()
MANIFEST=H/'game-plates-manifest.json'; FPS=60
ENC=['-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-bf','0','-g','120','-sc_threshold','0','-pix_fmt','yuv420p','-r','60','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
VIEW=(249,80,1422,800)
BG='#080d0a';WHITE='#f2f3ed';YELLOW='#f2d787';RED='#ed7169';MUTED='#abb9af'

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,v):
    p=Path(p);assert p==MANIFEST or p.resolve().is_relative_to(L.resolve())
    p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_suffix(p.suffix+'.writing')
    temp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8');os.replace(temp,p)
def path(p):return (R/Path(p)).resolve()
def rel(p):
    try:return Path(os.path.abspath(p)).relative_to(R).as_posix()
    except ValueError:return str(p)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
@lru_cache(None)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def run(args,log):
    Path(log).parent.mkdir(parents=True,exist_ok=True)
    with open(log,'w',encoding='utf8') as f:
        p=subprocess.run([str(x) for x in args],stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    if p.returncode:raise RuntimeError(f'{p.returncode}: {log}: '+Path(log).read_text('utf8',errors='replace')[-1800:])
def authorize(ep):
    c=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert c['renderAuthorized'] and c['fullLocalProductionAuthorized'] and ep in c['episodes'] and ep!='A03'
def intersect(a,b,c,d):return max(a,c)<min(b,d)
def subtract(a,b,ranges):
    spans=[(a,b)]
    for x,y in sorted(ranges):
        new=[]
        for s,e in spans:
            if not intersect(s,e,x,y):new.append((s,e));continue
            if s<x:new.append((s,x))
            if y<e:new.append((y,e))
        spans=new
    return spans
@lru_cache(None)
def font(size):return ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',size)
def text(d,xy,s,size=40,color=WHITE,width=None):
    while width and d.textlength(s,font=font(size))>width and size>24:size-=1
    d.text(xy,s,font=font(size),fill=color,anchor='lt')

def inputs():
    a=read(H/'footage/game-coverage-team-a.json');b=read(H/'footage/team-b/game-coverage.json')
    inter=read(H/'renderer/integration-manifest.json')
    return a,b,{x['id']:x for x in inter['episodes']}

def build_plan():
    a,b,inter=inputs();timing={e['id']:e for e in read(H/'baseline-sentence-timing.json')['records']}
    source={s['key']:s for s in a['sources']};source.update(b['sources'])
    episodes={e['id']:e for e in a['episodes']+b['episodes']}
    baseline={e['id']:e for e in read(H/'renderer/game-baseline-ranges.json')['episodes']}
    result=[]
    for eid,e in sorted(episodes.items()):
        authorize(eid);jobs=[];preserved=inter[eid]['preservedRelationRegions']
        protected=[(r['outputStartFrame'],r['outputEndFrame']) for r in preserved]
        protected += [(r['relationFrameStart'],r['relationFrameEnd']) for r in inter[eid]['rows'] if r['newFrames']!=r['relationFrameEnd']-r['relationFrameStart']]
        oldrows={r['id']:r for r in baseline[eid]['rows']}
        def add(j,exclude=()):
            for a0,b0 in subtract(j['startFrame'],j['endFrame'],list(protected)+list(exclude)):
                q=copy.deepcopy(j);off=a0-j['startFrame'];q['startFrame']=a0;q['endFrame']=b0;q['frames']=b0-a0
                if q['mode']=='game':q['localIn']+=off/60*q.get('speed',1);q['localOut']=q['localIn']+q['frames']/60*q.get('speed',1)
                q['id']=f"{eid}-gp-{a0:06}-{b0:06}-{q['mode']}"
                jobs.append(q)
        def base(row,mode,start,end):
            return {'episode':eid,'rowId':row['baselineGameRowId'],'mode':mode,'startFrame':start,'endFrame':end,
                'studyKey':row.get('recommendedStudyKey'),'sentenceIds':row.get('relatedSentenceIds',[]),
                'observedReason':row.get('observedReason') or row.get('explanationFocus') or row.get('reason'),
                'repeat':bool(row.get('baselineRepeat') or row.get('repeatIndex')),
                'repeatIndex':row.get('repeatIndex'),'sourceEvidence':rel(H/'footage/game-coverage-team-a.json') if eid in a['scope'] else rel(H/'footage/team-b/game-coverage.json')}
        def source_gap(row,start,end,native):
            """A named-game tail retains its actual pose, never a tiny mannequin flash."""
            if not native or row.get('recommendationKind')!='gameplay':
                add(base(row,'own',start,end));return
            seg=min(native,key=lambda s:min(abs(start-s['baselineEndFrame']),abs(end-s['baselineStartFrame'])))
            k=seg['sourceKey'];a0,b0=seg['localIn'],seg['localOut'];last=max(a0,b0-1/60)
            times=[last if start>=seg['baselineEndFrame'] else a0] if end-start<90 else [a0,(a0+last)/2,last]
            if b0-a0<.8:times=[last]
            q=base(row,'analysis',start,end)
            q.update(sourceKey=k,sourceFile=source[k]['file'],sourceUrl=source[k].get('sourceUrl',source[k].get('url')),game=source[k]['game'],frameTimes=times,
                     analysisStyle='continuity-hold' if len(times)==1 else 'pose-strip',repeat=False,
                     analysisReason='Finite native action followed or preceded by labelled observed poses; not new gameplay or looped audio.')
            add(q)
        def clear_own(start,end):
            keep=[]
            for j in jobs:
                if j['mode']!='own' or not intersect(start,end,j['startFrame'],j['endFrame']):keep.append(j);continue
                for x,y in subtract(j['startFrame'],j['endFrame'],[(start,end)]):
                    q=copy.deepcopy(j);q.update(startFrame=x,endFrame=y,frames=y-x);q['id']=f"{eid}-gp-{x:06}-{y:06}-own";keep.append(q)
            jobs[:]=keep
        for row in e['rows']:
            s,t=row['oldRelationStartFrame'],row['oldRelationEndFrame']
            if row.get('inheritedVersionOnly'):
                # Existing A02 edit already carries native/slow labels, detailed
                # marks and independent-source provenance. Leave it byte-exact.
                continue
            segments=row.get('nativeSegments')
            if segments is not None:
                spans=[]
                for seg in segments:
                    x,y=seg['baselineStartFrame'],seg['baselineEndFrame'];k=seg['sourceKey']
                    q=base(row,'game',x,y);q.update(sourceKey=k,sourceFile=source[k]['file'],sourceUrl=source[k].get('sourceUrl'),game=source[k]['game'],localIn=seg['localIn'],localOut=seg['localOut'],speed=seg.get('playbackSpeed',1));add(q);spans.append((x,y))
                for x,y in subtract(s,t,spans):source_gap(row,x,y,segments)
            else:
                segs=row.get('segments')
                if not segs and row['recommendationKind']=='gameplay':
                    segs=[{'recommendationKind':'gameplay','offsetFrame':0,'frames':row.get('selectedFrames',t-s),'selectedSourceKey':row['selectedSourceKey'],'localIn':row['localIn'],'localOut':row['localOut'],'speed':1}]
                spans=[]
                for seg in segs or []:
                    x=s+seg['offsetFrame'];y=min(t,x+seg['frames']);spans.append((x,y))
                    if seg['recommendationKind']=='gameplay':
                        k=seg['selectedSourceKey'];q=base(row,'game',x,y);q.update(sourceKey=k,sourceFile=source[k]['file'],sourceUrl=source[k].get('url'),game=source[k]['game'],localIn=seg['localIn'],localOut=seg['localOut'],speed=seg.get('speed',1));add(q)
                    else:
                        q=base(row,'own',x,y);q['studyKey']=seg.get('recommendedStudyKey',q['studyKey']);add(q)
                for x,y in subtract(s,t,spans):add(base(row,'own',x,y))
        # Additional spoken game anchors are NOT dropped just because their old
        # picture was an explanation. Only uncovered ranges are added once.
        anchor_records=[]
        for anchor in e.get('anchors',[]):
            for seg in anchor['nativeSegments']:
                k=seg['sourceKey'];j={'episode':eid,'rowId':'sentence-'+anchor['oldSentenceId'],'mode':'game','startFrame':seg['baselineStartFrame'],'endFrame':seg['baselineEndFrame'],
                    'sourceKey':k,'sourceFile':source[k]['file'],'sourceUrl':source[k].get('sourceUrl'),'game':source[k]['game'],'localIn':seg['localIn'],'localOut':seg['localOut'],'speed':1,
                    'sentenceIds':[anchor['oldSentenceId']],'observedReason':source[k]['observedReason'],'repeat':False,'studyKey':anchor['fallbackStudyKey'],'sourceEvidence':rel(H/'footage/game-coverage-team-a.json'),'anchor':True}
                clear_own(j['startFrame'],j['endFrame']);occupied=[(x['startFrame'],x['endFrame']) for x in jobs];add(j,occupied);anchor_records.append(anchor['oldSentenceId'])
        for anchor in b['requiredNarrationGameEvidence']:
            if anchor['episode']!=eid:continue
            s,t=anchor['oldSentenceStartFrame'],anchor['oldSentenceEndFrame'];k=anchor['selectedSourceKey']
            if anchor.get('recommendationKind')=='explanation':
                clear_own(s,t);occupied=[(x['startFrame'],x['endFrame']) for x in jobs]
                for x,y in subtract(s,t,occupied+protected):
                    add({'episode':eid,'rowId':'sentence-'+anchor['oldSentenceId'],'mode':'analysis','startFrame':x,'endFrame':y,
                         'sourceKey':k,'sourceFile':source[k]['file'],'sourceUrl':source[k].get('url'),'game':source[k]['game'],
                         'frameTimes':anchor['localFrameTimes'],'sentenceIds':[anchor['oldSentenceId']],'observedReason':anchor['evidencePurpose'],'repeat':False,
                         'studyKey':None,'sourceEvidence':rel(H/'footage/team-b/game-coverage.json'),'anchor':True})
                anchor_records.append(anchor['oldSentenceId']);continue
            occupied=[(x['startFrame'],x['endFrame']) for x in jobs]
            available=int((anchor['allowedLocalOut']-anchor['allowedLocalIn'])*60+.0001)
            for x,y in subtract(s,t,occupied+protected):
                n=min(y-x,available)
                if n<1:continue
                j={'episode':eid,'rowId':'sentence-'+anchor['oldSentenceId'],'mode':'game','startFrame':x,'endFrame':x+n,
                    'sourceKey':k,'sourceFile':source[k]['file'],'sourceUrl':source[k].get('url'),'game':source[k]['game'],'localIn':anchor['allowedLocalIn'],'localOut':anchor['allowedLocalIn']+n/60,'speed':1,
                    'sentenceIds':[anchor['oldSentenceId']],'observedReason':anchor['evidencePurpose'],'repeat':False,'studyKey':None,'sourceEvidence':rel(H/'footage/team-b/game-coverage.json'),'anchor':True};add(j);anchor_records.append(anchor['oldSentenceId'])
        if eid=='A13':
            # Keep the actual-game thesis opening. The allocation table spent
            # all finite source seconds on later named references; relocate
            # only the general fighting portion and retain the two specific
            # opposing-direction poses as a simultaneous analysis in009.
            moved=next(j for j in jobs if j['mode']=='game' and j.get('sourceKey')=='sf2-deejay' and j['startFrame']==5366)
            jobs.remove(moved);q=copy.deepcopy(moved);q.update(mode='analysis',frameTimes=[16.0,29.0],analysisStyle='pose-strip',repeat=False,
                analysisReason='Named passage009 retains actual opposite-facing poses; the general0–6.0667s native excerpt is moved to the existing three-pass opening.')
            q.pop('localIn',None);q.pop('localOut',None);add(q)
            for index,(start,end) in enumerate([(120,502),(502,884),(884,1266)]):
                clear_own(start,end);n=364;q=copy.deepcopy(moved);q.update(startFrame=start,endFrame=start+n,localIn=0,localOut=n/60,sentenceIds=['001'],rowId='A13-opening-pass-'+str(index+1),repeat=index>0,repeatIndex=index+1,anchor=True,
                    observedReason='Finite source0–6.0667 moved from009 to thesis. Existing three observation passes retained; no additional native loops.')
                add(q);q=copy.deepcopy(q);q.update(mode='analysis',startFrame=start+n,endFrame=end,frameTimes=[(n-1)/60],analysisStyle='continuity-hold',repeat=False)
                q.pop('localIn',None);q.pop('localOut',None);add(q)
        # Close the explicit commercial-example clauses with the actual
        # observed subject. These are evidence analyses, not new game loops.
        def replace_span(start,end):
            keep=[]
            for old in jobs:
                for x,y in subtract(old['startFrame'],old['endFrame'],[(start,end)]):
                    q=copy.deepcopy(old);off=x-old['startFrame'];q.update(startFrame=x,endFrame=y,frames=y-x)
                    if q['mode']=='game':q['localIn']+=off/60*q.get('speed',1);q['localOut']=q['localIn']+(y-x)/60*q.get('speed',1)
                    q['id']=f"{eid}-gp-{x:06}-{y:06}-{q['mode']}";keep.append(q)
            jobs[:]=keep
        def evidence_anchor(sid,start,end,specs,label):
            replace_span(start,end);k=specs[0]['sourceKey']
            expanded=[dict(sp,sourceFile=source[sp['sourceKey']]['file'],sourceSha256=source[sp['sourceKey']]['sha256']) for sp in specs]
            add({'episode':eid,'rowId':'sentence-'+sid,'mode':'analysis','startFrame':start,'endFrame':end,
                 'sourceKey':k,'sourceFile':source[k]['file'],'sourceUrl':source[k].get('sourceUrl'),'game':source[k]['game'],
                 'frameTimes':[sp['time'] for sp in specs],'analysisFrameSpecs':expanded,'analysisTargetLabel':label,
                 'sentenceIds':[sid],'observedReason':'Actual inspected source poses beside the named claim. No new motion loop or fictional joint measurement.',
                 'repeat':False,'studyKey':None,'sourceEvidence':rel(L/'qa/anchor-inspection'),'anchor':True,'renderRevision':'named-subject-observed-poses-v1'})
            anchor_records.append(sid)
        if eid=='A05':
            evidence_anchor('040',14250,14548,[{'sourceKey':'hifi-beat','time':7.5,'crop':[760,400,1050,745],'label':'팔·기타와 다리'}],'팔·기타와 다리의 방향')
            jobs[-1]['renderRevision']='named-subject-large-single-pose-v2'
        if eid=='A14':
            evidence_anchor('020',10851,11120,[{'sourceKey':'hzd-adult','time':5,'crop':[620,400,1000,1050],'label':'모닥불 앞의 출발 자세'},
                {'sourceKey':'hzd-aim-move','time':0,'crop':[0,280,840,1060],'label':'활을 겨눈 출발 자세'}],'같은 인물 · 다른 출발 자세')
            start,end=18355,18775;replace_span(start,end);k='fc25-movement'
            add({'episode':eid,'rowId':'sentence-043','mode':'game','startFrame':start,'endFrame':end,'sourceKey':k,
                 'sourceFile':source[k]['file'],'sourceUrl':source[k]['sourceUrl'],'game':source[k]['game'],'localIn':12,'localOut':19,'speed':1,
                 'sentenceIds':['043'],'observedReason':'Observed same selected footballer changes running direction. Cropped focus plus retained contextual pitch/HUD. No joint-angle claim.',
                 'repeat':False,'studyKey':'guard','sourceEvidence':rel(H/'footage/final-audio-adoption.json'),'anchor':True,
                 'editorialCropXYWH':[0,180,1920,900],'focusCropSize':[600,400],
                 'focusMarkerKeyframes':[[12,374,396],[13,500,351],[14,732,306],[15,883,307],[16,805,309],[17,772,257],[18,808,241],[19,994,246]],
                 'renderRevision':'fc25-focus-context-v1','originalSourceAudioQuarantined':True})
            anchor_records.append('043')
        if eid=='A18':
            evidence_anchor('043',15994,16410,[{'sourceKey':'goose-basket-start','time':4.8,'crop':[760,440,1200,820],'label':'목을 든 자세'},
                {'sourceKey':'goose-basket-start','time':7,'crop':[430,500,1100,820],'label':'부리가 바구니로'},
                {'sourceKey':'goose-basket-start','time':9.8,'crop':[430,500,1110,820],'label':'몸통이 이어진 자세'}],'부리 → 목 → 몸통')
            for sid,start,end,times in [('055',19882,20399,[5,7,10]),('065',23428,23844,[6,10]),('070',24957,25445,[5,7,10])]:
                specs=[{'sourceKey':'luigi-lobby','time':t,'label':('눈과 코끝' if sid=='065' else '강아지에 대한 반응')+' '+str(i+1)} for i,t in enumerate(times)]
                if sid=='065':
                    specs[0]['crop']=[500,350,820,690];specs[1]['crop']=[180,300,500,660]
                evidence_anchor(sid,start,end,specs,'눈과 코끝' if sid=='065' else '강아지의 위치와 루이지의 반응')
        jobs.sort(key=lambda j:j['startFrame'])
        # A continuous controlled explanation must not restart at every old
        # commercial-game cut boundary when the variable is unchanged.
        merged=[]
        for j in jobs:
            if merged and j['mode']=='own' and merged[-1]['mode']=='own' and j['studyKey']==merged[-1]['studyKey'] and merged[-1]['endFrame']==j['startFrame']:
                prev=merged[-1];prev.setdefault('baselineGameRowIds',[prev['rowId']]).append(j['rowId']);prev['endFrame']=j['endFrame'];prev['frames']=prev['endFrame']-prev['startFrame']
                prev['sentenceIds']=sorted(set(prev['sentenceIds']+j['sentenceIds']));prev['id']=f"{eid}-gp-{prev['startFrame']:06}-{prev['endFrame']:06}-own"
            else:merged.append(j)
        jobs=merged
        for left,right in zip(jobs,jobs[1:]):assert left['endFrame']<=right['startFrame'],(eid,left['id'],right['id'])
        for j in jobs:
            overlaps=[r for r in inter[eid]['rows'] if intersect(j['startFrame'],j['endFrame'],r['relationFrameStart'],r['relationFrameEnd'])]
            j['expectedUnderlyingExplanationIds']=[r['id'] for r in overlaps]
            # Evidence IDs must actually overlap this split job after rounding.
            actual=[s['id'] for s in timing[eid]['sentences'] if intersect(j['startFrame'],j['endFrame'],round(s['startSeconds']*60),round(s['endSeconds']*60))]
            if overlaps:j['sentenceIds']=actual
            j['narrationEvidence']={'path':rel(H/'baseline-sentence-timing.json'),'sha256':sha(H/'baseline-sentence-timing.json'),'sentenceIds':actual} if overlaps else None
            if overlaps:assert actual,('Unproven explanation overlay',j['id'])
            if j['mode']=='own':
                j['renderRevision']='caption-safe-math-v3' if j['studyKey'].startswith('legacy-') else 'complete-controlled-comparison-v2'
                assert j['studyKey'],('Missing specific study',j)
                if not j['studyKey'].startswith('legacy-'):
                    candidates=[x for x in inter[eid]['rows'] if x['key']==j['studyKey'] and x.get('mode')=='analysis' and x['newFrames']==x['frames']]
                    if not candidates:candidates=[x for x in inter[eid]['rows'] if x['key']==j['studyKey'] and x['newFrames']==x['frames']]
                    assert candidates,('No matching study',eid,j['studyKey'])
                    substantive=[c for c in candidates if c['newFrames']>=120]
                    if substantive:candidates=substantive
                    best=min(candidates,key=lambda c:abs(c['newFrames']-j['frames']))
                    j['ownPlate']=best['output'];j['ownPlateSha256']=best['sha256'];j['ownPlateFrames']=best['newFrames'];j['ownPlateMode']=best.get('mode')
            if j['mode']=='game':
                assert Path(j['sourceFile']).is_file(),j['sourceFile']
                j['sourceLicenseStatus']='local-review-source-evidence; public adoption checked separately'
                if Path(j['sourceFile']).name in ['juri-hit.mp4','odyssey-cactus-hit.mp4']:j['renderRevision']='contrast-outlined-tracked-guides-v2'
            if j['mode']=='analysis' and j.get('sourceKey')=='goose-basket-start' and len(j['frameTimes'])==3 and all(8.4<=t<=11.5 for t in j['frameTimes']):
                j['verifiedAnalysisCropPixels']=[430,500,1110,820]
                j['verifiedAnalysisTargetPixels']=[[788,683],[782,700],[722,664]]
                j['analysisTargetLabel']='부리와 바구니'
                j['analysisTargetEvidence']='Actual source frames 8.45,9.9667,11.4833 viewed at1920x1080; crop retains beak,basket,feet. Full unmodified image also shown.'
            j['output']=rel(L/eid/(j['id']+'.mp4'))
        result.append({'id':eid,'slug':e['slug'],'jobs':jobs,'additionalAnchorSentenceIds':sorted(set(anchor_records)),'protectedRegions':protected,'ready':False})
    plan={'schemaVersion':1,'clock':'relations-v4','codeSha256':LOADED_CODE_SHA256,'sourceCoverageHashes':{'teamA':sha(H/'footage/game-coverage-team-a.json'),'teamB':sha(H/'footage/team-b/game-coverage.json')},
          'baselineReviewSHA256':sha(H.parent/'relations-v4/review-manifest.json'),'episodes':result,'noGPU':True,'workers':1,'encodeThreads':4,'silent':True,
          'classification':'game pieces are independent-gameplay; own and frozen-pose analyses are authored-explanation. No new native loops/slowdown. Existing A02 original pieces remain inherited.'}
    save(L/'plan.json',plan);return plan

def header(j,p):
    im=Image.new('RGBA',(1920,1080),(0,0,0,0));d=ImageDraw.Draw(im)
    d.rectangle((0,0,1920,79),fill=BG)
    title=j.get('game','');text(d,(52,17),title,42,YELLOW,1350)
    label='정지화면 분석' if j['mode']=='analysis' else '실제 게임 · 1×'
    if j.get('repeat') and j['mode']=='game':label='실제 게임 · 기존 반복 관찰'
    text(d,(1480,24),label,29,WHITE,400)
    im.save(p)

def load_tracks():
    p=H/'footage/team-b/a10-editorial-callouts.json'
    return read(p)['tracks'] if p.exists() else []

def ass_time(sec):
    c=round(sec*100);return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'

def track_ass(j,p):
    matching=[t for t in load_tracks() if Path(j['sourceFile']).name==t['source']]
    if not matching:return False
    lines=['[Script Info]','ScriptType: v4.00+','PlayResX: 1920','PlayResY: 1080','ScaledBorderAndShadow: yes','[V4+ Styles]',
           'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
           'Style: Guide,Malgun Gothic,30,&H006971ED,&H006971ED,&H0022140B,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,7,0,0,0,1',
           '[Events]','Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
    events=0
    for frame in range(j['frames']):
        source_t=j['localIn']+frame/60*j.get('speed',1)
        for tr in matching:
            for g in tr['groups']:
                if not g['range'][0]<=source_t<g['range'][1]:continue
                if any(x['range'][0]<=source_t<x['range'][1] for x in tr.get('hide',[])):continue
                points=g['keyframes'];lo=max((x for x in points if x['time']<=source_t),key=lambda x:x['time'],default=points[0]);hi=min((x for x in points if x['time']>=source_t),key=lambda x:x['time'],default=points[-1])
                u=0 if hi['time']==lo['time'] else (source_t-lo['time'])/(hi['time']-lo['time']);vals=[x+(y-x)*u for x,y in zip(lo['xywh'],hi['xywh'])]
                x=round(VIEW[0]+vals[0]*VIEW[2]);y=round(VIEW[1]+vals[1]*VIEW[3]);w=round(vals[2]*VIEW[2]);h=round(vals[3]*VIEW[3]);a=ass_time(frame/60);b=ass_time((frame+1)/60)
                # Hollow rectangle: no fake confidence/hitbox measurement, no
                # target extrapolation through hidden or off-screen intervals.
                drawing=f'm {x} {y} l {x+w} {y} {x+w} {y+h} {x} {y+h} {x} {y}'
                lines.append(f'Dialogue: 0,{a},{b},Guide,,0,0,0,,{{\\an7\\pos(0,0)\\p1\\bord7\\1a&HFF&\\3c&H0A0D08&\\shad0}}'+drawing)
                lines.append(f'Dialogue: 1,{a},{b},Guide,,0,0,0,,{{\\an7\\pos(0,0)\\p1\\bord4\\1a&HFF&\\3c&H6971ED&\\shad0}}'+drawing)
                lines.append(f'Dialogue: 2,{a},{b},Guide,,0,0,0,,{{\\an7\\pos({x},{max(84,y-35)})\\p0\\1a&H00&}}'+tr['label']);events+=1
    p.write_text('\n'.join(lines)+'\n','utf8');return bool(events)

def escaped_filter(p):return str(Path(p).resolve()).replace('\\','/').replace(':','\\:').replace("'","\\'")

def render_game(j,out):
    src=path(j['sourceFile']);meta=probe(str(src));v=next(s for s in meta['streams'] if s['codec_type']=='video')
    assert v['height']>=1080 and v['width']*v['height']>=1920*1080,('Source below FHD sample area or vertical resolution',src,v['width'],v['height'])
    assets=out.parent/'assets';assets.mkdir(exist_ok=True);png=assets/(j['id']+'.png');header(j,png)
    ass=assets/(j['id']+'.ass');has=track_ass(j,ass)
    scale=f"scale={VIEW[2]}:{VIEW[3]}:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:{VIEW[1]}:color=0x080d0a"
    vf=f"[0:v]setpts=(PTS-STARTPTS)/{j.get('speed',1)},fps=60,{scale},setsar=1[bg];[bg][1:v]overlay=0:0:shortest=1"
    if j.get('focusMarkerKeyframes'):
        pts=j['focusMarkerKeyframes']
        def expression(axis,offset):
            exp=str(pts[-1][axis]-offset)
            for a,b in reversed(list(zip(pts,pts[1:]))):
                t0=a[0]-j['localIn'];t1=b[0]-j['localIn'];value=f'{a[axis]-offset}+({b[axis]-a[axis]})*(t-{t0})/{t1-t0}'
                exp=f'if(lt(t,{t1}),{value},{exp})'
            return exp
        d=ImageDraw.Draw(Image.open(png));im=Image.open(png);d=ImageDraw.Draw(im)
        text(d,(56,94),'선택 선수 · 방향 전환',36,YELLOW);text(d,(1120,365),'같은 순간의 전체 상황',32,WHITE);im.save(png)
        vf=f"[0:v]setpts=PTS-STARTPTS,fps=60,split=2[focus][context];[focus]crop=600:400:x='{expression(1,300)}':y='{expression(2,100)}',scale=1000:666,setsar=1,pad=1920:1080:56:145:color=0x080d0a[base];[context]crop=1920:900:0:180,scale=744:348,setsar=1[small];[base][small]overlay=1120:410[bg];[bg][1:v]overlay=0:0:shortest=1"
    if has:vf+=f",ass='{escaped_filter(ass)}'"
    vf+='[v]'
    run(['ffmpeg','-v','error','-y','-threads','4','-ss',f"{j['localIn']:.9f}",'-i',src,'-loop','1','-i',png,'-filter_complex_threads','1','-filter_complex',vf,'-map','[v]','-an','-frames:v',j['frames'],*ENC,out],out.with_suffix('.log'))
    return {'sourceSha256':sha(src),'sourceOriginalDimensions':[v['width'],v['height']],'originalAspectPreserved':True,'sourceWatermarkPreserved':True,
        'nativeSourceSeconds':[j['localIn'],j['localOut']],'nativeMotionFrames':j['frames'],'analysisFrames':0,'calloutTrack':rel(ass) if has else None,'calloutVerifiedEvidenceOnly':True,'viewport':list(VIEW),
        'sourceResolutionCriterion':'At least1080vertical and FHD pixel area; preserve non16:9 genuine high-resolution captures without stretching.',
        'editorialCropXYWH':j.get('editorialCropXYWH'),'focusMarkerKeyframes':j.get('focusMarkerKeyframes'),'sourceAudioQuarantined':j.get('originalSourceAudioQuarantined',False)}

def render_own(j,out):
    k=j['studyKey']
    if k.startswith('legacy-'):
        kind=k.removeprefix('legacy-');frames=max(60,j['frames']);temp=out.with_suffix('.shape-source.mp4')
        run(['node',H/'render_shape_diagram.cjs',kind,frames,temp],out.with_suffix('.log'))
        run(['ffmpeg','-v','error','-y','-threads','4','-i',temp,'-vf','drawbox=x=0:y=864:w=iw:h=ih-864:color=0x080d0a:t=fill','-frames:v',j['frames'],'-an',*ENC,out],out.with_suffix('.caption-safe.log'))
        return {'nativeMotionFrames':0,'analysisFrames':j['frames'],'authoredRenderer':rel(H/'render_shape_diagram.cjs'),'authoredRendererSha256':sha(H/'render_shape_diagram.cjs'),
                'sourceSha256':sha(temp),'sourcePlate':rel(temp),'sourcePlateFrames':frames,'studyKey':k,'commercialGameFootage':False,
                'captionSafeAdjustment':'Only repeated bottom helper phrase at y>=864 removed; equations, labels and complete animated geometry above remain unchanged.'}
    src=path(j['ownPlate']);assert sha(src)==j['ownPlateSha256']
    # Preserve a complete same-topic controlled contrast. Only this authored
    # analysis timing is fitted to the gap; commercial motion is never retimed.
    ratio=j['frames']/j['ownPlateFrames']
    vf=f'setpts={ratio:.12f}*(PTS-STARTPTS),fps=60,tpad=stop_mode=clone:stop_duration=1'
    run(['ffmpeg','-v','error','-y','-threads','4','-i',src,'-vf',vf,'-frames:v',j['frames'],'-an',*ENC,out],out.with_suffix('.log'))
    return {'nativeMotionFrames':0,'analysisFrames':j['frames'],'sameEpisodeStudyKey':k,'sourcePlate':rel(src),'sourcePlateSha256':j['ownPlateSha256'],
        'sourcePlateFrames':j['ownPlateFrames'],'authoredAnalysisDurationRatio':ratio,'commercialGameFootage':False}

def render_analysis(j,out):
    assets=out.parent/'assets';assets.mkdir(exist_ok=True);p=assets/(j['id']+'-analysis.png')
    im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
    text(d,(52,24),j['game'],43,YELLOW,1330);text(d,(1510,31),'정지화면 분석',32,WHITE,350)
    times=j['frameTimes'][:3];n=len(times);gap=24;width=(1808-gap*(n-1))//n
    if j.get('analysisFrameSpecs'):
        specs=j['analysisFrameSpecs'][:3];source_records=[]
        text(d,(56,103),j['analysisTargetLabel'],36,WHITE,1750)
        for i,sp in enumerate(specs):
            fp=assets/(j['id']+f'-source{i}.png');src=path(sp['sourceFile']);assert sha(src)==sp['sourceSha256']
            run(['ffmpeg','-v','error','-y','-threads','2','-ss',str(sp['time']),'-i',src,'-frames:v','1',fp],fp.with_suffix('.log'))
            original=Image.open(fp).convert('RGB');pic=original.copy();x=56+i*(width+gap)
            text(d,(x,169),sp['label'],35,[YELLOW,'#81cfc5','#f18b81'][i],width)
            if len(specs)==1 and sp.get('crop'):
                pic=original.crop(sp['crop']);scale=min(820/pic.width,610/pic.height);pic=pic.resize((round(pic.width*scale),round(pic.height*scale)),Image.Resampling.LANCZOS)
                im.paste(pic,(180+(820-pic.width)//2,225+(610-pic.height)//2))
                text(d,(1060,250),'같은 순간의 전체 상황',33,WHITE,750)
                original.thumbnail((750,460),Image.Resampling.LANCZOS);im.paste(original,(1060+(750-original.width)//2,310))
            elif sp.get('crop'):
                pic=original.crop(sp['crop']);scale=min(width/pic.width,370/pic.height);pic=pic.resize((round(pic.width*scale),round(pic.height*scale)),Image.Resampling.LANCZOS)
                im.paste(pic,(x+(width-pic.width)//2,231+(370-pic.height)//2))
                original.thumbnail((400,225),Image.Resampling.LANCZOS);im.paste(original,(x+(width-original.width)//2,622))
            else:
                pic.thumbnail((width,600),Image.Resampling.LANCZOS);im.paste(pic,(x+(width-pic.width)//2,230+(600-pic.height)//2))
            text(d,(x,859),f"실제 프레임 · {sp['time']:.2f}초",27,MUTED,width)
            source_records.append({'sourceKey':sp['sourceKey'],'sourceFile':sp['sourceFile'],'sourceSha256':sp['sourceSha256'],'sourceFrameTime':sp['time'],'focusCropPixels':sp.get('crop')})
        im.save(p);run(['ffmpeg','-v','error','-y','-loop','1','-framerate','60','-i',p,'-frames:v',j['frames'],'-an',*ENC,out],out.with_suffix('.log'))
        return {'nativeMotionFrames':0,'analysisFrames':j['frames'],'sourceSha256':source_records[0]['sourceSha256'],'sourceFrameTimes':times,'sourceFrames':source_records,
                'kind':'source-derived-pose-analysis','originalAspectPreserved':True,'watermarkPreserved':True,'analysisLabel':'정지화면 분석','fullImageRetainedAlongsideFocus':True}
    if j.get('analysisStyle')=='continuity-hold':
        fp=assets/(j['id']+'-source0.png')
        run(['ffmpeg','-v','error','-y','-threads','2','-ss',str(times[0]),'-i',path(j['sourceFile']),'-frames:v','1',fp],fp.with_suffix('.log'))
        pic=Image.open(fp).convert('RGB');pic.thumbnail((VIEW[2],VIEW[3]),Image.Resampling.LANCZOS)
        im.paste(pic,(VIEW[0]+(VIEW[2]-pic.width)//2,VIEW[1]));im.save(p)
        run(['ffmpeg','-v','error','-y','-loop','1','-framerate','60','-i',p,'-frames:v',j['frames'],'-an',*ENC,out],out.with_suffix('.log'))
        return {'nativeMotionFrames':0,'analysisFrames':j['frames'],'sourceSha256':sha(path(j['sourceFile'])),'sourceFrameTimes':times,'kind':'source-derived-pose-analysis','originalAspectPreserved':True,'watermarkPreserved':True,'analysisLabel':'정지화면 분석','shortGapContinuity':True}
    for i,t in enumerate(times):
        fp=assets/(j['id']+f'-source{i}.png')
        run(['ffmpeg','-v','error','-y','-threads','2','-ss',str(t),'-i',path(j['sourceFile']),'-frames:v','1',fp],fp.with_suffix('.log'))
        original=Image.open(fp).convert('RGB');pic=original.copy();x=56+i*(width+gap)
        if j.get('verifiedAnalysisCropPixels'):
            rect=j['verifiedAnalysisCropPixels'];pic=original.crop(rect);pic.thumbnail((width,420),Image.Resampling.LANCZOS)
            px=x+(width-pic.width)//2;py=260;im.paste(pic,(px,py));d=ImageDraw.Draw(im)
            tx,ty=j['verifiedAnalysisTargetPixels'][i];cx=px+(tx-rect[0])*pic.width/(rect[2]-rect[0]);cy=py+(ty-rect[1])*pic.height/(rect[3]-rect[1])
            d.ellipse((cx-25,cy-25,cx+25,cy+25),outline=RED,width=6)
            text(d,(x,575),j['analysisTargetLabel'],35,WHITE,width)
            original.thumbnail((355,200),Image.Resampling.LANCZOS);im.paste(original,(x+(width-original.width)//2,640))
        else:
            pic.thumbnail((width,660),Image.Resampling.LANCZOS);y=240+(660-pic.height)//2
            im.paste(pic,(x+(width-pic.width)//2,y));d=ImageDraw.Draw(im)
        text(d,(x,170),f'실제 자세 {i+1}',42,[YELLOW,'#81cfc5','#f18b81'][i],width)
        d.line((x,848,x+width,848),fill=[YELLOW,'#81cfc5','#f18b81'][i],width=6)
        text(d,(x,864),f'관찰 시점 {t:.2f}초',27,MUTED,width)
    im.save(p)
    run(['ffmpeg','-v','error','-y','-loop','1','-framerate','60','-i',p,'-frames:v',j['frames'],'-an',*ENC,out],out.with_suffix('.log'))
    return {'nativeMotionFrames':0,'analysisFrames':j['frames'],'sourceSha256':sha(path(j['sourceFile'])),'sourceFrameTimes':times,'kind':'source-derived-pose-analysis','originalAspectPreserved':True,'watermarkPreserved':True,'analysisLabel':'정지화면 분석',
            'verifiedFocusCropPixels':j.get('verifiedAnalysisCropPixels'),'verifiedTargetPixels':j.get('verifiedAnalysisTargetPixels'),'fullImageRetainedAlongsideFocus':bool(j.get('verifiedAnalysisCropPixels'))}

def media_segments(j,details):
    times=details.get('sourceFrameTimes')
    return [{'kind':'native-gameplay' if j['mode']=='game' else 'still-analysis' if j['mode']=='analysis' else 'authored-explanation',
             'offsetFrame':0,'frames':j['frames'],'sourceKey':j.get('sourceKey') or f"authored:{j['episode']}/{j['studyKey']}",
             'sourceLocalIn':j.get('localIn',times[0] if times else 0),
             'sourceLocalOut':j.get('localOut',times[-1] if times else details.get('sourcePlateFrames',j['frames'])/60),
             'sourceSha256':details.get('sourceSha256') or details.get('sourcePlateSha256') or details.get('authoredRendererSha256'),
             'sourceFrameTimes':times,'sourceFrameRecords':details.get('sourceFrames')}]

def render_one(j):
    authorize(j['episode']);out=path(j['output']);out.parent.mkdir(parents=True,exist_ok=True);receipt=out.with_suffix('.json')
    digest=hashlib.sha256(json.dumps(j,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    if out.exists() and receipt.exists():
        old=read(receipt)
        if old.get('jobSha256')==digest and sha(out)==old.get('sha256'):
            old['mediaSegments']=media_segments(j,old['details']);save(receipt,old);return old
    details=render_game(j,out) if j['mode']=='game' else render_analysis(j,out) if j['mode']=='analysis' else render_own(j,out)
    meta=probe(str(out));v=next(s for s in meta['streams'] if s['codec_type']=='video')
    assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',j['frames']),(j['id'],v)
    assert not any(s['codec_type']=='audio' for s in meta['streams'])
    media=media_segments(j,details)
    result={'jobId':j['id'],'jobSha256':digest,'codeSha256':LOADED_CODE_SHA256,'picture':j['output'],'sha256':sha(out),'frames':j['frames'],'dimensions':[1920,1080],'fps':60,'silent':True,'details':details,'mediaSegments':media,
        'sourceVerified':True,'verificationMeaning':'Existing source/observation provenance plus exact decoded technical delivery; public rights, continuous watching, audio and human review are separate.',
        'publicationReady':False,'humanReview':False}
    save(receipt,result);return result

def update_manifest(plan):
    output={'schemaVersion':1,'clock':'relations-v4','baselineReviewSHA256':plan['baselineReviewSHA256'],'codeSha256':LOADED_CODE_SHA256,'planSha256':sha(L/'plan.json'),
            'status':'incremental-silent-plates-in-progress','episodes':[],'workers':1,'cpuThreads':4,'gpuUsed':False,'audioIncluded':False,'finalHumanReview':False}
    for e in plan['episodes']:
        edits=[];pending=[]
        for j in e['jobs']:
            p=path(j['output']).with_suffix('.json')
            if not p.exists():pending.append(j['id']);continue
            rec=read(p);digest=hashlib.sha256(json.dumps(j,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
            if rec.get('jobSha256')!=digest:pending.append(j['id']);continue
            q={'id':j['id'],'kind':'independent-gameplay' if j['mode']=='game' else 'authored-explanation','startFrame':j['startFrame'],'endFrame':j['endFrame'],'newFrames':j['frames'],
               'picture':j['output'],'pictureSha256':rec['sha256'],'sourceStartFrame':0,'sourceVerified':True,'expectedUnderlyingExplanationIds':j['expectedUnderlyingExplanationIds'],
               'sourceClassification':j['mode'],'nativeFrames':rec['details']['nativeMotionFrames'],'analysisFrames':rec['details']['analysisFrames'],'receipt':rel(p),
               'baselineGameRowId':j['rowId'],'baselineGameRowIds':j.get('baselineGameRowIds',[j['rowId']]),'sentenceIds':j['sentenceIds'],'sourceEvidence':j['sourceEvidence']}
            q['mediaSegments']=rec['mediaSegments']
            if j.get('narrationEvidence'):q['narrationEvidence']=j['narrationEvidence']
            edits.append(q)
        output['episodes'].append({'id':e['id'],'slug':e['slug'],'ready':not pending,'pictureEdits':edits,'pendingJobs':pending,
            'plannedJobs':len(e['jobs']),'completedJobs':len(edits),'inheritedA02Preserved':e['id']=='A02','audioEdits':[],'additionalAnchorSentenceIds':e['additionalAnchorSentenceIds']})
    if all(e['ready'] for e in output['episodes']):output['status']='all17-silent-game-replacement-plates-ready'
    save(MANIFEST,output);return output

def sample_qa(j):
    # These are exact current narration strings on the unchanged baseline
    # clock, not placeholder captions. Root aligns revised speech afterwards.
    timing=next(e for e in read(H/'baseline-sentence-timing.json')['records'] if e['id']==j['episode'])
    revisions=read(H/'narration/source-verified-revisions.json');ep=next((e for e in revisions['episodes'] if e['id']==j['episode']),{})
    changes={c['id']:c['ko'] for c in ep.get('changes',[])}
    changes.update({c['id']:c['ko'] for c in revisions.get('existingApprovedChanges',[]) if c.get('episode')==j['episode']})
    qa=L/'qa';qa.mkdir(exist_ok=True);record=[]
    requested=[1,round(j['frames']*.35),round(j['frames']*.65),j['frames']-2]
    if j.get('sourceKey')=='juri-hit':requested.extend([30,45,150])
    for f in sorted(set([min(j['frames']-1,x) for x in requested])):
        img=qa/(j['id']+f'-{f:04}.png')
        run(['ffmpeg','-v','error','-y','-threads','2','-ss',str(f/60),'-i',path(j['output']),'-frames:v','1',img],img.with_suffix('.log'))
        im=Image.open(img).convert('RGB');d=ImageDraw.Draw(im);t=(j['startFrame']+f)/60
        s=next((s for s in timing['sentences'] if s['startSeconds']<=t<s['endSeconds']),None)
        if not s and j['sentenceIds']:s=next((s for s in timing['sentences'] if s['id']==j['sentenceIds'][0]),None)
        caption=changes.get(s['id'],s['text']) if s else ''
        caption=caption.split('. ')[0].rstrip('.')+'.' if caption else ''
        words=caption.split();lines=[];line=''
        for w in words:
            test=(line+' '+w).strip()
            if d.textlength(test,font=font(48))>1740 and line:lines.append(line);line=w
            else:line=test
        if line:lines.append(line)
        # Full sentence may span more clauses; only a real clause from the
        # actual sentence is used in this visual-layout proof, never invented.
        shown=lines[:2]
        if shown:
            width=max(d.textlength(x,font=font(48)) for x in shown)+56;height=68*len(shown)+20
            d.rectangle((960-width/2,970-height/2,960+width/2,970+height/2),fill='#f8f8f4')
            for i,line in enumerate(shown):d.text((960,970-height/2+10+i*68),line,font=font(48),fill='#183e31',anchor='mt')
        im.save(img);mobile=img.with_name(img.stem+'-375.png');im.resize((375,211),Image.Resampling.LANCZOS).save(mobile)
        record.append({'frame':f,'full':rel(img),'mobile':rel(mobile),'actualSentenceId':s['id'] if s else None,'caption':shown,'captionEvidence':rel(H/'narration/source-verified-revisions.json'),'actualCaptionText':True})
    save(qa/(j['id']+'-qa.json'),{'samples':record,'actualVisualInspection':False,'continuousReview':False,'actualAudioListening':False});return record

def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['plan','samples','run','status']);ap.add_argument('--episode');ap.add_argument('--all',action='store_true');ap.add_argument('--resume',action='store_true');args=ap.parse_args()
    L.mkdir(parents=True,exist_ok=True)
    snapshot=L/'render-code-snapshots';snapshot.mkdir(exist_ok=True)
    (snapshot/(LOADED_CODE_SHA256+'.py')).write_bytes(LOADED_SOURCE)
    if args.resume:(L/'pause-request.json').unlink(missing_ok=True)
    plan=build_plan() if args.action=='plan' or not (L/'plan.json').exists() else read(L/'plan.json')
    if args.action=='plan':print(json.dumps({e['id']:len(e['jobs']) for e in plan['episodes']}));update_manifest(plan);return
    if args.action=='status':print(json.dumps([{k:e[k] for k in ['id','ready','plannedJobs','completedJobs']} for e in update_manifest(plan)['episodes']]));return
    lock=L/'worker.lock'
    try:fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:raise RuntimeError('Existing owned worker lock; inspect that PID before starting another worker.')
    os.write(fd,str(os.getpid()).encode());os.close(fd)
    try:
        if args.action=='samples':
            choices=[next(j for e in plan['episodes'] if e['id']=='A01' for j in e['jobs'] if j['mode']=='game'),
                     next(j for e in plan['episodes'] if e['id']=='A10' for j in e['jobs'] if j.get('sourceKey')=='juri-hit' and j['mode']=='game')]
            for j in choices:render_one(j);print(json.dumps(sample_qa(j),ensure_ascii=False));update_manifest(plan)
            return
        assert args.all or args.episode,'Choose an explicitly authorized episode or the approved17 list.'
        ordered=sorted(plan['episodes'],key=lambda e:({'A01':0,'A16':1}.get(e['id'],2),e['id']))
        ready={e['id']:e['ready'] for e in update_manifest(plan)['episodes']}
        for e in ordered:
            if args.episode and args.episode!=e['id']:continue
            authorize(e['id'])
            if ready[e['id']]:
                print(json.dumps({'episode':e['id'],'ready':True,'unchangedCompletedCache':True}),flush=True);continue
            for index,j in enumerate(e['jobs']):
                if (L/'pause-request.json').exists():
                    save(L/'run-state.json',{'status':'paused-at-piece-boundary','episode':e['id'],'nextJob':j['id'],'resumeCommand':'python -X utf8 '+rel(__file__)+' run --all --resume','completedPicturesPreserved':True})
                    print(json.dumps({'paused':True,'episode':e['id'],'nextJob':j['id']}),flush=True);return
                render_one(j);update_manifest(plan);print(json.dumps({'episode':e['id'],'done':index+1,'total':len(e['jobs']),'job':j['id']}),flush=True)
                save(L/'run-state.json',{'status':'running','episode':e['id'],'completedJob':j['id'],'done':index+1,'total':len(e['jobs']),'processId':os.getpid()})
            print(json.dumps({'episode':e['id'],'ready':True}),flush=True)
        save(L/'run-state.json',{'status':'requested-queue-complete','episode':args.episode,'all':args.all})
    finally:lock.unlink(missing_ok=True)

if __name__=='__main__':main()

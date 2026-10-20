"""Bind game-left states/actions to the unchanged measured raw voice clock.

The default design command performs no source decode or rendering. Build only
after timing.py creates the actual21-scene Clock; --direct-source lets the root
paired compositor read finite native ranges once without intermediate video.
"""
from pathlib import Path
from fractions import Fraction
import argparse, bisect, hashlib, importlib.util, json, math

H=Path(__file__).resolve().parent;R=H.parents[3]
P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v7-part1';G=O/'gameplay'
FPS=60;RECT=[40,250,896,504]

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def path(p):return Path(p)if Path(p).is_absolute()else R/p
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,file):
    s=importlib.util.spec_from_file_location(name,H/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def design():
    assets=module('v7_left_design_prepare','left-prepare.py').design()
    guides=module('v7_left_design_guides','left-guides.py').build()
    d=dict(schemaVersion=1,part=1,status='implementation/design ready; no actualClock fabricated',
        modules=[rel(H/x)for x in ['left-prepare.py','left-guides.py','left-timing.py']],
        runWith='qwen3-tts/.venv/Scripts/python.exe',
        inputPlan=rel(P/'planning/revision-v7-two-part/part-01-left-game-plan.json'),
        gameInputs=rel(H/'game-inputs.json'),assets=rel(G/'left-asset-plan.json'),guideKeys=rel(G/'guide-keys.json'),
        outputManifest=rel(H/'left-visual-segments.json'),sceneASSDirectory=rel(G/'scene-ass'),
        schema=dict(sceneId='v7-a01..v7-a21',startFrame='global exact60fps inclusive',endFrameExclusive='global exact60fps exclusive',
            kind='still|video',file='workspace-relative existing source/cache',sourceStartFrame='frame offset into file; absolute native frame in direct-source mode',
            sourceFrames='segment native duration; for still1',sourceTotalFrames='actual probed video container length',
            rect=RECT,classification='independent-gameplay|gameplay-derived-analysis',
            sceneASS='manifest.sceneASS[sceneId] is a1920x1080 ASS file with scene-local times'),
        slot='No193second video extraction/encode in design; actual root compositor performs the one bounded native decode',
        nativeSeconds=assets['sourceSeconds'],manualGuideKeys=sum(len(x)for x in guides['streams'].values()),
        timing='Clock.frame(scene,line,approved Unicode offset); preserve native action order, hold correct source frame while speech/right continue, report cue drift',
        movingGuides='libass continuous move, sampled at the final60fps. At most100ms events split at observed/hide source keys; source anchor path unchanged, no6-frame position hold or occlusion bridge.',
        finalReview='Dense moving annotation target/occlusion and1080/375 final actual output remain pending')
    save(G/'left-timing-interface.json',d);return d

def clause_frame(clock,cue):
    line=int(cue['targetParagraph'].rsplit('L',1)[1]);return clock.frame(cue['targetScene'],line,cue['sourceKoOffset'])

def focus(row):
    k=row['annotationPreset']
    return {'sail':'옮길 위치 / 세울 방향','hook':'갈고리가 열린 쪽',
            'flight':'몸통과 펼친 팔의 방향','kart':'차체 앞쪽 / 머리 쪽','mario':'머리·발과 중간 동작'}[k]

def source_totals(prep,j):
    cache_file=G/'source-container-metadata.json';old=read(cache_file)if cache_file.exists()else {};result={}
    for sid,s in j['sources'].items():
        f=path(s['sourcePath']);stat=f.stat();signature=dict(sourceSha256=s['sourceSha256'],bytes=stat.st_size,mtimeNs=stat.st_mtime_ns)
        if old.get(sid,{}).get('inputSignature')==signature:result[sid]=old[sid];continue
        q=prep.probe(f);v=next(x for x in q['streams']if x['codec_type']=='video')
        assert(v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1')
        if v.get('nb_frames')is not None:
            n=int(v['nb_frames']);basis='container stream nb_frames';derived=False
        else:
            # A duration/CFR declaration supplies a selection range bound, not
            # a full-file decoded frame census. Superflight has no nb_frames.
            rate=Fraction(v['avg_frame_rate']);assert rate==Fraction(v['r_frame_rate'])==60
            bound=Fraction(int(v['duration_ts']))*Fraction(v['time_base'])*rate
            assert bound.denominator==1,'Nonintegral/VFR range requires a separately verified source bound'
            n=int(bound);basis='video duration_ts × time_base × declared CFR; selection header bound, not full-source decode count';derived=True
        assert n>0
        result[sid]=dict(inputSignature=signature,sourceTotalFrames=n,dimensions=[1920,1080],fps=60,
            averageFrameRate=v.get('avg_frame_rate'),timeBase=v.get('time_base'),sourcePath=s['sourcePath'],
            durationTs=v.get('duration_ts'),videoDuration=v.get('duration'),frameCountBasis=basis,
            durationDerivedRangeBound=derived,fullSourceDecodeCountPerformed=False,
            selectedLastFrameEvidence=(dict(file=j['stills']['flight-body-end']['file'],sourceFrame=20039,
                sha256=j['stills']['flight-body-end']['sha256'],meaning='Actual1920x1080 selected last-frame cache exists; no whole source census needed')if sid=='superflight'else None),
            verification='Previously hashed/decoded independent FHD source; actual container metadata verified, no source-content recapture')
    save(cache_file,result);return result

def schedule(clock,plan):
    """Pure scheduling: events do not modify PCM or create a silent interval."""
    base={s['id']:[]for s in clock.timeline['scenes']};issues=[];beats=[]
    after_live_analysis={}
    for scene in plan['scenes']:
        sid=scene['targetScene'];bounds=clock.scenes[sid]
        for row in scene['paragraphs']:
            for override in row.get('postLiveAnalysisOverrides',[]):
                after_live_analysis[override['afterBeatId']]=override
            line=int(row['targetParagraphs'][0].rsplit('L',1)[1]);f=clock.frame(sid,line,0)
            base[sid].append(dict(frame=max(bounds['startFrame'],f),stillId=row['analysisStillIds'][0],
                focus=focus(row),reason='approved-paragraph source-derived analysis',paragraphId=row['targetParagraphs'][0],priority=0))
            for state in row.get('analysisCueStates',[]):
                base[sid].append(dict(frame=clause_frame(clock,state['cue']),stillId=state['analysisStillId'],
                    focus=focus(row),reason=state['purpose'],paragraphId=row['targetParagraphs'][0],priority=1))
        # Cover initial raw lead-in without moving its spoken first word.
        initial=dict(base[sid][0]);initial['frame']=bounds['startFrame'];base[sid].append(initial)
    # A source-contiguous predecessor can finish after the next short cue. Its
    # native speed/order wins; expose drift for actual paired-output review.
    scene_cursor={}
    # Unicode offsets are local to a paragraph. Sorting only by offset lets
    # L06/offset0 precede L03/offset17 and silently delays the earlier action.
    # The measured global cue is the authoritative order across paragraphs.
    ordered=sorted(plan['livePhases'],key=lambda q:clause_frame(clock,q['sourceBeats'][0]['sourceCue']))
    for phase in ordered:
        sid=phase['targetScene'];bounds=clock.scenes[sid];previous_end=scene_cursor.get(sid)
        for b in phase['sourceBeats']:
            desired=clause_frame(clock,b['sourceCue'])
            start=max(desired,previous_end or bounds['startFrame']);wanted=b['sourceOutFrameExclusive']-b['sourceInFrame']
            end=min(start+wanted,bounds['endFrame'])
            if end<=start:
                issues.append(dict(beatId=b['id'],kind='no-room-before-scene-boundary',desiredFrame=desired,sourceFramesOmitted=wanted));continue
            used=end-start;drift=start-desired
            if drift or used!=wanted:
                issues.append(dict(beatId=b['id'],kind='cue-order-drift'if used==wanted else'boundary-trim',
                    preferredFrame=desired,actualStartFrame=start,driftFrames=drift,sourceFramesPlanned=wanted,sourceFramesUsed=used,
                    reason='No speed change, PCM change, silence or unrelated later-scene spill; inspect the actual action/word join'))
            row=dict(sceneId=sid,startFrame=start,endFrameExclusive=end,beatId=b['id'],phaseId=phase['id'],
                sourceId=phase['sourceId'],nativeSourceInFrame=b['sourceInFrame'],nativeSourceOutFrameExclusive=b['sourceInFrame']+used,
                phaseNativeInFrame=phase['sourceInFrame'],kind='video',classification='independent-gameplay',focus=b['largeFocusLabel'],
                sourceCue=b['sourceCue'],preferredCueFrame=desired,cueDriftFrames=drift,sourceAudioAllowed=b['sourceAudioAllowed'],silent=b['silent'])
            beats.append(row);previous_end=end;scene_cursor[sid]=end
            base[sid].append(dict(frame=end,sourceId=phase['sourceId'],sourceFrame=row['nativeSourceOutFrameExclusive']-1,
                focus=b['largeFocusLabel'],reason='exact-last-frame analysis after native action; speech and right continue',
                paragraphId=b['sourceCue']['targetParagraph'],priority=2))
            if b['id']in after_live_analysis:
                override=after_live_analysis[b['id']]
                base[sid].append(dict(frame=end,stillId=override['analysisStillId'],
                    focus=override['focus'],reason=override['purpose'],
                    paragraphId=b['sourceCue']['targetParagraph'],priority=3))
    for sid in base:
        selected=sorted((b for b in beats if b['sceneId']==sid),key=lambda b:b['startFrame'])
        assert all(a['endFrameExclusive']<=b['startFrame']for a,b in zip(selected,selected[1:])),('Two native actions overlap one left pane',sid)
    return base,beats,issues

def segments(clock,j,plan,assets,totals,direct):
    base,beats,issues=schedule(clock,plan);out=[]
    still_by_id={s['id']:s for s in assets['stills'].values()}
    for scene in clock.timeline['scenes']:
        sid=scene['id'];events=sorted(base[sid],key=lambda x:(x['frame'],x['priority']))
        live=[x for x in beats if x['sceneId']==sid]
        edges=sorted({scene['startFrame'],scene['endFrame'],*[e['frame']for e in events if scene['startFrame']<=e['frame']<scene['endFrame']],
                      *[f for b in live for f in [b['startFrame'],b['endFrameExclusive']]]})
        for a,b in zip(edges,edges[1:]):
            if b<=a:continue
            active=next((x for x in live if x['startFrame']<=a<x['endFrameExclusive']),None)
            if active:
                d=dict(active);offset=a-active['startFrame'];native=active['nativeSourceInFrame']+offset
                asset=assets['clips'][active['phaseId']]
                d.update(startFrame=a,endFrameExclusive=b,frames=b-a,sourceFrames=b-a,rect=RECT,
                    file=j['sources'][d['sourceId']]['sourcePath']if direct else asset['file'],
                    sourceStartFrame=native if direct else native-asset['nativeSourceInFrame'],
                    sourceTotalFrames=totals[d['sourceId']]['sourceTotalFrames']if direct else asset['sourceFrames'],
                    sourceStartSeconds=native/60,sourceFrame=native,originalSource=j['sources'][d['sourceId']]['sourcePath'],
                    originalSourceSha256=j['sources'][d['sourceId']]['sourceSha256'],sourceSpeed=1,loop=False,
                    assetMode='bounded-original-source'if direct else'finite-native-phase-cache',dimensions=[1920,1080])
            else:
                e=next(x for x in reversed(events)if x['frame']<=a)
                asset=still_by_id[e['stillId']]if e.get('stillId')else assets['stills'][f'{e["sourceId"]}:{e["sourceFrame"]}']
                d=dict(sceneId=sid,startFrame=a,endFrameExclusive=b,frames=b-a,kind='still',file=asset['file'],rect=RECT,
                    sourceStartFrame=0,sourceFrames=1,sourceTotalFrames=1,sourceId=asset['sourceId'],sourceFrame=asset['sourceFrame'],
                    classification='gameplay-derived-analysis',analysisStillId=asset['id'],focus=e['focus'],reason=e['reason'],
                    paragraphId=e['paragraphId'],originalSource=asset['originalSource'],originalSourceSha256=asset['sourceSha256'],
                    sourceAudioAllowed=False,silent=True,dimensions=[1920,1080],editorialClock='explicit frozen actual frame; progressive marks do not count as live gameplay')
            # The root decoder uses each segment's exact half-open bounds once.
            assert d['sourceStartFrame']+(b-a if d['kind']=='video'else 1)<=d['sourceTotalFrames']
            if out and out[-1]['sceneId']==sid and out[-1]['endFrameExclusive']==a:
                p=out[-1]
                same=(p['kind'],p['file'],p['focus'],p.get('beatId'))==(d['kind'],d['file'],d['focus'],d.get('beatId'))
                continuous=p['kind']=='still'or p['sourceStartFrame']+p['frames']==d['sourceStartFrame']
                if same and continuous:
                    p['endFrameExclusive']=b;p['frames']=b-p['startFrame']
                    if p['kind']=='video':p['sourceFrames']=p['frames']
                    continue
            out.append(d)
    validate(clock.timeline,out)
    for beat in beats:
        captured=sum(r['frames']for r in out if r.get('beatId')==beat['beatId']and r['kind']=='video')
        assert captured==beat['endFrameExclusive']-beat['startFrame'],('Native action was masked or silently omitted',beat['beatId'],captured)
    return out,beats,issues

def validate(timeline,rows):
    for s in timeline['scenes']:
        q=[x for x in rows if x['sceneId']==s['id']];cursor=s['startFrame']
        for x in q:assert x['startFrame']==cursor;cursor=x['endFrameExclusive']
        assert cursor==s['endFrame'],(s['id'],cursor,s['endFrame'])
    assert all(x['kind']in ['video','still']and x['endFrameExclusive']>x['startFrame']for x in rows)

def stamp(frame,floor=False):
    cs=frame*100//60 if floor else round(frame*100/60)
    h,cs=divmod(cs,360000);m,cs=divmod(cs,6000);s,cs=divmod(cs,100)
    return f'{h}:{m:02}:{s:02}.{cs:02}'
def color(c):return '&H'+c.lstrip('#')[4:6]+c.lstrip('#')[2:4]+c.lstrip('#')[:2]+'&'
def escape(t):return t.replace('\\','\\\\').replace('{','(').replace('}',')').replace('\n',r'\N')
def header():return '''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Game,맑은 고딕,48,&H00F5F5F5,&H00F5F5F5,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Kind,맑은 고딕,48,&H00B8B8B8,&H00B8B8B8,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Focus,맑은 고딕,64,&H0083CFE8,&H0083CFE8,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Vector,Arial,24,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def event(a,b,style,text,layer=5,native_frame_boundaries=False):
    assert 0<=a<b
    return f'Dialogue: {layer},{stamp(a,native_frame_boundaries)},{stamp(b,native_frame_boundaries)},{style},,0,0,0,,{text}\n'
def line_path(points):return 'm '+(' l '.join(f'{x:.1f} {y:.1f}'for x,y in points))
def stroke_paths(points,width=6):
    paths=[]
    for a,b in zip(points,points[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
        if length<.01:continue
        nx,ny=-dy/length*width/2,dx/length*width/2
        p=[(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)]
        paths.append(line_path(p+[p[0]]))
    return paths
def guide_paths(g):
    x,y=40+g['point'][0]*896,250+g['point'][1]*504
    if not(54<=x<=922 and 264<=y<=740):return []
    # Hollow attention bracket, not a detector or a calibrated rotation ring.
    r=18;wing=10
    corners=[[(x-r,y-r+wing),(x-r,y-r),(x-r+wing,y-r)],[(x+r-wing,y-r),(x+r,y-r),(x+r,y-r+wing)],
             [(x+r,y+r-wing),(x+r,y+r),(x+r-wing,y+r)],[(x-r+wing,y+r),(x-r,y+r),(x-r,y+r-wing)]]
    return [p for q in corners for p in stroke_paths(q)]

def focus_markup(row,guides):
    t=escape(row['focus'])
    if row['sourceId']=='mariokart'and('앞쪽'in t or'기울어진'in t):
        return r'{\1c'+color(guides['colorRoles']['reference'])+r'}차체 앞쪽'+r'{\1c&H00F5F5F5&} / '+r'{\1c'+color(guides['colorRoles']['focus'])+r'}머리 쪽'
    if row['sourceId']=='odyssey'and'머리'in t:
        return r'{\1c'+color(guides['colorRoles']['focus'])+r'}머리'+r'{\1c&H00F5F5F5&} / '+r'{\1c'+color(guides['colorRoles']['reference'])+r'}발'+r'{\1c&H0083CFE8&} · 중간 동작'
    return t

def guide_windows(row,guides):
    """At most100ms, split at every observed/hide source key, no new path."""
    n=row['endFrameExclusive']-row['startFrame']
    if row['kind']=='still':return [(0,n)]
    first=row['sourceFrame'];edges={0,n}
    edges.update(range(0,n,6))
    edges.update(k['sourceFrame']-first for k in guides['streams'].get(row['sourceId'],[])
                 if first<k['sourceFrame']<first+n)
    edges=sorted(edges)
    return list(zip(edges,edges[1:]))

def matching_guides(a,b):
    return bool(a)and[(x['label'],x['colorRole'])for x in a]==[(x['label'],x['colorRole'])for x in b]

def move_tag(start_local_frame,count,start_guide,end_guide):
    r"""Continuous60fps libass sampling of the existing source-key interpolation.

    ASS event bounds are centiseconds. Floor them so the interval contains
    exactly the intended native video frames, then offset \move's millisecond
    clock to the actual first frame. No6-frame position hold is introduced.
    """
    if count<=1:return r'\pos(0,0)'
    dx=(end_guide['point'][0]-start_guide['point'][0])*896
    dy=(end_guide['point'][1]-start_guide['point'][1])*504
    floored_cs=start_local_frame*100//60
    t0=round((start_local_frame/60-floored_cs/100)*1000)
    t1=t0+round((count-1)*1000/60)
    return f'\\move(0,0,{dx:.4f},{dy:.4f},{t0},{t1})'

def ass_scene(scene,rows,j,guides,guide_module):
    sid=scene['id'];start=scene['startFrame'];text=header();drawn=hidden=0
    from PIL import ImageFont
    ff=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',64)
    for row in rows:
        a=row['startFrame']-start;b=row['endFrameExclusive']-start
        game=j['sources'][row['sourceId']]['game'];kind='실제 게임 재생'if row['kind']=='video'else'실제 화면 분석'
        assert ff.getlength(row['focus'])<=896,('Focus exceeds left pane',row['focus'])
        text+=event(a,b,'Game',r'{\an7\pos(40,184)}'+escape(game))
        text+=event(a,b,'Kind',r'{\an5\pos(488,782)}'+kind)
        text+=event(a,b,'Focus',r'{\an5\pos(488,848)}'+focus_markup(row,guides))
        for local,local_end in guide_windows(row,guides):
            moving=row['kind']=='video';sf=row['sourceFrame']+(local if moving else 0)
            last_sf=sf+(local_end-local-1 if moving else 0)
            gs=guide_module.at(guides,row['sourceId'],sf)
            end_gs=guide_module.at(guides,row['sourceId'],last_sf)
            # A hide/unknown endpoint hides the entire tiny interval. Explicit
            # key boundaries above prevent interpolation through an occlusion.
            if not matching_guides(gs,end_gs):hidden+=1;continue
            for g,end_g in zip(gs,end_gs):
                c=color(guides['colorRoles'][g['colorRole']])
                position=move_tag(a+local,local_end-local,g,end_g)if moving else r'\pos(0,0)'
                for drawing in guide_paths(g):
                    # Filled6px stroke strips preserve open corners; there is
                    # no implicit closed-polygon diagonal or decorative glow.
                    tags=r'{\an7'+position+r'\p1\bord0\shad0\1a&H00&\1c'+c+r'\clip(40,250,936,754)}'
                    text+=event(a+local,a+local_end,'Vector',tags+drawing+r'{\p0}',3,native_frame_boundaries=True);drawn+=1
    f=G/'scene-ass'/(sid+'.ass');f.parent.mkdir(parents=True,exist_ok=True);f.write_text(text,encoding='utf-8-sig')
    return dict(file=rel(f),sha256=sha(f),timeBase='scene-local60fps; guide event centiseconds floored and move clock offset to actual first native frame',sourceKeyedGuideEvents=drawn,
        guideMotion='Continuous libass move sampled each60fps video frame, using unchanged linear source anchors. At most100ms per event, split at every source/hide key; no6-frame coordinate hold or occlusion bridge.',
        hiddenGuideSamples=hidden,full1920and375MovingReview='pending final current paired encode; anchor interpolation is not approval')

def build(direct=False,allow_missing=False):
    tm=module('v7_left_actual_timing','timing.py');tm.authorized();clock=tm.Clock()
    prep=module('v7_left_actual_prepare','left-prepare.py');gm=module('v7_left_actual_guides','left-guides.py')
    j=read(H/'game-inputs.json');plan=read(P/'planning/revision-v7-two-part/part-01-left-game-plan.json')
    assets=prep.design();totals=source_totals(prep,j);guides=gm.build()
    rows,beats,issues=segments(clock,j,plan,assets,totals,direct)
    critical=[x for x in issues if x['kind']in ['boundary-trim','no-room-before-scene-boundary']]
    if critical:raise RuntimeError('Useful native action/result would be lost at a scene boundary; explicitly repair source windows, never silently truncate: '+json.dumps(critical,ensure_ascii=False))
    missing=sorted({x['file']for x in rows if not path(x['file']).exists()})
    if missing and not allow_missing:raise RuntimeError('Run left-prepare.py --prepare-stills first; preserve input plan. Missing '+str(missing[:5]))
    ass={s['id']:ass_scene(s,[x for x in rows if x['sceneId']==s['id']],j,guides,gm)for s in clock.timeline['scenes']}
    result=dict(schemaVersion=1,part=1,status='timed-source-manifest-ready'if not missing else'planned-missing-frames-not-renderable',
        width=1920,height=1080,fps=60,rect=RECT,sourceAspectPreserved=True,sourceRaster=[1920,1080],
        segments=rows,sceneASS=ass,liveBeats=beats,sourceContainers=totals,
        inputs=dict(timelineSha256=sha(H/'timeline.json'),gameInputsSha256=sha(H/'game-inputs.json'),
            leftPlanSha256=sha(P/'planning/revision-v7-two-part/part-01-left-game-plan.json'),
            guideKeysSha256=sha(G/'guide-keys.json'),implementationSha256=sha(Path(__file__))),
        measuredUniqueLiveFrames=sum(x['endFrameExclusive']-x['startFrame']for x in rows if x['kind']=='video'),
        measuredAnalysisFrames=sum(x['endFrameExclusive']-x['startFrame']for x in rows if x['kind']=='still'),
        noLoops=True,sourceSpeed=1,insertedSpeechPauseFrames=0,missingFiles=missing,timingIssues=issues,
        sceneBoundaryTruncations=0,explicitSourceCuts={q['id']:q.get('explicitSourceCuts',[])for q in j['livePhases']if q.get('explicitSourceCuts')},
        sourceAudioPolicy='Exact native sourceStartSeconds/duration under original standard mix only for live segments; no audio under frozen analysis.',
        finalQA='Actual action cue drift, all moving guide anchors/occlusion, speech/motion relation and native/mobile pixel review pending')
    save(H/'left-visual-segments.json',result)
    print(json.dumps(dict(scenes=len(clock.timeline['scenes']),segments=len(rows),liveFrames=result['measuredUniqueLiveFrames'],
        analysisFrames=result['measuredAnalysisFrames'],cueIssues=len(issues),missing=len(missing),directSource=direct)))
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--design',action='store_true');ap.add_argument('--build',action='store_true')
    ap.add_argument('--direct-source',action='store_true');ap.add_argument('--allow-missing-frames',action='store_true');a=ap.parse_args()
    if a.build:build(a.direct_source,a.allow_missing_frames)
    elif a.design:
        j=design();print(json.dumps(dict(modules=j['modules'],nativeSeconds=j['nativeSeconds'],actualClockFabricated=False,mediaDecoded=False)))
    else:ap.print_help()
if __name__=='__main__':main()

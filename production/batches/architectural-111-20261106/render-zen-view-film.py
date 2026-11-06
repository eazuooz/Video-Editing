"""07.04 finite portrait compositor. Import/default validation starts no process.

--sample-frame is an explicit still-creation operation; --execute encodes one
fresh C-media attempt. A coordinator must establish resource ownership first.
No engine/model/GPU/browser, platform, project state or first-film writes.
"""
from __future__ import annotations
import argparse,bisect,copy,hashlib,importlib.util,json,math,os,shutil,subprocess,time,uuid
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image,ImageDraw

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PROJECT=ROOT/'projects/shorts-leveldesign-07-04';SLUG=PROJECT.name
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')/SLUG
FIRST=ROOT/'projects/shorts-leveldesign-03-02'
FPS=60;SIZE=(1080,1920);PANEL=(48,410,880,495);LOWER=(48,992,880,495)
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
GUIDES=('centerline','mouths')
CONTROLLER=None

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def save(p,value):
    p=Path(p);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,p)
def owned_popen(command,**kwargs):
    if CONTROLLER is None:raise RuntimeError('Expensive process requires selected compositor resource ownership')
    return CONTROLLER.launch(command,**kwargs)
def bound(row,role):
    if not isinstance(row,dict) or not isinstance(row.get('path'),str) or not isinstance(row.get('sha256'),str):raise ValueError('Missing pin: '+role)
    p=Path(row['path']).resolve()
    if not p.is_file() or sha(p)!=row['sha256']:raise ValueError('Changed input: '+role)
    return p
def integer(v):return type(v)is int
def span(row):
    a,b=row.get('startFrame'),row.get('endFrameExclusive')
    if not integer(a)or not integer(b)or not 0<=a<b:raise ValueError('Positive integer end-exclusive frame interval required')
    return a,b
def native_frame(section,frame):
    a,b=span(section)
    if not a<=frame<b:raise ValueError('Frame outside section')
    n=section['native'];return n['startNativeFrame'] if n.get('holdPolicy') else n['startNativeFrame']+frame-a
def source_index(pts,desired):
    if not pts or not math.isfinite(desired):raise ValueError('Actual finite source clock required')
    i=bisect.bisect_right(pts,desired+.000001)-1
    if i<0:raise ValueError('No presented source frame; never invent a hold')
    return i
def section_at(timeline,frame):
    if not integer(frame)or not 0<=frame<timeline['totalFrames']:raise ValueError('Output frame outside film')
    i=bisect.bisect_right([s['startFrame']for s in timeline['sections']],frame)-1
    return timeline['sections'][i]
def cat_allowed(section):return section['kind']=='native'and section['native']['layout']=='singlePlayer'

def validate_structure(t):
    if t.get('schemaVersion')!='07-04-final-timeline-v1'or t.get('topicId')!='07.04'or t.get('format')!=dict(width=1080,height=1920,fps=60):raise ValueError('Only selected07.04 portrait60 timeline supported')
    total=t.get('totalFrames');sections=t.get('sections')
    if not integer(total)or total<=0 or not isinstance(sections,list)or not sections:raise ValueError('Complete finite timeline required')
    cursor=0;ids=set();moving={'narrow':[],'wide':[]};game={};mc={};freezes=0
    for s in sections:
        a,b=span(s)
        if a!=cursor or b>total or not s.get('id')or s['id']in ids:raise ValueError('Unique contiguous picture cuts must cover every frame')
        cursor=b;ids.add(s['id']);kind=s.get('kind')
        if s.get('loop')or s.get('interpolate'):raise ValueError('No source loops or synthetic interpolated motion')
        if kind in ('gameplay','observation-freeze','mc'):
            if any(not isinstance(s.get(k),str)or not s[k]for k in ('sourcePath','sourceSHA256')):raise ValueError('Source path/hash required')
        if kind=='gameplay':
            p=s.get('sourceLocalInPts')
            if type(s.get('rate'))not in (int,float)or s['rate']!=1 or isinstance(p,bool)or not isinstance(p,(int,float))or not math.isfinite(p)or p<0 or not s.get('sourceId'):raise ValueError('Actual gameplay must retain exact1x motion and source PTS')
            window=(p,p+(b-a)/FPS)
            if any(min(v,window[1])-max(u,window[0])>.000001 for u,v in game.setdefault(s['sourceId'],[])):raise ValueError('Repeated actual-game motion interval')
            game[s['sourceId']].append(window)
            if s.get('holdPolicy')or s.get('annotationCues'):raise ValueError('Moving-source guides need separately verified tracks; no implicit holds')
        elif kind=='observation-freeze':
            freezes+=1
            if s.get('sourceFrameIndex')!=150 or s.get('sourceLocalPts')!=2.5 or not s.get('holdReason')or s.get('label')!='관찰용 정지':raise ValueError('Observation freeze must use exact sourceFrame150/PTS2.5 and an explicit teaching reason')
            if not s.get('sourceId'):raise ValueError('Freeze retains actual independent source identity')
            inset=s.get('detailInset')
            if inset is not None and inset!=dict(sourceCropXYXY=[1500,280,1740,500],destinationXYWH=[70,1010,360,330],label='창밖 표지판 확대'):raise ValueError('Only reviewed same-frame CF-sign detail crop/placement supported')
        elif kind=='native':
            n=s.get('native',{});layout=n.get('layout');mode=n.get('mode')
            if layout not in ('singlePlayer','dual','sameClockAB')or mode not in moving:raise ValueError('Only existing native views/modes supported')
            first,count=n.get('startNativeFrame'),n.get('frameCount')
            if not integer(first)or not integer(count)or not 0<=first<480 or not 1<=count<=480-first or type(n.get('playbackRate'))not in (int,float)or n['playbackRate']!=1:raise ValueError('Exact native0..479 clock at1x required')
            hold=n.get('holdPolicy')
            if hold is not None:
                if not isinstance(hold,dict)or hold.get('frame')!=first or count!=1 or not hold.get('reason'):raise ValueError('Native still needs explicit actual frame and teaching reason')
            else:
                if count!=b-a:raise ValueError('Moving native duration must equal source frame count')
                for m in (('narrow','wide')if layout=='sameClockAB'else(mode,)):moving[m].extend(range(first,first+count))
            parts=s.get('guideParts',[])
            if not isinstance(parts,list)or len(parts)!=len(set(parts))or any(p not in GUIDES for p in parts):raise ValueError('Only actual centerline/mouth native guides supported')
        elif kind=='mc':
            start,count=s.get('sourceStartFrame'),s.get('frameCount')
            if not integer(start)or start<0 or count!=b-a or s.get('rate')!=1 or type(s.get('rate'))is bool or not s.get('cropManifest'):raise ValueError('Exact silent MC crop1x clock/manifest required')
            r=mc.setdefault(s['sourcePath'],[])
            if any(min(v,start+count)>max(u,start)for u,v in r):raise ValueError('Repeated MC motion')
            r.append((start,start+count))
        else:raise ValueError('Unsupported picture kind')
        if s.get('catPose'):raise ValueError('Use explicit timed catCues only')
        terms=s.get('termChips',[])
        if len(terms)>1 or (terms and kind!='native'):raise ValueError('At most one term overlay on our native scene')
        for term in terms:
            if term.get('presentation')not in ('definition','chip')or any(not isinstance(term.get(k),str)or not term[k].strip()for k in ('english','korean','meaning')):raise ValueError('Canonical English/Korean/plain-meaning term required')
    if cursor!=total or freezes>1:raise ValueError('Incomplete film or duplicate observation freeze')
    for mode,frames in moving.items():
        if frames and frames!=list(range(480)):raise ValueError('Each moving mode must present0..479 once, without omissions/repeated motion')
    last=0
    for c in t.get('catCues',[]):
        a,b=span(c)
        if a<last or b>total or c.get('pose')not in ('puzzled','realize','relief'):raise ValueError('Nonoverlapping approved reaction cues required')
        if any(not integer(c.get(k))or not 0<c[k]<=b-a for k in ('easeInFrames','easeOutFrames')):raise ValueError('Bounded reaction easing required')
        if any(not cat_allowed(s)for s in sections if max(a,s['startFrame'])<min(b,s['endFrameExclusive'])):raise ValueError('Large cat only single-player; forbidden on actual/dual/AB/maps')
        if any(any(term['presentation']=='definition'for term in s.get('termChips',[]))for s in sections if max(a,s['startFrame'])<min(b,s['endFrameExclusive'])):raise ValueError('Term definition must not be obscured by the large cat')
        last=b
    for language in ('ko','en'):
        last=0
        for c in t.get('captions',{}).get(language,[]):
            a,b=span(c)
            if a<last or b>total or not c.get('text')or not 1<=len(c.get('lines',[]))<=2 or ' '.join(c['lines'])!=c['text']:raise ValueError('Exact nonoverlapping authored caption text/lines required')
            if len(c.get('emphasis',[]))>1:raise ValueError('At most one emphasized caption span')
            last=b
    return dict(totalFrames=total,sections=len(sections),movingNativeFrames={k:len(v)for k,v in moving.items()},observationFreezes=freezes)

def style_adapter():
    """Reuse verified style-only methods, never instantiate first-film scene state."""
    m=module('zen_style_only',FIRST/'production/composite-native-frame.py');o=m.NativeFrameComposer.__new__(m.NativeFrameComposer)
    o.spec=copy.deepcopy(read(FIRST/'visual-layout-v1.json'));o.spec['caption']['nativeCenter']=[488,1600]
    o.tokens=o.spec['tokens']['scene'];o.caption_tokens=o.spec['tokens']['caption'];o.font_cache={};o.cat_images={}
    for pin in o.spec['fontMeasurement']['fontFiles']:bound(pin,'approved style font')
    for pose in o.spec['cat']['poses']:
        p=bound(dict(path=str(ROOT/pose['path']),sha256=pose['sha256']),'approved original cat')
        with Image.open(p)as im:o.cat_images[pose['pose']]=im.convert('RGBA')
    return o

def emphasis(cue):
    spans=cue.get('emphasis',[])
    if not spans:return None
    if len(spans)!=1:raise ValueError('Single emphasis only')
    e=spans[0];a,b=e['start'],e['end'];text=cue['text']
    if not integer(a)or not integer(b)or not 0<=a<b<=len(text)or e['role']not in ('term','problem','result'):raise ValueError('Invalid authored emphasis')
    offset=0
    for i,line in enumerate(cue['lines']):
        if offset<=a<b<=offset+len(line):return(i,a-offset,b-offset,e['role'])
        offset+=len(line)+1
    raise ValueError('Emphasis crosses wrapped line')

def verify_inputs(t,require_mix=True):
    result=validate_structure(t)
    if t.get('status')!='final-asr-aligned':raise ValueError('Actual current ASR-aligned timeline required')
    rows=t.get('inputs',[])
    required={'layout':PROJECT/'edit-layout-v1.json','native-evidence':PROJECT/'native-evidence-v1.json','native-helper':HERE/'prepare-zen-view-previews.py','style':FIRST/'visual-layout-v1.json','style-helper':FIRST/'production/composite-native-frame.py','stream-helper':HERE/'render-first-film.py','opening-focus':PROJECT/'opening-focus-v1.json','source-footage':PROJECT/'source-footage.json','narration':PROJECT/'narration-draft.json','render-helper':Path(__file__)}
    for row in rows:bound(row,row.get('role','input'))
    for role,path in required.items():
        selected=[r for r in rows if r.get('role')==role]
        if len(selected)!=1 or Path(selected[0]['path']).resolve()!=path.resolve():raise ValueError('Missing exact selected '+role+' pin')
    if not all(any(r.get('role')==role for r in rows)for role in ('caption-timing','voice-evidence','asr')):raise ValueError('Current caption/voice/blind-ASR proofs required')
    timing=read(next(r['path']for r in rows if r.get('role')=='caption-timing'))
    if timing.get('topicId')!='07.04'or t.get('captions')!=timing.get('captions')or t['totalFrames']!=timing['totalFrames']:raise ValueError('Captions/film clock differ from exact selected ASR timing')
    for pin in timing['inputs']:bound(pin,'caption timing input')
    ve=read(next(r['path']for r in rows if r.get('role')=='voice-evidence'))
    if ve.get('aggregateWav')!=t.get('audio',{}).get('voice')or timing['voiceBinding']['voiceFingerprint']!=ve['fingerprint']:raise ValueError('Canonical voice differs from bound timing')
    evidence=read(PROJECT/'native-evidence-v1.json')
    if evidence.get('captureComplete')is not True or evidence.get('topicId')!='07.04':raise ValueError('Actual completed native evidence required')
    for pin in evidence['captureProofs']:bound(pin,'native capture proof')
    hashes=read(bound(evidence['frameHashManifest'],'native frame hash manifest'))
    if hashes['fingerprint']!=evidence['fingerprint']or len(hashes['frames'])!=1920:raise ValueError('Complete native frame manifest required')
    for record in hashes['frames']:
        p=Path(evidence['output'])/record['path']
        if not p.is_file()or p.stat().st_size!=record['bytes']:raise ValueError('Missing native JPEG before encoding')
    style=style_adapter()
    for lang in ('ko','en'):
        for cue in t['captions'][lang]:style._captions(Image.new('RGB',(1,1)),tuple(cue['lines']),emphasis(cue))
        bound(t.get('subtitles',{}).get(lang),lang+' SRT')
    sources={s['id']:s for s in read(PROJECT/'source-footage.json')['sources']if s.get('selectedForCut')and s.get('rightsVerified')and s.get('decodedDimensionsVerified')}
    for s in t['sections']:
        if s['kind']in ('gameplay','observation-freeze'):
            source=sources.get(s['sourceId'])
            if not source or source['sha256']!=s['sourceSHA256']or Path(source['path']).resolve()!=Path(s['sourcePath']).resolve():raise ValueError('Independent source not currently selected/rights-verified')
            bound(dict(path=s['sourcePath'],sha256=s['sourceSHA256']),'actualgame')
            if s['kind']=='observation-freeze'and source['id']!=read(PROJECT/'opening-focus-v1.json')['source']['id']:raise ValueError('Freeze target is from another source')
        elif s['kind']=='mc':
            p=bound(s['cropManifest'],'actual silent crop manifest');m=read(p)
            if m.get('topicId')!='07.04'or not m.get('complete')or m.get('schemaVersion')!='07-04-mc-crop-render-v1'or m['contract']['width']!=1080 or m['contract']['height']!=900 or m['contract']['fps']!=60 or m['contract']['audio']is not False:raise ValueError('Actual current MC crop proof required')
            if Path(m['output']['path']).resolve()!=Path(s['sourcePath']).resolve()or m['output']['sha256']!=s['sourceSHA256']or s['sourceStartFrame']+s['frameCount']>m['contract']['frames']:raise ValueError('MC crop identity/frame bounds differ')
            bound(m['output'],'MC crop')
            for pin in m['inputPins']:bound(pin,'MC bound input')
    import soundfile as sf
    voice=t.get('audio',{}).get('voice');vp=bound(voice,'exact canonical voice');info=sf.info(vp)
    if (info.samplerate,info.channels,info.frames)!=(voice.get('sampleRate'),voice.get('channels'),voice.get('frames')):raise ValueError('Canonical voice sample properties differ')
    mix=t.get('audio',{}).get('mix')
    if mix is None:
        if require_mix:raise ValueError('Real final voice+BGM mix is not ready')
        result['audioMixReady']=False
    else:
        p=bound(mix,'real final mix');inf=sf.info(p)
        if (inf.samplerate,inf.channels,inf.frames)!=(mix.get('sampleRate'),mix.get('channels'),mix.get('frames'))or abs(inf.frames/inf.samplerate-info.frames/info.samplerate)>1/inf.samplerate or t['totalFrames']!=math.ceil(inf.frames*60/inf.samplerate):raise ValueError('Final mix/film clock changes exact voice duration')
        result['audioMixReady']=True
    return result

def fresh_authorization():
    c=read(ROOT/'shared/publishing/video-production-control.json')['explicitArchitectural111Batch20261106'];b=read(HERE/'batch.json')
    if c['status']in ('paused','stopped','cancelled','canceled')or not c['automaticAdvanceWithinExactList']or c['automaticAdvanceOutsideList']or not b['localFinalReviewOnly']or not any(p['topicId']=='07.04'and p['slug']==SLUG for p in b['projects']):raise ValueError('Selected111 local-production authorization inactive')
    return dict(localFinalReviewOnly=True,controlSHA256=sha(ROOT/'shared/publishing/video-production-control.json'))

def probe_pts(path,size,ffprobe):
    p=owned_popen([ffprobe,'-v','error','-threads','1','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time,width,height','-of','json',str(path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=CREATE);out,err=p.communicate()
    if p.returncode:raise RuntimeError('Source PTS inspection failed')
    rows=json.loads(out)['frames']
    if not rows or any((r.get('width'),r.get('height'))!=tuple(size)for r in rows):raise ValueError('Actual decoded source dimensions differ')
    pts=[float(r['best_effort_timestamp_time'])for r in rows]
    if any(not math.isfinite(x)or x<0 for x in pts)or any(a>=b for a,b in zip(pts,pts[1:])):raise ValueError('Source PTS not strictly increasing')
    return pts

class StreamDecoder:
    """One pipe per cut; actual presented source PTS, no per-frame process."""
    def __init__(self,path,size,pts,start,frames,ffmpeg,log):
        first=source_index(pts,start);last=source_index(pts,start+(frames-1)/60)
        if start+(frames-1)/60>pts[-1]+1/60+.000001:raise ValueError('Cut would hold missing tail frames')
        self.selected=pts[first:last+1];self.size=tuple(size);self.index=-1;self.image=None;self.last=-math.inf;self.log=Path(log).open('xb')
        vf=f"select='between(t,{self.selected[0]-.0000005:.7f},{self.selected[-1]+.0000005:.7f})'"
        self.process=owned_popen([ffmpeg,'-hide_banner','-nostdin','-threads','1','-i',str(path),'-vf',vf,'-fps_mode','passthrough','-frames:v',str(len(self.selected)),'-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE,stderr=self.log,creationflags=CREATE)
    def at(self,desired):
        if desired<self.last:raise ValueError('No backwards source clock')
        self.last=desired
        while self.index+1<len(self.selected)and self.selected[self.index+1]<=desired+.000001:
            data=self.process.stdout.read(self.size[0]*self.size[1]*3)
            if len(data)!=self.size[0]*self.size[1]*3:raise RuntimeError('Truncated actual frame; never substitute/hold')
            self.image=Image.frombytes('RGB',self.size,data);self.index+=1
        if self.image is None:raise RuntimeError('No presented frame')
        return self.image,self.selected[self.index]
    def close(self,failed=False):
        if getattr(self,'closed',False):return
        self.closed=True;self.process.stdout.close()
        if failed and self.process.poll()is None:self.process.terminate()
        code=self.process.wait(timeout=30);self.log.close()
        if code and not failed:raise RuntimeError('Owned source decoder failed')

class FrameRouter:
    def __init__(self,timeline,work,ffmpeg,ffprobe):
        self.t=timeline;self.work=Path(work);self.ffmpeg=ffmpeg;self.ffprobe=ffprobe
        self.preview=module('zen_preview_actual',HERE/'prepare-zen-view-previews.py').ZenPreviewComposer();self.style=style_adapter()
        self.layout=read(PROJECT/'edit-layout-v1.json');self.focus=read(PROJECT/'opening-focus-v1.json')
        self.current=None;self.decoder=None;self.counter=0;self.pts={};self.freeze=None
    def base(self,subtitle=''):
        im=Image.new('RGB',SIZE,self.preview.tokens['background']);d=ImageDraw.Draw(im)
        for line in self.layout['header']['lines']:self.preview.text(d,line['text'],(488,line['centerY']),line['fontPx'],self.preview.tokens['title'if line['role']=='heading'else'ink'])
        if subtitle:self.preview.text(d,subtitle,(488,326),34,self.preview.tokens['muted'])
        return im
    def open_decoder(self,s,offset):
        size=(1080,900)if s['kind']=='mc'else(1920,1080);key=(s['sourcePath'],size)
        if key not in self.pts:self.pts[key]=probe_pts(s['sourcePath'],size,self.ffprobe)
        start=s['sourceStartFrame']/60 if s['kind']=='mc'else s['sourceLocalPts']if s['kind']=='observation-freeze'else s['sourceLocalInPts']
        count=1 if s['kind']=='observation-freeze'else s['endFrameExclusive']-s['startFrame']
        self.counter+=1;self.decoder=StreamDecoder(s['sourcePath'],size,self.pts[key],start+offset/60,count-offset,self.ffmpeg,self.work/f'decode-{self.counter:03}.log')
        return start
    def native_picture(self,s,frame):
        n=s['native'];f=native_frame(s,frame);layout=n['layout'];mode=n['mode'];im=self.base('같은 길과 카메라 · 틈 폭만 비교'if layout=='sameClockAB'else('좁은 틈'if mode=='narrow'else'넓은 창')+' · 같은 길과 카메라');d=ImageDraw.Draw(im);pins=[];marks=[]
        rows=[('narrow','player',PANEL),('wide','player',LOWER)]if layout=='sameClockAB'else[(mode,'player',PANEL)]+([(mode,'observer',LOWER)]if layout=='dual'else[])
        for m,camera,panel in rows:
            label=('좁은 틈'if m=='narrow'else'넓은 창')+' · 직접 만든 Unity 시연'if layout=='sameClockAB'else'직접 만든 Unity 시연 · 눈높이'if camera=='player'else'위에서 본 같은 순간 · 관찰용 단면'
            self.preview.text(d,label,(488,panel[1]-34),34,self.preview.tokens['relationship'if camera=='observer'else'ink'])
            pins.append(self.preview.picture(im,m,camera,f,panel));anchors,ray=self.preview.frame_data(m,f)
            if 'centerline'in s.get('guideParts',[]):
                if camera=='player':marks.extend(self.preview.player_mark(im,anchors,ray,panel))
                else:
                    eye=self.preview.point(anchors['eye'],'observer',panel);end=self.preview.point(anchors['fixed-landmark-center-actual-end'],'observer',panel);col=self.preview.tokens['result'if ray['visible']else'problem']
                    d.line([eye,end],fill=col,width=10)
                    for p in (eye,end):d.ellipse((p[0]-12,p[1]-12,p[0]+12,p[1]+12),outline=col,width=7)
                    self.preview.text(d,'카메라 눈',(panel[0]+185,panel[1]+452),32)
                    d.line([(panel[0]+270,panel[1]+449),eye],fill=self.preview.tokens['ink'],width=5)
                    label_pos=(panel[0]+660,panel[1]+175)if ray['visible']else(panel[0]+668,panel[1]+399)
                    self.preview.text(d,'중심 시야선 통과'if ray['visible']else'벽에 막힌 지점',label_pos,32,col)
                    d.line([(label_pos[0]-75,label_pos[1]+15),end],fill=col,width=6)
                    marks.append(dict(eye=eye,actualEndpoint=end,centerVisible=ray['visible']))
            if camera=='observer'and'mouths'in s.get('guideParts',[]):
                for name,tint,label,pos in [('front','relationship','입구',(panel[0]+188,panel[1]+353)),('back','title','출구',(panel[0]+650,panel[1]+260))]:
                    l=self.preview.point(anchors[name+'-left'],'observer',panel);r=self.preview.point(anchors[name+'-right'],'observer',panel);color=self.preview.tokens[tint]
                    d.line([l,r],fill=color,width=8)
                    for p in (l,r):d.line([(p[0],p[1]-9),(p[0],p[1]+9)],fill=color,width=5)
                    self.preview.text(d,label,pos,34,color)
                    d.line([pos,((l[0]+r[0])/2,(l[1]+r[1])/2)],fill=color,width=5)
        if n.get('holdPolicy'):self.preview.text(d,'설명을 위한 정지 화면',(488,926 if layout=='singlePlayer' else 1499),28,self.preview.tokens['muted'])
        return im,dict(nativeFrame=f,layout=layout,sources=pins,editorialGuides=marks,visibilityMeaning='Actual lighthouse center-point ray only; partial silhouette untouched',observerCutaway='Lintel rendering removed in observer only; physical ray/player occlusion unchanged')
    def compose(self,frame):
        s=section_at(self.t,frame);offset=frame-s['startFrame'];kind=s['kind']
        if self.current!=s['id']:
            if self.decoder:self.decoder.close(failed=self.decoder.index!=len(self.decoder.selected)-1);self.decoder=None
            self.freeze=None;self.current=s['id']
        if kind=='native':clean,evidence=self.native_picture(s,frame)
        else:
            if self.decoder is None:self.start=self.open_decoder(s,0 if kind=='observation-freeze'else offset)
            desired=self.start if kind=='observation-freeze'else(self.start+offset/60)
            if kind=='observation-freeze'and self.freeze is not None:picture,actual=self.freeze
            else:
                picture,actual=self.decoder.at(desired)
                if kind=='observation-freeze':self.freeze=(picture,actual)
            clean=self.base('Half-Life 2 · 실제 게임 화면'if kind!='mc'else'');d=ImageDraw.Draw(clean)
            if kind=='mc':
                if picture.size!=(1080,900):raise ValueError('Exact MC crop expected')
                clean.paste(picture,(0,500))
            else:
                clean.paste(picture.resize(PANEL[2:],Image.Resampling.LANCZOS),PANEL[:2])
                if kind=='observation-freeze':
                    if abs(actual-2.5)>.000002:raise ValueError('Exact verified freeze source frame missing')
                    key=next(k for k in self.focus['keyframes']if k['id']=='cf-0250');x1,y1,x2,y2=key['targetBBoxXYXY'];pad=36;sc=880/1920
                    box=(48+(x1-pad)*sc,410+(y1-pad)*sc,48+(x2+pad)*sc,410+(y2+pad)*sc)
                    d.ellipse(box,outline=self.preview.tokens['result'],width=10)
                    self.preview.text(d,'창밖 표지판',(680,970),40,self.preview.tokens['result']);d.line([(680,943),((box[0]+box[2])/2,box[3]+8)],fill=self.preview.tokens['result'],width=7)
                    inset=s.get('detailInset')
                    if inset:
                        x,y,w,h=inset['destinationXYWH'];crop=picture.crop(inset['sourceCropXYXY'])
                        if crop.width*h!=crop.height*w:raise ValueError('Detail crop must preserve actual aspect ratio')
                        clean.paste(crop.resize((w,h),Image.Resampling.LANCZOS),(x,y));d.rectangle((x-4,y-4,x+w+4,y+h+4),outline=self.preview.tokens['result'],width=4)
                        self.preview.text(d,inset['label'],(x+w/2,y-33),34,self.preview.tokens['result'])
                    self.preview.text(d,s['label'],(680,1040),30,self.preview.tokens['muted'])
            evidence=dict(sourcePath=s['sourcePath'],sourceSHA256=s['sourceSHA256'],actualSourcePts=actual,sourceDimensions=list(picture.size),sourceAspectPreserved=True,annotations='exact observation frame only'if kind=='observation-freeze'else'none; cleared at source cut',freeze=kind=='observation-freeze')
        terms=s.get('termChips',[])
        if terms:
            term=terms[0];heading=term['english']+' ('+term['korean']+')';d=ImageDraw.Draw(clean)
            if self.style.font(40).getlength(heading)>800:raise ValueError('Canonical term heading exceeds measured width')
            if term['presentation']=='chip':
                # Replace only the secondary subtitle row. Keep the permanent
                # claim above and the picture-kind label below fully visible.
                d.rectangle((48,300,928,354),fill='black');self.style.text(d,heading,(488,326),40,self.style.tokens['title'])
            else:
                dim=Image.new('RGBA',SIZE,(0,0,0,0));ImageDraw.Draw(dim).rectangle((48,410,928,1487),fill=(0,0,0,110));clean=Image.alpha_composite(clean.convert('RGBA'),dim).convert('RGB');d=ImageDraw.Draw(clean)
                self.style.text(d,heading,(488,1060),40,self.style.tokens['title']);lines=[];line=''
                for word in term['meaning'].split():
                    if self.style.font(40).getlength(word)>760:raise ValueError('Definition word too wide')
                    candidate=(line+' '+word).strip()
                    if self.style.font(40).getlength(candidate)>760:lines.append(line);line=word
                    else:line=candidate
                if line:lines.append(line)
                if len(lines)>4:raise ValueError('Definition exceeds legible four-line scene area')
                for i,text in enumerate(lines):self.style.text(d,text,(488,1120+i*54),40,self.style.tokens['ink'])
        pose=None
        for cue in self.t.get('catCues',[]):
            a,b=span(cue)
            if a<=frame<b:
                pose=cue['pose'];cat=clean.copy();self.style._cat(cat,pose);alpha=min(1,(frame-a+1)/cue['easeInFrames'],(b-frame)/cue['easeOutFrames']);clean=Image.blend(clean,cat,alpha)
        captioned=clean.copy();cue=next((c for c in self.t['captions']['ko']if c['startFrame']<=frame<c['endFrameExclusive']),None)
        if cue:self.style._captions(captioned,tuple(cue['lines']),emphasis(cue))
        return clean,captioned,dict(outputFrame=frame,sectionId=s['id'],source=evidence,captionId=cue['id']if cue else None,catPose=pose)
    def close(self,failed=False):
        if self.decoder:self.decoder.close(failed);self.decoder=None

def output_root(value=None):
    expected=(MEDIA/'render-attempts').resolve();p=Path(value).resolve()if value else expected
    if p!=expected:raise ValueError('Only selected07.04 C-media render-attempts output permitted')
    return p
def run(command,log):
    fresh_authorization()
    with Path(log).open('xb')as f:r=owned_popen([str(x)for x in command],stdout=f,stderr=subprocess.STDOUT,creationflags=CREATE);code=r.wait()
    if code:raise RuntimeError('Owned ffmpeg stage failed; preserve exact log')

class VideoEncoder:
    """Verified first-film software encoding pattern with exact child tracking."""
    def __init__(self,path,frames,ffmpeg,log):
        self.log=Path(log).open('xb')
        self.process=owned_popen([ffmpeg,'-hide_banner','-nostdin','-f','rawvideo','-pixel_format','rgb24','-video_size','1080x1920','-framerate','60','-i','pipe:0','-an','-c:v','libx264','-threads','2','-preset','medium','-crf','18','-pix_fmt','yuv420p','-frames:v',str(frames),'-video_track_timescale','60000','-movflags','+faststart','-n',str(path)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=self.log,creationflags=CREATE)
    def write(self,image):self.process.stdin.write(image.tobytes())
    def close(self,failed=False):
        if getattr(self,'closed',False):return
        self.closed=True;error=None
        try:
            if not self.process.stdin.closed:self.process.stdin.close()
        except (BrokenPipeError,OSError)as e:error=e
        if failed and self.process.poll()is None:self.process.terminate()
        code=self.process.wait(timeout=300);self.log.close()
        if (code or error)and not failed:raise RuntimeError('Owned software encoder failed')

def _render(path,attempt,sample_frame=None):
    path=Path(path).resolve();t=read(path);inspection=verify_inputs(t,require_mix=sample_frame is None);authority=fresh_authorization()
    shared=module('zen_verified_stream_encoder',HERE/'render-first-film.py');ffmpeg,ffprobe=shared.binaries()
    work=attempt/'work';work.mkdir()
    tsha=sha(path);(attempt/'timeline.input.json').write_bytes(path.read_bytes());router=None;encoders=[]
    try:
        router=FrameRouter(t,work,ffmpeg,ffprobe)
        if sample_frame is not None:
            clean,captioned,e=router.compose(sample_frame)
            for kind,picture in [('clean',clean),('captioned',captioned)]:
                picture.save(attempt/f'sample-{sample_frame:06d}.{kind}.png');picture.resize((375,667),Image.Resampling.LANCZOS).save(attempt/f'sample-{sample_frame:06d}.{kind}.375px.png')
            (attempt/'sample-evidence.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n',encoding='utf8');router.close(True)
            return dict(status='sample-only-no-film',output=str(attempt),actualMotionReviewed=False,actualSpeechTimingReviewed=False)
        aac=work/'shared-audio.m4a';mix=t['audio']['mix'];run([ffmpeg,'-hide_banner','-nostdin','-i',mix['path'],'-vn','-c:a','aac','-b:a','192k','-n',aac],work/'audio-encode.log')
        video={k:work/(k+'.video.mp4')for k in ('clean','captioned')}
        for k in ('clean','captioned'):encoders.append(VideoEncoder(video[k],t['totalFrames'],ffmpeg,work/(k+'-encode.log')))
        samples=[]
        for frame in range(t['totalFrames']):
            if frame%60==0:
                fresh_authorization()
                if sha(path)!=tsha:raise ValueError('Timeline changed during render')
            clean,captioned,e=router.compose(frame);encoders[0].write(clean);encoders[1].write(captioned)
            if frame in {s['startFrame']for s in t['sections']}:samples.append(e)
        router.close();[e.close()for e in encoders];encoders=[];outputs={}
        for kind in ('clean','captioned'):
            target=attempt/f'{SLUG}.{kind}.mp4';run([ffmpeg,'-hide_banner','-nostdin','-i',video[kind],'-i',aac,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart','-n',target],work/(kind+'-mux.log'));outputs[kind]=dict(path=str(target),sha256=sha(target))
        for lang in ('ko','en'):
            p=bound(t['subtitles'][lang],lang+' SRT');target=attempt/f'{SLUG}.{lang}.srt';target.write_bytes(p.read_bytes());outputs[lang]=dict(path=str(target),sha256=sha(target))
        if sha(path)!=tsha:raise ValueError('Timeline changed before completion')
        verify_inputs(t);fresh_authorization()
        result=dict(schemaVersion='07-04-render-manifest-v1',slug=SLUG,topicId='07.04',complete=True,timeline=dict(path=str(path),sha256=tsha),format=dict(width=1080,height=1920,fps=60,totalFrames=t['totalFrames']),outputs=outputs,audioAac=dict(path=str(aac),sha256=sha(aac),sharedPacketCopy=True),inputs=t['inputs'],inspection=inspection,authorization=authority,sectionStartSamples=samples,renderer=dict(path=str(Path(__file__)),sha256=sha(__file__),gpuUsed=False,modelStarted=False),encodedMotionQA=False,humanListening=False,humanFinalApproval=False,platformActions=[])
        (attempt/'render-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');return result
    except BaseException as error:
        if router:
            try:router.close(True)
            except Exception:pass
        for e in encoders:
            try:e.close(True)
            except Exception:pass
        (attempt/'failed.json').write_text(json.dumps(dict(complete=False,error=str(error),timelineSHA256=tsha),indent=2)+'\n',encoding='utf8');raise

def pending_child(rec,runtime):
    """Conservatively preserve exact command launch gaps and recorded children."""
    if any(runtime.alive(c)for c in rec.get('children',[])):return True
    command=rec.get('pendingCommand')
    if not command:return False
    import psutil
    for p in psutil.process_iter(['cmdline','create_time']):
        try:
            if p.info['cmdline']==command and p.info['create_time']>=rec.get('pendingAfter',0)-.1:return True
        except psutil.NoSuchProcess:continue
        except psutil.AccessDenied:return True
    return False

def reclaimable_lease(rec,known,runtime):
    return (runtime.ours(rec)and rec['token']in known and not runtime.alive(rec)
        and not runtime.alive(rec.get('child'))and not pending_child(rec,runtime))

class OwnedController:
    def __init__(self,runtime,worker,record):self.runtime=runtime;self.worker=worker;self.record=record;self.handles=[]
    def write(self):
        current=read(self.runtime.LEASE)
        if not self.runtime.ours(current)or current['token']!=self.record['token']:raise RuntimeError('Preserve changed/foreign resource lease')
        save(self.runtime.LEASE,self.record);self.worker.update(child=self.record.get('child'),children=self.record.get('children',[]))
    def launch(self,command,**kwargs):
        fresh_authorization();command=[str(x)for x in command]
        self.record.update(phase='launching',pendingCommand=command,pendingAfter=time.time());self.write()
        child=subprocess.Popen(command,**kwargs);self.handles.append(child);identity=self.runtime.identity(child.pid)
        self.record.setdefault('children',[]).append(identity);self.record.update(child=identity,phase='running',pendingCommand=None);self.write();return child
    def terminate_owned(self):
        for p in self.handles:
            if p.poll()is None:p.terminate()
        for p in self.handles:
            try:p.wait(timeout=30)
            except subprocess.TimeoutExpired:pass # lease remains while possibly live

def execute(path,output=None,sample_frame=None):
    global CONTROLLER
    path=Path(path).resolve();timeline=read(path);verify_inputs(timeline,require_mix=sample_frame is None);fresh_authorization();root=output_root(output)
    if sample_frame is not None:section_at(timeline,sample_frame)
    resource=module('zen_composite_isolated_resource',HERE/'run-zen-view-native.py');rt=resource.runtime
    rt.PROTOCOL='architectural111-07-04-composite-v1';rt.OWNER='architectural-111-07-04-composite'
    worker_path=MEDIA.parent/'07-04-composite-worker.json';state=MEDIA.parent/'07-04-composite-progress.json'
    worker=rt.SingleWorker(worker_path).acquire();token=None;rec=None;controller=None;known=set();attempt=None
    try:
        old=worker.previous or {};known=set(old.get('recoverableLeaseTokens',[]))
        if old.get('leaseToken'):known.add(old['leaseToken'])
        worker.update(recoverableLeaseTokens=sorted(known))
        if rt.LEASE.exists():
            oldlease=read(rt.LEASE)
            if reclaimable_lease(oldlease,known,rt):rt.archive(rt.LEASE,oldlease['token'])
        reason=resource.busy_reason()
        if reason:return dict(status='resource-declined-no-process',reason=reason,exitCode=75)
        if shutil.disk_usage(MEDIA).free<3*1024**3:raise ValueError('Preserve old media; require3GiB C reserve')
        attempt=root/(datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:10]);attempt.mkdir(parents=True,exist_ok=False)
        proposed=uuid.uuid4().hex;rec=dict(protocol=rt.PROTOCOL,owner=rt.OWNER,token=proposed,**rt.identity(),child=None,children=[],phase='reserved',output=str(attempt),timelineSHA256=sha(path))
        try:
            with rt.LEASE.open('x',encoding='utf8')as f:json.dump(rec,f)
        except FileExistsError:return dict(status='resource-race-no-process',exitCode=75)
        token=proposed;known.add(token);worker.update(leaseToken=token,recoverableLeaseTokens=sorted(known),attempt=str(attempt));controller=OwnedController(rt,worker,rec);CONTROLLER=controller
        if resource.busy_reason(token):raise RuntimeError('Resources changed after lease reservation; nothing launched')
        save(state,dict(rec,status='compositing-owned-software-only',gpuEncoding=False,modelStarted=False,complete=False))
        result=_render(path,attempt,sample_frame);save(state,dict(rec,status=result.get('status','encoded-local-review-pending'),complete=bool(result.get('complete')),gpuEncoding=False,modelStarted=False));return result
    except BaseException as error:
        if controller:controller.terminate_owned()
        save(state,dict(protocol=rt.PROTOCOL,owner=rt.OWNER,**rt.identity(),status='failed-preserved',complete=False,error=str(error),output=str(attempt)if attempt else None,children=rec.get('children',[])if rec else [],recoverableLeaseTokens=sorted(known)));raise
    finally:
        CONTROLLER=None;live=bool(rec and (rt.alive(rec.get('child'))or pending_child(rec,rt)))
        if token and not live and rt.LEASE.exists():
            current=read(rt.LEASE)
            if rt.ours(current)and current['token']==token:rt.LEASE.unlink()
        unresolved=rt.LEASE.exists()and rt.ours(read(rt.LEASE))and read(rt.LEASE).get('token')in known
        worker.close(remove=not live and not unresolved)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--timeline',required=True);p.add_argument('--execute',action='store_true');p.add_argument('--sample-frame',type=int);p.add_argument('--output-root');a=p.parse_args()
    if a.execute and a.sample_frame is not None:raise ValueError('Choose single-frame sample or complete film')
    if a.execute or a.sample_frame is not None:result=execute(a.timeline,a.output_root,a.sample_frame)
    else:
        t=read(a.timeline);result=dict(status='CPU-contract-only-no-process',structure=validate_structure(t))
        try:result['readiness']=verify_inputs(t)
        except (ValueError,OSError)as e:result.update(status='not-ready-no-process',reason=str(e))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if result.get('exitCode'):return result['exitCode']
if __name__=='__main__':raise SystemExit(main())

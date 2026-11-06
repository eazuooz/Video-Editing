"""Frame-exact selected module edit. Native game motion, original continuous narration.

Preparation writes captions/annotation instructions only. Rendering requires a
finished word-aligned Unity queue and the exclusive resource lease. Completion
here means encoded files, never human listening or visual approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, html, importlib.util, json, math, os, re, shutil, subprocess, time, uuid
import psutil

R=Path(__file__).resolve().parents[3];FPS=60;SR=48000
BOOT=argparse.ArgumentParser(add_help=False);BOOT.add_argument('--queue',required=True);BA,_=BOOT.parse_known_args();QB=json.loads(Path(BA.queue).read_text(encoding='utf-8-sig'));P=R/'projects'/QB['project']
CONTROL=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf-8-sig'))['explicitMathRemainingBatch20261104'];assert CONTROL['productionAllowedNow'] and P.name in CONTROL['projectSlugs'] and P.name!='game-math-shading-lights'
FF=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')
LEASE=R/'shared/output/GPU_HANDOFF.json';CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
VIEW=(192,48,1536,864)
GAME_LABELS={'_wH_-1saHnw':'슈퍼 마리오 오디세이','4Odvp_TIeQU':'라이더스 리퍼블릭',
 'Hu94MHBQCis':'둠 3 (2004)','FRfnXAIbA-M':'타운스케이퍼','AmJ4orxVpss':'포털',
 'xPnKcvo8A1E':'포르자 호라이즌 5','YNQ20CKbY8U':'젤다: 왕국의 눈물','T3ncWUwKUns':'비시지',
 'd5fiou39Htc':'BeamNG.drive','Eoh7qwVDsbk':'BeamNG.drive','_HVv2GnldbU':'새티스팩토리',
 'E-Sj-E0Ssds':'슈퍼 마리오 메이커 2','HALSoFBzIlw':'슈퍼 마리오 갤럭시'}
BOOK=R/'projects/game-reward-planning/production/final-v1/white-segments'

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
C=module('existing_caption_geometry',R/'projects/buckshot-roulette-reverse-engineering/production/assemble_documentary.py')
G=module('resource_guard',R/'projects/game-math-shading-lights/production/run-capture-queue.py')
PIPELINE_FIGURES=module('pipeline_figures',Path(__file__).parent/'part2/pipeline_figures.py') if P.name=='game-math-pipeline-shaders' else None
VELOCITY_FIGURES=module('velocity_figures',Path(__file__).parent/'part2/velocity_figures.py') if P.name=='game-math-velocity-derivatives' else None
VELOCITY_ART=module('diagram_art',Path(__file__).parent/'part2/pipeline_figures.py') if VELOCITY_FIGURES else None
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def probe(p):return json.loads(subprocess.check_output([str(FF.with_name('ffprobe.exe')),'-v','error','-show_streams','-show_format','-of','json',str(p)],creationflags=CREATE))
def reuse_visual_only_segment(args,log,cwd,target,signature):
    work=Path(BA.queue).resolve().parent
    if target is None or not target.is_relative_to(work/'composite'):return False
    file=P/'production/part2-review/final-picture-correction.json'
    if not file.exists():return False
    proof=read(file)
    if not proof.get('reuseIdenticalSegments') or proof['renderRevision']!=work.name:return False
    if target.suffix=='.mp4':
        if target.parent.name!='segments':return False
        if target.stem.split('-')[-1] in proof['correctedScenes']:return False
    elif target.suffix not in {'.wav','.m4a'}:return False
    old=work.parent/proof['sourceRevision']
    def earlier(value):return str(value).replace(str(work),str(old))
    source=Path(earlier(target));prior=Path(earlier(log)).with_suffix('.success.json')
    if not source.is_file() or not prior.is_file():return False
    # Same command, sample count and inputs; only the output folder changed.
    original=read(prior)
    old_args=[earlier(v) for v in args];previous=hashlib.sha256(json.dumps([old_args,earlier(cwd)],ensure_ascii=False).encode()).hexdigest()
    if previous!=original['commandSha256'] or original['outputSha256']!=sha(source):return False
    for value in args:
        for name in re.findall(r'ass=([\w.-]+\.ass)',value):
            if sha(Path(cwd)/name)!=sha(Path(earlier(cwd))/name):return False
    try:os.link(source,target)
    except OSError:return False
    save(log.with_suffix('.success.json'),dict(commandSha256=signature,outputSha256=original['outputSha256'],
         reusedFrom=str(source),previousCommandSha256=previous,finishedAt=now()))
    return True
def ff(args,log,cwd=None):
    G.authorized();log=Path(log);log.parent.mkdir(parents=True,exist_ok=True)
    args=list(map(str,args));signature=hashlib.sha256(json.dumps([args,str(cwd)],ensure_ascii=False).encode()).hexdigest()
    receipt=log.with_suffix('.success.json');target=Path(args[-1]) if args[-1]!='-' else None
    if target is not None and not target.is_absolute():target=Path(cwd or Path.cwd())/target
    if target is not None and target.is_file():
        assert receipt.is_file(),'Preserve partial output without success receipt: '+str(target)
        prior=read(receipt)
        assert prior['commandSha256']==signature and prior['outputSha256']==sha(target),'Cached output changed; preserve and use a new revision: '+str(target)
        return
    if reuse_visual_only_segment(args,log,cwd,target,signature):return
    with log.open('w',encoding='utf-8') as f:subprocess.run([str(FF),'-hide_banner','-nostdin','-n','-threads','2',*map(str,args)],stdout=f,stderr=f,check=True,cwd=cwd,creationflags=CREATE)
    if target is not None:save(receipt,{'commandSha256':signature,'outputSha256':sha(target),'finishedAt':now()})
def encoder():return ['-c:v','h264_nvenc','-preset','p5','-tune','hq','-rc','vbr','-cq','18','-b:v','0','-g','120','-pix_fmt','yuv420p','-video_track_timescale','90000']
def video_check(path,frames):
    stream=next(s for s in probe(path)['streams'] if s['codec_type']=='video')
    assert (stream['width'],stream['height'],stream['r_frame_rate'],int(stream['nb_frames']))==(1920,1080,'60/1',frames),str(path)

def prepared_insert(cut,source,track):
    name=cut['scene']+('-'+cut['insertVersion'] if cut.get('insertVersion') else '')
    cache=P/'production/local/part2-game-inserts'/name
    receipt=cache/'receipt.json';picture=cache/'picture.mkv'
    if not receipt.is_file() or not picture.is_file():return None
    inputs=dict(sourceSha256=source['sha256'],start=cut['sourceIn'],end=cut['sourceOut'],frames=cut['frames'],
                filter=game_filters(cut,'track.ass'),annotationSha256=sha(track))
    actual=read(receipt)
    if actual['input']!=inputs:return None
    assert sha(picture)==actual['pictureSha256'],'Cached game insert changed; inspect it before using it'
    return picture
def game_filters(cut,annotation):
    x,y,w,h=VIEW
    base=f'scale={w}:{h}:force_original_aspect_ratio=decrease:flags=lanczos,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,pad=1920:1080:{x}:{y}:black,setsar=1,fps=60'
    inset=cut.get('nativeDetailInset')
    if not inset:return base+',ass='+annotation
    assert inset['kind']=='same-instant-native-crop' and cut['sourceIn']<=inset['start']<inset['end']<=cut['sourceOut']
    k=inset['centers'];cw,ch=inset['cropSize'];dw,dh=inset['displaySize'];dx,dy=inset['displayAt']
    assert dw*ch==dh*cw and dx>=x and dx+dw+8<=x+w and dy>=y and dy+dh+8<=y+h and len(k)>=2
    assert all(k[i][0]<k[i+1][0] for i in range(len(k)-1))
    def position(axis,half):
        vals=[(t-cut['sourceIn'],p[axis]-half) for t,*p in k]
        expr=f'{vals[-1][1]:.3f}'
        for (ta,va),(tb,vb) in reversed(list(zip(vals,vals[1:]))):
            expr=f'if(lt(t,{tb:.5f}),{va:.3f}+({vb-va:.3f})*max(0,t-{ta:.5f})/{tb-ta:.5f},{expr})'
        return expr
    # The two branches share source PTS; no secondary clip, freeze or respeed.
    return f"split=2[whole][detail];[whole]{base}[field];[detail]crop={cw}:{ch}:x='{position(0,cw/2)}':y='{position(1,ch/2)}',scale={dw}:{dh}:flags=lanczos,setsar=1,pad={dw+8}:{dh+8}:4:4:0x73c7c2[zoom];[field][zoom]overlay={dx}:{dy}:enable='between(t,{inset['start']-cut['sourceIn']:.5f},{inset['end']-cut['sourceIn']:.5f})',ass={annotation}"
def points(frame):
    if 'points' in frame:return frame['points']
    x,y,w,h=frame['bbox']
    # Hollow perimeter leaves the actual surface detail visible. ASS paths close;
    # use a full ellipse rather than drawing an accidental chord across the gap.
    return [[x+w/2+w/2*math.cos(t),y+h/2+h/2*math.sin(t)] for t in [math.radians(i*360/48) for i in range(49)]]
def reveal_polyline(ps,portion):
    lengths=[math.dist(a,b) for a,b in zip(ps,ps[1:])]
    left=sum(lengths)*max(0,min(1,portion));out=[ps[0]]
    for a,b,d in zip(ps,ps[1:],lengths):
        if d<1e-9:continue
        if left>=d:out.append(b);left-=d
        else:
            out.append([a[j]+(b[j]-a[j])*left/d for j in (0,1)])
            break
    return out
def stroke_path(ps,radius):
    # ASS fills every subpath, so a conventional open contour creates a closing
    # chord during its reveal. Explicit segment quads and round joints draw
    # only the observed contour, including its genuinely open intermediate state.
    paths=[]
    def polygon(v):
        paths.append('m '+f'{v[0][0]:.2f} {v[0][1]:.2f} '+'l '+' '.join(f'{x:.2f} {y:.2f}' for x,y in v[1:]+v[:1]))
    for a,b in zip(ps,ps[1:]):
        d=math.dist(a,b)
        if d<1e-6:continue
        nx=-(b[1]-a[1])*radius/d;ny=(b[0]-a[0])*radius/d
        polygon([[a[0]+nx,a[1]+ny],[b[0]+nx,b[1]+ny],[b[0]-nx,b[1]-ny],[a[0]-nx,a[1]-ny]])
    # Keep joints and quads at the same winding. Opposite windings create
    # dot-shaped holes where the circles overlap the strip in libass.
    for x,y in ps:polygon([[x+radius*math.cos(-i*math.tau/12),y+radius*math.sin(-i*math.tau/12)] for i in range(12)])
    return ' '.join(paths)
def annotation_ass(cut,source,out):
    lines=C.ass_header();dur=cut['frames']/60;x,y,w,h=VIEW
    labels=read(P/'planning/game-annotation-tracks.json')
    windows=[r for r in labels['windows'] if r['sourceId']==source['id'] and min(r['end'],cut['sourceOut'])>max(r['start'],cut['sourceIn'])]
    assert windows,'Every selected real-game example needs a reviewed narrated focus'
    game=source.get('displayGameKo',GAME_LABELS.get(source['id'],source['game']))
    header_font=C.ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',36)
    C.event(lines,0,dur,'{\\an7\\pos(192,4)\\fs36\\1c&HFFFFFF&}'+game,4)
    C.event(lines,0,dur,'{\\an9\\pos(1728,4)\\fs36\\1c&HFFFFFF&}실제 게임 녹화',4)
    inset=cut.get('nativeDetailInset')
    if inset and inset.get('label'):
        left,top=inset['displayAt']
        C.event(lines,inset['start']-cut['sourceIn'],inset['end']-cut['sourceIn'],
                '{\\an1\\fs42\\bord3\\pos('+str(left)+','+str(top-5)+')}'+inset['label'],5)
    proofs=[]
    for window in windows:
        data=read(R/window['trackFile']);assert data['sourceSha256']==source['sha256']
        assert window['visualQa']['status']=='temporal-samples-reviewed-final-encoded-pending'
        kfs=data['keyframes'];start=max(cut['sourceIn'],data['start']);end=min(cut['sourceOut'],data['end'])
        phases=window.get('observedPhases') or [dict(start=start,end=end,label=data['label'])]
        for pi,phase in enumerate(phases):
            assert phase['end']>phase['start'] and (pi==0 or phase['start']>=phases[pi-1]['end'])
            left,right=max(cut['sourceIn'],phase['start']),min(cut['sourceOut'],phase['end'])
            if right<=left:continue
            focus_width=header_font.getlength(phase['label'])
            assert 192+header_font.getlength(game)+24 < 960-focus_width/2, 'Game title overlaps narrated focus label'
            assert 960+focus_width/2+24 < 1728-header_font.getlength('실제 게임 녹화'), 'Focus label overlaps picture-source kind'
            C.event(lines,left-cut['sourceIn'],right-cut['sourceIn'],'{\\an8\\pos(960,4)\\fs36\\1c&HC2C773&}'+phase['label'],5)
            if phase.get('sideLabel'):
                small=phase['sideLabel'];assert len(small)<=2 and C.ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',72).getlength(small)<x-24
                C.event(lines,left-cut['sourceIn'],right-cut['sourceIn'],'{\\an5\\pos(96,450)\\fs72\\b1\\1c&HFFFFFF&}'+small,5)
        for a,b in zip(kfs,kfs[1:]):
            lo=max(start,a['time']);hi=min(end,b['time'])
            if hi<=lo or not a.get('visible',True) or not b.get('visible',True):continue
            pa=points(a);pb=points(b);assert len(pa)==len(pb)
            count=max(1,math.ceil((hi-lo)*60))
            for i in range(count):
                t=lo+(hi-lo)*i/count;u=(t-a['time'])/max(1e-8,b['time']-a['time'])
                ps=[[x+(p[0]+(q[0]-p[0])*u)*w/1920,y+(p[1]+(q[1]-p[1])*u)*h/1080] for p,q in zip(pa,pb)]
                ps=reveal_polyline(ps,min(1,(t-start+.0167)/.18))
                assert min(p[1] for p in ps)>=8 and max(p[1] for p in ps)<920,'Annotation conflicts with captions'
                for stroke,color,layer in [(8,'101010',2),(5,'C2C773',3)]:
                    path=stroke_path(ps,stroke)
                    C.event(lines,t-cut['sourceIn'],lo+(hi-lo)*(i+1)/count-cut['sourceIn'],f'{{\\an7\\pos(0,0)\\p1\\bord0\\shad0\\1a&H00&\\1c&H{color}&}}'+path,layer)
        proofs.append(dict(id=data['id'],trackFile=window['trackFile'],trackSha256=sha(R/window['trackFile']),sourceSha256=source['sha256'],labelPhases=phases))
    Path(out).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return dict(scene=cut['scene'],viewport=VIEW,tracks=proofs,finalMotionQa=False)

def prepare(queue,work):
    t=read(queue['wordAlignment']);assert not t['flags'];assert sha(queue['wordAlignment'])==queue['wordAlignmentSha256']
    audit=read(P/'planning/footage-audit.json');sources={s['id']:s for s in audit['sources']}
    terms=['스키닝','노멀 맵','접선 공간','클립 공간','픽셀 셰이더','정점 셰이더','깊이 버퍼','래스터화','가속도','각속도','접선','제어점','양방향 반사 분포 함수','하프웨이 벡터','표면 법선','라이트 프로브','구면 조화 함수','라이트맵','복사조도','복사휘도','정반사','난반사','환경광','발광','정점','픽셀']
    emphasis={}
    for i,cue in enumerate(t['ko']):
        matches=[term for term in terms if cue['text'].count(term)==1]
        if matches:emphasis[str(i+1)]={'text':matches[0],'role':'term'}
    layout=C.caption_ass(work/'captions.ko.ass',[dict(c,id=i+1) for i,c in enumerate(t['ko'])],2,emphasis)
    assert all(len(x['lines'])==1 for x in layout),'Chosen viewport requires one-line final clauses; revise layout rather than move captions'
    receipts=[]
    for i,cut in enumerate(queue['cuts']):
        if cut['kind']=='actual-gameplay':
            s=sources[cut['sourceId']];assert sha(R/s['file'])==s['sha256']
            receipts.append(annotation_ass(cut,s,work/f'game-{i:03}.ass'))
        elif P.name=='game-math-velocity-derivatives' and cut['scene']=='007':
            frequency_guides(work/f'period-{i:03}.ass',cut['frames']/FPS)
        elif VELOCITY_FIGURES and cut['scene'] in VELOCITY_FIGURES.PURPOSES:
            VELOCITY_FIGURES.render(work/f'velocity-{i:03}.ass',cut,t,C,stroke_path,reveal_polyline,VELOCITY_ART)
        elif P.name=='game-math-pipeline-shaders' and cut['scene']=='020':
            shot=read(work.parent/'shots/020.json')
            clipping_guides(work/f'clip-plane-{i:03}.ass',cut,shot)
        elif PIPELINE_FIGURES and cut['scene'] in PIPELINE_FIGURES.TEACHING_SCENES:
            PIPELINE_FIGURES.render(work/f'vertex-{i:03}.ass',cut,t,C,stroke_path,reveal_polyline)
    record={'createdAt':now(),'queueSha256':sha(work.parent/'queue.json'),'narrationSha256':t['narrationSha256'],'captionLayout':layout,'gameAnnotations':receipts,'addedBackgroundMusic':False,'audioChoice':'Original synchronized game audio retained and ducked; source-specific exceptions must be recorded per source. No added lecture BGM.','humanListening':False,'finalVisualQa':False}
    save(work/'preflight.json',record);return sources,record

def frequency_guides(file,duration):
    # Positions come from the native 1080p four-cycle plot. One crest-to-crest
    # span is one period, while the longer bracket measures the full interval.
    lines=C.ass_header()
    def bracket(left,right,y,label,color,begin):
        if begin>=duration:return
        points=[(left,y+10),(left,y),(right,y),(right,y+10)]
        C.event(lines,begin,duration,r'{\an7\pos(0,0)\p1\bord0\shad0\1c&H'+color+'&}'+stroke_path(points,2.5),3)
        C.event(lines,begin,duration,r'{\an2\pos('+str((left+right)//2)+','+str(y-4)+r')\fs36\bord2\1c&H'+color+'&}'+label,4)
    bracket(1169,1313,460,'한 주기 T','C2C773',0.35)
    bracket(1133,1709,405,'관찰 시간 Δt','83CEE9',1.1)
    Path(file).write_text('\n'.join(lines)+'\n',encoding='utf-8')

def clipping_guides(file,cut,shot):
    lines=C.ass_header();duration=cut['frames']/FPS
    for x,label,color in [(1320,'안쪽','A6CA88'),(1535,'바깥쪽','ABA0F0')]:
        C.event(lines,0,duration,r'{\an2\fs43\bord2\pos('+f'{x},338'+r')\1c&H'+color+'&}'+label,4)
    times=shot.get('phaseSeconds') or [0,shot['durationSeconds']]
    positions=shot.get('phasePositions') or [0,1]
    assert len(times)==len(positions) and times[0]==0
    line_color=r'{\an7\pos(0,0)\p1\bord0\shad0\1c&H83CEE9&}'
    for start in range(0,cut['frames'],4):
        t=cut['sourceIn']+start/FPS
        k=next((j for j in range(1,len(times)) if t<=times[j]),len(times)-1)
        frac=max(0,min(1,(t-times[k-1])/(times[k]-times[k-1])))
        u=positions[k-1]+frac*(positions[k]-positions[k-1])
        if u<.5:continue
        # ClipDiagram keeps the upper endpoint (.1,.8) fixed while the outer
        # endpoint is (1.1+.8u,-.4). The right plane is x=1. The verified
        # orthographic mapping of the native scene is 180 px per diagram unit.
        y=535-180*(.8-1.2*.9/(1+.8*u))
        a=start/FPS;b=min(start+4,cut['frames'])/FPS
        C.event(lines,a,b,line_color+stroke_path([(1452,y-2),(1530,y-30),(1585,y-30)],2.4),3)
        C.event(lines,a,b,r'{\an4\fs42\bord2\pos('+f'1592,{y-30:.1f}'+r')\1c&H83CEE9&}교점',4)
    Path(file).write_text('\n'.join(lines)+'\n',encoding='utf-8')

def normalized_audio(source,start,frames,target,target_lufs,work,stem,source_decision=None):
    n=frames*800;duration=frames/60
    analysis=work/'logs'/(stem+'-loudness.log')
    base=['-ss',str(start),'-t',str(duration),'-i',str(source),'-vn']
    ff([*base,'-af',f'loudnorm=I={target_lufs}:TP=-2:LRA=11:print_format=json','-f','null','-'],analysis)
    matches=re.findall(r'\{\s*"input_i"[\s\S]+?\}',analysis.read_text(encoding='utf-8'))
    assert matches,'Missing actual source loudness measurement';m=json.loads(matches[-1]);save(work/(stem+'-loudness.json'),m)
    if not math.isfinite(float(m['input_i'])):gain='anull'
    elif source_decision and target_lufs-float(m['input_i'])>source_decision['maxUpwardGainDb']:
        assert stem!='narration' and source_decision['policy']=='preserve-quiet-original' and 0<=source_decision['maxUpwardGainDb']<=6
        gain=f"volume={source_decision['maxUpwardGainDb']}dB"
        save(work/(stem+'-preserved-quiet-original.json'),dict(source=source_decision,actualLufs=m['input_i'],gain=gain,nominalTarget=target_lufs,muted=False))
    else:gain=f"loudnorm=I={target_lufs}:TP=-2:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
    fades='' if stem=='narration' else f',afade=t=in:d=0.06,afade=t=out:st={max(0,duration-.08):.6f}:d=0.08'
    ff([*base,'-af',gain+f',aresample=48000,asetpts=N/SR/TB,apad,atrim=end_sample={n}'+fades,'-ac','2','-c:a','pcm_f32le',target],work/'logs'/(stem+'-audio.log'))
    stream=next(s for s in probe(target)['streams'] if s['codec_type']=='audio')
    assert stream['time_base']=='1/48000' and int(stream['duration_ts'])==n,('Normalized audio must retain exact sample count',stem,n,stream.get('duration_ts'))
def silence(target,frames,work,stem):ff(['-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-af',f'atrim=end_sample={frames*800}','-c:a','pcm_f32le',target],work/'logs'/(stem+'-silence.log'))
def concat(paths,target,work,name,audio=False):
    listing=work/(name+'.ffconcat');assert all("'" not in str(p) for p in paths)
    listing.write_text('ffconcat version 1.0\n'+''.join("file '"+str(Path(p).resolve()).replace('\\','/')+"'\n" for p in paths),encoding='utf-8')
    args=['-f','concat','-safe','0','-i',listing]
    args+=['-c:a','pcm_f32le','-ar','48000','-ac','2'] if audio else ['-an','-c:v','copy','-video_track_timescale','90000']
    ff([*args,target],work/'logs'/(name+'.log'))
def render(queue,work,sources,receipt,dest):
    owner=work/'render-owner.json';identity={'queueSha256':receipt['queueSha256'],'compositorSha256':sha(Path(__file__)),'narrationSha256':receipt['narrationSha256'],'destination':str(dest)}
    if dest.exists():assert owner.is_file() and read(owner)==identity,'Preserve existing output revision'
    else:dest.mkdir(parents=True);save(owner,identity)
    segments=work/'segments';segments.mkdir(exist_ok=True);videos=[];audios=[]
    for i,cut in enumerate(queue['cuts']):
        G.authorized();stem=f'{i:03}-{cut["scene"]}';v=segments/(stem+'.mp4');a=segments/(stem+'.wav');n=cut['frames'];duration=n/60
        picture_start=cut['sourceIn']
        if cut['kind']=='actual-gameplay':
            src=sources[cut['sourceId']];source=R/src['file'];x,y,w,h=VIEW
            vf=game_filters(cut,f'game-{i:03}.ass')
            cached=prepared_insert(cut,src,work/f'game-{i:03}.ass')
            if cached is not None:
                picture_source=cached;picture_start=0;vf='setsar=1,fps=60'
            else:picture_source=source
        else:
            picture_source=Path(cut['file']);vf='setsar=1,fps=60'
            if P.name=='game-math-velocity-derivatives' and cut['scene']=='007':
                vf+=f',ass=period-{i:03}.ass'
            if VELOCITY_FIGURES and cut['scene'] in VELOCITY_FIGURES.PURPOSES:
                vf+=f',ass=velocity-{i:03}.ass'
            if P.name=='game-math-pipeline-shaders' and cut['scene']=='020':
                vf+=f',ass=clip-plane-{i:03}.ass'
            if PIPELINE_FIGURES and cut['scene'] in PIPELINE_FIGURES.TEACHING_SCENES:
                vf+=f',ass=vertex-{i:03}.ass'
        ff(['-ss',picture_start,'-i',picture_source,'-an','-vf',vf,'-frames:v',n,*encoder(),'-movflags','+faststart',v],work/'logs'/(stem+'-video.log'),work)
        video_check(v,n)
        if cut['kind']=='actual-gameplay' and not src.get('excludeOriginalAudioReason'):
            sound=src.get('audio',{})
            audio=R/sound.get('separateFullOriginalAudio',sound.get('separateOriginalAudio',sound.get('recoveredOriginalAudio',src['file'])))
            assert any(s['codec_type']=='audio' for s in probe(audio)['streams']),'Original game audio missing; record evidence rather than inventing silence'
            offset=cut.get('originalAudioIn',cut['sourceIn']) if audio!=source else cut['sourceIn']
            normalized_audio(audio,offset,n,a,-23,work,stem,cut.get('sourceSoundDecision'))
        else:silence(a,n,work,stem)
        videos.append(v);audios.append(a)
        save(work/'progress.json',{'status':'compositing','completedCuts':i+1,'totalCuts':len(queue['cuts']),'updatedAt':now(),'finalReviewReady':False})
    books=[]
    for name,frames in [('branding',120),('membership',600)]:
        source=BOOK/(name+'.mp4');v=segments/(name+'.mp4');a=segments/(name+'.wav')
        video_check(source,frames)
        ff(['-i',source,'-an','-frames:v',frames,*encoder(),v],work/'logs'/(name+'-video.log'))
        if any(s['codec_type']=='audio' for s in probe(source)['streams']):normalized_audio(source,0,frames,a,-23,work,name)
        else:silence(a,frames,work,name)
        books.append((v,a))
    concat([books[0][0],*videos,books[1][0]],work/'visuals.mp4',work,'visuals')
    concat(audios,work/'game-bed.wav',work,'game-bed',True)
    voice=Path(queue['audioDirectory'])/'narration.wav';assert sha(voice)==receipt['narrationSha256']
    normalized_audio(voice,0,queue['bodyFrames'],work/'narration-normalized.wav',-16,work,'narration')
    filt='[0:a]asplit=2[voice][side];[1:a][side]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[game];[voice][game]amix=inputs=2:duration=first:normalize=0[body]'
    ff(['-i',work/'narration-normalized.wav','-i',work/'game-bed.wav','-filter_complex',filt,'-map','[body]','-ar','48000','-ac','2','-c:a','pcm_f32le',work/'body-mix.wav'],work/'logs/mix.log')
    concat([books[0][1],work/'body-mix.wav',books[1][1]],work/'whole-mix.wav',work,'whole-mix',True)
    ff(['-i',work/'whole-mix.wav','-af','aresample=192000,alimiter=limit=0.831764:level=false:latency=true,aresample=48000','-ar','48000','-ac','2','-c:a','aac','-b:a','192k',work/'pair-audio.m4a'],work/'logs/pair-audio.log')
    clean=dest/(P.name+'.clean.mp4');cap=dest/(P.name+'.captioned.mp4')
    ff(['-i',work/'visuals.mp4','-i',work/'pair-audio.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-map_metadata','-1','-movflags','+faststart',clean],work/'logs/clean.log')
    ff(['-i',clean,'-vf','ass=captions.ko.ass','-map','0:v:0','-map','0:a:0',*encoder(),'-c:a','copy','-map_metadata','-1','-movflags','+faststart',cap],work/'logs/captioned.log',work)
    for lang in ['ko','en']:shutil.copy2(Path(queue['editDirectory'])/('narration.'+lang+'.srt'),dest/(P.name+'.'+lang+'.srt'))
    for path in [clean,cap]:video_check(path,queue['bodyFrames']+720)
    meta=read(P/'project.json')
    title=html.escape(meta['titles']['ko']+' · '+meta.get('localReviewHeading','로컬 검수본'))
    (dest/'index.html').write_text(f'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>body{{max-width:1100px;margin:24px auto;padding:20px;background:#080808;color:white;font:18px/1.6 system-ui}}a{{color:#73c7c2}}video{{width:100%}}h1{{color:#e8cf83}}</style><h1>{title}</h1><p>1920×1080 · 60fps · 사용자 시청/청취 검수 전</p><video controls preload="metadata" src="{P.name}.captioned.mp4"></video><p><a href="{P.name}.clean.mp4">자막 없는 영상</a> · <a href="{P.name}.ko.srt">한국어 자막</a> · <a href="{P.name}.en.srt">영어 자막</a></p>',encoding='utf-8')
    if P.name=='game-math-skinning-normal-map':
        from runpy import run_path
        run_path(str(P/'production/meaning-guides/player.py'))['review_page'](dest,queue)
    elif (P/'planning/part2-picture-plan.json').is_file():
        from runpy import run_path
        run_path(str(Path(__file__).parent/'part2/player.py'))['render'](dest,queue)
    save(work/'progress.json',{'status':'encoded-internal-QA-pending','output':str(dest),'files':[{'path':str(p),'sha256':sha(p)} for p in dest.glob('*')],'originalPcmUnchanged':sha(voice)==receipt['narrationSha256'],'humanReview':False,'finalReviewReady':False,'finishedAt':now()})
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--queue',required=True);ap.add_argument('--render',action='store_true');ap.add_argument('--wait-hours',type=float,default=0);a=ap.parse_args()
    q=Path(a.queue).resolve();assert q.is_relative_to(P/'production/local');G.authorized();queue=read(q)
    work=q.parent/'composite';work.mkdir(exist_ok=True);sources,receipt=prepare(queue,work)
    if not a.render:print(json.dumps({'prepared':True,'cuts':len(queue['cuts']),'rendered':False}));return
    worker=work/'worker.json'
    if worker.exists():
        old=read(worker)
        try:assert abs(psutil.Process(old['pid']).create_time()-old['createTime'])>.1,'Existing compositor is active'
        except psutil.NoSuchProcess:pass
        assert old.get('status')!='encoded','Unchanged encoded work must not be repeated'
    state={'pid':os.getpid(),'createTime':psutil.Process().create_time(),'status':'waiting','startedAt':now(),'automation':False,'nextVideo':False}
    deadline=time.monotonic()+a.wait_hours*3600;owned=None
    while owned is None:
        G.authorized();capture=read(q.parent/'progress.json');reason=None
        if capture['status']=='failed-or-blocked':raise RuntimeError('Capture failed; inspect original log before composing')
        if capture['status']!='body-captures-complete-compositing-and-QA-pending':reason='Waiting for the current finite body capture'
        if reason is None:reason=G.idle_reason()
        state.update(reason=reason,checkedAt=now());save(worker,state)
        if reason is None:
            candidate=str(uuid.uuid4())
            try:
                with LEASE.open('x',encoding='utf-8') as f:json.dump({'owner':P.name+'-composite','id':candidate,'pid':os.getpid(),'createdAt':now()},f)
                owned=candidate
            except FileExistsError:reason='Another scoped job acquired the lease'
        if owned is None:
            if time.monotonic()>=deadline:raise RuntimeError(reason+'; bounded wait ended, other jobs preserved')
            time.sleep(5)
    try:
        state.update(status='compositing',reason=None);save(worker,state)
        render(queue,work,sources,receipt,R/'output'/(P.name+'-'+q.parent.name))
        state.update(status='encoded',finishedAt=now());save(worker,state)
    except BaseException as exc:
        state.update(status='failed',error=repr(exc),finishedAt=now());save(worker,state);raise
    finally:
        G.release_lease(owned)
if __name__=='__main__':main()

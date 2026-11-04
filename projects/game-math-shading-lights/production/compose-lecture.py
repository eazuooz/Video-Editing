"""Frame-exact M21 edit. Native game motion, original continuous narration.

Preparation writes captions/annotation instructions only. Rendering requires a
finished word-aligned Unity queue and the exclusive resource lease. Completion
here means encoded files, never human listening or visual approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, html, importlib.util, json, math, os, re, shutil, subprocess, time, uuid
import psutil

P=Path(__file__).resolve().parents[1];R=P.parents[1];FPS=60;SR=48000
FF=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')
LEASE=R/'shared/output/GPU_HANDOFF.json';CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
VIEW=(192,48,1536,864)
ANNOTATIONS={'000':'abstract-rock','007':'bonnet','018':'matte-wall','027':'bloom','031':'ceiling','049':'spot-surface','060':'doom-surface'}
GAME_LABELS={'dYyWmhVuc3w':'서브노티카 2','X9UdRR_4Rog':'포르자 모터스포츠 6','FRfnXAIbA-M':'타운스케이퍼','pM6hIROLoyw':'젤다: 왕국의 눈물','Hu94MHBQCis':'둠 3 (2004)'}
BOOK=R/'projects/game-reward-planning/production/final-v1/white-segments'

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
C=module('existing_caption_geometry',R/'projects/buckshot-roulette-reverse-engineering/production/assemble_documentary.py')
G=module('m21_resource_guard',P/'production/run-capture-queue.py')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def probe(p):return json.loads(subprocess.check_output([str(FF.with_name('ffprobe.exe')),'-v','error','-show_streams','-show_format','-of','json',str(p)],creationflags=CREATE))
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
    with log.open('w',encoding='utf-8') as f:subprocess.run([str(FF),'-hide_banner','-nostdin','-n','-threads','2',*map(str,args)],stdout=f,stderr=f,check=True,cwd=cwd,creationflags=CREATE)
    if target is not None:save(receipt,{'commandSha256':signature,'outputSha256':sha(target),'finishedAt':now()})
def encoder():return ['-c:v','h264_nvenc','-preset','p5','-tune','hq','-rc','vbr','-cq','18','-b:v','0','-g','120','-pix_fmt','yuv420p','-video_track_timescale','90000']
def video_check(path,frames):
    stream=next(s for s in probe(path)['streams'] if s['codec_type']=='video')
    assert (stream['width'],stream['height'],stream['r_frame_rate'],int(stream['nb_frames']))==(1920,1080,'60/1',frames),str(path)
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
    lines=C.ass_header();dur=cut['frames']/60;sid=cut['scene'];x,y,w,h=VIEW
    C.event(lines,0,dur,'{\\an7\\pos(192,4)\\fs36\\1c&HFFFFFF&}'+GAME_LABELS[source['id']],4)
    C.event(lines,0,dur,'{\\an9\\pos(1728,4)\\fs36\\1c&HFFFFFF&}실제 게임 녹화',4)
    name=ANNOTATIONS.get(sid)
    if name:
        data=read(P/'production/local/annotation-refined-v2'/(name+'.json'))
        assert data['sourceId']==source['id'] and data['sourceSha256']==source['sha256']
        kfs=data['keyframes'];start=max(cut['sourceIn'],data['start']);end=min(cut['sourceOut'],data['end'])
        assert end>start,'Selected game cut removed its observed teaching target'
        C.event(lines,start-cut['sourceIn'],end-cut['sourceIn'],'{\\an8\\pos(960,4)\\fs36\\1c&HC2C773&}'+data['label'],5)
        for a,b in zip(kfs,kfs[1:]):
            lo=max(start,a['time']);hi=min(end,b['time'])
            if hi<=lo or not a.get('visible',True):continue
            pa=points(a);pb=points(b);assert len(pa)==len(pb)
            count=max(1,math.ceil((hi-lo)*60))
            for i in range(count):
                t=lo+(hi-lo)*i/count;u=(t-a['time'])/max(1e-8,b['time']-a['time'])
                ps=[[x+(p[0]+(q[0]-p[0])*u)*w/1920,y+(p[1]+(q[1]-p[1])*u)*h/1080] for p,q in zip(pa,pb)]
                if sid=='031':
                    cy=(min(p[1] for p in ps)+max(p[1] for p in ps))/2
                    ps=[[px,cy-18+(py-cy)*.76] for px,py in ps] # Inset the lamp contour above its construction-cost UI.
                ps=reveal_polyline(ps,min(1,(t-start+.0167)/.18))
                assert min(p[1] for p in ps)>=8 and max(p[1] for p in ps)<920,'Annotation conflicts with caption'
                for stroke,color,layer in [(8,'101010',2),(5,'C2C773',3)]:
                    path=stroke_path(ps,stroke)
                    C.event(lines,t-cut['sourceIn'],lo+(hi-lo)*(i+1)/count-cut['sourceIn'],f'{{\\an7\\pos(0,0)\\p1\\bord0\\shad0\\1a&H00&\\1c&H{color}&}}'+path,layer)
    Path(out).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return {'scene':sid,'sourceSha256':source['sha256'],'viewport':VIEW,'annotation':name,'finalMotionQa':False}
def prepare(queue,work):
    t=read(queue['wordAlignment']);assert not t['flags'];assert sha(queue['wordAlignment'])==queue['wordAlignmentSha256']
    audit=read(P/'planning/footage-audit.json');sources={s['id']:s for s in audit['sources']}
    terms=['양방향 반사 분포 함수','하프웨이 벡터','표면 법선','라이트 프로브','구면 조화 함수','라이트맵','복사조도','복사휘도','정반사','난반사','환경광','발광','정점','픽셀']
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
    record={'createdAt':now(),'queueSha256':sha(work.parent/'queue.json'),'narrationSha256':t['narrationSha256'],'captionLayout':layout,'gameAnnotations':receipts,'addedBackgroundMusic':False,'audioChoice':'Native game audio retained except Forza menu track: third-party music not identified/cleared. No fabricated substitute. This is a documented source-specific rights exception, not an effects-only extraction.','humanListening':False,'finalVisualQa':False}
    save(work/'preflight.json',record);return sources,record
def normalized_audio(source,start,frames,target,target_lufs,work,stem):
    n=frames*800;duration=frames/60
    analysis=work/'logs'/(stem+'-loudness.log')
    base=['-ss',str(start),'-t',str(duration),'-i',str(source),'-vn']
    ff([*base,'-af',f'loudnorm=I={target_lufs}:TP=-2:LRA=11:print_format=json','-f','null','-'],analysis)
    matches=re.findall(r'\{\s*"input_i"[\s\S]+?\}',analysis.read_text(encoding='utf-8'))
    assert matches,'Missing actual source loudness measurement';m=json.loads(matches[-1]);save(work/(stem+'-loudness.json'),m)
    if not math.isfinite(float(m['input_i'])):gain='anull'
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
        if cut['kind']=='actual-gameplay':
            src=sources[cut['sourceId']];source=R/src['file'];x,y,w,h=VIEW
            vf=f'scale={w}:{h}:force_original_aspect_ratio=decrease:flags=lanczos,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,pad=1920:1080:{x}:{y}:black,setsar=1,fps=60,ass=game-{i:03}.ass'
        else:source=Path(cut['file']);vf='setsar=1,fps=60'
        ff(['-ss',cut['sourceIn'],'-i',source,'-an','-vf',vf,'-frames:v',n,*encoder(),'-movflags','+faststart',v],work/'logs'/(stem+'-video.log'),work)
        video_check(v,n)
        if cut['kind']=='actual-gameplay' and cut['sourceId']!='X9UdRR_4Rog':
            audio=R/src.get('audio',{}).get('recoveredOriginalAudio',src['file'])
            normalized_audio(audio,cut['sourceIn'],n,a,-23,work,stem)
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
    voice=P/'production/local/audio-v1/narration.wav';assert sha(voice)==receipt['narrationSha256']
    normalized_audio(voice,0,queue['bodyFrames'],work/'narration-normalized.wav',-16,work,'narration')
    filt='[0:a]asplit=2[voice][side];[1:a][side]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[game];[voice][game]amix=inputs=2:duration=first:normalize=0[body]'
    ff(['-i',work/'narration-normalized.wav','-i',work/'game-bed.wav','-filter_complex',filt,'-map','[body]','-ar','48000','-ac','2','-c:a','pcm_f32le',work/'body-mix.wav'],work/'logs/mix.log')
    concat([books[0][1],work/'body-mix.wav',books[1][1]],work/'whole-mix.wav',work,'whole-mix',True)
    ff(['-i',work/'whole-mix.wav','-af','aresample=192000,alimiter=limit=0.831764:level=false:latency=true,aresample=48000','-ar','48000','-ac','2','-c:a','aac','-b:a','192k',work/'pair-audio.m4a'],work/'logs/pair-audio.log')
    clean=dest/(P.name+'.clean.mp4');cap=dest/(P.name+'.captioned.mp4')
    ff(['-i',work/'visuals.mp4','-i',work/'pair-audio.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-map_metadata','-1','-movflags','+faststart',clean],work/'logs/clean.log')
    ff(['-i',clean,'-vf','ass=captions.ko.ass','-map','0:v:0','-map','0:a:0',*encoder(),'-c:a','copy','-map_metadata','-1','-movflags','+faststart',cap],work/'logs/captioned.log',work)
    for lang in ['ko','en']:shutil.copy2(P/'production/local/edit-v1'/('narration.'+lang+'.srt'),dest/(P.name+'.'+lang+'.srt'))
    for path in [clean,cap]:video_check(path,queue['bodyFrames']+720)
    title=html.escape('빛과 셰이딩 — 로컬 검수본')
    (dest/'index.html').write_text(f'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>body{{max-width:1100px;margin:24px auto;padding:20px;background:#080808;color:white;font:18px/1.6 system-ui}}a{{color:#73c7c2}}video{{width:100%}}h1{{color:#e8cf83}}</style><h1>{title}</h1><p>1920×1080 · 60fps · 사용자 시청/청취 검수 전</p><video controls preload="metadata" src="{P.name}.captioned.mp4"></video><p><a href="{P.name}.clean.mp4">자막 없는 영상</a> · <a href="{P.name}.ko.srt">한국어 자막</a> · <a href="{P.name}.en.srt">영어 자막</a></p>',encoding='utf-8')
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

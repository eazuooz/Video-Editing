"""Apply inspected gameplay-only patches without regenerating approved lessons.

Native gameplay, analytical stills, and the unchanged model have separate time
accounting. A resumed source interval is continuous, never looped or slowed.
"""
from pathlib import Path
import datetime, hashlib, json, math, subprocess, sys, shutil
R=Path(__file__).resolve().parents[3]; B=Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for part in iter(lambda:f.read(1048576),b''):h.update(part)
    return h.hexdigest()
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def auth(episode):
    a=read(R/'shared/publishing/video-production-control.json')['scopedBatchAuthorizations'][B.name]
    assert a['status']=='active' and a['renderAuthorized'] and episode in a['ids']
    assert not a['newTtsAuthorized'] and not a['uploadAuthorized']
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def stamp(t):
    n=round(t*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
HEADER='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Malgun Gothic,42,&H00EFF5F5,&H00FFFFFF,&H00120D09,&H00120D09,0,0,0,0,100,100,0,0,1,3,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
ENC=['-c:v','h264_nvenc','-preset','p5','-rc','vbr','-cq','18','-b:v','0','-pix_fmt','yuv420p','-r','60','-fps_mode','cfr','-video_track_timescale','60000']
def ff(args,log,cwd):
    with Path(log).open('w',encoding='utf8') as f:
        subprocess.run(['ffmpeg','-hide_banner','-nostdin','-y',*map(str,args)],stdout=f,stderr=f,cwd=cwd,check=True)
def guides(patch,source):
    rows=[];duration=patch['duration']
    def event(a,b,text,layer=2): rows.append(f'Dialogue: {layer},{stamp(a)},{stamp(b)},Default,,0,0,0,,{text}')
    def label(a,b,x,y,text,size=42,color='EFF5F5'):
        event(a,b,'{\\pos('+f'{x},{y}'+')\\fs'+str(size)+'\\1c&H'+color+'&}'+text)
    label(0,duration,36,22,patch['title'],52,'73D7FF')
    label(0,duration,36,87,source['game'],32,'BCC0A7')
    label(0,duration,1320,145,'원리 비교',48,'73D7FF')
    label(0,duration,1320,205,'계산용 모형',34,'BCC0A7')
    label(0,duration,36,862,patch['meaning'],39,'A2D380')
    at=0
    for s in patch['segments']:
        label(at,at+s['seconds'],850,92,'실제 게임 · 정상 재생' if s['kind']=='motion' else '실제 화면 · 관찰 정지',32)
        at+=s['seconds']
    def line(a,b,pts,color='A2D380',width=4):
        x=min(p[0] for p in pts);y=min(p[1] for p in pts)
        drawing='m '+f'{pts[0][0]-x:.2f} {pts[0][1]-y:.2f} '+' '.join('l '+f'{p[0]-x:.2f} {p[1]-y:.2f}' for p in pts[1:])
        event(a,b,'{\\an7\\pos('+f'{x},{y}'+')\\p1\\bord'+str(width)+'\\shad0\\1a&HFF&\\3c&H'+color+'&}'+drawing,1)
    def xy(q):return (q[0]*1280,130+q[1]*720)
    for g in patch['guides']:
        a,b=g['from'],g['to'];kind=g['kind']
        if kind in ['circle','arc']:
            cx,cy=xy(g['xy']);radius=g['radius']
            angles=[i*2*math.pi/64 for i in range(65)] if kind=='circle' else [(-2.7+i*4.7/48) for i in range(49)]
            pts=[(cx+radius*math.cos(v),cy+radius*math.sin(v)) for v in angles]
            line(a,b,pts)
            if kind=='arc':
                end=pts[-1];v=angles[-1]+math.pi/2
                line(a,b,[(end[0]-24*math.cos(v-.5),end[1]-24*math.sin(v-.5)),end,(end[0]-24*math.cos(v+.5),end[1]-24*math.sin(v+.5))])
            label(a,b,max(20,min(1000,cx-radius)),min(800,cy+radius+8),g['label'],36)
        elif kind=='arrow':
            x,y=xy(g['a']);xx,yy=xy(g['b']);line(a,b,[(x,y),(xx,yy)])
            v=math.atan2(yy-y,xx-x)
            line(a,b,[(xx-22*math.cos(v-.5),yy-22*math.sin(v-.5)),(xx,yy),(xx-22*math.cos(v+.5),yy-22*math.sin(v+.5))])
            label(a,b,x+20,y,g['label'],36)
        elif kind=='path':
            pts=[xy(q) for q in g['points']];reveal=min(1.3,(b-a)/3)
            for i in range(1,len(pts)):
                line(a+reveal*(i-1)/(len(pts)-1),b,pts[i-1:i+1])
            label(a+reveal,b,pts[0][0]-30,pts[0][1]+30,g['label'],36)
    return HEADER+'\n'.join(rows)+'\n'

def main():
    plan_path=Path(sys.argv[1]).resolve();plan=read(plan_path);auth(plan['episode'])
    slug=plan['slug'];P=R/'projects'/slug;H=P/'production'/plan['revision'];O=P/'production/local'/plan['revision'];O.mkdir(parents=True,exist_ok=True)
    old=P/'production/concept-fit-v2';T=read(old/'timeline.json');models=read(old/'render-progress.json')['scenes']
    timeline={s['id']:s for s in T['scenes']};receipts=[]
    for p in plan['patches']:
        auth(plan['episode']);sid=p['scene'];slot=timeline[sid];src=R/plan['sources'][p['source']]['path']
        meta=probe(src);v=next(s for s in meta['streams'] if s['codec_type']=='video')
        if v['height']<1080:
            exception=read(R/'production/batches/private-game-math-polish-20261022/portal-original-resolution-exception.json')
            allowed=exception['episodes'].get(plan['episode'],{}).get('scenes',{}).get(sid,{})
            assert exception['status']=='approved' and rel(src) in allowed.get('sourcePaths',[])
            assert plan['sources'][p['source']].get('resolutionException') and v['height']==720
        assert abs(sum(s['seconds'] for s in p['segments'])-p['duration'])<.0001
        assert p['offset']+p['duration']<=slot['seconds']+.01
        dest=O/'patches'/plan.get('patchSet','pass-1')/p.get('key',sid);dest.mkdir(parents=True,exist_ok=True)
        identity=hashlib.sha256((json.dumps(p,sort_keys=True)+sha(src)+sha(__file__)).encode()).hexdigest()
        receipt=dest/'receipt.json'
        if receipt.exists():
            prior=read(receipt)
            if prior['identity']==identity and (R/prior['path']).exists() and sha(R/prior['path'])==prior['sha256']:
                receipts.append(prior);continue
            raise RuntimeError('Preserve prior patch; use another revision before replacing '+sid)
        parts=[];at=0
        for i,s in enumerate(p['segments']):
            f=dest/f'part-{i}.mp4';frames=round(s['seconds']*60)
            common=['-ss',s['in'],'-i',src]
            filt='scale=1280:720:flags=lanczos,setsar=1,fps=60'
            if s['kind']=='still':filt='trim=end_frame=1,setpts=PTS-STARTPTS,'+filt+f',tpad=stop_mode=clone:stop_duration={s["seconds"]+.1}'
            else:filt+=',setpts=N/(60*TB)'
            ff(common+['-vf',filt,'-frames:v',frames,'-an',*ENC,f],dest/f'part-{i}.log',dest)
            parts.append(f);at+=s['seconds']
        listing=dest/'parts.txt';listing.write_text('\n'.join("file '"+f.as_posix()+"'" for f in parts)+'\n',encoding='utf8')
        game=dest/'game.mp4';ff(['-f','concat','-safe','0','-i',listing,'-c','copy',game],dest/'join.log',dest)
        (dest/'guides.ass').write_text(guides(p,plan['sources'][p['source']]),encoding='utf8')
        model=R/models[sid]['path'];assert sha(model)==models[sid]['sha256']
        n=round(p['duration']*60)
        cx,cy,cw,ch=p.get('modelCrop',[80,210,850,540]);mh=round(ch*620/cw/2)*2
        graph=f'[0:v]crop={cw}:{ch}:{cx}:{cy},scale=620:{mh},setsar=1[model];color=c=0x090D12:s=1920x1080:r=60:d={p["duration"]}[bg];[bg][1:v]overlay=0:130[game];[game][model]overlay=1300:240,ass=guides.ass,setsar=1[v]'
        dst=dest/'patch.mp4'
        ff(['-ss',p['offset'],'-i',model,'-i',game,'-filter_complex_threads','2','-filter_complex',graph,'-map','[v]','-frames:v',n,'-an',*ENC,dst],dest/'patch.log',dest)
        v=next(x for x in probe(dst)['streams'] if x['codec_type']=='video');assert int(v['nb_frames'])==n and v['height']==1080 and v['r_frame_rate']=='60/1'
        row=dict(scene=sid,key=p.get('key',sid),path=rel(dst),sha256=sha(dst),identity=identity,start=slot['start']+p['offset'],duration=p['duration'],frames=n,
            nativeGameSeconds=sum(s['seconds'] for s in p['segments'] if s['kind']=='motion'),analyticalStillSeconds=sum(s['seconds'] for s in p['segments'] if s['kind']=='still'),
            sourceSha256=sha(src),explanationSourceSha256=sha(model),actualPixelReview=False)
        save(receipt,row);receipts.append(row);save(H/'patches.json',dict(status='patches-rendering',patches=receipts,plan=rel(plan_path),finalReview=False))
        print('Rendered',sid,'native',row['nativeGameSeconds'],'analysis',row['analyticalStillSeconds'],flush=True)
    save(H/'patches.json',dict(status='patches-rendered-review-pending',patches=receipts,plan=rel(plan_path),finalReview=False))
    print('Patch render complete; no final approval inferred',flush=True)
if __name__=='__main__':main()

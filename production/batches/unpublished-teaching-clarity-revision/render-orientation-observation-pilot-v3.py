"""CPU2/GPU0 six-second screen-geometry prototype; silent, not a final video.

Observe a manually inspected torso image point and its screen displacement.
These describe image coordinates only, not physical centroids or game-world axes.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, math, os, subprocess, traceback
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='2'
import psutil
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/observation-pilot-v3'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
FONT='C:/Windows/Fonts/malgunbd.ttf'
RED,GOLD,TEAL='#f54e4e','#ffe16b','#43ddce'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def now():return datetime.now(timezone.utc).isoformat()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,x):
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8');os.replace(tmp,p)
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
def label(d,xy,text,color,size=28):
    f=ImageFont.truetype(FONT,size);b=d.textbbox(xy,text,font=f)
    d.rounded_rectangle((b[0]-10,b[1]-6,b[2]+10,b[3]+8),radius=5,fill=(14,19,23,232))
    d.text(xy,text,font=f,fill=color)
def line(d,a,b,color,w=5):
    d.line((a,b),fill='#15191e',width=w+4);d.line((a,b),fill=color,width=w)
def arrow(d,a,b,color,w=5):
    line(d,a,b,color,w);dx=b[0]-a[0];dy=b[1]-a[1];n=math.hypot(dx,dy)
    if n>1:
        u,v=dx/n,dy/n
        d.polygon([b,(b[0]-18*u+9*v,b[1]-18*v-9*u),(b[0]-18*u-9*v,b[1]-18*v+9*u)],fill=color)
def drawing(im,frame,t):
    layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
    label(d,(64,28),'Superflight · NCR Gameplay · 화면 관찰','#ffffff',22)
    label(d,(64,95),'화면 위치와 몸의 자세를 구분하세요',GOLD,34)
    if frame>=20:
        arrow(d,(1720,370),(1720,195),GOLD)
        label(d,(1580,390),'화면의 위',GOLD)
    x,y=t['screenPoint']
    if frame>=35:
        d.ellipse((x-15,y-15,x+15,y+15),outline='#10191c',width=6)
        d.ellipse((x-12,y-12,x+12,y+12),outline=TEAL,width=4)
        d.ellipse((x-3,y-3,x+3,y+3),fill=TEAL)
        label(d,(64,178),'청록: 몸통의 화면 관찰점 p',TEAL)
    if frame>=100:
        arrow(d,t['previousScreenPoint'],t['screenPoint'],RED,5)
        label(d,(64,242),'빨강: 0.5초 동안의 화면 위치 변화',RED)
        label(d,(64,310),'Δp = p(t) − p(t − 0.5s)',RED,26)
    label(d,(64,810),'화면 위치에는 카메라의 움직임도 함께 나타납니다.','#ffffff',27)
    label(d,(64,855),'몸의 3D 자세는 다음 모형에서 세 축으로 설명합니다.','#ffffff',25)
    assert layer.getbbox()[3]<=910
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')

def point_at(frame,keyframes):
    for a,b in zip(keyframes,keyframes[1:]):
        if a['frame']<=frame<=b['frame']:
            u=(frame-a['frame'])/(b['frame']-a['frame'])
            return [round(a[k]+u*(b[k]-a[k]),3) for k in ('x','y')]
    raise ValueError(frame)

def main():
    sp=R/'observation-pilot-execution-v3.json'
    assert not sp.exists() and not LOCAL.exists(),'Resume existing pilot; never overwrite'
    baseline=read(R/'baseline-preservation-v1.json')
    assert all(sha(ROOT/x['path'])==x['sha256'] for x in baseline['protectedFiles'])
    processes=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',
        "Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python|ffmpeg|node)' -and ($_.CommandLine -match 'unpublished-teaching|train_multiview|phase1_train|gpu-handoff|queue|serve-native-review') } | Select-Object ProcessId,ParentProcessId,CreationDate,Name,CommandLine | ConvertTo-Json -Depth 3"],text=True,encoding='utf8'))
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],text=True)
    assert not any(x.get('CommandLine') and any(s in x['CommandLine'] for s in ('extract-orientation','render-orientation-observation')) and x['ProcessId']!=os.getpid() for x in processes)
    assert psutil.virtual_memory().available>8_000_000_000
    source=ROOT/'shared/output/game-math-part2-full-series/sources/-Hpr1dqRzIk.mp4'
    sourceHash=sha(source);assert sourceHash=='469df1da0e7fce4b5480064e43a2982e1121f9e1adb899acdbbd8f464371fd66'
    anchors={x['sourceFrame']-50400:x for x in read(R/'selected-native-v1/manifest.json')['samples'] if 50400<=x['sourceFrame']<50760}
    LOCAL.mkdir(parents=True)
    me=psutil.Process();state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,
        cpuThreads=2,gpuJobs=0,status='silent-observation-pilot-rendering',source=rel(source),sourceSha256=sourceHash,
        sourceFirstNativeFrame=50400,sourceEndExclusiveNativeFrame=50760,sourceTimebase='1/15360',nativePtsStep=256,
        sourcePtsIn=50400*256,sourcePtsOutExclusive=50760*256,frames=360,writtenFrames=0,
        resource={'cim':processes,'gpu':gpu.strip(),'observedAt':now()},actualOuterExitCode=None,workerExitCode=None,
        newTtsStarted=False,sourceAdoptionApproved=False,allMovingPixelsApproved=False,finalCueApproved=False,
        publicRightsApproved=False,humanListeningApproved=False,newImageGitAdded=0,researchManipulations=0)
    save(sp,state)
    dec=[FF,'-hide_banner','-nostdin','-v','error','-threads','1','-filter_threads','1','-ss','840','-i',str(source),'-frames:v','360','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
    target=LOCAL/'orientation.observation.silent-pilot.mp4'
    enc=[FF,'-hide_banner','-nostdin','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','60','-i','pipe:0','-frames:v','360','-an','-c:v','libx264','-threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(target)]
    save(LOCAL/'commands.json',dict(decode=dec,encode=enc))
    keyframes=read(R/'observation-point-keyframes-v3.json')['keyframes'];tracks=[]
    assert all(sha(ROOT/a['inspectedImage'])==a['inspectedImageSha256'] for a in keyframes)
    try:
        with (LOCAL/'decode.log').open('wb') as dl,(LOCAL/'encode.log').open('wb') as el:
            dp=subprocess.Popen(dec,stdout=subprocess.PIPE,stderr=dl,cwd=ROOT)
            ep=subprocess.Popen(enc,stdin=subprocess.PIPE,stderr=el,cwd=ROOT)
            state.update(decodePid=dp.pid,encodePid=ep.pid);save(sp,state)
            for frame in range(360):
                raw=dp.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3,(frame,len(raw))
                im=Image.frombytes('RGB',(1920,1080),raw)
                if frame in anchors:
                    a=anchors[frame];assert sha(ROOT/a['path'])==a['sha256']
                    with Image.open(ROOT/a['path']) as observed:assert observed.convert('RGB').tobytes()==raw,('native-pixel-mismatch',frame)
                point=point_at(frame,keyframes)
                previous=point_at(max(0,frame-30),keyframes)
                t=dict(frame=frame,sourceFrame=50400+frame,sourcePts=(50400+frame)*256,screenOnly=True,
                    visible=True,screenPoint=point,previousScreenPoint=previous,
                    screenDisplacementPixels=[round(point[k]-previous[k],3) for k in range(2)],
                    physicalCentroid=False,gameWorldAxis=False)
                tracks.append(t);ep.stdin.write(drawing(im,frame,t).tobytes())
                if frame%120==0:state['writtenFrames']=frame+1;save(sp,state)
            assert dp.stdout.read(1)==b'';dp.stdout.close();ep.stdin.close();dx=dp.wait();ex=ep.wait();assert dx==ex==0,(dx,ex)
        save(R/'observation-point-track-v3.json',dict(source=rel(source),sourceSha256=sourceHash,points=tracks,
            method='Manually inspected torso/back-block image observation point with linear interpolation. Red vector is p(t)-p(t-0.5s); it includes camera projection effects. This is not a physical centroid or world-space vector.',
            automaticTrackIsApproval=False,gameWorldMeasurement=False,rigidBodyRotationMeasurement=False))
        decode=[FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(target),'-f','null','-']
        with (LOCAL/'whole-decode.log').open('wb') as l:qa=subprocess.run(decode,stdout=l,stderr=subprocess.STDOUT).returncode
        assert qa==0
        samples=sorted(set(range(0,360,15))|{359});sel='+'.join(f'eq(pts,{n*1500})' for n in samples)
        extract=[FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-i',str(target),'-vf',f"select='{sel}',showinfo",'-fps_mode','passthrough','-frames:v',str(len(samples)),'-threads','2',str(LOCAL/'encoded-%03d.png')]
        with (LOCAL/'encoded-extract.log').open('wb') as l:rc=subprocess.run(extract,stdout=l,stderr=subprocess.STDOUT).returncode
        assert rc==0
        records=[dict(frame=n,path=rel(LOCAL/f'encoded-{j:03d}.png'),sha256=sha(LOCAL/f'encoded-{j:03d}.png')) for j,n in enumerate(samples,1)]
        boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
        for offset in range(0,len(records),6):
            board=Image.new('RGB',(1920,780),'#171a1e');d=ImageDraw.Draw(board)
            for j,r in enumerate(records[offset:offset+6]):
                x=j%3*640;y=j//3*390
                with Image.open(ROOT/r['path']) as im:board.paste(im.resize((640,360)),(x,y+30))
                t=tracks[r['frame']];d.text((x+8,y+5),f"f{r['frame']} source{t['sourceFrame']} authored image observation",font=font,fill='white')
            p=LOCAL/f'board-{offset//6+1:02d}.png';board.save(p);boards.append(dict(path=rel(p),sha256=sha(p)))
        assert all(sha(ROOT/x['path'])==x['sha256'] for x in baseline['protectedFiles'])
        probe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,time_base,nb_frames,duration','-of','json',str(target)],text=True))
        state.update(status='completed-silent-prototype-awaiting-direct-review',workerExitCode=0,finishedAt=now(),writtenFrames=360,
            decodeExitCode=dx,encodeExitCode=ex,wholeDecodeExitCode=qa,extractionExitCode=rc,hiddenFrames=sum(not x['visible'] for x in tracks),
            output=rel(target),outputSha256=sha(target),probe=probe,samples=records,boards=boards,baseline38Unchanged=True)
        save(sp,state);print(json.dumps({'workerExitCode':0,'frames':360,'samples':len(records),'boards':len(boards),'hiddenFrames':state['hiddenFrames']},ensure_ascii=False),flush=True)
    except BaseException as e:
        state.update(status='failed',workerExitCode=1,error=repr(e),traceback=traceback.format_exc(),finishedAt=now());save(sp,state);raise
if __name__=='__main__':main()

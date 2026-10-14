"""Decode five current-PCM explanation blocks and extract bounded encoded samples."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,os,psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OUT=ROOT/'shared/output/cross-game-example-coverage/motion/narration-timed-comparisons-qa-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
resource=dict(observedAt=datetime.now(timezone.utc).isoformat(),cpuLoadPercent=psutil.cpu_percent(interval=1),freePhysicalMemoryKiB=psutil.virtual_memory().available//1024,ownHeavyCpuJobs=0)
assert resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
execution=read(R/'narration-timed-comparisons-render-execution-v1.json')
assert execution['actualOuterExitCode']==0 and execution['actualExitCode']==0
assert not psutil.pid_exists(execution['pid'])
assert not OUT.exists();OUT.mkdir()
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21)
rows=[];decodes=[]
for row in execution['completed']:
    sid=row['id'];n=row['frames'];source=ROOT/row['path']
    assert sha(source)==row['sha256'] and sha(ROOT/row['source'])==row['sourceSha256']
    stream=json.loads(subprocess.check_output([FP,'-v','error','-show_streams','-of','json',str(source)],text=True))['streams'][0]
    assert stream['width']==1920 and stream['height']==1080 and int(stream['nb_frames'])==n
    assert stream['time_base']=='1/90000' and stream['avg_frame_rate']=='60/1'
    decode=subprocess.run([FF,'-v','error','-threads','2','-i',str(source),'-f','null','-'],capture_output=True,text=True)
    assert decode.returncode==0 and not decode.stderr,decode.stderr
    decodes.append(dict(id=sid,frames=n,wholeDecodeExitCode=0))
    frames=sorted(set([0,1,n-1,*[round((n-1)*k/8) for k in range(1,8)]]))
    folder=OUT/sid;folder.mkdir()
    select='+'.join(f'eq(n\\,{f})' for f in frames)
    ext=subprocess.run([FF,'-v','error','-threads','2','-i',str(source),'-vf','select='+select,'-vsync','0','-threads','2',str(folder/'sample-%02d.png')],capture_output=True,text=True)
    assert ext.returncode==0,ext.stderr
    files=sorted(folder.glob('sample-*.png'));assert len(files)==len(frames)
    for f,p in zip(frames,files):rows.append(dict(id=sid,frame=f,pts=f*1500,timeBase='1/90000',path=p.relative_to(ROOT).as_posix(),sha256=sha(p),source=row['path']))
boards=[]
for i in range(0,len(rows),4):
    items=rows[i:i+4];canvas=Image.new('RGB',(1920,1160),'#e4e8ed');draw=ImageDraw.Draw(canvas)
    for j,x in enumerate(items):
        xx=j%2*960;yy=j//2*580
        draw.text((xx+10,yy+5),f"{x['id']} frame{x['frame']} PTS{x['pts']} current-PCM explanation",font=font,fill='black')
        with Image.open(ROOT/x['path']) as im:canvas.paste(im.resize((960,540)),(xx,yy+40))
    p=OUT/f'board-{i//4+1:02d}.png';canvas.save(p);boards.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),samples=items))
value=dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),pid=os.getpid(),createTime=psutil.Process().create_time(),resource=resource,
    totalSelectedFrames=sum(x['frames'] for x in decodes),wholeDecodes=decodes,encodedSamples=len(rows),boards=boards,allSamples=rows,
    cpuThreads=2,gpuJobs=0,actualExtractionExitCode=0,directPixelReview=False,authoredAgainstMeasuredNarration=True,
    narrationTimedMovingPixelReview=False,finalCueApproval=False,allFinalPixelsApproved=False)
(R/'narration-timed-comparisons-qa-v1.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(wholeDecodes=len(decodes),samples=len(rows),boards=len(boards),frames=value['totalSelectedFrames'])))

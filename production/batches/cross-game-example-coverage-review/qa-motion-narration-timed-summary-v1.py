"""Decode the three selected 33.28s current-PCM landmark renders and sample exact encoded frames."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,os
from PIL import Image,ImageDraw,ImageFont
import psutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OUT=ROOT/'shared/output/cross-game-example-coverage/motion/narration-timed-summary-qa-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
resource=dict(observedAt=datetime.now(timezone.utc).isoformat(),cpuLoadPercent=psutil.cpu_percent(interval=1),freePhysicalMemoryKiB=psutil.virtual_memory().available//1024,ownHeavyCpuJobs=0)
assert resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
assert not OUT.exists();OUT.mkdir()
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
frames=[0,1,180,192,246,336,390,480,512,540,600,648,690,764,810,895,960,1020,1086,1140,1230,1380,1500,1596,1680,1715,1750,1800,1900,1996]
rows=[]
for sid in ['11b']:
    execution=read(R/'narration-timed-summary-render-execution-v1.json')
    assert execution['actualOuterExitCode']==0
    assert not psutil.pid_exists(execution['pid'])
    row=next(x for x in execution['completed'] if x['id']==sid)
    assert execution['actualExitCode']==0 and row['actualFfmpegExitCode']==0
    source=ROOT/row['path'];assert sha(source)==row['sha256']
    assert sha(ROOT/row['source'])==row['sourceSha256']
    probe=json.loads(subprocess.check_output([FP,'-v','error','-show_streams','-show_format','-of','json',str(source)],text=True))
    stream=probe['streams'][0];assert stream['width']==1920 and stream['height']==1080 and stream['nb_frames']=='1997'
    assert stream['time_base']=='1/90000' and stream['avg_frame_rate']=='60/1'
    decode=subprocess.run([FF,'-v','error','-threads','2','-i',str(source),'-f','null','-'],capture_output=True,text=True)
    assert decode.returncode==0 and not decode.stderr,decode.stderr
    folder=OUT/sid;folder.mkdir()
    select='+'.join(f'eq(n\\,{f})' for f in frames)
    cmd=[FF,'-v','error','-threads','2','-i',str(source),'-vf','select='+select,'-vsync','0','-threads','2',str(folder/'sample-%02d.png')]
    ext=subprocess.run(cmd,capture_output=True,text=True);assert ext.returncode==0,ext.stderr
    files=sorted(folder.glob('sample-*.png'));assert len(files)==len(frames)
    for f,p in zip(frames,files):rows.append(dict(id=sid,frame=f,pts=f*1500,timeBase='1/90000',path=str(p.relative_to(ROOT)),sha256=sha(p),source= row['path']))
boards=[]
for i in range(0,len(rows),4):
    items=rows[i:i+4];canvas=Image.new('RGB',(1920,1160),'#e4e8ed');draw=ImageDraw.Draw(canvas)
    for j,x in enumerate(items):
        xx=(j%2)*960;yy=(j//2)*580
        draw.text((xx+10,yy+5),f"{x['id']} exact frame {x['frame']} / PTS {x['pts']} / 33.28s current-PCM landmark render",font=font,fill='black')
        with Image.open(ROOT/x['path']) as im:canvas.paste(im.resize((960,540)),(xx,yy+40))
    p=OUT/f'board-{i//4+1:02d}.png';canvas.save(p);boards.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),samples=items))
value=dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),pid=os.getpid(),createTime=psutil.Process().create_time(),
    totalSelectedFrames=1997,wholeDecodeExitCodes=[0],encodedSamples=30,boards=boards,allSamples=rows,
    cpuThreads=2,gpuJobs=0,actualExtractionExitCode=0,directPixelReview=False,authoredAgainstMeasuredNarration=True,narrationTimedMovingPixelReview=False,finalCueApproval=False,allFinalPixelsApproved=False)
(R/'narration-timed-summary-qa-v1.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8')
print('One whole decode0/30 exact encoded samples/8boards; current-narration moving pixel direct review pending.')

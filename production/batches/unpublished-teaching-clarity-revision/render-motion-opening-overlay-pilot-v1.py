"""Bounded moving annotation pilot on the exact selected 58–69s action.

Silent visual draft only. Track one visible post with template matching;
hide a lost marker instead of attaching it to an invented world point.
All final narration/caption/mix/timing approvals remain false.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, math, os, subprocess, traceback
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:
    os.environ[key] = '2'
import psutil
import numpy as np
from scipy.signal import correlate2d
from scipy.ndimage import uniform_filter
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
R = ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
LOCAL = ROOT/'shared/output/unpublished-teaching-clarity-revision/motion/opening-overlay-pilot-v1'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FP = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
def now():return datetime.now(timezone.utc).isoformat()
def save(p,x):
    temp=p.with_name(p.name+f'.{os.getpid()}.writing')
    temp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(temp,p)
FONT = 'C:/Windows/Fonts/malgunbd.ttf'
RED, BLUE, GOLD = '#ff4949','#55bfff','#ffe06b'
def label(draw,xy,text,color,size=30):
    font=ImageFont.truetype(FONT,size);box=draw.textbbox(xy,text,font=font)
    draw.rounded_rectangle((box[0]-10,box[1]-5,box[2]+10,box[3]+7),radius=5,fill=(15,21,25,220))
    draw.text(xy,text,font=font,fill=color)
def line(draw,a,b,color,width=5):
    draw.line((a,b),fill=(8,14,20,255),width=width+4)
    draw.line((a,b),fill=color,width=width)
def arrow(draw,a,b,color,width=5):
    line(draw,a,b,color,width);dx,dy=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dy)
    if n:
        u,v=dx/n,dy/n
        draw.polygon([b,(b[0]-20*u+10*v,b[1]-20*v-10*u),
                        (b[0]-20*u-10*v,b[1]-20*v+10*u)],fill=color)
def annotate(im,frame,track):
    layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
    label(d,(600,120),'물줄기로 바닥의 때를 지우는 작업',GOLD,32)
    label(d,(605,28),'PowerWash Simulator · FuturLab 개발 시연 (2022 WIP) · 발췌','#ffffff',22)
    # Reticle/nozzle remain at these observed screen positions in this selected
    # action. Offset the line slightly alongside the jet to retain its pixels.
    if frame>=18:
        arrow(d,(1090,625),(1000,516),RED)
        label(d,(1150,526),'조준 방향',RED)
    if track['visible'] and frame>=45:
        x,y=track['xy'];line(d,(x,y-64),(x,y+64),BLUE,5)
        line(d,(x-14,y-64),(x+14,y-64),BLUE,4)
        line(d,(x-14,y+64),(x+14,y+64),BLUE,4)
        lx=min(1510,max(620,x+35));ly=max(190,min(690,y-48))
        label(d,(lx,ly),'배경 기둥',BLUE,28)
    if frame>=95:
        label(d,(550,706),'닿는 바닥',GOLD,28)
        arrow(d,(750,704),(890,586),GOLD,4)
    label(d,(650,850),'조준 방향과 배경의 변화를 따로 보세요','#ffffff',28)
    # No glyph extends below910; final boxed narration is not burned into this
    # silent pilot. Its actual cues will be checked after measured voice timing.
    assert layer.getbbox()[3]<=910
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
    resource=read(ROOT/args.resource)
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
    assert resource['ownHeavyCpuJobs']==0 and resource['cpuLoadPercent']<85
    assert resource['freePhysicalMemoryKiB']>8_000_000
    statepath=R/'opening-overlay-pilot-execution-v1.json';assert not statepath.exists() and not LOCAL.exists()
    bank=read(R/'sources/source-action-bank-v1.json');action=bank['actions'][0]
    assert action['id']=='early-cleaning' and action['sourceFirstFrame']==3480 and action['frames']==660
    assert bank['sourceSelectionPreflightApproved'] and sha(ROOT/bank['source'])==bank['sourceSha256']
    protected=read(R/'narration-tts-waiting-v1.json')['protectedInputs']
    for row in protected:assert sha(ROOT/row['path'])==row['sha256']
    LOCAL.mkdir(parents=True)
    me=psutil.Process();state=dict(schemaVersion=1,startedAt=now(),pid=me.pid,createTime=me.create_time(),
        commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,cpuThreads=2,gpuJobs=0,
        resource=resource,status='rendering-silent-annotation-pilot',source=bank['source'],
        sourceSha256=bank['sourceSha256'],sourceFirstFrame=3480,sourceEndExclusiveFrame=4140,
        frames=660,writtenFrames=0,outerExitCode=None,exitCode=None,
        worldCoordinateMeasurement=False,clinicalComfortOutcomeClaimed=False,
        timedNarrationApproved=False,allMovingPixelsApproved=False,finalCuePixelsApproved=False,
        finalVideoApproved=False,sourceAudioUsed=False,newImageGitAdded=0,researchManipulations=0)
    save(statepath,state)
    dec=[FF,'-hide_banner','-nostdin','-v','error','-threads','1','-filter_threads','1',
        '-ss','58','-i',str(ROOT/bank['source']),'-frames:v','660','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
    clean=LOCAL/'opening.annotated.silent-pilot.mp4'
    enc=[FF,'-hide_banner','-nostdin','-v','error','-f','rawvideo','-pixel_format','rgb24',
        '-video_size','1920x1080','-framerate','60','-i','pipe:0','-frames:v','660','-an',
        '-c:v','libx264','-threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',
        '-video_track_timescale','90000','-movflags','+faststart',str(clean)]
    state.update(decodeCommand=dec,encodeCommand=enc);save(statepath,state)
    native=read(ROOT/'production/batches/unpublished-teaching-clarity-revision/motion-opening-native-execution-v6.json')['windows'][0]
    anchors={row['sourceFrame']-3480:row for row in native['samples']}
    points=set(range(0,660,30))|set(anchors)|{659}
    records=[];tracks=[];previous=np.array([325.,117.]);template=None;failures=0
    try:
        with (LOCAL/'source-decode.log').open('wb') as dl,(LOCAL/'annotation-encode.log').open('wb') as el:
            decoder=subprocess.Popen(dec,stdout=subprocess.PIPE,stderr=dl,cwd=ROOT)
            encoder=subprocess.Popen(enc,stdin=subprocess.PIPE,stderr=el,cwd=ROOT)
            for frame in range(660):
                raw=decoder.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3,(frame,len(raw))
                im=Image.frombytes('RGB',(1920,1080),raw)
                if frame in anchors:
                    p=ROOT/anchors[frame]['path'];assert sha(p)==anchors[frame]['sha256']
                    with Image.open(p) as observed:
                        assert observed.convert('RGB').tobytes()==raw,('native-sample-mismatch',frame)
                gray=np.asarray(im.resize((640,360)).convert('L'),dtype=np.float32)
                if frame==0:
                    template=gray[107:127,318:332].copy();center=previous.copy();score=1.;visible=True
                else:
                    x,y=previous
                    x0=max(7,int(round(x))-22);x1=min(633,int(round(x))+22)
                    y0=max(10,int(round(y))-18);y1=min(350,int(round(y))+18)
                    area=gray[y0-10:y1+10,x0-7:x1+7]
                    t=template-template.mean();den=float(np.sum(t*t))
                    dot=correlate2d(area,t,mode='valid')
                    # Sum/sum-of-square of each template-sized window.
                    kernel=np.ones(template.shape,dtype=np.float32)
                    totals=correlate2d(area,kernel,mode='valid')
                    squares=correlate2d(area*area,kernel,mode='valid')
                    variance=np.maximum(squares-totals*totals/template.size,1.)
                    ncc=dot/np.sqrt(variance*max(den,1.))
                    yy,xx=np.unravel_index(int(np.argmax(ncc)),ncc.shape)
                    score=float(ncc[yy,xx]);candidate=np.array([x0+xx,y0+yy],dtype=float)
                    # Reject sudden hops; a failed marker is hidden, never called
                    # a reliable world/object coordinate.
                    visible=score>=.72 and np.linalg.norm(candidate-previous)<18
                    if visible:
                        previous=candidate;failures=0
                        if score>.92:template=gray[int(candidate[1])-10:int(candidate[1])+10,
                                                  int(candidate[0])-7:int(candidate[0])+7].copy()
                    else:failures+=1
                    center=previous.copy()
                track=dict(frame=frame,sourceFrame=3480+frame,sourcePts=(3480+frame)*256,
                    xy=[round(float(v)*3,2) for v in center],confidence=round(score,5),
                    visible=bool(visible),consecutiveFailures=failures,screenOnly=True)
                tracks.append(track)
                annotated=annotate(im,frame,track);encoder.stdin.write(annotated.tobytes())
                if frame in points:
                    target=LOCAL/f'prepared-f{frame:04d}.png';annotated.save(target)
                    records.append(dict(frame=frame,path=rel(target),sha256=sha(target)))
                if frame%120==0:
                    state['writtenFrames']=frame+1;save(statepath,state)
            assert decoder.stdout.read(1)==b''
            decoder.stdout.close();encoder.stdin.close();dx=decoder.wait();ex=encoder.wait()
            assert dx==ex==0,(dx,ex)
        tracking=R/'opening-background-post-track-v1.json'
        save(tracking,dict(source=bank['source'],sourceSha256=bank['sourceSha256'],
            sourceFirstFrame=3480,points=tracks,method='Local normalized template matching with hidden low-confidence markers',
            automaticTrackIsApproval=False,worldCoordinateMeasurement=False))
        boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
        for n in range(0,len(records),6):
            board=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(board)
            for j,row in enumerate(records[n:n+6]):
                x=j%3*640;y=j//3*390
                with Image.open(ROOT/row['path']) as img:board.paste(img.resize((640,360)),(x,y+30))
                track=tracks[row['frame']]
                d.text((x+6,y+4),f"f{row['frame']} / postNCC{track['confidence']:.2f} / visible{track['visible']}",font=font,fill='white')
            target=LOCAL/f'board-{n//6+1:02d}.png';board.save(target)
            boards.append(dict(path=rel(target),sha256=sha(target)))
        with (LOCAL/'whole-decode.log').open('wb') as log:
            decode=subprocess.run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(clean),'-f','null','-'],stdout=log,stderr=log,check=True).returncode
        pts=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_frames',
            '-show_entries','frame=pts','-of','json',str(clean)]))
        assert [int(x['pts']) for x in pts['frames']]==list(range(0,660*1500,1500))
        for row in protected:assert sha(ROOT/row['path'])==row['sha256'],row['path']
        state.update(status='silent-pilot-completed-awaiting-direct-moving-review',exitCode=0,finishedAt=now(),
            writtenFrames=660,sourceDecodeExitCode=dx,annotationEncodeExitCode=ex,wholeDecodeExitCode=decode,
            allPts1500Verified=True,all25NativeRgbSamplesMatched=True,
            sourceTrack=rel(tracking),sourceTrackSha256=sha(tracking),
            hiddenTrackFrames=sum(not x['visible'] for x in tracks),
            silentPilot=dict(path=rel(clean),sha256=sha(clean),audioStreams=0),
            preparedSamples=records,boards=boards,allProtectedInputsUnchanged=True)
        save(statepath,state)
        print(json.dumps(dict(exitCode=0,frames=660,samples=len(records),boards=len(boards),
            hiddenTrackFrames=state['hiddenTrackFrames'],silentVisualDraft=True)),flush=True)
    except BaseException:
        state.update(status='failed-preserve-pilot-and-history',exitCode=1,error=traceback.format_exc(),finishedAt=now())
        save(statepath,state);raise

if __name__=='__main__':main()

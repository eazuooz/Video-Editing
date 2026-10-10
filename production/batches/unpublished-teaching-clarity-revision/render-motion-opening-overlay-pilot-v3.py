"""Dense same-post native anchors; preserve V1 and V2 observations.

Manual anchors identify the same front timber support in native reviewed samples.
Dense reviewed anchor interpolation follows that support; no NCC/color-match substitution.
Lost/offscreen markers are hidden. This is a silent moving pilot, not final QA.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json, os, subprocess, traceback
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']: os.environ[k]='2'
import psutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/motion/opening-overlay-pilot-v3'
spec=importlib.util.spec_from_file_location('pilot_v1',Path(__file__).with_name('render-motion-opening-overlay-pilot-v1.py'))
v1=importlib.util.module_from_spec(spec);spec.loader.exec_module(v1)
read=v1.read;sha=v1.sha;save=v1.save;rel=v1.rel;now=v1.now;FF=v1.FF;FP=v1.FP
# These are semantic guides at y320 on the same front post, not a claimed world
# coordinate. Values outside1920 intentionally suppress the marker.
GUIDE=[(0,986),(1,986),(15,1021),(30,1217),(45,1406),(60,1713),(75,2020),
 (90,1860),(105,1529),(120,1304),(135,1152),(150,1008),(165,996),(180,1142),
 (195,1344),(210,1561),(225,1561),(240,1567),(255,1491),(270,1817),(285,2010),
 (300,2070),(315,1960),(330,1852),(345,1592),(360,1444),(375,1269),(390,1465),
 (405,1753),(420,1888),(435,2070),(450,2090),(465,1880),(480,1605),(495,1362),
 (510,1346),(525,1576),(540,1841),(555,2010),(570,2180),(585,2175),(600,2170),
 (615,2025),(630,1869),(645,1885),(658,1885),(659,1885)]
def track(im, frame):
    x=float(np.interp(frame,[v[0] for v in GUIDE],[v[1] for v in GUIDE]))
    return dict(frame=frame,sourceFrame=3480+frame,sourcePts=(3480+frame)*256,
        guidedX=round(x,2),xy=[round(x,2),320],visible=x<1905,
        semanticObject='same front gold timber support of playground tower',
        method='Dense native semantic anchors interpolated; inspect continuous moving pixels',
        automaticTrackIsApproval=False)
def annotate(im, frame, t):
    layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
    v1.label(d,(575,115),'物줄기로 바닥의 때를 지우는 작업'.replace('物','물'),v1.GOLD,32)
    v1.label(d,(560,28),'PowerWash Simulator · FuturLab 개발 시연 (2022 WIP) · 발췌','#ffffff',22)
    if frame>=18:
        v1.arrow(d,(1090,625),(1000,516),v1.RED)
        v1.label(d,(1150,526),'조준 방향',v1.RED)
    if t['visible'] and frame>=45:
        x,y=t['xy'];v1.line(d,(x,y-60),(x,y+60),v1.BLUE,5)
        v1.line(d,(x-14,y-60),(x+14,y-60),v1.BLUE,4)
        v1.line(d,(x-14,y+60),(x+14,y+60),v1.BLUE,4)
        # Keep its label beside the support, away from sourceHUD and reticle.
        lx=x+34 if x<1450 else x-235
        v1.label(d,(lx,235),'배경 기둥',v1.BLUE,28)
    elif frame>=45:
        v1.label(d,(1520,235),'기둥은 화면 밖',v1.BLUE,28)
        v1.arrow(d,(1760,325),(1870,325),v1.BLUE,4)
    if frame>=95:
        v1.label(d,(550,706),'닿는 바닥',v1.GOLD,28)
        v1.arrow(d,(750,704),(890,586),v1.GOLD,4)
    v1.label(d,(650,850),'조준 방향과 배경의 변화를 따로 보세요','#ffffff',28)
    assert layer.getbbox()[3]<=910
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
    resource=read(ROOT/args.resource)
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
    assert resource['ownHeavyCpuJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
    sp=R/'opening-overlay-pilot-execution-v3.json';assert not sp.exists() and not LOCAL.exists()
    old=read(R/'opening-overlay-pilot-execution-v1.json');assert old['exitCode']==0
    bank=read(R/'sources/source-action-bank-v1.json');assert sha(ROOT/bank['source'])==bank['sourceSha256']
    protected=read(R/'narration-tts-waiting-v1.json')['protectedInputs']
    for row in protected:assert sha(ROOT/row['path'])==row['sha256']
    LOCAL.mkdir(parents=True);me=psutil.Process()
    state=dict(schemaVersion=1,startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),
        cwd=me.cwd(),sessionId=None,cpuThreads=2,gpuJobs=0,resource=resource,status='rendering-dense-native-post-silent-pilot',
        source=bank['source'],sourceSha256=bank['sourceSha256'],sourceFirstFrame=3480,sourceEndExclusiveFrame=4140,
        frames=660,writtenFrames=0,exitCode=None,allMovingPixelsApproved=False,finalVideoApproved=False,
        timedNarrationApproved=False,finalCuePixelsApproved=False,worldCoordinateMeasurement=False,
        clinicalComfortOutcomeClaimed=False,sourceAudioUsed=False,researchManipulations=0,newImageGitAdded=0,
        v1Preserved=True,v2Preserved=True,v2Finding='Semantic color refinement still hid visible post at f255/375/495; dense native guides added',v1Finding='NCC followed a different structure despite high match confidence',
        semanticGuides=GUIDE,semanticGuidesAreFinalPixelApproval=False)
    save(sp,state)
    dec=[FF,'-hide_banner','-nostdin','-v','error','-threads','1','-filter_threads','1','-ss','58',
         '-i',str(ROOT/bank['source']),'-frames:v','660','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
    target=LOCAL/'opening.annotated.silent-pilot.mp4'
    enc=[FF,'-hide_banner','-nostdin','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080',
         '-framerate','60','-i','pipe:0','-frames:v','660','-an','-c:v','libx264','-threads','1','-preset','veryfast',
         '-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(target)]
    native=read(ROOT/'production/batches/unpublished-teaching-clarity-revision/motion-opening-native-execution-v6.json')['windows'][0]
    refs={row['sourceFrame']-3480:row for row in native['samples']};points=set(refs)|set(range(0,660,15))|{659}
    tracks=[];samples=[]
    try:
        with (LOCAL/'source-decode.log').open('wb') as dl,(LOCAL/'annotation-encode.log').open('wb') as el:
            decoder=subprocess.Popen(dec,stdout=subprocess.PIPE,stderr=dl,cwd=ROOT)
            encoder=subprocess.Popen(enc,stdin=subprocess.PIPE,stderr=el,cwd=ROOT)
            for f in range(660):
                raw=decoder.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3
                im=Image.frombytes('RGB',(1920,1080),raw)
                if f in refs:
                    p=ROOT/refs[f]['path'];assert sha(p)==refs[f]['sha256']
                    with Image.open(p) as img:assert img.convert('RGB').tobytes()==raw
                t=track(im,f);tracks.append(t);out=annotate(im,f,t);encoder.stdin.write(out.tobytes())
                if f in points:
                    p=LOCAL/f'prepared-f{f:04d}.png';out.save(p)
                    samples.append(dict(frame=f,path=rel(p),sha256=sha(p)))
                if f%120==0:state['writtenFrames']=f+1;save(sp,state)
            assert decoder.stdout.read(1)==b'';decoder.stdout.close();encoder.stdin.close()
            dx=decoder.wait();ex=encoder.wait();assert dx==ex==0
        tp=R/'opening-background-post-track-v3.json';save(tp,dict(points=tracks,guides=GUIDE,
            method='Dense directly reviewed semantic post anchors, interpolated in screen coordinates; offscreen arrow explicitly labelled',
            automaticTrackIsApproval=False,worldCoordinateMeasurement=False))
        boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
        for n in range(0,len(samples),6):
            im=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(im)
            for j,row in enumerate(samples[n:n+6]):
                x=j%3*640;y=j//3*390
                with Image.open(ROOT/row['path']) as pic:im.paste(pic.resize((640,360)),(x,y+30))
                t=tracks[row['frame']];d.text((x+5,y+4),f"f{row['frame']} / post={t['xy'][0]} / visible={t['visible']}",font=font,fill='white')
            p=LOCAL/f'board-{n//6+1:02d}.png';im.save(p);boards.append(dict(path=rel(p),sha256=sha(p)))
        with (LOCAL/'whole-decode.log').open('wb') as log:
            dx2=subprocess.run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(target),'-f','null','-'],stdout=log,stderr=log,check=True).returncode
        pts=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=pts','-of','json',str(target)]))
        assert [int(x['pts']) for x in pts['frames']]==list(range(0,660*1500,1500))
        for row in protected:assert sha(ROOT/row['path'])==row['sha256']
        state.update(status='silent-pilot-complete-awaiting-direct-moving-review',exitCode=0,finishedAt=now(),
            sourceDecodeExitCode=dx,annotationEncodeExitCode=ex,wholeDecodeExitCode=dx2,writtenFrames=660,
            allPts1500Verified=True,all25NativeRgbSamplesMatched=True,allProtectedInputsUnchanged=True,
            hiddenTrackFrames=sum(not x['visible'] for x in tracks),sourceTrack=rel(tp),sourceTrackSha256=sha(tp),
            preparedSamples=samples,boards=boards,silentPilot=dict(path=rel(target),sha256=sha(target),audioStreams=0))
        save(sp,state);print(json.dumps(dict(exitCode=0,frames=660,samples=len(samples),boards=len(boards),hiddenTrackFrames=state['hiddenTrackFrames'])))
    except BaseException:
        state.update(status='failed-preserve-v3',exitCode=1,error=traceback.format_exc(),finishedAt=now());save(sp,state);raise
if __name__=='__main__': main()

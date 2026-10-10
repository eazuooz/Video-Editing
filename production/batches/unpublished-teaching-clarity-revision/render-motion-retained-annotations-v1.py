"""One serial CPU-only job: six retained native windows with editable annotations.

Prepared still review precedes this job. The result remains a silent visual
intermediate until its encoded moving pixels and final narrated captions pass.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, importlib.util, json, os, subprocess, traceback
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='2'
import psutil
from PIL import Image, ImageDraw, ImageFont
spec=importlib.util.spec_from_file_location('anchors_v5',Path(__file__).with_name('prepare-motion-semantic-anchors-v5.py'))
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
ROOT,R,draw=a.ROOT,a.R,a.draw
OUT=ROOT/'shared/output/unpublished-teaching-clarity-revision/motion/retained-annotations-v1'
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
    resource=draw.read(ROOT/args.resource)
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
    assert resource['ownHeavyCpuJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
    review=draw.read(R/'retained-semantic-sample-direct-review-v5.json');assert review['selectedSampleReviewPassed']
    checkpoint=draw.read(R/'latest-checkpoint.json');assert checkpoint['currentUnmixedContentReviewPassed']
    subprocess.run([NODE,'scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],cwd=ROOT,check=True)
    protected=draw.read(R/'narration-tts-waiting-v1.json')['protectedInputs']
    for row in protected:assert draw.sha(ROOT/row['path'])==row['sha256']
    selected=draw.read(R/'retained-semantic-anchor-preparation-v5.json')
    for w in selected['windows']:
        for row in w['samples']+w['boards']:assert draw.sha(ROOT/row['path'])==row['sha256']
    sp=R/'retained-annotation-render-execution-v1.json';assert not sp.exists() and not OUT.exists()
    OUT.mkdir(parents=True);me=psutil.Process()
    state=dict(schemaVersion=1,startedAt=draw.now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),
      sessionId=None,status='rendering-six-retained-annotation-windows',cpuThreads=2,gpuJobs=0,resource=resource,
      selectedSampleReview=draw.rel(R/'retained-semantic-sample-direct-review-v5.json'),windows=[],actualExitCode=None,
      allMovingPixelsApproved=False,allFinalCaptionedPixelsApproved=False,currentMixedAudioApproved=False,
      sourceAudioUsed=False,sourceSpeed=1,researchManipulations=0,newGitImages=0,sourceOrPcmModified=0)
    draw.save(sp,state)
    try:
        for w in a.v4.pre['windows']:
            sid=w['scene'];n=w['frames'];folder=OUT/f'scene{sid}';folder.mkdir()
            src=ROOT/w['source'];assert draw.sha(src)==w['sourceSha256']
            target=folder/'annotated.silent.mp4'
            dec=[draw.FF,'-hide_banner','-nostdin','-v','error','-threads','1','-filter_threads','1','-i',str(src),
              '-frames:v',str(n),'-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
            enc=[draw.FF,'-hide_banner','-nostdin','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080',
              '-framerate','60','-i','pipe:0','-frames:v',str(n),'-an','-c:v','libx264','-threads','1','-preset','veryfast',
              '-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(target)]
            refs={r['frame']:r for r in w['samples']}
            prepared=next(x for x in selected['windows'] if x['scene']==sid);prepared_refs={r['frame']:r for r in prepared['samples']}
            critical={'01':[89,90,91,210,211],'03':[],'05':[1,14,15,90,91],
              '07':[44,45,46,149,150,151,204,205],'09':[299,300,301,314,315,316,337,338,339],
              '11':[60,61,179,180,181,210,211]}[sid]
            points=set(refs)|set(critical);tracks=[]
            ws=dict(scene=sid,source=w['source'],sourceSha256=w['sourceSha256'],sceneLocalStart=w['sceneLocalStart'],
              frames=n,writtenFrames=0,sourceDecodeExitCode=None,encodeExitCode=None)
            state['windows'].append(ws);draw.save(sp,state)
            with (folder/'source-decode.log').open('wb') as dl,(folder/'encode.log').open('wb') as el:
                decoder=subprocess.Popen(dec,stdout=subprocess.PIPE,stderr=dl,cwd=ROOT)
                encoder=subprocess.Popen(enc,stdin=subprocess.PIPE,stderr=el,cwd=ROOT)
                for f in range(n):
                    raw=decoder.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3
                    im=Image.frombytes('RGB',(1920,1080),raw)
                    if f in refs:
                        row=refs[f];p=ROOT/row['path'];assert draw.sha(p)==row['sha256']
                        with Image.open(p) as pic:assert pic.convert('RGB').tobytes()==raw
                    p=a.point(im,sid,f);p['frame']=f;tracks.append(p);out=a.annotate(im,sid,f,p)
                    if f in prepared_refs:
                        with Image.open(ROOT/prepared_refs[f]['path']) as pic:assert out.tobytes()==pic.convert('RGB').tobytes()
                    encoder.stdin.write(out.tobytes())
                    if f%120==0:ws['writtenFrames']=f+1;draw.save(sp,state)
                decoder.stdout.close();encoder.stdin.close()
                dx=decoder.wait();ex=encoder.wait();assert dx==ex==0
            trackpath=folder/'all-frame-semantic-guides.json';draw.save(trackpath,dict(points=tracks,worldCoordinatesMeasured=False,automaticTrackIsApproval=False))
            with (folder/'whole-decode.log').open('wb') as log:
                dx2=subprocess.run([draw.FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(target),'-f','null','-'],stdout=log,stderr=log,check=True).returncode
            probe=json.loads(subprocess.check_output([draw.FP,'-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=pts','-of','json',str(target)]))
            assert [int(x['pts']) for x in probe['frames']]==list(range(0,n*1500,1500))
            # Use absolute PTS, not filter-frame n, for every critical encoded sample.
            frames=sorted(points);expression='+'.join(f'eq(pts,{f*1500})' for f in frames)
            with (folder/'encoded-extraction.log').open('wb') as log:
                qx=subprocess.run([draw.FF,'-hide_banner','-nostdin','-v','error','-threads','2','-filter_threads','1','-i',str(target),
                  '-vf',f'select={expression.replace(",",chr(92)+",")}','-fps_mode','passthrough',str(folder/'encoded-%04d.png')],stdout=log,stderr=log,check=True).returncode
            pngs=sorted(folder.glob('encoded-*.png'));assert len(pngs)==len(frames)
            samples=[dict(frame=f,pts=f*1500,path=draw.rel(p),sha256=draw.sha(p)) for f,p in zip(frames,pngs)]
            boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
            for i in range(0,len(samples),6):
                im=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(im)
                for j,row in enumerate(samples[i:i+6]):
                    x=j%3*640;y=j//3*390;im.paste(Image.open(ROOT/row['path']).resize((640,360)),(x,y+30))
                    t=tracks[row['frame']];d.text((x+5,y+4),f"scene{sid} f{row['frame']} visible{t['visible']}",font=font,fill='white')
                dest=folder/f'board-{i//6+1:02d}.png';im.save(dest);boards.append(dict(path=draw.rel(dest),sha256=draw.sha(dest)))
            ws.update(writtenFrames=n,sourceDecodeExitCode=dx,encodeExitCode=ex,wholeDecodeExitCode=dx2,extractionExitCode=qx,
              allPts1500Verified=True,allNativeSampleRgbMatched=True,allPreparedSampleRgbMatched=True,
              video=dict(path=draw.rel(target),sha256=draw.sha(target),audioStreams=0),samples=samples,boards=boards,
              allFrameGuides=dict(path=draw.rel(trackpath),sha256=draw.sha(trackpath)))
            draw.save(sp,state);print(json.dumps(dict(scene=sid,frames=n,samples=len(samples),boards=len(boards))),flush=True)
        for row in protected:assert draw.sha(ROOT/row['path'])==row['sha256']
        state.update(status='six-silent-windows-complete-awaiting-direct-encoded-review',actualExitCode=0,finishedAt=draw.now(),
          allProtectedInputsUnchanged=True,frames=sum(x['frames'] for x in state['windows']),samples=sum(len(x['samples']) for x in state['windows']))
        draw.save(sp,state)
    except BaseException:
        state.update(status='failed-preserve-local-output',actualExitCode=1,error=traceback.format_exc(),finishedAt=draw.now());draw.save(sp,state);raise
if __name__=='__main__':main()

"""One owned CPU batch, six repaired narrated gameplay overlays; previous pilots are preserved.

Original PCM/timing and source credits are retained. Pilot audio is for
review only; the final whole video must copy the original whole AAC.
"""
from pathlib import Path
from datetime import datetime, timezone
import os, json, subprocess, importlib.util, argparse
os.environ['OMP_NUM_THREADS']='2'
os.environ['OPENBLAS_NUM_THREADS']='2'
import psutil
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/six-moving-pilots-v4'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
spec=importlib.util.spec_from_file_location('polar_remaining_annotation',Path(__file__).with_name('prepare-polar-remaining-annotations-v4.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
sha,rel=module.sha,module.rel
def secs(value):
    a,b,c=value.split(':');return int(a)*3600+int(b)*60+float(c)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);ap.add_argument('--asr-outer-exit-code',required=True,type=int);args=ap.parse_args()
    assert args.asr_outer_exit_code==0
    asr=json.loads((OUT/'current-whole-audio-asr-execution-v1.json').read_text(encoding='utf-8'))
    assert asr['exitCode']==0 and asr['completed']==38
    assert not psutil.pid_exists(asr['pid']) or psutil.Process(asr['pid']).create_time()!=asr['createTime']
    resource=json.loads((ROOT/args.resource).read_text(encoding='utf-8'))
    assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8000000
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
    LOCAL.mkdir(parents=True,exist_ok=True)
    statefile=OUT/'six-moving-pilots-execution-v4.json';assert not statefile.exists()
    preparation=json.loads((OUT/'remaining-editorial-annotation-preparation-v4.json').read_text(encoding='utf-8'))
    proof=json.loads((OUT/'remaining-editorial-annotation-direct-review-v4.json').read_text(encoding='utf-8'))
    assert proof['sixBoundedPreparedLayoutsApproved'] and proof['all150PreparedSamplesAnd27BoardsDirectlyRead']
    snapshot=json.loads((OUT/'baseline-protected-sha-v1.json').read_text(encoding='utf-8'))
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in snapshot['files'])
    state={'resourceEvidence':args.resource,'priorAsrOuterExitCode':args.asr_outer_exit_code,'startedAt':datetime.now(timezone.utc).isoformat(),'pid':os.getpid(),'createTime':psutil.Process().create_time(),'commandLine':psutil.Process().cmdline(),'cwd':str(ROOT),'cpuThreads':2,'gpuJobs':0,'status':'running','jobs':[],
      'scene08RepairEvidence':'scene08-selected-source-direct-review-v2.json',
      'narrationChanged':False,'baselineMutations':0,'currentWholeMixedAsrApproved':False,'wholeVideoApproved':False,'allFinalPixelsApproved':False}
    def save():statefile.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def run(cmd,log):
        state['currentCommand']=cmd;save()
        with log.open('wb') as f:r=subprocess.run(cmd,stdout=f,stderr=f,check=True,cwd=ROOT)
        return r.returncode
    save();print(json.dumps({'pid':state['pid'],'createTime':state['createTime']}),flush=True)
    try:
        for prepared in preparation['jobs']:
            sid=prepared['scene']
            planfile=ROOT/prepared['plan'];assert sha(planfile)==prepared['planSha256']
            plan=json.loads(planfile.read_text(encoding='utf-8'));source=ROOT/plan['source'];assert sha(source)==plan['sourceSha256']
            count=plan['frames'];start=plan['globalStartFrame'];folder=LOCAL/sid;folder.mkdir(parents=True,exist_ok=True)
            clean=folder/f'scene{sid}.annotated.clean.mp4';captioned=folder/f'scene{sid}.annotated.captioned.mp4'
            assert not clean.exists() and not captioned.exists()
            job={'scene':sid,'frames':count,'globalStartFrame':start,'plan':rel(planfile),'planSha256':sha(planfile),'sourceSha256':sha(source),'status':'rendering','writtenFrames':0}
            state['jobs'].append(job);state['currentScene']=sid;save()
            dec=[FF,'-hide_banner','-nostdin','-v','error','-threads','1','-filter_threads','1','-i',str(source),'-f','rawvideo','-pix_fmt','rgb24','pipe:1']
            enc=[FF,'-hide_banner','-nostdin','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','60','-i','pipe:0','-frames:v',str(count),'-an','-c:v','libx264','-threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(clean)]
            job.update(decodeCommand=dec,encodeCommand=enc);save()
            with (folder/'source-decode.log').open('wb') as dl,(folder/'annotation-encode.log').open('wb') as el:
                decoder=subprocess.Popen(dec,stdout=subprocess.PIPE,stderr=dl,cwd=ROOT)
                encoder=subprocess.Popen(enc,stdin=subprocess.PIPE,stderr=el,cwd=ROOT)
                for frame in range(count):
                    raw=decoder.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3,(sid,frame,len(raw))
                    encoder.stdin.write(module.annotate(Image.frombytes('RGB',(1920,1080),raw),frame,plan).tobytes())
                    if frame%600==0:
                        job['writtenFrames']=frame+1;save();print(json.dumps({'scene':sid,'writtenFrames':frame+1}),flush=True)
                assert decoder.stdout.read(1)==b''
                encoder.stdin.close();decoder.stdout.close();dx=decoder.wait();ex=encoder.wait();assert dx==ex==0,(dx,ex)
            job.update(writtenFrames=count,sourceDecodeExitCode=dx,annotationEncodeExitCode=ex,status='fixed-caption-review-pilot');save()
            baseline=ROOT/'shared/output/motion-canvas/game-math-polar-3d.mp4'
            vf=f'setpts=PTS+{start}/60/TB,ass=projects/game-math-polar-3d/script/final.ko.ass,setpts=PTS-STARTPTS'
            ac=f'[1:a]atrim=start={start/60:.12f}:end={(start+count)/60:.12f},asetpts=PTS-STARTPTS[a]'
            cmd=[FF,'-hide_banner','-nostdin','-v','error','-threads','2','-filter_threads','1','-filter_complex_threads','1','-i',str(clean),'-i',str(baseline),'-filter_complex',ac,'-map','0:v','-map','[a]','-vf',vf,'-frames:v',str(count),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-c:a','aac','-b:a','192k','-movflags','+faststart',str(captioned)]
            job['captionEncodeExitCode']=run(cmd,folder/'caption-encode.log')
            job['pilotAudioNote']='Decoded original final AAC interval, re-encoded for review only; not the final whole AAC.'
            job['status']='technical-check-and-extraction';save()
            for p in [clean,captioned]:
                code=run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(p),'-f','null','-'],folder/(p.stem+'-decode.log'))
                raw=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=pts','-of','json',str(p)]))
                assert [int(f['pts']) for f in raw['frames']]==list(range(0,count*1500,1500))
                job[p.stem]={'path':rel(p),'sha256':sha(p),'wholeDecodeExitCode':code,'frames':count,'allPts1500Verified':True};save()
            points=set(range(0,count,30))|{0,count-1}
            for c in plan['cuts']:
                f=c['sceneStartFrame'];points.update(v for v in [f-1,f,f+1] if 0<=v<count)
            for s in plan['stagesSeconds']:
                f=round(s*60);points.update(v for v in [f-1,f,f+1] if 0<=v<count)
            for line in (ROOT/'projects/game-math-polar-3d/script/final.ko.ass').read_text(encoding='utf-8').splitlines():
                if not line.startswith('Dialogue:'):continue
                fields=line.split(',',9)
                for stamp in fields[1:3]:
                    f=round(secs(stamp)*60)-start
                    if 0<=f<count:points.update(v for v in [f-1,f,f+1] if 0<=v<count)
            points=sorted(points);vf='select='+ '+'.join(f'eq(pts\\,{f*1500})' for f in points)
            job['extractionExitCode']=run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-filter_threads','1','-i',str(captioned),'-vf',vf,'-frames:v',str(len(points)),'-fps_mode','passthrough',str(folder/'sample-%04d.png')],folder/'extraction.log')
            files=sorted(folder.glob('sample-*.png'));assert len(files)==len(points)
            rows=[{'frame':f,'pts':f*1500,'path':rel(p),'sha256':sha(p)} for f,p in zip(points,files)];boards=[]
            font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
            for n in range(0,len(rows),6):
                board=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(board)
                for j,r in enumerate(rows[n:n+6]):
                    x=j%3*640;y=j//3*390
                    with Image.open(ROOT/r['path']) as im:board.paste(im.resize((640,360)),(x,y+30))
                    d.text((x+8,y+5),f"scene{sid} f{r['frame']} / {r['frame']/60:.3f}s",fill='white',font=font)
                p=folder/f'board-{n//6+1:03d}.png';board.save(p);boards.append({'path':rel(p),'sha256':sha(p)})
            job.update(status='completed',samples=rows,boards=boards,finishedAt=datetime.now(timezone.utc).isoformat(),sampledPixelsApproved=False,movingReviewApproved=False);save()
            print(json.dumps({'scene':sid,'frames':count,'samples':len(rows),'boards':len(boards),'exitCode':0}),flush=True)
        assert all(sha(ROOT/r['path'])==r['sha256'] for r in snapshot['files'])
        state.update(status='completed',exitCode=0,finishedAt=datetime.now(timezone.utc).isoformat(),protectedBaselineUnchanged=True);save()
        print(json.dumps({'exitCode':0,'scenes':6,'wholeVideoApproved':False}),flush=True)
    except Exception as e:
        state.update(status='failed',exitCode=1,exception=str(e));save();raise
if __name__=='__main__':main()

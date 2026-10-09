"""Build only new selected normal-speed inputs, serial CPU2, with real identities."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess, psutil

BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
    t=p.with_name(p.name+'.recording');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def identity(p):return dict(pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd())
def queue(state):
    cp=BASE/'latest-checkpoint.json';current=read(cp)
    current.update(stage=state['status'],updatedAt=now(),revisionNativeInputs=rel(EP),
        activeRevisionJob=dict(processIdentity=state['processIdentity'],child=state.get('activeChild'),
            completed=state['completed'],total=state['total'],sessionId=state.get('sessionId'),
            workerExpectedRunning=state['exitCode'] is None),
        finalTimingApproved=False,finalMixedAsrApproved=False,pairRendered=False,allFinalPixels=False,qa=False,collected=False)
    save(cp,current)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
    for _ in range(8):
        raw=qp.read_text('utf-8-sig');q=json.loads(raw)
        item=next(x for x in q['items'] if x['slug']=='presenting-game-scores')
        item.update(stage=state['status'],currentExecution=dict(state=rel(EP),processIdentity=state['processIdentity'],
            child=state.get('activeChild'),completed=state['completed'],total=state['total'],sessionId=state.get('sessionId')),
            nextAction='Finish only new native inputs; measured black scenes and all current cue/motion/UI pixels pending. Final mix/pair/QA/private remain false.')
        q['updatedAt']=now();q['lastProgressAt']=now()
        if qp.read_text('utf-8-sig')==raw:save(qp,q);return
    raise RuntimeError('Concurrent queue modification; preserve foreign work.')

ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
rp=ROOT/args.resource;r=read(rp)
assert r['ownHeavyJobs']==0
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<180
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
pp=BASE/'revision-balatro60-v2/measured-editorial-candidate-v3.json';plan=read(pp)
vp=ROOT/plan['voiceSelection'];v=read(vp)
assert sha(vp)==plan['voiceSelectionSha256'] and v['currentCompleteVoiceApproved']
assert sha(ROOT/plan['bank'])==plan['bankSha256'] and plan['mathRatioVerified']
rows=[s for s in plan['segments'] if s['role']=='actual-existing-game']
assert len(rows)==18 and sum(s['frames'] for s in rows)==plan['actualFrames']
assert plan['measuredEditorialApproved'] and plan['currentCompleteVoiceApproved']
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
OUT=ROOT/'shared/output/presenting-game-scores/revision-balatro60-v2/measured-native-inputs-v1'
EP=BASE/'revision-balatro60-v2/measured-native-inputs-execution-v1.json'
assert not OUT.exists() and not EP.exists(), 'Preserve completed/partial inputs; read execution before explicit recovery.'
for s in rows:
    assert sha(Path(s['sourcePath']))==s['sourceSha256']
    assert sha(Path(s['nativePtsEvidence']))==s['nativePtsEvidenceSha256']
OUT.mkdir(parents=True)
credit_lines=['Footage:','Squeaky','Whale','Gameplay','Archive']
credit_paths=[]
for i,line in enumerate(credit_lines):
    path=OUT/f'credit-line-{i:02}.txt';path.write_text(line,'utf-8');credit_paths.append(rel(path))
state=dict(schemaVersion=7,slug='presenting-game-scores',startedAt=now(),processIdentity=identity(psutil.Process()),
    pid=os.getpid(),createTime=psutil.Process().create_time(),sessionId=None,cpuThreads=2,gpuJobs=0,
    status='building-Balatro60-revision-native-inputs-v1',completed=0,total=len(rows),exitCode=None,
    resource=args.resource,resourceSha256=sha(rp),plan=rel(pp),planSha256=sha(pp),
    recoveryFrom='Preserved baseline v8 files; new approved source/timing only',results=[],activeChild=None,allFinalPixels=False,finalTimingApproved=False,finalMixedAsrApproved=False,
    preparedWorkerVersion='revision-native-v1',newRasterGitAdditions=0,sourceAudio=False,loop=False,slowdown=False,sourceAcquisitionRepeated=False)
save(EP,state);queue(state)
try:
    old=read(BASE/'measured-native-inputs-execution-v8.json');assert old['exitCode']==0
    for s in rows:
        reuse=next((x for x in old['results'] if x['sourceSha256']==s['sourceSha256'] and x['sourceStartFrame']==s['sourceStartFrame'] and x['sourceEndFrameExclusive']==s['sourceEndFrameExclusive'] and x['frames']==s['frames'] and x['framing']==s['framing']),None)
        if reuse:
            assert sha(ROOT/reuse['path'])==reuse['sha256'] and reuse['allPtsVerified'] and reuse['wholeDecodeExitCode']==0
            result={**reuse,'id':s['id'],'reusedUnchangedVerifiedBaselineInput':True,'baselineExecution':'projects/presenting-game-scores/production/measured-native-inputs-execution-v8.json','encodeRepeated':False,'decodeRepeated':False,'finalCuePixelsReviewed':False}
            state['results'].append(result);state['completed']+=1;save(EP,state);queue(state)
            print('Reused unchanged verified input '+s['id'],flush=True);continue
        dest=OUT/(s['id']+'.mp4');log=OUT/(s['id']+'.encode.log')
        from fractions import Fraction
        endpts=int(Fraction(s['sourceEndFrameExclusive'],1)/Fraction(s['nativeFps'])/Fraction(s['nativeTimebase']))
        trim=f"trim=start_pts={s['nativeStartPts']}:end_pts={endpts},setpts=PTS-{s['nativeStartPts']}"
        shift=120 if s['source'] in ['classic','modern'] else 48 if s['id']=='balatro-countup' else 0
        if s['source']=='balatro-longplay':
            filters=f'[0:v]{trim},split=2[b][f];[b]scale=1920:1080,gblur=sigma=28:steps=2,eq=brightness=-0.3[bg];[f]scale=1600:900[fg];[bg][fg]overlay=160:0:shortest=1[fit];[fit]drawbox=x=8:y=308:w=144:h=170:color=black@0.92:t=fill[creditbg];'
            prior='creditbg'
            for i,line in enumerate(credit_lines):
                label='credit'+str(i);filters+=f"[{prior}]drawtext=fontfile='C\\:/Windows/Fonts/segoeuib.ttf':textfile='{credit_paths[i]}':fontcolor=white:fontsize=22:x=12:y={320+i*29}[{label}];";prior=label
            filters+=f'[{prior}]null[framed];'
        elif shift:
            filters=f'[0:v]{trim},split=2[b][f];[b]gblur=sigma=24:steps=2[bg];[f]crop=1920:{1080-shift}:0:{shift}[fg];[bg][fg]overlay=0:0:shortest=1[framed];'
        else:
            filters=f'[0:v]{trim}[framed];'
        filters+=f'[framed]tpad=stop_mode=clone:stop=1,fps=60:start_time=0:round=near,trim=end_frame={s["frames"]},settb=1/90000,setpts=N*1500,setsar=1,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v]'
        cmd=[str(FF),'-nostdin','-hide_banner','-loglevel','warning','-threads','2','-reinit_filter','0','-i',s['sourcePath'],
            '-filter_complex_threads','1','-filter_complex',filters,'-map','[v]','-an',
            '-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-frames:v',str(s['frames']),
            '-fps_mode','cfr','-r','60','-video_track_timescale','90000','-movflags','+faststart',str(dest)]
        with log.open('wb') as handle:
            child=subprocess.Popen(cmd,stdout=handle,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            state['activeChild']=identity(psutil.Process(child.pid));state['activeChild']['log']=rel(log)
            state['activeSegment']=s['id'];save(EP,state);queue(state)
            code=child.wait()
        assert code==0,log.read_text('utf-8',errors='replace')[-3000:]
        probe=subprocess.run([str(FP),'-v','error','-threads','2','-select_streams','v:0','-show_frames',
            '-show_entries','frame=best_effort_timestamp,width,height:stream=time_base,avg_frame_rate,nb_frames,codec_name',
            '-of','json',str(dest)],capture_output=True,text=True,check=True)
        info=json.loads(probe.stdout);frames=info['frames'];stream=info['streams'][0]
        assert len(frames)==s['frames'] and stream['time_base']=='1/90000'
        assert all(f['best_effort_timestamp']==i*1500 and (f['width'],f['height'])==(1920,1080) for i,f in enumerate(frames))
        probe_path=OUT/(s['id']+'.probe.json');save(probe_path,info)
        decode_cmd=[str(FF),'-nostdin','-v','error','-threads','2','-i',str(dest),'-map','0:v:0','-an','-f','null','-']
        decoded=subprocess.run(decode_cmd,capture_output=True,text=True)
        assert decoded.returncode==0,decoded.stderr
        result=dict(id=s['id'],path=rel(dest),sha256=sha(dest),frames=s['frames'],fps='60/1',timebase='1/90000',ptsStep=1500,
            allPtsVerified=True,wholeDecodeExitCode=decoded.returncode,encodeExitCode=code,probe=rel(probe_path),probeSha256=sha(probe_path),
            sourcePath=s['sourcePath'],sourceSha256=s['sourceSha256'],sourceStartFrame=s['sourceStartFrame'],
            sourceEndFrameExclusive=s['sourceEndFrameExclusive'],framing=s['framing'],foregroundScale=1,
            normalSpeed=True,loop=False,slowdown=False,sourceAudio=False,command=cmd,
            finalCuePixelsReviewed=False,activeChildAtExecution=state['activeChild'])
        state['results'].append(result);state['completed']+=1;state['activeChild']=None
        save(EP,state);queue(state)
        print(json.dumps(dict(completed=state['completed'],total=state['total'],id=s['id'],frames=s['frames']),ensure_ascii=False),flush=True)
    state.update(status='measured-native-inputs-complete-current-cue-review-pending',exitCode=0,finishedAt=now(),activeChild=None)
    save(EP,state);queue(state)
except BaseException as error:
    state.update(status='measured-native-inputs-failed-preserve-completed-files',exitCode=1,error=repr(error),finishedAt=now())
    save(EP,state);queue(state);raise

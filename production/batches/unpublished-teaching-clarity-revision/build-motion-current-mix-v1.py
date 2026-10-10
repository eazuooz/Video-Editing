"""Serial CPU2 mix of retained12 and additive2 approved PCM. No synthesis."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, math, os, re, subprocess, traceback, wave
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']: os.environ[k]='2'
import psutil
ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
OUT=ROOT/'shared/output/unpublished-teaching-clarity-revision/motion/current-mix-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,o):
    t=p.with_name(p.name+'.writing');t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def wav(p,data,rate,channels):
    with wave.open(str(p),'wb') as w:w.setnchannels(channels);w.setsampwidth(2);w.setframerate(rate);w.writeframes(data)
def params(p):
    with wave.open(str(p),'rb') as w:return dict(samples=w.getnframes(),rate=w.getframerate(),channels=w.getnchannels(),bytesPerSample=w.getsampwidth())
def run(args,name):
    with (OUT/(name+'.log')).open('wb') as log:
        x=subprocess.run([FF,'-hide_banner','-nostdin','-threads','2','-filter_threads','2','-filter_complex_threads','2',*args],stdout=log,stderr=log,cwd=ROOT).returncode
    assert x==0,name
    state['subprocesses'].append(dict(name=name,exitCode=x,log=rel(OUT/(name+'.log'))));checkpoint()
def scan(p,name,I=-16,TP=-2):
    run(['-i',str(p),'-af',f'loudnorm=I={I}:TP={TP}:LRA=11:print_format=json','-f','null','-'],name)
    txt=(OUT/(name+'.log')).read_text('utf-8',errors='replace')
    return json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}',txt)[0])
def checkpoint():
    session=R/'current-mix-execution-v1.session.json'
    if session.exists():
        v=read(session);assert v['pid']==me.pid and abs(v['createTime']-me.create_time())<.01;state['sessionId']=v['sessionId']
    state['updatedAt']=now();save(R/'current-mix-execution-v1.json',state)
    cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],ownedJob=dict(pid=me.pid,
      createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=state['sessionId'],state=rel(R/'current-mix-execution-v1.json'),
      cpuThreads=2,gpuJobs=0,actualExitCode=state['actualExitCode']),retainedEncodedSampleReview=rel(R/'retained-encoded-sample-direct-review-v1.json'),
      retainedAnnotationPlayback=rel(R/'retained-annotation-playback-observation-v1.json'),
      currentMixedAudioApproved=False,next='Verify actual mix exit, read current14 whole and66 complete paragraph mixed ASR, then retime KOEN captions/chapters and review final narrated pair pixels.')
    save(R/'latest-checkpoint.json',cp)
    qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)
    q['execution'].update(currentSlug='motion-sickness-games',stage=cp['stage'],ownedJob=cp['ownedJob'],next=cp['next'])
    next(x for x in q['items'] if x['slug']=='motion-sickness-games').update(status=cp['stage'],currentExecution=cp['ownedJob'])
    q['updatedAt']=now();assert qp.read_text('utf-8-sig')==raw;save(qp,q)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
    resource=read(ROOT/args.resource)
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
    assert resource['ownHeavyCpuJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
    subprocess.run([NODE,'scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],cwd=ROOT,check=True)
    protected=read(R/'narration-tts-waiting-v1.json')['protectedInputs']
    for row in protected:assert sha(ROOT/row['path'])==row['sha256']
    tts=read(R/'narration-tts-execution-v1.json');resume=read(R/'research-handoff-verification-v1.json')
    assert tts['exitCode']==0 and tts['actualExitObserved'] and resume['restorationVerified'] and resume['ttsLeaseToken']==tts['leaseToken']
    assert read(R/'retained-encoded-sample-direct-review-v1.json')['encodedSelectedSampleReviewPassed']
    assert read(R/'retained-annotation-playback-observation-v1.json')['normalSpeedStartsAndEndsObserved']
    plan=read(R/'measured-additive-plan-v1.json');assert len(plan['scenes'])==14 and len(plan['paragraphs'])==66
    mf=read(ROOT/'projects/motion-sickness-games/project.json')
    assert mf['audio']['backgroundMusic']['approvalStatus']=='approved'
    music=ROOT/mf['audio']['backgroundMusic']['file'];assert sha(music)=='36a0c40b73e7dc656470c242cce0047bd987abc595f28b013265d947a10d98ef'
    assert not OUT.exists() and not (R/'current-mix-execution-v1.json').exists()
    OUT.mkdir(parents=True);me=psutil.Process()
    if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
    state=dict(schemaVersion=1,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,
      startedAt=now(),status='assembling-current14-PCM-and-Nimbus',actualExitCode=None,resource=resource,
      cpuThreads=2,gpuJobs=0,researchManipulations=0,subprocesses=[],placements=[],protectedInputs=protected,
      plan=rel(R/'measured-additive-plan-v1.json'),planSha256=sha(R/'measured-additive-plan-v1.json'),
      currentMixedAudioApproved=False,humanListeningApproved=False,humanPronunciationApproved=False,
      sourceAudioUsed=False,originalPcmRegenerated=False,newGitMedia=0)
    checkpoint()
    try:
        fullsamples=plan['totalFrames']*400;bodysamples=plan['bodyFrames']*400
        raw=bytearray(fullsamples*2)
        for s in plan['scenes']:
            p=ROOT/s['voice'];assert sha(p)==s['audioSha256']
            with wave.open(str(p),'rb') as w:
                assert w.getframerate()==24000 and w.getnchannels()==1 and w.getsampwidth()==2
                n=w.getnframes();pcm=w.readframes(n);assert n<=s['frames']*400
            a=s['startFrame']*400;b=a+n;raw[a*2:b*2]=pcm
            assert bytes(raw[a*2:b*2])==pcm
            state['placements'].append(dict(scene=s['id'],path=s['voice'],sha256=s['audioSha256'],startSample=a,endSample=b,
              pcmSha256=hashlib.sha256(pcm).hexdigest(),exactOriginalPcmBytesMatched=True))
        assert not any(raw[:120*400*2]) and not any(raw[(120+plan['bodyFrames'])*400*2:])
        rawp=OUT/'current14.raw-placement.wav';wav(rawp,raw,24000,1)
        body=bytes(raw[120*400*2:(120+plan['bodyFrames'])*400*2]);assert len(body)==bodysamples*2
        bodyp=OUT/'current14.body.raw.wav';wav(bodyp,body,24000,1)
        measured=scan(bodyp,'raw-body-loudness')
        normalbody=OUT/'voice-normalized-body.wav'
        filt=f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:offset={measured['target_offset']}:linear=true,aresample=48000,aformat=channel_layouts=stereo"
        run(['-i',str(bodyp),'-af',filt,'-c:a','pcm_s16le',str(normalbody)],'normalize-body')
        assert params(normalbody)==dict(samples=bodysamples*2,rate=48000,channels=2,bytesPerSample=2)
        with wave.open(str(normalbody),'rb') as w:norm=w.readframes(w.getnframes())
        padded=b'\0'*96000*4+norm+b'\0'*480000*4
        assert len(padded)==fullsamples*2*4
        voicepass=OUT/'voice-loudnorm-pass.wav';wav(voicepass,padded,48000,2)
        voice_measure=scan(voicepass,'voice-pass-loudness')
        gain=min(-16-float(voice_measure['input_i']),-2-float(voice_measure['input_tp']))
        normal=OUT/'voice-normalized.wav';run(['-i',str(voicepass),'-af',f'volume={gain}dB','-c:a','pcm_s16le',str(normal)],'voice-constant-gain')
        assert params(normal)==dict(samples=fullsamples*2,rate=48000,channels=2,bytesPerSample=2)
        duration=json.loads(subprocess.check_output([FP,'-v','error','-show_format','-of','json',str(music)]))
        md=float(duration['format']['duration']);D=plan['seconds']
        if md<D:
            n=math.ceil((D-1)/(md-1));inputs=sum([['-i',str(music)] for i in range(n)],[])
            chain=';'.join(f"{'[0:a]' if i==1 else '[b'+str(i-1)+']'}[{i}:a]acrossfade=d=1:c1=tri:c2=tri[b{i}]" for i in range(1,n))
            continuous=OUT/'nimbus-continuous.wav';run([*inputs,'-filter_complex',chain,'-map',f'[b{n-1}]','-c:a','pcm_s16le',str(continuous)],'music-crossfade')
        else:continuous=music;n=1
        mixfilter=f'[0:a]asplit[n][d];[1:a]aresample=48000,atrim=end_sample={fullsamples*2},asetpts=PTS-STARTPTS,loudnorm=I=-28:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.45,afade=t=out:st={D-.45}:d=0.45[b];[b][d]sidechaincompress=threshold=.08:ratio=2.2:attack=15:release=280[bg];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=.80:level=false:latency=true,atrim=end_sample={fullsamples*2}[mix]'
        (OUT/'mix-filter.txt').write_text(mixfilter,'utf-8')
        mix=OUT/'current14.final-mix.wav';run(['-i',str(normal),'-i',str(continuous),'-filter_complex_script',str(OUT/'mix-filter.txt'),'-map','[mix]','-ar','48000','-ac','2','-c:a','pcm_s16le',str(mix)],'mix')
        assert params(mix)==dict(samples=fullsamples*2,rate=48000,channels=2,bytesPerSample=2)
        final=scan(mix,'final-mix-loudness',-16,-1.5)
        assert abs(float(final['input_i'])+16)<=.6 and float(final['input_tp'])<=-1.45
        aac=OUT/'current14.final-mix.m4a';run(['-i',str(mix),'-c:a','aac','-b:a','192k',str(aac)],'encode-AAC')
        decoded=OUT/'current14.AAC-decoded.wav';run(['-i',str(aac),'-af',f'atrim=end_sample={fullsamples*2}','-ar','48000','-ac','2','-c:a','pcm_s16le',str(decoded)],'decode-current-AAC')
        assert params(decoded)==params(mix)
        aacmeasured=scan(decoded,'AAC-decoded-loudness',-16,-1.5)
        assert abs(float(aacmeasured['input_i'])+16)<=.6 and float(aacmeasured['input_tp'])<=-1.45
        for row in protected:assert sha(ROOT/row['path'])==row['sha256']
        files=[rawp,bodyp,normal,continuous,mix,aac,decoded]
        state.update(status='current14-mix-created-awaiting-actual-exit-and-mixed-ASR',actualExitCode=0,finishedAt=now(),
          all26ProtectedInputsUnchanged=True,all14RawPcmPlacementsExact=True,rawNarration=measured,voicePass=voice_measure,
          constantVoiceGainDb=gain,finalWavMeasurement=final,aacDecodedMeasurement=aacmeasured,
          totalFrames=plan['totalFrames'],seconds=D,music=dict(path=rel(music),sha256=sha(music),copies=n,crossfadeSeconds=1),
          files=[dict(path=rel(p),sha256=sha(p),size=p.stat().st_size) for p in files],
          mixWav=rel(mix),mixWavSha256=sha(mix),mixAac=rel(aac),mixAacSha256=sha(aac),decodedAac=rel(decoded),decodedAacSha256=sha(decoded))
        checkpoint();print(json.dumps(dict(totalFrames=plan['totalFrames'],seconds=D,finalMeasurement=final,decodedAac=aacmeasured,raw14PcmExact=True),ensure_ascii=False),flush=True)
    except BaseException:
        state.update(status='failed-current-mix-preserve-local-files',actualExitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise

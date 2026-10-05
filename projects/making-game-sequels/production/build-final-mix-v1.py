"""Preserve all placed PCM and mix the approved continuous Nimbus, without TTS."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, re, subprocess, time, traceback
import numpy as np
import soundfile as sf

ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent; FINAL=BASE/'final-v1'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'); FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
STATE=FINAL/'mix-execution.json'; assert not STATE.exists()
plan=read(FINAL/'plan.json'); manifest=read(BASE.parent/'project.json')
assert plan['finalTimingApproved'] and plan['bodyRatioApproved'] and plan['allInputSegmentCaptionPixelsReviewed']
assert plan['finalFrames']==35583 and plan['body60_40ErrorFrames']<=1
state=dict(schemaVersion=1,pid=os.getpid(),sessionId=None,startedAt=now(),status='preparing-lossless-timeline',
    cpuThreads=2,gpuJobs=0,newTts=0,commands=[],activeTasks=[],finalMixAsrApproved=False,
    humanWholeListening='pending',sourceAudioStreams=0)
def write(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing')
    for n in range(30):
        try:t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p);return
        except OSError:
            if n==29:raise
            time.sleep(.1)
def checkpoint():
    session=FINAL/'mix-session.json'
    if session.exists() and read(session).get('pid')==os.getpid():state['sessionId']=read(session)['sessionId']
    state['observedAt']=now();write(STATE,state)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='making-game-sequels')
    i.update(stage='current13-guided60-final-Nimbus-mix-preparing',updatedAt=state['observedAt'],
        nextAction='Complete and measure current continuousNimbus mix; directly compare final mixed13chapters and independent joins. Frame85 native cuts, assemble exact35583PTS frames, inspect all final cues/cuts, QA/collect/private/Git.')
    alive='endedAt' not in state
    i['execution'].update(status=state['status'],phase=i['stage'],observedAt=state['observedAt'],
        pid=os.getpid(),sessionId=state['sessionId'],commandLine='build-final-mix-v1.py CPU2/GPU0',
        alive=alive,activeTasks=state['activeTasks'],state=rel(STATE),
        cpuProductionJobs=int(alive),primaryCpuProductionJobs=int(alive),gpuSynthesisJobs=0,renderJobs=0,uploads=0)
    q['updatedAt']=i['updatedAt'];write(qp,q)
    for p in [BASE/'latest-checkpoint.json',ROOT/'production/batches/sakurai-planning-game-design/proof-making-game-sequels/latest-checkpoint.json']:
        d=read(p)
        for k in ['stage','updatedAt','nextAction','execution']:d[k]=i[k]
        d.update(finalMixBuilt=(FINAL/'mix-settings.json').exists(),finalMixAsrApproved=False,rendered=False,qaApproved=False,collected=False,privateUploaded=False)
        write(p,d)
def run(exe,args,kind):
    log=FINAL/f'mix-{len(state["commands"])+1:02d}.log'
    with log.open('w',encoding='utf-8') as fh:
        command=[str(exe),*map(str,args)]
        p=subprocess.Popen(command,cwd=ROOT,stdout=fh,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        state['status']=kind;state['activeTasks']=[dict(kind=kind,pid=p.pid,command=command,log=rel(log))];checkpoint();code=p.wait()
    state['commands'].append(dict(command=command,pid=p.pid,exitCode=code,log=rel(log)));state['activeTasks']=[];checkpoint()
    if code:raise RuntimeError(f'{kind} exit{code}: {log}')
    return log.read_text(encoding='utf-8')
def ff(args,kind):return run(FF,['-hide_banner','-nostdin','-threads','2',*args],kind)
def scan(p,I=-16,TP=-2):
    text=ff(['-i',p,'-af',f'loudnorm=I={I}:TP={TP}:LRA=11:print_format=json','-f','null','-'],'CPU-loudness-scan')
    return json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}',text).group())
try:
    checkpoint();D=plan['finalFrames']/60
    timeline=np.zeros(plan['finalFrames']*400,dtype='int16');placements=[]
    for s in plan['scenes']:
        path=ROOT/s['placedVoice'];assert sha(path)==s['placedVoiceSha256']
        x,rate=sf.read(path,dtype='int16');assert rate==24000 and len(x)==s['frames']*400
        a=s['startFrame']*400;timeline[a:a+len(x)]=x
        placements.append(dict(scene=s['id'],startFrame=s['startFrame'],frames=s['frames'],
            placedPath=s['placedVoice'],placedSha256=s['placedVoiceSha256'],allSamplesIdentical=True))
    assert np.count_nonzero(timeline[:48000])==0 and np.count_nonzero(timeline[-240000:])==0
    voice=FINAL/'narration-timed.wav';sf.write(voice,timeline,24000,subtype='PCM_16')
    back,rate=sf.read(voice,dtype='int16');assert rate==24000 and np.array_equal(timeline,back)
    write(FINAL/'pcm-timeline-preservation.json',dict(createdAt=now(),planSha256=sha(FINAL/'plan.json'),
        voicePath=rel(voice),voiceSha256=sha(voice),samples=len(back),seconds=D,sampleRate=24000,
        scenes=placements,all13PlacedPcmSamplesIdentical=True,currentComponentSeconds=554.584,
        introAndMembershipNarrationSilent=True,newTts=0,finalMixBuilt=False))
    raw=scan(voice);normal=FINAL/'voice-normalized-pass.wav'
    ff(['-i',voice,'-af',f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={raw['input_i']}:measured_TP={raw['input_tp']}:measured_LRA={raw['input_lra']}:measured_thresh={raw['input_thresh']}:offset={raw['target_offset']}:linear=true,aresample=48000,aformat=channel_layouts=stereo",'-c:a','pcm_s16le',normal],'CPU-two-pass-voice-normalization')
    x,rate=sf.read(normal,dtype='int16',always_2d=True);assert rate==48000 and len(x)==plan['finalFrames']*800
    initial=int(np.count_nonzero(x[:96000]));x[:96000]=0;x[-480000:]=0
    repaired=FINAL/'voice-normalized-body-only.wav';sf.write(repaired,x,rate,subtype='PCM_16')
    write(FINAL/'normalization-outside-body-silence.json',dict(createdAt=now(),originalPassSha256=sha(normal),
        bodyOnlySha256=sha(repaired),brandingOriginalNonzeroSamples=initial,
        changedOnlyBrandingAndMembership=True,allBodyNormalizedSamplesRetained=True,currentSourcePcmUnchanged=True))
    measured=scan(repaired);gain=min(-16-float(measured['input_i']),-2-float(measured['input_tp']))
    normalized=FINAL/'voice-normalized.wav'
    ff(['-i',repaired,'-af',f'volume={gain}dB','-c:a','pcm_s16le',normalized],'CPU-voice-constant-level')
    music=ROOT/manifest['audio']['backgroundMusic']['file'];approval=manifest['audio']['backgroundMusic']
    assert approval['approvalStatus']=='approved' and sha(music)==approval['restoration']['sha256']
    originalMusicSha=sha(music)
    pr=json.loads(run(FP,['-v','error','-show_format','-of','json',music],'CPU-Nimbus-probe'));md=float(pr['format']['duration'])
    n=int(np.ceil((D-1)/(md-1)))
    if n>1:
        chain=';'.join(f"{'[0:a]' if k==1 else '[b'+str(k-1)+']'}[{k}:a]acrossfade=d=1:c1=tri:c2=tri[b{k}]" for k in range(1,n))
        continuous=FINAL/'nimbus-continuous.wav'
        ff([*sum((['-i',music] for _ in range(n)),[]),'-filter_complex',chain,'-map',f'[b{n-1}]','-c:a','pcm_s16le',continuous],'CPU-continuous-approved-Nimbus')
        music=continuous
    bg=FINAL/'bgm-before-ducking.wav'
    ff(['-i',music,'-af',f'atrim=duration={D},asetpts=PTS-STARTPTS,loudnorm=I=-28:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=.45,afade=t=out:st={D-.45}:d=.45','-c:a','pcm_s16le',bg],'CPU-continuous-background-level')
    mix=FINAL/'final-mix.wav';aac=FINAL/'final-mix.m4a'
    filt='[0:a]asplit[n][d];[1:a][d]sidechaincompress=threshold=.08:ratio=2.2:attack=15:release=280[bg];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=.80:level=false:latency=true[mix]'
    ff(['-i',normalized,'-i',bg,'-filter_complex',filt,'-map','[mix]','-ar','48000','-ac','2','-c:a','pcm_s16le',mix],'CPU-final-Nimbus-ducked-mix')
    ff(['-i',mix,'-c:a','aac','-b:a','192k',aac],'CPU-current-final-AAC')
    final=scan(aac,-16,-1.5)
    assert abs(float(final['input_i'])+16)<=.6 and float(final['input_tp'])<=-1.5,final
    assert len(sf.read(mix,dtype='int16')[0])==plan['finalFrames']*800
    write(FINAL/'mix-settings.json',dict(createdAt=now(),durationSeconds=D,frames=35583,
        planSha256=sha(FINAL/'plan.json'),voiceSourceSha256=sha(voice),narration=raw,normalizedVoice=measured,
        constantVoiceGainDb=gain,finalAacMeasurement=final,wavSha256=sha(mix),aacSha256=sha(aac),bgmSha256=sha(bg),
        approvedNimbusReferenceSha256=originalMusicSha,continuousApprovedNimbus=True,
        sourceAudioStreams=0,newTts=0,originalNimbusFileVerified=False,currentFinalMixedWindowAsr='pending',
        humanWholeListening='pending',humanPronunciation='pending'))
    state.update(status='closed-final-Nimbus-mix-built-awaiting-full-ASR',endedAt=now(),exitCode=0,activeTasks=[]);checkpoint()
    print(json.dumps(dict(frames=35583,seconds=D,mixedLufs=final['input_i'],truePeak=final['input_tp'],newTts=0,finalAsrApproved=False)))
except BaseException:
    state.update(status='closed-final-mix-failed',endedAt=now(),exitCode=1,error=traceback.format_exc(),activeTasks=[]);checkpoint();raise

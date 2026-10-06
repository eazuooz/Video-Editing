"""One CPU worker; preserve all27PCM fragments and mix approved continuous Nimbus."""
from final_cpu_common import *
import argparse, numpy as np, re, pcm16_wav_io as sf, traceback
parser=argparse.ArgumentParser();parser.add_argument('--resource',required=True);a=parser.parse_args()
plan=read(FINAL/'plan.json');manifest=read(BASE.parent/'project.json')
assert plan['finalTimingApproved'] and plan['bodyRatioApproved'] and plan['allInputSegmentCaptionPixelsReviewed'] and plan['finalFrames']==23570
w=Worker('mix',a.resource,'Finish current Nimbus mix, then frame current85cuts/8white and directly review current mixed19chapters+independent contexts. Final pair/pixels/QA/collection/private/Git then PAUSE24; no next queued video.')
def scan(p,I=-16,TP=-2):
    t=w.ff(['-i',p,'-af',f'loudnorm=I={I}:TP={TP}:LRA=11:print_format=json','-f','null','-'],'CPU-loudness-scan')
    return json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}',t).group())
try:
    w.checkpoint();D=plan['finalSeconds'];timeline=np.zeros(23570*400,dtype='int16');used=np.zeros(len(timeline),dtype=bool);placements=[]
    for p in plan['pieces']:
        src=ROOT/p['audioPath'];assert sha(src)==p['audioSha256']
        x,rate=sf.read(src,dtype='int16');assert rate==24000 and x.ndim==1 and len(x)==p['samples']
        start=p['voiceStartFrame']*400;end=start+len(x);assert end<=p['endFrame']*400 and not used[start:end].any()
        timeline[start:end]=x;used[start:end]=True
        assert np.array_equal(timeline[start:end],x)
        placements.append(dict(piece=p['id'],scene=p['logicalScene'],startSample=start,endSample=end,samples=len(x),path=p['audioPath'],sha256=p['audioSha256'],allSamplesIdentical=True))
    assert used.sum()==plan['allCurrentPcmSamples']==8968322
    assert not np.count_nonzero(timeline[:48000]) and not np.count_nonzero(timeline[-240000:])
    voice=FINAL/'narration-timed.wav';assert not voice.exists();sf.write(voice,timeline,24000,subtype='PCM_16')
    back,rate=sf.read(voice,dtype='int16');assert np.array_equal(timeline,back)
    write(FINAL/'pcm-timeline-preservation.json',dict(createdAt=now(),planSha256=sha(FINAL/'plan.json'),voicePath=rel(voice),voiceSha256=sha(voice),samples=len(back),sampleRate=24000,seconds=D,placements=placements,all27CurrentPcmSamplesIdentical=True,originalPcmSeconds=296.72,currentGuidePcmSeconds=76.96008333333333,allCurrentPcmSeconds=373.68008333333336,discardedSamples=0,repeatedSamples=0,introAndMembershipNarrationSilent=True,newTts=0))
    raw=scan(voice);normal=FINAL/'voice-normalized-pass.wav'
    w.ff(['-i',voice,'-af',f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={raw['input_i']}:measured_TP={raw['input_tp']}:measured_LRA={raw['input_lra']}:measured_thresh={raw['input_thresh']}:offset={raw['target_offset']}:linear=true,aresample=48000,aformat=channel_layouts=stereo",'-c:a','pcm_s16le',normal],'CPU-two-pass-voice-normalization')
    x,rate=sf.read(normal,dtype='int16',always_2d=True);assert rate==48000 and len(x)==23570*800
    initial=int(np.count_nonzero(x[:96000]));x[:96000]=0;x[-480000:]=0
    repaired=FINAL/'voice-normalized-body-only.wav';sf.write(repaired,x,rate,subtype='PCM_16')
    write(FINAL/'normalization-outside-body-silence.json',dict(createdAt=now(),originalPassSha256=sha(normal),bodyOnlySha256=sha(repaired),brandingOriginalNonzeroSamples=initial,changedOnlyBrandingAndMembership=True,allBodyNormalizedSamplesRetained=True,currentSourcePcmUnchanged=True))
    measured=scan(repaired);gain=min(-16-float(measured['input_i']),-2-float(measured['input_tp']));normalized=FINAL/'voice-normalized.wav'
    w.ff(['-i',repaired,'-af',f'volume={gain}dB','-c:a','pcm_s16le',normalized],'CPU-voice-constant-level')
    approval=manifest['audio']['backgroundMusic'];music=ROOT/approval['file'];assert approval['approvalStatus']=='approved' and sha(music)==approval['restoration']['sha256'];musicSha=sha(music)
    md=float(json.loads(w.run(FP,['-v','error','-show_format','-of','json',music],'CPU-Nimbus-probe'))['format']['duration']);n=int(np.ceil((D-1)/(md-1)))
    if n>1:
        chain=';'.join(f"{'[0:a]' if k==1 else '[b'+str(k-1)+']'}[{k}:a]acrossfade=d=1:c1=tri:c2=tri[b{k}]" for k in range(1,n))
        continuous=FINAL/'nimbus-continuous.wav';w.ff([*sum((['-i',music] for _ in range(n)),[]),'-filter_complex',chain,'-map',f'[b{n-1}]','-c:a','pcm_s16le',continuous],'CPU-continuous-approved-Nimbus');music=continuous
    bg=FINAL/'bgm-before-ducking.wav'
    w.ff(['-i',music,'-af',f'atrim=duration={D},asetpts=PTS-STARTPTS,loudnorm=I=-28:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.45,afade=t=out:st={D-.45}:d=0.45','-c:a','pcm_s16le',bg],'CPU-continuous-background-level')
    assert len(sf.read(bg,dtype='int16')[0])==23570*800
    mix=FINAL/'final-mix.wav';aac=FINAL/'final-mix.m4a'
    filt='[0:a]asplit[n][d];[1:a][d]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280[bg];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=0.80:level=false:latency=true[mix]'
    w.ff(['-i',normalized,'-i',bg,'-filter_complex',filt,'-map','[mix]','-ar','48000','-ac','2','-c:a','pcm_s16le',mix],'CPU-final-Nimbus-ducked-mix')
    w.ff(['-i',mix,'-c:a','aac','-b:a','192k',aac],'CPU-current-final-AAC');final=scan(aac,-16,-1.5)
    assert abs(float(final['input_i'])+16)<=.6 and float(final['input_tp'])<=-1.5,final
    assert len(sf.read(mix,dtype='int16')[0])==23570*800
    write(FINAL/'mix-settings.json',dict(createdAt=now(),durationSeconds=D,frames=23570,planSha256=sha(FINAL/'plan.json'),voiceSourceSha256=sha(voice),narration=raw,normalizedVoice=measured,constantVoiceGainDb=gain,finalAacMeasurement=final,wavSha256=sha(mix),aacSha256=sha(aac),bgmSha256=sha(bg),approvedNimbusReferenceSha256=musicSha,continuousApprovedNimbus=True,sourceAudioStreams=0,newTts=0,originalNimbusFileVerified=False,currentFinalMixedWindowAsr='pending',humanWholeListening='pending',humanPronunciation='pending'))
    w.close('closed-final-Nimbus-mix-built-awaiting-current-ASR');print(json.dumps(dict(frames=23570,seconds=D,mixedLufs=final['input_i'],truePeak=final['input_tp'],newTts=0,finalAsrApproved=False)),flush=True)
except BaseException:
    w.close('closed-final-mix-failed',1,traceback.format_exc());raise

"""CPU V6 synchronized game/voice mix, no separately added BGM.

Native game excerpts appear once at the frame-exact visual motion positions.
The ordinary voice-driven sidechain processes the GAME input only. Program
peak protection is one common fixed gain after the separately verified rare
narration-transient safety stage; no mix-driven voice limiter or fade.
"""
from pathlib import Path
import hashlib,importlib.util,json,math,subprocess
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v6_audio_prepare',H/'audio-prepare.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
R,P,O,A=a.R,a.P,a.O,a.A
def run(args,name):
 q=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-y',*map(str,args)],cwd=R,capture_output=True)
 (A/(name+'.log')).write_bytes(q.stderr);assert q.returncode==0,q.stderr.decode(errors='replace')[-2500:]
def scale(source,destination,gain):
 factor=10**(gain/20)
 with sf.SoundFile(source) as src,sf.SoundFile(destination,'w',samplerate=src.samplerate,channels=src.channels,subtype='FLOAT') as dst:
  for block in src.blocks(blocksize=480000,dtype='float32',always_2d=True):dst.write(block*factor)
def main():
 a.selected();plan=a.read(H/'timeline.json');voice=a.read(A/'audio-build.json')
 assert voice['inputs']['timelineSha256']==a.sha(H/'timeline.json')
 native_file=O/'footage/finite-clips/finite-assets.json';native=a.read(native_file);byid={x['id']:x for x in native['clips']}
 narration=R/voice['narrationFile'];assert any(x['sha256']==a.sha(narration) for x in voice['outputs'])
 inputs=dict(timelineSha256=a.sha(H/'timeline.json'),voicePreparationSha256=a.sha(A/'audio-build.json'),nativeGameReceiptSha256=a.sha(native_file),
  implementationSha256=a.sha(Path(__file__)),voicePreparationImplementationSha256=a.sha(H/'audio-prepare.py'))
 receipt=O/'audio-build.json'
 if receipt.exists():
  old=a.read(receipt)
  if old['inputs']==inputs and all((R/x['file']).exists() and a.sha(R/x['file'])==x['sha256'] for x in old['outputs']):
   print('Exact successful final mix reused; no WAV/AAC rewritten');return
  raise RuntimeError('Different existing V6 mix requires preservation before an authorized change')
 total=plan['totalFrames']*800;game=A/'game-normalized.wav';a.initialize(game,48000,2,total,'FLOAT');game_rows=[]
 with sf.SoundFile(game,'r+') as out:
  for cut in plan['cuts']:
   a.selected();source=byid[cut['id']];assert source['frames']==cut['frames'] and source['sourceSpeed']==cut['sourceSpeed']==1
   wav=R/source['audioFile'];assert a.sha(wav)==source['audioSha256'];raw,rate=sf.read(wav,dtype='float32',always_2d=True)
   assert rate==44100 and raw.shape==(source['audioSamples'],2)
   data=resample_poly(raw,160,147,axis=0);expected=cut['frames']*800;assert len(data)==expected
   measured=source['sourceAudioMeasurement'];silent=bool(measured['silent'])
   gain=0. if silent else -23.-float(measured['integratedLufs']);assert abs(gain)<=16
   data*=10**(gain/20)
   fade_in=min(round(.12*48000),len(data)//2);fade_out=min(round(.3*48000),len(data)//2)
   data[:fade_in]*=np.linspace(0,1,fade_in,dtype=np.float32)[:,None];data[-fade_out:]*=np.linspace(1,0,fade_out,dtype=np.float32)[:,None]
   start=cut['globalStartFrame']*800;out.seek(start);out.write(data)
   game_rows.append(dict(id=cut['id'],beat=cut['beat'],sourceFile=source['audioFile'],sourceSha256=source['audioSha256'],
    sourceSampleRate=rate,sourceSamples=len(raw),sourceAudioMeasurement=measured,targetInitialLufs=None if silent else -23,
    fixedGameGainDb=gain,originalSilencePreserved=silent,sourceSpeed=1,outputStartSample=start,outputSamples=expected,
    outputStartFrame=cut['globalStartFrame'],frames=cut['frames'],fadeInSeconds=.12,fadeOutSeconds=.3,
    musicSeparation='Original synchronized mixed game sound preserved; no separate BGM added; inseparable in-game music is not falsely removed.',humanListening='pending'))
 ducked=A/'game-ducked.wav';premix=A/'final-mix-pre-gain.wav'
 graph=f'[0:a]asplit=2[voice][control];[1:a][control]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1,apad=whole_len={total},atrim=end_sample={total},asplit=2[gameout][gameformix];[voice][gameformix]amix=inputs=2:normalize=0:duration=longest:dropout_transition=0[mix]'
 run(['-threads','2','-filter_complex_threads','2','-i',narration,'-i',game,'-filter_complex',graph,'-map','[gameout]','-c:a','pcm_f32le',ducked,'-map','[mix]','-c:a','pcm_f32le',premix],'game-sidechain-and-sum')
 stats=a.loudness(premix,'final-premix-loudness');program_gain=min(0.,-2.3-float(stats['input_tp']))
 final_wav=O/'final-mix.wav';final_aac=O/'final-mix.m4a';final_voice=A/'narration-final-stem.wav';final_game=A/'game-final-stem.wav'
 scale(premix,final_wav,program_gain);scale(narration,final_voice,program_gain);scale(ducked,final_game,program_gain)
 run(['-threads','2','-i',final_wav,'-map','0:a:0','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',final_aac],'final-aac')
 encoded=a.loudness(final_aac,'final-aac-loudness');peak=float(encoded['input_tp'])
 assert peak<=-1.5,f'Encoded true peak{peak} exceeds ceiling; keep receipt logs and inspect before a justified correction'
 # Exact mixing relation in bounded blocks. The subtraction check does not
 # pretend that residual energy alone measures voice inside game sound.
 maximum_residual=0.;windows=[]
 with sf.SoundFile(final_wav) as mixed,sf.SoundFile(final_voice) as voice_stream,sf.SoundFile(final_game) as game_stream:
  assert mixed.frames==voice_stream.frames==game_stream.frames==total
  for m,v,g in zip(mixed.blocks(blocksize=480000,dtype='float32',always_2d=True),voice_stream.blocks(blocksize=480000,dtype='float32',always_2d=True),game_stream.blocks(blocksize=480000,dtype='float32',always_2d=True)):
   maximum_residual=max(maximum_residual,float(np.max(np.abs(m.astype(np.float64)-v.astype(np.float64)-g.astype(np.float64)))))
 assert maximum_residual<2e-6,'Final mix must equal its two actual stems without automatic normalization'
 continuity=[];voice_by={r['scene']:r for r in voice['scenes']}
 with sf.SoundFile(final_voice) as current_voice,sf.SoundFile(narration) as known_limited_voice:
  for scene in plan['scenes']:
   source_row=voice_by[scene['id']];raw,rate=sf.read(R/scene['rawVoiceFile'],dtype='int16',always_2d=True)
   mono=raw[:,0].astype(np.float32)/32768.;reference=resample_poly(mono,2,1)
   expected=reference*a.g.curve(source_row['clipGainPlan'],len(reference),48000)
   expected*=10**(source_row['constantGlobalGainDb']/20)
   current_voice.seek(scene['startFrame']*800);current_pcm=current_voice.read(scene['frames']*800,dtype='float32',always_2d=True)
   known_limited_voice.seek(scene['startFrame']*800);limited_pcm=known_limited_voice.read(scene['frames']*800,dtype='float32',always_2d=True)
   assert np.max(np.abs(current_pcm-limited_pcm*10**(program_gain/20)))<2e-6,'Mixer must preserve the approved narration stem with one program gain only'
   maximum_error=0.;local=[];recovered_processed=np.zeros(len(reference),dtype=np.float32);asr_file=R/scene['rawAsrFile'];assert a.sha(asr_file)==scene['rawAsrSha256'];asr=a.read(asr_file);assert asr['audio_sha256']==scene['rawVoiceSha256'];active=np.repeat(a.mask(len(mono),rate,asr['words']),2)
   for segment in scene['voiceSegments']:
    left,right,destination=[segment[k]*2 for k in ['sourceSampleStart','sourceSampleEnd','destinationSampleStart']]
    observed=current_pcm[destination:destination+right-left]
    recovered_processed[left:right]=observed[:,0]
    expected_final=limited_pcm[destination:destination+right-left]*10**(program_gain/20)
    maximum_error=max(maximum_error,float(np.max(np.abs(observed-expected_final))))
    for offset in range(left,right-round(.4*48000)+1,round(.1*48000)):
     end=offset+round(.4*48000);speech_mask=active[offset:end]
     if speech_mask.sum()<.15*48000:continue
     actual=observed[offset-left:end-left].mean(axis=1)[speech_mask]
     source_ref=reference[offset:end][speech_mask]
     source_level=a.db(a.rms(source_ref));stem_level=a.db(a.rms(actual))
     limited_local=limited_pcm[destination+offset-left:destination+end-left,0][speech_mask]
     gain=a.db(a.rms(limited_local*10**(program_gain/20)))-source_level
     limiter_change=a.db(a.rms(limited_local))-a.db(a.rms(expected[offset:end][speech_mask]))
     local.append(dict(rawStart=offset/48000,rawEnd=end/48000,globalStart=scene['startFrame']/60+(destination+offset-left)/48000,
      sourceResampledSpeechDbfs=source_level,stemSpeechDbfs=stem_level,expectedClipAndGlobalGainDb=gain,measuredGainDb=stem_level-source_level,
      transferDeviationDb=stem_level-source_level-gain,intendedTransientLimiterLevelChangeDb=limiter_change))
   assert maximum_error<2e-6,'Final narration stem differs from the approved sample-aligned limited stem plus fixed program gain'
   paragraphs=[]
   for paragraph in source_row['clipGainPlan']['sourceParagraphs']:
    left,right=[round(t*48000) for t in paragraph['rawRange']];selection=active[left:right]
    before=a.db(a.rms(reference[left:right][selection]));after=a.db(a.rms(recovered_processed[left:right][selection]))
    paragraphs.append(dict(line=paragraph['line'],rawRange=paragraph['rawRange'],sourceSpeechDbfs=before,processedSpeechDbfs=after,
     measuredEffectiveGainDb=after-before,clipGroup=next(i for i,g in enumerate(source_row['clipGainPlan']['groups']) if g['firstLine']<=paragraph['line']<=g['lastLine']),humanListening='pending'))
   continuity.append(dict(scene=scene['id'],sourceSha256=scene['rawVoiceSha256'],
    entireResampledSourceCompared=True,sourceToStemMaximumAbsoluteError=maximum_error,localWindows=local,
    processingDropFlags=[x for x in local if abs(x['transferDeviationDb'])>1.0],
    sourceProsody='Intra-phrase stress retained; sustained whole-paragraph decay corrected with constant group gain/quiet joins; approved transient-only peak attenuation recorded separately.',clipGainPlan=source_row['clipGainPlan'],paragraphLevelBeforeAfter=paragraphs,
    transientLimiterReviewWindows=[x for x in local if x['intendedTransientLimiterLevelChangeDb']<-3],humanListening='pending'))
 # Joins are exact global times, not an assertion that a human listened.
 for previous,current in zip(plan['scenes'],plan['scenes'][1:]):
  boundary=current['startFrame']/60
  with sf.SoundFile(final_voice) as f:
   f.seek(max(0,round((boundary-3)*48000)));sample=f.read(6*48000,dtype='float32',always_2d=True)
  windows.append(dict(previous=previous['id'],next=current['id'],boundarySeconds=boundary,range=[max(0,boundary-3),boundary+3],voiceRmsDbfs=a.db(a.rms(sample)),voicePeakDbfs=a.db(np.max(np.abs(sample))),actualListening='pending'))
 files=[final_wav,final_aac,final_voice,final_game,game,ducked]
 report=dict(schemaVersion=1,revision='article-flow-v6',inputs=inputs,outputs=[dict(file=a.rel(f),sha256=a.sha(f)) for f in files],
  audioMix=a.rel(final_wav),encodedAudio=a.rel(final_aac),narrationStem=a.rel(final_voice),gameStem=a.rel(final_game),
  totalFrames=plan['totalFrames'],totalSamples=total,sampleRate=48000,channels=2,seconds=plan['seconds'],games=game_rows,
  sourcePcmProof=a.rel(A/'audio-build.json'),sourcePcmProofSha256=a.sha(A/'audio-build.json'),
  separatelyAddedBgm=False,voiceDucking=False,voiceFades=False,limiter=voice['transientLimiter'],amixNormalize=0,
  gameDucking=dict(threshold=.08,ratio=2.2,attackMs=15,releaseMs=280,makeup=1,sidechain='narration controls game input only'),
  preGainMeasurement=stats,constantProgramGainDb=program_gain,encodedMeasurement=encoded,
  finalMixEqualsVoicePlusGameMaximumAbsoluteError=maximum_residual,joinWindows=windows,
  sourceToFinalNarrationStem=continuity,sourceToStemProcessingDropFlags=sum(len(s['processingDropFlags']) for s in continuity),
  localContinuity='Source→voice-stem expected constant clip-group/quiet-only join gains and exact mixed-stem relation proven; encoded speech-active comparisons and contextual human listening pending final QA.',
  wholeFinalMixAsr='pending root-owned once-only final encoded-audio ASR',humanWholeListening='pending')
 a.save(receipt,report);print('Final synchronized no-added-BGM lecture mix ready;48k stereo192kbps AAC; true peak',peak)
if __name__=='__main__':main()

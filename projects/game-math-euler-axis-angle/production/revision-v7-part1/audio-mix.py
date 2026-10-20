"""Finite CPU Part1 mix: native game audio, approved voice and original ends."""
from pathlib import Path
import hashlib,importlib.util,json,math,subprocess
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v7_narration_prepare',H/'audio-prepare.py')
a=importlib.util.module_from_spec(s);s.loader.exec_module(a);c=a.c
def scale(src,dst,gain):
 with sf.SoundFile(src)as inp,sf.SoundFile(dst,'w',samplerate=inp.samplerate,channels=inp.channels,subtype='FLOAT')as out:
  for x in inp.blocks(blocksize=480000,dtype='float32',always_2d=True):out.write(x*10**(gain/20))
def write_at(stream,start,data):
 assert start>=0 and start+len(data)<=stream.frames
 stream.seek(start);stream.write(data)
def decode(source,start,frames,dst,name):
 samples=frames*800
 a.run(['-threads','2','-ss',f'{start:.9f}','-i',source,'-map','0:a:0','-vn',
        '-af',f'aresample=48000,apad=whole_len={samples},atrim=end_sample={samples}',
        '-ac','2','-c:a','pcm_f32le',dst],name)
 x,rate=sf.read(dst,dtype='float32',always_2d=True)
 assert rate==48000 and x.shape==(samples,2),'Exact native excerpt must match frame clock'
 return x
def audio_streams(source):
 q=subprocess.run(['ffprobe','-v','error','-select_streams','a','-show_entries','stream=index,codec_name,sample_rate,channels','-of','json',str(source)],capture_output=True,check=True)
 return json.loads(q.stdout)['streams']
def fingerprint(value):
 return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def build():
 c.validate(preserve_pcm=True);timeline_file=H/'timeline.json';left_file=H/'left-visual-segments.json'
 timeline=c.read(timeline_file);left=c.read(left_file);game_inputs=c.read(H/'game-inputs.json')
 voice_file=c.O/'narration-build.json';voice=c.read(voice_file);narration=c.R/voice['narrationFile']
 assert voice['inputs']['timelineSha256']==c.sha(timeline_file)
 assert left['inputs']['timelineSha256']==c.sha(timeline_file)
 narration_sha=c.sha(narration);assert any(x['sha256']==narration_sha for x in voice['outputs'])
 assert timeline['introFrames']==120 and timeline['outroFrames']==600
 audio_cuts=[{k:x[k]for k in ['beatId','sourceId','startFrame','endFrameExclusive','nativeSourceInFrame','nativeSourceOutFrameExclusive','sourceAudioAllowed','silent']}for x in sorted(left['liveBeats'],key=lambda q:q['startFrame'])]
 audio_sources={sid:{k:game_inputs['sources'][sid].get(k)for k in ['sourcePath','sourceSha256','sourceAudioAllowed','silent']}for sid in sorted({x['sourceId']for x in audio_cuts})}
 audio_clock=dict(totalFrames=timeline['totalFrames'],introFrames=timeline['introFrames'],outroFrames=timeline['outroFrames'],bodyEndFrame=timeline['bodyEndFrame'],branding=timeline['branding'])
 observed=dict(timelineSha256=c.sha(timeline_file),leftFullManifestSha256=c.sha(left_file),gameInputsFullSha256=c.sha(H/'game-inputs.json'),narrationBuildSha256=c.sha(voice_file))
 inputs=dict(audioClockSha256=fingerprint(audio_clock),nativeAudioCutsSha256=fingerprint(audio_cuts),
  originalAudioSourcesAndPolicySha256=fingerprint(audio_sources),narrationFile=c.rel(narration),narrationPcmSha256=narration_sha,
  implementationSha256=c.sha(Path(__file__)),voicePreparationImplementationSha256=c.sha(H/'audio-prepare.py'),
  branding=[dict(file=x['file'],sha256=c.sha(c.R/x['file']))for x in timeline['branding'].values()])
 receipt=c.O/'audio-build.json'
 if receipt.exists():
  old=c.read(receipt)
  if old['inputs']==inputs and all((c.R/x['file']).exists()and c.sha(c.R/x['file'])==x['sha256']for x in old['outputs']):
   print('Exact successful current audio contract reused; annotation-only manifest changes do not regenerate audio');return old
  raise RuntimeError('Preserve differing existing mix before an authorized revision')
 total=timeline['totalFrames']*800;parts=c.O/'mix-inputs';parts.mkdir(exist_ok=True)
 game=c.O/'game-normalized.wav';brand=c.O/'branding-original.wav'
 assert not any(x.exists()for x in [game,brand,c.O/'final-mix.wav',c.O/'final-mix.m4a']),'Inspect unreceipted output before retry'
 a.initialize(game,48000,2,total,'FLOAT');a.initialize(brand,48000,2,total,'FLOAT')
 checked=set();rows=[];last_end=0
 with sf.SoundFile(game,'r+')as out:
  for i,cut in enumerate(sorted(left['liveBeats'],key=lambda x:x['startFrame'])):
   c.selected();start=cut['startFrame'];end=cut['endFrameExclusive'];frames=end-start
   assert start>=last_end and end<=timeline['bodyEndFrame']and frames>0,'Native game audio must not overlap'
   last_end=end;sid=cut['sourceId'];source=game_inputs['sources'][sid];f=c.R/source['sourcePath']
   assert not cut['sourceAudioAllowed']or source['sourceAudioAllowed'],'A cut cannot grant audio excluded by its original source policy'
   if sid not in checked:
    assert c.sha(f)==source['sourceSha256'],'Changed independently verified game source';checked.add(sid)
   row=dict(id=cut['beatId'],sourceId=sid,sourceFile=source['sourcePath'],sourceSha256=source['sourceSha256'],
    sourceStartFrame=cut['nativeSourceInFrame'],sourceEndFrameExclusive=cut['nativeSourceOutFrameExclusive'],
    startFrame=start,endFrameExclusive=end,frames=frames,sourceSpeed=1,sourceAudioAllowed=cut['sourceAudioAllowed'],
    sourceMarkedSilent=cut['silent'],sourceAudioPolicy='Original mixed game sound only during the actual native action; no audio extension under frozen analysis.',
    humanListening='pending')
   assert cut['nativeSourceOutFrameExclusive']-cut['nativeSourceInFrame']==frames
   if not cut['sourceAudioAllowed']:
    row.update(audioWritten=False,reason='Source permission excludes audio; silence retained')
   else:
    decoded=parts/(f'{i+1:03}-{sid}.wav')
    x=decode(f,cut['nativeSourceInFrame']/60,frames,decoded,f'game-{i+1:03}-decode')
    stats=a.loudness(decoded,f'game-{i+1:03}-measurement');value=stats['input_i']
    silent=float(np.max(abs(x)))<1e-7;measurable=value not in ['-inf','inf']
    gain=0. if silent or not measurable else -23-float(value)
    assert abs(gain)<=20,'Large original-game gain needs evidence before automatic use'
    if cut['silent']:assert silent,'Claimed-silent source contains sound; inspect source permission'
    x*=10**(gain/20)
    ni=min(round(.12*48000),len(x)//2);no=min(round(.30*48000),len(x)//2)
    if ni:x[:ni]*=np.linspace(0,1,ni,dtype=np.float32)[:,None]
    if no:x[-no:]*=np.linspace(1,0,no,dtype=np.float32)[:,None]
    write_at(out,start*800,x)
    row.update(audioWritten=True,decodedFile=c.rel(decoded),decodedSha256=c.sha(decoded),
     originalMeasurement=stats,actualSilent=silent,loudnessMeasurable=measurable,initialTargetLufs=None if silent or not measurable else -23,
     constantGainDb=gain,fadeInSeconds=.12,fadeOutSeconds=.30)
   rows.append(row)
 brand_rows=[]
 with sf.SoundFile(brand,'r+')as out:
  for key,item in timeline['branding'].items():
   f=c.R/item['file'];dst=parts/(key+'-original.wav')
   streams=audio_streams(f)
   if streams:x=decode(f,0,item['frames'],dst,key+'-original-decode')
   else:
    x=np.zeros((item['frames']*800,2),dtype=np.float32)
    sf.write(dst,x,48000,subtype='FLOAT')
   write_at(out,item['startFrame']*800,x)
   brand_rows.append(dict(kind=key,sourceFile=item['file'],sourceSha256=c.sha(f),
    outputStartFrame=item['startFrame'],frames=item['frames'],sourceGainDb=0,decodedSha256=c.sha(dst),
    sourceAudioStreams=streams,originalSilencePreserved=not streams,noExtraMusicAdded=True))
 ducked=c.O/'game-ducked.wav';premix=c.O/'final-mix-pre-gain.wav'
 graph=f'[0:a]asplit=2[voice][control];[1:a][control]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1,apad=whole_len={total},atrim=end_sample={total},asplit=2[gameout][gameformix];[voice][gameformix][2:a]amix=inputs=3:normalize=0:duration=longest:dropout_transition=0[mix]'
 a.run(['-threads','2','-filter_complex_threads','2','-i',narration,'-i',game,'-i',brand,
  '-filter_complex',graph,'-map','[gameout]','-c:a','pcm_f32le',ducked,
  '-map','[mix]','-c:a','pcm_f32le',premix],'game-only-sidechain-and-sum')
 stats=a.loudness(premix,'final-premix-loudness');gain=min(0.,-2.3-float(stats['input_tp']))
 final=c.O/'final-mix.wav';aac=c.O/'final-mix.m4a'
 fv=c.O/'narration-final-stem.wav';fg=c.O/'game-final-stem.wav';fb=c.O/'branding-final-stem.wav'
 for src,dst in [(premix,final),(narration,fv),(ducked,fg),(brand,fb)]:scale(src,dst,gain)
 a.run(['-threads','2','-i',final,'-map','0:a:0','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',aac],'final-aac')
 encoded=a.loudness(aac,'final-aac-loudness')
 assert float(encoded['input_tp'])<=-1.5,'Encoded current audio exceeds true-peak limit; inspect before a justified change'
 residual=0.;voice_error=0
 with sf.SoundFile(final)as m,sf.SoundFile(fv)as v,sf.SoundFile(fg)as g,sf.SoundFile(fb)as b,sf.SoundFile(narration)as ref:
  assert all(x.frames==total and x.samplerate==48000 and x.channels==2 for x in [m,v,g,b,ref])
  streams=[x.blocks(blocksize=480000,dtype='float32',always_2d=True)for x in [m,v,g,b,ref]]
  for mx,vx,gx,bx,rx in zip(*streams):
   residual=max(residual,float(np.max(abs(mx.astype(np.float64)-vx.astype(np.float64)-gx.astype(np.float64)-bx.astype(np.float64)))))
   voice_error=max(voice_error,float(np.max(abs(vx-rx*10**(gain/20)))))
 assert residual<2e-6 and voice_error<2e-6
 report=dict(schemaVersion=1,revision='v7-part1',part=1,inputs=inputs,observedManifests=observed,
  semanticAudioContract=dict(clock=audio_clock,nativeCuts=audio_cuts,sources=audio_sources),annotationOnlyChangesExcludedFromCacheIdentity=True,
  outputs=[dict(file=c.rel(x),sha256=c.sha(x))for x in [final,aac,fv,fg,fb,game,ducked,brand]],
  audioMix=c.rel(final),encodedAudio=c.rel(aac),narrationStem=c.rel(fv),gameStem=c.rel(fg),brandingStem=c.rel(fb),
  sampleRate=48000,channels=2,totalFrames=timeline['totalFrames'],totalSamples=total,seconds=timeline['duration'],
  games=rows,branding=brand_rows,separatelyAddedBgm=False,voiceDucking=False,voiceFades=False,
  amixNormalize=0,gameDucking=dict(threshold=.08,ratio=2.2,attackMs=15,releaseMs=280,makeup=1,control='narration controls game input only'),
  preGainMeasurement=stats,constantProgramGainDb=gain,encodedMeasurement=encoded,
  exactStemSumMaximumError=residual,narrationTransferMaximumError=voice_error,
  sourceToNarrationProof=c.rel(voice_file),sourceToNarrationProofSha256=c.sha(voice_file),
  wholeFinalMixAsr='pending once-only current encoded mix ASR',encodedLevelContinuity='pending',
  humanWholeListening='pending')
 c.save(receipt,report);print(json.dumps(dict(seconds=report['seconds'],encodedAudio=report['encodedAudio'],truePeak=encoded['input_tp'],programGainDb=gain)))
 return report
if __name__=='__main__':build()

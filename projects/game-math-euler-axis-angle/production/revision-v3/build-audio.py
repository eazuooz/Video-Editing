"""No added BGM. Constant narration gain and quiet synchronized native game audio."""
from pathlib import Path
import json, importlib.util, math
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v3';O.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('v2_audio',P/'production/revision-v2/build-audio.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
read=h.read;sha=h.sha;save=h.save;rel=h.relative
def run(args,name):return h.run(args,name,O)
def quiet_game_cut(c,cache):
 raw=cache/(c['id']+'-raw.wav');quiet=cache/(c['id']+'.wav');receipt=cache/(c['id']+'.json');sig=dict(sourceSha256=c['sourceSha256'],sourceStart=c['sourceStart'],frames=c['frames'],targetLufs=-32,sourceSpeed=1)
 if not(quiet.exists() and receipt.exists() and read(receipt).get('inputs')==sig):
  run(['-ss',c['sourceStart'],'-i',R/c['sourceFile'],'-t',c['seconds'],'-vn','-ar',48000,'-ac',2,'-c:a','pcm_f32le',raw],c['id']+'-game-extract')
  log=run(['-i',raw,'-af','loudnorm=I=-32:TP=-2:LRA=11:print_format=json','-f','null','-'],c['id']+'-game-measure')
  stats_game=json.loads(log[log.rfind('{'):log.rfind('}')+1])
  # Some independently supplied captures are genuinely silent. Retain silence
  # rather than amplify noise or fabricate replacement game effects.
  silent_source=not math.isfinite(float(stats_game['input_i']))
  if silent_source:
   measured,measured_rate=sf.read(raw,dtype='float32');assert float(np.max(np.abs(measured)))<1e-4
  gain_game=0. if silent_source else min(0.,-32-float(stats_game['input_i']))
  run(['-i',raw,'-af',f'volume={gain_game}dB:precision=double,alimiter=limit=0.1:attack=3:release=80:level=false:latency=true,afade=t=in:d=0.025,afade=t=out:st={max(0,c["seconds"]-.025)}:d=0.025','-ar',48000,'-ac',2,'-c:a','pcm_f32le',quiet],c['id']+'-game-quiet')
  save(receipt,dict(inputs=sig,measurement=stats_game,gainDb=gain_game,silentSource=silent_source,sha256=sha(quiet)))
 info=read(receipt);assert sha(quiet)==info['sha256'];return quiet,info
def build():
 h.require_selected();planfile=Path(__file__).parent/'timeline.json';plan=read(planfile);assert plan['actualFrames']*3==plan['explanationFrames']*2
 for f,d in plan['inputHashes'].items():assert sha(R/f)==d,('Stale timeline input',f)
 duration=plan['totalFrames']/60;voice=np.zeros(round(duration*24000),dtype=np.float32);reports=[]
 for s in plan['scenes']:
  raw,rate=sf.read(R/s['voice'],dtype='float32');placed,pr=sf.read(R/s['placedVoice'],dtype='float32');assert rate==pr==24000
  assert sha(R/s['voice'])==s['voiceSha256'] and sha(R/s['placedVoice'])==s['placedVoiceSha256']
  asr=read(R/s['asr']);assert asr['audio_sha256']==s['voiceSha256']
  proof=h.preserved_placement(raw,placed,s['observationPauses'],rate);mask=h.speech_mask(len(raw),rate,asr['words']);speech=h.db(h.rms(raw[mask]));gain=-20-speech;assert abs(gain)<24
  current=placed*(10**(gain/20));edge=144;current[:edge]*=np.linspace(0,1,edge);current[-edge:]*=np.linspace(1,0,edge)
  start=s['startFrame']*400;assert start+len(current)<len(voice);voice[start:start+len(current)]=current
  windows=[]
  for a in range(0,max(0,len(raw)-rate+1),rate//2):
   vals=raw[a:a+rate][mask[a:a+rate]]
   if len(vals)>=rate*.25:windows.append(dict(rawTime=a/rate,sourceSpeechDbfs=h.db(h.rms(vals)),afterConstantGainDbfs=h.db(h.rms(vals))+gain))
  reports.append(dict(scene=s['id'],sourceSha256=s['voiceSha256'],placedSha256=s['placedVoiceSha256'],sourceSpeechRmsDbfs=speech,fixedGainDb=gain,pcmPreservation=proof,speechWindows=windows,outputStartSeconds=start/rate,outputEndSeconds=(start+len(current))/rate,edgeFadeMs=6,noSourcePcmOverwrite=True))
 fixed=O/'voice-fixed-gain.wav';sf.write(fixed,voice,24000,subtype='FLOAT');del voice
 stats=h.loudness_stats(run(['-i',fixed,'-af','pan=stereo|c0=c0|c1=c0,loudnorm=I=-16:TP=-2:LRA=9:print_format=json','-f','null','-'],'voice-measure'))
 global_gain=-16-float(stats['input_i']);narration=O/'narration-stem.wav'
 run(['-i',fixed,'-af',f'volume={global_gain}dB:precision=double,alimiter=limit=0.7499:attack=5:release=50:level=false:latency=true,pan=stereo|c0=c0|c1=c0','-ar',48000,'-c:a','pcm_s24le',narration],'narration-fixed-gain')
 game=np.zeros((round(duration*48000),2),dtype=np.float32);game_report=[];cache=O/'game-audio';cache.mkdir(exist_ok=True)
 for c in plan['cuts']:
  quiet,info=quiet_game_cut(c,cache);samples,rate=sf.read(quiet,dtype='float32',always_2d=True);assert rate==48000 and samples.shape[1]==2
  count=c['frames']*800;assert abs(len(samples)-count)<=1024
  at=c['globalStartFrame']*800;game[at:at+min(count,len(samples))]=samples[:count]
  game_report.append(dict(cut=c['id'],sourceId=c['sourceId'],sourceStart=c['sourceStart'],seconds=c['seconds'],outputStart=c['globalStartFrame']/60,gainDb=info['gainDb'],targetLufs=-32,peakCeilingDbfs=-20,silentSource=info.get('silentSource',False),sourceAudioKind='original synchronous mixed game track; silent captures remain silent; not separated effects',separationClaim=False))
 gamefile=O/'game-stem.wav';sf.write(gamefile,game,48000,subtype='PCM_24');del game
 # Narration never receives a sidechain or automatic background duck.
 graph='[0:a]asplit=2[voice][side];[1:a][side]sidechaincompress=threshold=0.025:ratio=3:attack=25:release=250[quiet];[voice][quiet]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.794:level=false:latency=true[out]'
 mix=O/'final-mix.wav';run(['-i',narration,'-i',gamefile,'-filter_complex',graph,'-map','[out]','-t',duration,'-ar',48000,'-ac',2,'-c:a','pcm_s24le',mix],'final-mix')
 aac=O/'final-mix.m4a';run(['-i',mix,'-ar',48000,'-ac',2,'-c:a','aac','-b:a','192k',aac],'final-aac');save(O/'aac-source.json',dict(sha256=sha(mix),rate=48000,bitrate='192k'))
 loudness=h.loudness_stats(run(['-i',aac,'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],'encoded-measure'))
 report=dict(schemaVersion=3,slug=P.name,revision='nintendo-annotated-no-bgm-v3',seconds=duration,timeline=rel(planfile),timelineSha256=sha(planfile),scenes=reports,voiceGainMode='constant scene gain plus constant global gain',globalGainDb=global_gain,normalizationMeasurementOnly=stats,music={'addedBgm':False,'externalMusicStem':None,'previousNimbusRemoved':True},voiceDucked=False,sourceAudioUsed=True,gameAudio=game_report,amixNormalize=False,outputSampleRate=48000,outputChannels=2,aacBitrate='192k',encodedLoudnessMeasurement=loudness,outputs=[dict(file=rel(f),sha256=sha(f),bytes=f.stat().st_size) for f in [fixed,narration,gamefile,mix,aac]],sourceToStemToEncodedSpeechContinuity='pending-current-encoded-review',currentFinalMixFullAsr='pending-one-pass',humanWholeListening='pending')
 save(O/'audio-build.json',report);print(json.dumps(dict(seconds=duration,addedBgm=False,gameCuts=len(game_report))))
if __name__=='__main__':build()

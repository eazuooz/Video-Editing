"""Preserve approved-reference PCM and keep background ducking off the voice bus."""
from pathlib import Path
import math
import json,subprocess,hashlib
import numpy as np
import soundfile as sf
from revision_context import paths, ensure_authorized, REVISION
R=Path(__file__).resolve().parents[3];P=R/'projects/ai-games-showcase-2026';V=P/'production';O=P/'production/local/compact-edit';N=R/'shared/output/narration/ai-games-showcase-2026/game-tools-five-second-ppt-v1'
def run(args,name):
 p=subprocess.run(['ffmpeg','-hide_banner','-y',*args],cwd=R,capture_output=True);(O/(name+'.log')).write_bytes(p.stderr)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-3000:])
 return p.stderr.decode(errors='replace')
def db(v):return float(20*np.log10(max(float(v),1e-10)))
def rms(a):return float(np.sqrt(np.mean(a*a))) if len(a) else 0.
def speech_mask(n,rate,words):
 mask=np.zeros(n,dtype=bool)
 for w in words:
  a,b=w['timestamp']
  if a is None or b is None:continue
  mask[max(0,round(a*rate)):min(n,round(b*rate))]=True
 return mask
if __name__=='__main__':
 O,N,EDIT_PLAN,STEM=paths();ensure_authorized()
 plan=json.loads(EDIT_PLAN.read_text(encoding='utf8'));duration=plan['totalFrames']/60
 assert plan.get('timing')=='measured-and-asr-aligned','Estimated timing must not enter production'
 sr=48000 if REVISION else 24000;voice=np.zeros(round(duration*sr),dtype=np.float32);reports=[]
 commonLevel=None
 if REVISION:
  # ASR/alignment uses a24k derivative. Mix from the original44.1k downloads
  # directly at48k, preserving their high-frequency content in the master.
  assembly=json.loads((N/'source-assembly.json').read_text(encoding='utf8'));parts=[]
  for idx,source in enumerate(assembly['inputs']['sources']):
   src=R/source['path'];assert hashlib.sha256(src.read_bytes()).hexdigest()==source['sha256']
   target=N/f'native-source-{idx+1}-48k.wav'
   if not target.exists():run(['-i',str(src),'-ac','1','-ar','48000','-c:a','pcm_f32le',str(target)],f'native-source-{idx+1}')
   a,r=sf.read(target,dtype='float32');assert r==sr;parts.append(a)
  full=np.concatenate([parts[0],np.zeros(round(.2*sr),dtype=np.float32),parts[1]])
  sf.write(N/'native-narration-48k.wav',full,sr,subtype='FLOAT')
  allWords=json.loads((N/'whole-source-asr.json').read_text(encoding='utf8'))['words']
  commonLevel=db(rms(full[speech_mask(len(full),sr,allWords)]))
 for s in plan['scenes']:
  f=N/'chunks'/(s['id']+'-scene.wav');a,r=sf.read(f,dtype='float32');assert r==24000
  q=json.loads((N/'asr'/(s['id']+'.json')).read_text(encoding='utf8'));assert q['audio_sha256']==hashlib.sha256(f.read_bytes()).hexdigest()
  if REVISION:
   lo=round((s['voiceStart']-2)*sr);a=full[lo:lo+len(a)*2]
  mask=speech_mask(len(a),sr,q['words']);level=db(rms(a[mask]));gain=float(10**((-20-(commonLevel if commonLevel is not None else level))/20))
  # Constant per-scene gain preserves local prosody; only the background has
  # time-varying sidechain compression. Drift flags require bounded review.
  out=a*gain
  edge=min(round(.006*sr),len(out)//2)
  if not REVISION or s['id']==plan['scenes'][0]['id']:out[:edge]*=np.linspace(0,1,edge)
  if not REVISION or s['id']==plan['scenes'][-1]['id']:out[-edge:]*=np.linspace(1,0,edge)
  start=round(s['voiceStart']*sr);voice[start:start+len(out)]=out
  windows=[]
  for i in range(0,len(a)-sr,round(sr*.5)):
   m=mask[i:i+sr];v=a[i:i+sr][m]
   if len(v)>=sr*.25:windows.append({'time':i/sr,'sourceSpeechDbfs':db(rms(v)),'afterConstantGainDbfs':db(rms(v*gain))})
  reports.append({'scene':s['id'],'sourceSha256':q['audio_sha256'],'sourceSpeechRmsDbfs':level,'fixedGainDb':db(gain),'windows':windows,'noSourcePcmOverwrite':True})
 sf.write(O/'voice-fixed-gain.wav',voice,sr,subtype='FLOAT')
 logs=run(['-i',str(O/'voice-fixed-gain.wav'),'-af','loudnorm=I=-16:TP=-2:LRA=9:print_format=json','-f','null','-'],'voice-measure')
 stats=json.loads(logs[logs.rfind('{'):logs.rfind('}')+1]);gainDb=-16-float(stats['input_i'])
 # loudnorm silently falls back to dynamic mode when the requested linear
 # gain would exceed its peak ceiling. Keep one constant global gain and a short peak limiter;
 # never apply a seconds-long adaptive normalization envelope to narration.
 norm=f'volume={gainDb}dB:precision=double,alimiter=limit=0.7499:attack=5:release=50:level=false:latency=true'
 run(['-i',str(O/'voice-fixed-gain.wav'),'-af',norm+',pan=stereo|c0=c0|c1=c0','-ar','48000','-c:a','pcm_s24le',str(O/'narration-stem.wav')],'voice-normalize')
 rate=48000;game=np.zeros((round(duration*rate),2),dtype=np.float32);gameRecords=[]
 for c in plan['cuts']:
  if c['kind']!='independent-gameplay':continue
  if c.get('originalAudio')=='exclude':
   gameRecords.append({'cut':c['id'],'mixedOriginalAudio':False,'reason':'Creator mixed music not cleared; exclude source soundtrack'})
   continue
  d=c['frames']/60;f=O/(c['id']+'-game.wav');run(['-ss',str(c['sourceStart']),'-i',c['sourceFile'],'-t',str(d),'-vn','-ar','48000','-ac','2','-c:a','pcm_f32le',str(f)],c['id']+'-game')
  a,r=sf.read(f,dtype='float32',always_2d=True);a=a[:round(d*rate)];level=rms(a);gain=min(1.,10**(-33/20)/max(level,1e-9));a*=gain
  fade=min(960,len(a)//2);a[:fade]*=np.linspace(0,1,fade)[:,None];a[-fade:]*=np.linspace(1,0,fade)[:,None]
  start=round(c['startFrame']/60*rate);game[start:start+len(a)]+=a;gameRecords.append({'cut':c['id'],'sourceRmsDbfs':db(level),'gainDb':db(gain),'mixedOriginalAudio':True})
 sf.write(O/'game-stem.wav',game,rate,subtype='PCM_24')
 music=R/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3'
 assert hashlib.sha256(music.read_bytes()).hexdigest()=='06ddb8d0f2aa82e499ab2cb398b8a241c626d9d3da82bbaf274d1178435f8c08'
 musicDuration=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(music)]))['format']['duration'])
 repeat=max(1,math.ceil((duration-1)/(musicDuration-1)));inputs=sum((['-i',str(music)] for _ in range(repeat)),[]);filters=[];last='0:a'
 for i in range(1,repeat):
  filters.append(f'[{last}][{i}:a]acrossfade=d=1:c1=tri:c2=tri[m{i}]');last=f'm{i}'
 filters.append(f'[{last}]atrim=duration={duration},loudnorm=I=-31:TP=-4:LRA=7,afade=t=in:st=0:d=0.45,afade=t=out:st={duration-.45}:d=0.45[music]')
 run([*inputs,'-filter_complex',';'.join(filters),'-map','[music]','-t',str(duration),'-ar','48000','-ac','2','-c:a','pcm_s24le',str(O/'music-stem.wav')],'music-level')
 graph='[0:a]asplit=3[voice][side1][side2];[1:a][side1]sidechaincompress=threshold=0.025:ratio=3:attack=35:release=400[bg];[2:a][side2]sidechaincompress=threshold=0.035:ratio=2:attack=15:release=250[game];[voice][bg][game]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.794:level=false:latency=true[out]'
 run(['-i',str(O/'narration-stem.wav'),'-i',str(O/'music-stem.wav'),'-i',str(O/'game-stem.wav'),'-filter_complex',graph,'-map','[out]','-t',str(duration),'-ar','48000','-c:a','pcm_s24le',str(O/'final-mix.wav')],'final-mix')
 report={'scenes':reports,'gameAudio':gameRecords,'duration':duration,'normalizationMeasurementOnly':stats,'voiceGainMode':'constant-global-gain-with-short-peak-limiter','globalGainDb':gainDb,'peakLimiter':{'ceilingDbfs':-2.5,'attackMs':5,'releaseMs':50,'autoMakeup':False},'musicInitialLufs':-31,'music':'Nimbus — Eveningland','voiceDucked':False,'amixNormalize':False,'sourcePcmPreserved':True,'sourceToStemToEncodedContinuity':'pending','fullFinalAsr':'pending','humanWholeListening':'pending'}
 if REVISION:report.update(nativeSourceMixing=True,mixingSampleRate=48000,sourceDownloadSampleRate=44100,asrDerivativeSampleRate=24000,internalSceneFades=False,nativeSourceSha256=hashlib.sha256((N/'native-narration-48k.wav').read_bytes()).hexdigest())
 (O/'audio-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('Mixed',duration,'seconds')

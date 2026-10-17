"""Preserve approved-reference PCM and keep background ducking off the voice bus."""
from pathlib import Path
import json,subprocess,hashlib
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parents[4];P=R/'projects/avoid-game-comparisons';V=P/'production/reference-preserving-v2';O=P/'production/local/reference-preserving-v2/edit';N=R/'shared/output/narration/avoid-game-comparisons/reference-preserving-v2'
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
 plan=json.loads((V/'edit-plan.json').read_text(encoding='utf8'));duration=plan['totalFrames']/60
 sr=24000;voice=np.zeros(round(duration*sr),dtype=np.float32);reports=[]
 for s in plan['scenes']:
  f=N/'chunks'/(s['id']+'-scene.wav');a,r=sf.read(f,dtype='float32');assert r==sr
  q=json.loads((N/'asr'/(s['id']+'.json')).read_text(encoding='utf8'));assert q['audio_sha256']==hashlib.sha256(f.read_bytes()).hexdigest()
  mask=speech_mask(len(a),sr,q['words']);level=db(rms(a[mask]));gain=float(10**((-20-level)/20))
  # Constant per-scene gain preserves local prosody; only the background has
  # time-varying sidechain compression. Drift flags require bounded review.
  out=a*gain;start=round(s['voiceStart']*sr);voice[start:start+len(out)]=out
  windows=[]
  for i in range(0,len(a)-sr,round(sr*.5)):
   m=mask[i:i+sr];v=a[i:i+sr][m]
   if len(v)>=sr*.25:windows.append({'time':i/sr,'sourceSpeechDbfs':db(rms(v)),'afterConstantGainDbfs':db(rms(v*gain))})
  reports.append({'scene':s['id'],'sourceSha256':q['audio_sha256'],'sourceSpeechRmsDbfs':level,'fixedGainDb':db(gain),'windows':windows,'noSourcePcmOverwrite':True})
 sf.write(O/'voice-fixed-gain.wav',voice,sr,subtype='FLOAT')
 logs=run(['-i',str(O/'voice-fixed-gain.wav'),'-af','loudnorm=I=-16:TP=-2:LRA=9:print_format=json','-f','null','-'],'voice-measure')
 stats=json.loads(logs[logs.rfind('{'):logs.rfind('}')+1]);gainDb=-16-float(stats['input_i'])
 # loudnorm silently falls back to dynamic mode when the requested linear
 # gain would exceed its peak ceiling. That changed local voice gain by17dB
 # in the first mix. Keep one constant global gain and a short peak limiter;
 # never apply a seconds-long adaptive normalization envelope to narration.
 norm=f'volume={gainDb}dB:precision=double,alimiter=limit=0.7499:attack=5:release=50:level=false:latency=true'
 run(['-i',str(O/'voice-fixed-gain.wav'),'-af',norm+',pan=stereo|c0=c0|c1=c0','-ar','48000','-c:a','pcm_s24le',str(O/'narration-stem.wav')],'voice-normalize')
 rate=48000;game=np.zeros((round(duration*rate),2),dtype=np.float32);gameRecords=[]
 for c in plan['cuts']:
  if c['kind']!='independent-gameplay':continue
  d=c['frames']/60;f=O/(c['id']+'-game.wav');run(['-ss',str(c['sourceStart']),'-i',c['sourceFile'],'-t',str(d),'-vn','-ar','48000','-ac','2','-c:a','pcm_f32le',str(f)],c['id']+'-game')
  a,r=sf.read(f,dtype='float32',always_2d=True);a=a[:round(d*rate)];level=rms(a);gain=min(1.,10**(-33/20)/max(level,1e-9));a*=gain
  fade=min(960,len(a)//2);a[:fade]*=np.linspace(0,1,fade)[:,None];a[-fade:]*=np.linspace(1,0,fade)[:,None]
  start=round(c['startFrame']/60*rate);game[start:start+len(a)]+=a;gameRecords.append({'cut':c['id'],'sourceRmsDbfs':db(level),'gainDb':db(gain),'mixedOriginalAudio':True})
 sf.write(O/'game-stem.wav',game,rate,subtype='PCM_24')
 music=R/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3'
 assert hashlib.sha256(music.read_bytes()).hexdigest()=='06ddb8d0f2aa82e499ab2cb398b8a241c626d9d3da82bbaf274d1178435f8c08'
 run(['-stream_loop','-1','-i',str(music),'-t',str(duration),'-af',f'loudnorm=I=-31:TP=-4:LRA=7,afade=t=in:st=0:d=1,afade=t=out:st={duration-2}:d=2','-ar','48000','-ac','2','-c:a','pcm_s24le',str(O/'music-stem.wav')],'music-level')
 graph='[0:a]asplit=3[voice][side1][side2];[1:a][side1]sidechaincompress=threshold=0.025:ratio=3:attack=35:release=400[bg];[2:a][side2]sidechaincompress=threshold=0.035:ratio=2:attack=15:release=250[game];[voice][bg][game]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.794:level=false:latency=true[out]'
 run(['-i',str(O/'narration-stem.wav'),'-i',str(O/'music-stem.wav'),'-i',str(O/'game-stem.wav'),'-filter_complex',graph,'-map','[out]','-t',str(duration),'-ar','48000','-c:a','pcm_s24le',str(O/'final-mix.wav')],'final-mix')
 report={'scenes':reports,'gameAudio':gameRecords,'duration':duration,'normalizationMeasurementOnly':stats,'voiceGainMode':'constant-global-gain-with-short-peak-limiter','globalGainDb':gainDb,'peakLimiter':{'ceilingDbfs':-2.5,'attackMs':5,'releaseMs':50,'autoMakeup':False},'musicInitialLufs':-31,'music':'Nimbus — Eveningland','voiceDucked':False,'amixNormalize':False,'sourcePcmPreserved':True,'sourceToStemToEncodedContinuity':'pending','fullFinalAsr':'pending','humanWholeListening':'pending'}
 (O/'audio-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('Mixed',duration,'seconds')

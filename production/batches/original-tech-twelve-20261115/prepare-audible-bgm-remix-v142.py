"""New audible BGM mix; retain approved speech/timing and original game audio."""
from pathlib import Path
import argparse, datetime, hashlib, importlib.util, json, math, re, subprocess, time
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
FF=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
n=module('audible142_guard',H/'run-camera-native-v1.py');module('audible142_policy',H/'cooperative-resource-policy-v19.py').install(n)
read,pin,sha,save=n.read,n.pin,n.sha,n.save
def prepare(slug):
 n.authority();binding=read(H/'audible-bgm-baseline-bindings-v142.json');row=next(x for x in binding['projects']if x['slug']==slug)
 assert row['order']!=2,'Mario camera comparison requires its separately accepted extended voice.'
 for k in ['oldMix','oldEncodedQa','voiceProof','paragraphTiming','captionTiming']:assert pin(row[k]['path'])==row[k],k
 old=read(row['oldMix']['path'])
 for k in ['voice','mix','musicStem']:assert pin(old[k]['path'])==old[k]
 music=ROOT/'shared/assets/music/incompetech/Wholesome.mp3';assert sha(music)=='9eadc79a1a2cb68cd63be1432ebf8f8ae3387cb9d2e85f9b8dbc74ba5a96b231'
 identity=dict(adapter=pin(__file__),binding=pin(H/'audible-bgm-baseline-bindings-v142.json'),source=row,music=pin(music),musicLicense=pin(music.with_suffix('.LICENSE.md')),nominalMusicLufs=-28,maximumMusicToVoiceWordRmsDb=-14,backgroundOnlyDucking=True,wholeMasterConstantGainOnly=True,narrationPcmModified=False,speed=1,trim=0,padding=0,executionResourcePolicy=n.cooperative_policy_proof)
 return row,old,identity
def build(slug,base):
 import av,numpy as np,soundfile as sf
 from scipy.ndimage import minimum_filter1d
 from scipy.signal import resample_poly
 row,old,identity=prepare(slug);frames=old['frames'];rate=24000
 v,vr=sf.read(old['voice']['path'],dtype='float32',always_2d=True);prior,pr=sf.read(old['mix']['path'],dtype='float32',always_2d=True);oldbg,br=sf.read(old['musicStem']['path'],dtype='float32',always_2d=True)
 assert vr==pr==br==rate and len(v)==len(prior)==len(oldbg)==frames
 assert v.shape[1]==1 and prior.shape[1]==oldbg.shape[1]==2
 # Subtract only the known old music stem. This retains any paired game audio
 # and its existing approved envelope, rather than guessing or separating it.
 retained=(prior-oldbg).astype(np.float32);assert np.isfinite(retained).all()
 parts=[];resampler=av.AudioResampler(format='fltp',layout='stereo',rate=rate)
 with av.open(identity['music']['path'])as src:
  for f in src.decode(audio=0):
   parts.extend(z.to_ndarray().T.copy()for z in resampler.resample(f))
   if sum(len(z)for z in parts)>=frames:break
 assert sum(len(z)for z in parts)>=frames
 raw=np.concatenate(parts)[:frames].astype(np.float32)
 base.mkdir(parents=True,exist_ok=True);rawfile=base/'music-source-excerpt.wav';assert not rawfile.exists();sf.write(rawfile,raw,rate,subtype='FLOAT')
 command=[str(FF),'-hide_banner','-nostats','-threads','2','-i',str(rawfile),'-af','loudnorm=I=-28:TP=-3:LRA=11:print_format=json','-f','null','NUL']
 result=subprocess.run(command,capture_output=True,creationflags=n.CREATE,check=True);log=result.stderr.decode('utf8','replace');(base/'music-loudness-measurement.log').write_text(log,encoding='utf8');measurement=json.loads(log[log.rfind('{'):]);gain=10**((-28-float(measurement['input_i']))/20)
 bgm=raw*gain;fade=min(frames,round(.45*rate));bgm[:fade]*=np.linspace(0,1,fade,dtype=np.float32)[:,None];bgm[-fade:]*=np.linspace(1,0,fade,dtype=np.float32)[:,None]
 qa=read(row['oldEncodedQa']['path']);words=qa['wordLevelWindows'];assert words
 target=np.ones(frames,dtype=np.float32)
 def rms(a):return float(np.sqrt(np.mean(np.square(a.astype(np.float64)))))
 def db(a):return 20*math.log10(max(1e-12,rms(a)))
 for w in words:
  a,b=w['startSample'],w['endSample']
  if not 0<=a<b<=frames:continue
  limit=min(1,rms(v[a:b])/max(rms(bgm[a:b]),1e-12)*10**(-14/20));a=max(0,a-480);b=min(frames,b+480);target[a:b]=np.minimum(target[a:b],limit)
 env=minimum_filter1d(target,size=961,mode='nearest');release=math.exp(-1/(.28*rate))
 for j in range(1,frames):env[j]=min(env[j],release*env[j-1]+1-release)
 bgm*=env[:,None];unmastered=retained+bgm
 peak=float(np.max(np.abs(resample_poly(unmastered,4,1,axis=0))));bus=min(1,10**(-3/20)/max(peak,1e-12))
 mixed=unmastered*bus;bgm*=bus;voice=v*bus
 windows=[]
 for w in words:
  a,b=w['startSample'],w['endSample']
  if not 0<=a<b<=frames:continue
  delta=db(bgm[a:b])-db(voice[a:b]);assert delta<=-12+.001,(w,delta)
  windows.append(dict(text=w['text'],startSample=a,endSample=b,musicMinusVoiceDb=delta,oldMusicDbfs=db(oldbg[a:b]),newMusicDbfs=db(bgm[a:b])))
 med=float(np.median([x['musicMinusVoiceDb']for x in windows]));improvement=float(np.median([x['newMusicDbfs']-x['oldMusicDbfs']for x in windows]));assert med>-22 and improvement>6,(med,improvement)
 out=base/'final-mix.wav';assert not out.exists();sf.write(out,mixed,rate,subtype='FLOAT');bg=base/'music-audible.wav';sf.write(bg,bgm,rate,subtype='FLOAT')
 proof=dict(identity=identity,fingerprint=n.digest(identity),mix=pin(out),musicStem=pin(bg),voice=old['voice'],voiceProof=row['voiceProof'],paragraphTiming=row['paragraphTiming'],captionTiming=row['captionTiming'],oldEncodedQa=row['oldEncodedQa'],oldMix=row['oldMix'],frames=frames,rate=rate,channels=2,durationSeconds=frames/rate,bodyOnly=True,voiceOffsetSamples=0,voiceRawPcmUnchanged=True,retainedOriginalGameAudioBeforeMaster=True,masterConstantGain=bus,narrationInternalEnvelopeChanged=False,musicSourceGain=gain,musicNominalLufs=-28,measurement=measurement,medianMusicMinusVoiceDb=med,medianMusicIncreaseDb=improvement,wordWindows=windows,actualListening=False,humanApproval=False,independentMixedAsrRequired=True)
 save(base/'audio-build.json',proof);return dict(proof=pin(base/'audio-build.json'),musicIncreaseDb=improvement,musicVsVoiceDb=med,masterGain=bus)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--execute',action='store_true');ap.add_argument('--wait-minutes',type=float,default=0);a=ap.parse_args()
 base=M/a.project/'camera-music-v139/audio-mix-v142';row,old,identity=prepare(a.project)
 if not a.execute:print(json.dumps(dict(sourceReady=True,guardReason=n.busy(),modelStarted=False)));return
 assert a.wait_minutes==15
 protocol='original-tech-twelve-'+a.project+'-audible-bgm-v142';owner='original-tech-twelve-'+a.project+'-audible-bgm';n.runtime.PROTOCOL=protocol;n.runtime.OWNER=owner;n.guard.qualifier.BASE=base/'resource-observations'
 module('audible142_bootstrap',H/'bootstrap-parent-identity-v1.py').install(n,__file__,a.project,base,protocol,owner)
 assert not(base/'audio-build.json').exists(),'Successful mixes are not repeated'
 worker=n.runtime.SingleWorker(path=base/'worker.json');owned=None;deadline=time.monotonic()+a.wait_minutes*60
 try:
  worker.acquire();last=''
  while True:
   reason=n.busy()
   if reason is None:
    token=worker.record['token']
    try:
     with n.LEASE.open('x',encoding='utf8')as f:json.dump(dict(protocol=protocol,owner=owner,token=token,**n.identity(),phase='audible-bgm-remix'),f)
    except FileExistsError:reason='Concurrent foreign lease preserved'
    else:
     owned=token;reason=n.busy(token)
     if reason is None:break
     if read(n.LEASE).get('token')==token:n.LEASE.unlink()
     owned=None
   if reason!=last:print(json.dumps(dict(wait=reason,modelStarted=False)),flush=True);last=reason
   if time.monotonic()>=deadline:raise TimeoutError(reason)
   time.sleep(20)
  print(json.dumps(build(a.project,base)),flush=True)
 finally:
  if owned and n.LEASE.exists()and read(n.LEASE).get('token')==owned:n.LEASE.unlink()
  if worker.handle is not None:worker.close()
if __name__=='__main__':main()

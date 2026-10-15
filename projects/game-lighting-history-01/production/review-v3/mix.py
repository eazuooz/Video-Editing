"""Retain v2 final PCM outside the selected RNM replacement and its quiet joins."""
import pathlib,json,hashlib,subprocess,shutil,runpy,re
import numpy as np,soundfile as sf
from scipy.signal import resample_poly
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;O=P/'production/local/review-v3';B=P/'production/local/continuity-v2';FF=shutil.which('ffmpeg')
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def rms(a):
 a=a.mean(axis=1) if a.ndim==2 else a;w=19200;hop=4800;lo=np.arange(0,max(1,len(a)-w+1),hop);hi=np.minimum(lo+w,len(a));c=np.r_[0,np.cumsum(a.astype('float64')**2)];return 10*np.log10(np.maximum((c[hi]-c[lo])/(hi-lo),1e-12)),lo,hi
def main():
 runpy.run_path(str(H.parent/'beginner-revision-v1/production-authority.py'))['require_selected_production']()
 assert not (O/'mix-execution.json').exists();plan=rd(O/'plan.json');rows={r['key']:r for r in rd(O/'alignment-proposal.json')['rows']};assert rd(O/'source-review.json')['fullTextAndEdgesReviewed']
 count=plan['newExplanationFrames']*800;newVoice=np.zeros((count,2),dtype='float32');gains=[]
 def run(label,args):
  with (O/(label+'.log')).open('w') as log:subprocess.run([FF,'-v','info','-nostdin','-n',*args],cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 def measure(label,path):
  run(label,['-i',str(path),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']);return json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}',(O/(label+'.log')).read_text())[-1])
 for v in plan['voice']:
  if v['key'] not in rows:continue
  row=rows[v['key']];data,sr=sf.read(R/v['path'],dtype='float32');assert sr==24000;data=data[v['sourceStartSample']:v['sourceStartSample']+v['samples']];assert len(data)==v['samples'];data=resample_poly(data,2,1)
  db,lo,hi=rms(data);mask=np.zeros(len(data),dtype='int8')
  for c in row['koCues']:mask[round(c['seconds'][0]*48000):round(c['seconds'][1]*48000)]=1
  cs=np.r_[0,np.cumsum(mask)];active=(cs[hi]-cs[lo])/(hi-lo)>=.5;median=float(np.median(db[active]));gain=-20.1-median;processed=data*10**(gain/20)
  src=O/(v['key']+'-voice-gain.wav');dst=O/(v['key']+'-voice.wav');sf.write(src,processed,48000,subtype='FLOAT')
  run(v['key']+'-peak-limit',['-i',str(src),'-af',f'alimiter=limit=0.70:attack=5:release=50:level=false:latency=true,apad=whole_len={len(processed)},atrim=end_sample={len(processed)}','-c:a','pcm_f32le',str(dst)])
  processed,rate=sf.read(dst,dtype='float32');assert rate==48000 and len(processed)==len(data)
  after,_,_=rms(processed);assert abs(float(np.median(after[active]))-(-20.1))<3
  offset=(v['startFrame']-64119)*800;newVoice[offset:offset+len(processed)]=np.repeat(processed[:,None],2,axis=1)
  gains.append(dict(key=v['key'],sourceMedianDbfs=median,gainDb=gain,processedMedianDbfs=float(np.median(after[active])),sourceToProcessedLocalGainMinDb=float(np.min((after-db)[active])),speechActiveWindows=int(active.sum()),sourceLowSpeechWindows=int(((db<median-6)&active).sum()),contextListening='pending',timeStretch=False))
 # Reuse the exact licensed background stem recovered in v2, separated before
 # its constant final gain. It contains no narration or invented game effects.
 start=64119*800
 with sf.SoundFile(B/'premix-current.wav') as p,sf.SoundFile(B/'narration-current.wav') as v:
  p.seek(start);v.seek(start);background=p.read(count,dtype='float32',always_2d=True)-v.read(count,dtype='float32',always_2d=True)
 finalGain=10**(rd(B/'mix-execution.json')['constantFinalGainDb']/20)
 background*=finalGain
 def oldbg(frame,n):
  with sf.SoundFile(B/'premix-current.wav') as p,sf.SoundFile(B/'narration-current.wav') as v:
   p.seek(round(frame*800));v.seek(round(frame*800));return (p.read(n,dtype='float32',always_2d=True)-v.read(n,dtype='float32',always_2d=True))*finalGain
 joinN=9600;fade=np.linspace(0,1,joinN,dtype='float32')[:,None]

 # New speech drives only the background gain; narration is never sidechained.
 db,lo,hi=rms(newVoice);env=np.interp(np.arange(count),lo,np.where(db>-45,.7079458,1)).astype('float32');background*=env[:,None]
 bgpath=O/'replacement-background.wav';sf.write(bgpath,background,48000,subtype='FLOAT');bgmeasure=measure('replacement-background-level',bgpath)
 if float(bgmeasure['input_i'])>-30:background*=10**((-31-float(bgmeasure['input_i']))/20)
 background[:joinN]=oldbg(64119,joinN)*(1-fade)+background[:joinN]*fade
 background[-joinN:]=background[-joinN:]*(1-fade)+oldbg(65953-joinN/800,joinN)*fade
 block=newVoice+background;sf.write(O/'replacement-premix.wav',block,48000,subtype='FLOAT')
 run('replacement-peak-limit',['-i',str(O/'replacement-premix.wav'),'-af',f'alimiter=limit=0.72:attack=5:release=50:level=false:latency=true,apad=whole_len={count},atrim=end_sample={count}','-c:a','pcm_s24le',str(O/'replacement-final.wav')]);block,sr=sf.read(O/'replacement-final.wav',dtype='float32',always_2d=True)
 sf.write(O/'replacement-voice.wav',newVoice,48000,subtype='PCM_24')
 # PCM remains identical outside the deliberately replaced narration interval.
 retained=[]
 with sf.SoundFile(B/'final-mix.wav') as old,sf.SoundFile(B/'narration-current.wav') as voice,sf.SoundFile(O/'final-mix.wav','x',samplerate=48000,channels=2,subtype='PCM_24') as out,sf.SoundFile(O/'narration-current.wav','x',samplerate=48000,channels=2,subtype='PCM_24') as stem:
  for part in plan['audioSplices']:
   if part['kind']=='new':out.write(block);stem.write(newVoice);continue
   lo,hi=part['oldStartFrame']*800,part['oldEndFrame']*800;old.seek(lo);voice.seek(lo);h=hashlib.sha256()
   for at in range(lo,hi,480000):
    n=min(480000,hi-at);data=old.read(n,dtype='int32',always_2d=True)
    if part['oldStartFrame']==67924 and at==lo:
     repaired=data.astype('float64')/2147483648
     repaired[:joinN]+=(oldbg(66973,joinN)-oldbg(67924,joinN))*(1-fade)
     out.write(repaired);h.update(data[joinN:].tobytes())
    else:out.write(data);h.update(data.tobytes())
    v=voice.read(n,dtype='float32',always_2d=True);stem.write(v*finalGain)
   retained.append(dict(**part,pcmInt32Sha256=h.hexdigest(),samples=hi-lo,hashExcludesFirstSamples=joinN if part['oldStartFrame']==67924 else 0))
 assert sf.info(O/'final-mix.wav').frames==plan['frames']*800
 run('encode-aac',['-i',str(O/'final-mix.wav'),'-c:a','aac','-b:a','192k','-ar','48000',str(O/'final-mix.m4a')])
 loud=measure('encoded-loudness',O/'final-mix.m4a');assert float(loud['input_tp'])<=-1.5,loud
 wr(O/'mix-execution.json',dict(status='complete-awaiting-current-mixed-ASR',currentWav='final-mix.wav',outputs={f:sha(O/f) for f in ['final-mix.wav','final-mix.m4a','narration-current.wav']},currentAac='final-mix.m4a',loudness=loud,gains=gains,retainedPcm=retained,replacedSpeechKeys=list(rows),backgroundSource='v2 premix minus processed narration; same licensed Nimbus track',backgroundDucking='new voice -> background only',backgroundOnlyCrossfades=dict(durationSeconds=.2,joins=[64119,64119+plan['newExplanationFrames'],64119+plan['newExplanationFrames']+1020],narrationFades=False),humanListening='pending'))
 print(loud)
if __name__=='__main__':main()

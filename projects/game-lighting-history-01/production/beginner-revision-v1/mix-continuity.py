"""Patch only changed narration into the recovered stem; retain background rights.

Final mix uses one constant gain and peak-only limiting, avoiding dynamic
loudness normalization that previously caused local speech attenuation.
"""
import pathlib,json,hashlib,datetime,runpy,subprocess,shutil,re,math
import numpy as np,soundfile as sf
from scipy.signal import resample_poly
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;B=P/'production/local/beginner-revision-v1';O=P/'production/local/continuity-v2';FF=shutil.which('ffmpeg')
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def rms(a,sr):
 w=round(.4*sr);hop=round(.1*sr);x=np.arange(0,max(1,len(a)-w+1),hop);z=np.minimum(x+w,len(a));c=np.r_[0,np.cumsum(a.astype(np.float64)**2)];return x,z,10*np.log10(np.maximum((c[z]-c[x])/(z-x),1e-12))
def main():
 runpy.run_path(str(H/'production-authority.py'))['require_selected_production']()
 assert not (O/'mix-execution.json').exists(),'Preserve completed/current mixes.'
 plan=rd(O/'plan.json');assert plan['finalTimingApproved'];base=rd(B/'plan.json');a=rd(O/'alignment-proposal.json');assert rd(O/'source-review.json')['fullTextAndEdgesReviewed']
 changed={r['key']:r for r in a['rows']};vs={v['key']:v for v in plan['voice']};old={v['key']:v for v in base['voice']};levels=rd(B/'mixed-level-review-current.json');sources=rd(B/'speech-level-review.json')
 state=dict(status='running',startedAt=now(),planSha256=sha(O/'plan.json'),steps=[],sourcePcmPreserved=True,humanListening='pending',backgroundSource='Exact recovered premix minus exact recovered processed narration; same approved Nimbus content.',backgroundTrackChanged=False,sourceAudioUsed=False)
 def save():wr(O/'mix-execution.json',state)
 def run(label,args):
  log=O/(label+'.log');cmd=[FF,'-hide_banner','-nostdin','-n','-threads','2',*args]
  with log.open('w',encoding='utf8') as f:r=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  state['steps'].append(dict(label=label,exitCode=r.returncode));save();assert r.returncode==0,label
  return log.read_text(encoding='utf8')
 def measure(label,p):return json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}',run(label,['-i',str(p),'-af','loudnorm=I=-16.5:TP=-2:LRA=11:print_format=json','-f','null','-']))[-1])
 save();patches=[];clear=[];gainrows=[]
 for key,r in changed.items():
  wav=R/r['audioPath'];assert sha(wav)==r['audioSha256'];raw,sr=sf.read(wav,dtype='float32');assert sr==24000
  asrpath=wav.parent.parent/'asr'/f"{r['id']}.json";asr=rd(asrpath);mask=np.zeros(len(raw),dtype=np.int8)
  intervals=[]
  for w in asr['words']:
   lo,hi=w['timestamp']
   if lo is not None and hi is not None and hi>lo:mask[round(lo*sr):min(len(raw),round(hi*sr))]=1;intervals.append([lo,hi])
  starts,ends,db=rms(raw,sr);c=np.r_[0,np.cumsum(mask)];coverage=(c[ends]-c[starts])/(ends-starts);speech=db[coverage>=.5];median=float(np.median(speech));target=levels['rows'][key]['processedVoice']['speechMedianDbfs'];gain=target-median
  data=resample_poly(raw,2,1).astype('float32')*10**(gain/20);peak=float(np.max(np.abs(data)));limited=False
  if peak>.707945784:
   folder=O/'processed-chunks';folder.mkdir(exist_ok=True);src=folder/f'{key}-gain-float.wav';dst=folder/f'{key}.wav'
   assert not src.exists() and not dst.exists();sf.write(src,data,48000,subtype='FLOAT')
   run('peak-limit-'+key,['-i',str(src),'-af',f'alimiter=limit=0.707945784:attack=5:release=50:level=false:latency=true,apad=whole_len={len(data)},atrim=end_sample={len(data)}','-ar','48000','-c:a','pcm_f32le',str(dst)])
   data,rate=sf.read(dst,dtype='float32');assert rate==48000 and len(data)==len(raw)*2;limited=True
  _,_,postlevels=rms(data,48000);postmedian=float(np.median(postlevels[coverage>=.5]));assert abs(postmedian-target)<3,(key,postmedian,target)
  peak=float(np.max(np.abs(data)));assert peak<.79
  data=np.repeat(data[:,None],2,axis=1);v=vs[key];patches.append(dict(key=key,start=v['targetStartSample']*2,data=data))
  ov=old[key];clear.append((ov['targetStartSample']*2,(ov['targetStartSample']+ov['samples'])*2))
  runs=[]
  for i in np.flatnonzero((coverage>=.5)&(db<median-6)):
   if runs and i==runs[-1][-1]+1:runs[-1].append(int(i))
   else:runs.append([int(i)])
  lows=[dict(sourceSeconds=[v[0]*.1,v[-1]*.1+.4],minimumDbfs=float(min(db[v])),contextListening='pending',origin='source-PCM-before-mix') for v in runs if (v[-1]-v[0])*.1+.4>=.5]
  sources['rows'][key]=dict(samples=len(raw),asrPath=asrpath.relative_to(R).as_posix(),asrSha256=sha(asrpath),speechIntervals=intervals,speechWindowCoverage=np.round(coverage,3).tolist(),allRmsDbfs=np.round(db,3).tolist(),speechMedianDbfs=median,sourceLowRuns=lows,sourcePeakDbfs=float(20*np.log10(max(np.max(np.abs(raw)),1e-12))))
  gainrows.append(dict(key=key,sourceMedianDbfs=median,targetProcessedMedianDbfs=target,actualProcessedMedianDbfs=postmedian,gainDb=gain,peakOnlyLimiter=limited,processedPeakDbfs=20*np.log10(peak),timeStretch=False))
 moved=[m['key'] for m in plan['continuity']['retainedPcmMoves']]
 with sf.SoundFile(B/'narration-local-corrected.wav') as f:
  for key in moved:
   ov=old[key];v=vs[key];f.seek(ov['targetStartSample']*2);data=f.read(ov['samples']*2,dtype='float32',always_2d=True)
   patches.append(dict(key=key,start=v['targetStartSample']*2,data=data));clear.append((ov['targetStartSample']*2,(ov['targetStartSample']+ov['samples'])*2))
 total=plan['frames']*800
 with sf.SoundFile(B/'narration-local-corrected.wav') as voice,sf.SoundFile(B/'premix-local-corrected.wav') as pre,sf.SoundFile(O/'narration-current.wav','x',samplerate=48000,channels=2,subtype='PCM_24') as out,sf.SoundFile(O/'premix-current.wav','x',samplerate=48000,channels=2,subtype='PCM_24') as pm:
  assert voice.frames==pre.frames==total and voice.samplerate==pre.samplerate==48000
  for start in range(0,total,48000*10):
   size=min(48000*10,total-start);oldvoice=voice.read(size,dtype='float32',always_2d=True);oldpre=pre.read(size,dtype='float32',always_2d=True);new=oldvoice.copy()
   for lo,hi in clear:
    l,h=max(lo,start),min(hi,start+size)
    if h>l:new[l-start:h-start]=0
   for p in patches:
    lo=p['start'];hi=lo+len(p['data']);l,h=max(lo,start),min(hi,start+size)
    if h>l:new[l-start:h-start]+=p['data'][l-lo:h-lo]
   # The existing voice-driven quiet music envelope is retained. New speech
   # only uses short adjacent pauses; acoustic review checks the new balance.
   out.write(new);pm.write(oldpre+(new-oldvoice))
 sources.update(planSha256=sha(O/'plan.json'),currentRevision='continuity-v2',sourceLowRunsForChanged='Measured separately in current level review; not automatically passed.',humanContextListening='pending');wr(O/'speech-level-review.json',sources)
 state.update(changedGains=gainrows,retainedProcessedPcmMoves=moved,currentProcessedVoice='narration-current.wav');save()
 m=measure('premix-loudness',O/'premix-current.wav');gain=-16.5-float(m['input_i']);state['constantFinalGainDb']=gain;state['premixLoudness']=m;save()
 filt=f'volume={gain:.8f}dB,alimiter=limit=0.7762471166:attack=5:release=50:level=false:latency=true,aresample=48000,apad=whole_len={total},atrim=end_sample={total}'
 run('final-constant-gain',['-i',str(O/'premix-current.wav'),'-af',filt,'-ar','48000','-ac','2','-c:a','pcm_s24le',str(O/'final-mix.wav')])
 assert sf.info(O/'final-mix.wav').frames==total
 run('final-aac',['-i',str(O/'final-mix.wav'),'-c:a','aac','-b:a','192k','-ar','48000',str(O/'final-mix.m4a')])
 run('decode-final-aac',['-i',str(O/'final-mix.m4a'),'-c:a','pcm_f32le',str(O/'final-aac-decoded.wav')])
 loud=measure('final-loudness',O/'final-mix.m4a');assert -18<=float(loud['input_i'])<=-14 and float(loud['input_tp'])<=-1.5,loud
 state.update(status='complete-awaiting-current-mixed-ASR',exitCode=0,endedAt=now(),currentWav='final-mix.wav',currentAac='final-mix.m4a',currentDecodedAac='final-aac-decoded.wav',outputs={n:sha(O/n) for n in ['final-mix.wav','final-mix.m4a','narration-current.wav']},loudness=loud,finalMixedAsrApproved=False)
 save();print(json.dumps(dict(status=state['status'],loudness=loud,gain=gain)))
if __name__=='__main__':main()

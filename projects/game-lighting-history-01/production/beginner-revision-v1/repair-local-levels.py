"""Correct six measured, processing-introduced speech dips; retain source PCM."""
import pathlib,json,hashlib,datetime,subprocess,os,re
import numpy as np,soundfile as sf,psutil
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/beginner-revision-v1'
FF='C:/Users/eazuo/miniconda3/envs/renderformer/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 assert rd(P/'production/checkpoint.json')['beginnerRevision']['privateUploadAuthorized']
 assert not (O/'local-level-repair.json').exists()
 plan=rd(O/'plan.json');review=rd(O/'mixed-level-review.json');src=rd(O/'speech-level-review.json');mix=rd(O/'mix-execution.json');assert mix['exitCode']==0
 # A reduction in gain alone includes intentional peak compression. Also
 # require actual processed speech below its median and formerly normal input.
 dips=[]
 for key,row in review['rows'].items():
  a=np.array(row['editGain']['allRmsDbfs']);b=np.array(row['processedVoice']['allRmsDbfs']);cv=np.array(src['rows'][key]['speechWindowCoverage']);delta=b-a;mid=np.median(delta[cv>=.5]);ix=np.flatnonzero((cv>=.5)&(b<row['processedVoice']['speechMedianDbfs']-6)&(a>-32)&(delta<mid-6));runs=[]
  for i in ix:
   if runs and i==runs[-1][-1]+1:runs[-1].append(int(i))
   else:runs.append([int(i)])
  for run in runs:
   if (run[-1]-run[0])*.1+.4>=.5:dips.append(dict(key=key,utteranceSeconds=[run[0]*.1,run[-1]*.1+.4],gainDb=4,fadeSeconds=.35,reason='Actual processed voice below median by6dB for>=0.5s; corresponding edit-copy speech above median-6dB, processing gain reduction>=6dB.'))
 assert [d['key'] for d in dips]==['03-p7','g32','x29','08-p9','09b-p9','10-p5']
 state=dict(startedAt=now(),status='running',pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),cpuThreads=2,gpuJobs=0,planSha256=sha(O/'plan.json'),priorMix=mix,dips=dips,steps=[],humanContextListening='pending',sourcePcmChanged=False)
 def save():wr(O/'local-level-repair.json',state)
 def run(label,args):
  cmd=[FF,'-hide_banner','-nostdin','-n','-threads','2',*args];log=O/(label+'.log');state['active']=dict(label=label,command=cmd,log=log.relative_to(R).as_posix());save()
  with log.open('w') as f:
   child=subprocess.Popen(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);state['active']['pid']=child.pid;save();rc=child.wait()
  state['steps'].append(dict(label=label,exitCode=rc));save();assert rc==0
  return log.read_text()
 def loud(label,path):return json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}',run(label,['-i',str(path),'-af','loudnorm=I=-16:TP=-2:LRA=11:print_format=json','-f','null','-']))[-1])
 save()
 try:
  voice,sr=sf.read(O/'narration-normalized.wav',dtype='float32',always_2d=True);premix,sr2=sf.read(O/'premix.wav',dtype='float32',always_2d=True);assert sr==sr2==48000 and voice.shape==premix.shape
  old=voice.copy()
  for d in dips:
   pieces=[v for v in plan['voice'] if v['key']==d['key']];assert len(pieces)==1
   v=pieces[0];a,z=d['utteranceSeconds'];origin=v['targetStartSample']/24000;fade=d['fadeSeconds'];start=max(origin,origin+a-fade);end=min(origin+v['samples']/24000,origin+z+fade);lo,hi=round(start*sr),round(end*sr);t=np.arange(lo,hi)/sr-origin
   ramp=np.minimum(np.clip((t-(a-fade))/fade,0,1),np.clip(((z+fade)-t)/fade,0,1));gain=10**(d['gainDb']*ramp/20)
   voice[lo:hi]*=gain[:,None];d['timelineSeconds']=[start,end]
  premix += voice-old
  sf.write(O/'narration-local-corrected.wav',voice,sr,subtype='PCM_24');sf.write(O/'premix-local-corrected.wav',premix,sr,subtype='PCM_24');del voice,old,premix
  measured=loud('local-final-measure',O/'premix-local-corrected.wav')
  filt=f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:offset={measured['target_offset']}:linear=true,volume=-0.5dB,aresample=48000,atrim=end_sample={plan['frames']*800}"
  run('local-final-normalize',['-i',str(O/'premix-local-corrected.wav'),'-af',filt,'-ar','48000','-ac','2','-c:a','pcm_s24le',str(O/'final-mix-local-corrected.wav')])
  info=sf.info(O/'final-mix-local-corrected.wav');assert info.samplerate==48000 and info.frames==plan['frames']*800
  run('local-final-aac',['-i',str(O/'final-mix-local-corrected.wav'),'-c:a','aac','-b:a','192k','-ar','48000',str(O/'final-mix-local-corrected.m4a')])
  result=loud('local-final-loudness',O/'final-mix-local-corrected.m4a');assert -18<=float(result['input_i'])<=-14 and float(result['input_tp'])<=-1.5,result
  run('local-decode-aac',['-i',str(O/'final-mix-local-corrected.m4a'),'-c:a','pcm_f32le',str(O/'final-aac-local-corrected-decoded.wav')])
  state.update(status='complete-awaiting-level-rereview',exitCode=0,endedAt=now(),active=None,loudness=result,outputs={n:sha(O/n) for n in ['narration-local-corrected.wav','final-mix-local-corrected.wav','final-mix-local-corrected.m4a']});save()
  mix.update(currentWav='final-mix-local-corrected.wav',currentAac='final-mix-local-corrected.m4a',currentProcessedVoice='narration-local-corrected.wav',currentDecodedAac='final-aac-local-corrected-decoded.wav',loudness=result,outputs=state['outputs'],localLevelRepair='local-level-repair.json',finalMixedAsrApproved=False)
  wr(O/'mix-execution.json',mix);print(json.dumps(dict(status=state['status'],dips=len(dips),loudness=result)))
 except BaseException as e:state.update(status='failed',error=repr(e),endedAt=now());save();raise
if __name__=='__main__':main()

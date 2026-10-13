"""Single measured mix. Preserve original/guide samples before processing."""
import pathlib,json,hashlib,datetime,subprocess,os,sys,re
import numpy as np,soundfile as sf,psutil
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-01';O=P/'production/local/final-edit-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 assert rd(P/'production/checkpoint.json')['publishingAuthorization']['privateUploadForMobileReview']
 assert not (O/'mix-execution.json').exists(),'Inspect current mix; do not restart completed processing.'
 plan=rd(O/'plan.json');assert plan['finalTimingApproved']
 state=dict(status='running',startedAt=now(),pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),cpuThreads=2,gpuJobs=0,planSha256=sh(O/'plan.json'),steps=[])
 wr(O/'mix-execution.json',state)
 def run(label,args):
  log=O/(label+'.log');cmd=[FF,'-hide_banner','-nostdin','-n','-threads','2',*args]
  with log.open('w',encoding='utf8') as f:rc=subprocess.call(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  state['steps'].append(dict(label=label,command=cmd,exitCode=rc,log=log.relative_to(R).as_posix()));wr(O/'mix-execution.json',state)
  assert rc==0,(label,rc)
  return log.read_text(encoding='utf8')
 try:
  # FLAC24 preserves the24-bit integer input; normalized WAV is a separate file.
  narration=np.zeros(plan['frames']*400,dtype=np.int32);checks=[];cache={}
  for v in plan['voice']:
   if v['path'] not in cache:cache[v['path']]=sf.read(R/v['path'],dtype='int32')
   data,sr=cache[v['path']];assert sr==24000 and data.ndim==1
   a=v['sourceStartSample'];z=a+v['samples'];t=v['targetStartSample']
   narration[t:t+v['samples']]=data[a:z]
   assert np.array_equal(narration[t:t+v['samples']],data[a:z])
   checks.append(dict(key=v['key'],kind=v['kind'],samples=v['samples'],sha256=hashlib.sha256(data[a:z].tobytes()).hexdigest(),exactPremixSampleCopy=True))
  sf.write(O/'placed-narration.wav',narration,24000,subtype='PCM_32');del narration,cache
  wr(O/'pcm-placement.json',dict(planSha256=sh(O/'plan.json'),originalSamples=plan['original108SamplesPreserved'],placements=checks,allExact=True))
  def norm(label,src,dst,target,tp):
   report=run(label+'-measure',['-i',str(src),'-af',f'loudnorm=I={target}:TP={tp}:LRA=11:print_format=json','-f','null','-'])
   m=json.loads(re.findall(r'\{\s*"input_i"[\s\S]*?\}',report)[-1])
   filt=f"loudnorm=I={target}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=json"
   run(label+'-normalize',['-i',str(src),'-af',filt,'-ar','48000','-ac','2','-c:a','pcm_s24le',str(dst)])
   return m
  narrationMeasure=norm('narration',O/'placed-narration.wav',O/'narration-normalized.wav',-16,-3)
  music=R/rd(P/'project.json')['audio']['backgroundMusic']['file'];assert sh(music)=='36a0c40b73e7dc656470c242cce0047bd987abc595f28b013265d947a10d98ef'
  musicMeasure=norm('music',music,O/'music-normalized.wav',-31,-5)
  bgm,sr=sf.read(O/'music-normalized.wav',dtype='float32');assert sr==48000
  total=plan['frames']*800;xf=sr;track=np.zeros((total,2),dtype=np.float32);step=len(bgm)-xf
  ramp=np.linspace(0,1,xf,dtype=np.float32)[:,None]
  for at in range(0,total,step):
   count=min(len(bgm),total-at);part=bgm[:count].copy()
   if at:part[:min(xf,count)]*=ramp[:min(xf,count)]
   if at+len(bgm)<total:part[-xf:]*=1-ramp
   track[at:at+count]+=part
  fade=round(.45*sr);track[-fade:]*=np.linspace(1,0,fade,dtype=np.float32)[:,None]
  sf.write(O/'music-continuous.wav',track,sr,subtype='PCM_24');del bgm,track
  run('premix',['-i',str(O/'narration-normalized.wav'),'-i',str(O/'music-continuous.wav'),'-filter_complex_threads','2','-filter_complex','[0:a]asplit=2[n][side];[1:a][side]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=400:makeup=1[b];[n][b]amix=inputs=2:duration=first:normalize=0[out]','-map','[out]','-ar','48000','-c:a','pcm_s24le',str(O/'premix.wav')])
  finalMeasure=norm('final',O/'premix.wav',O/'final-mix.wav',-16,-1.5)
  run('aac',['-i',str(O/'final-mix.wav'),'-c:a','aac','-b:a','192k','-ar','48000',str(O/'final-mix.m4a')])
  measured=run('final-loudness',['-i',str(O/'final-mix.m4a'),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
  m=json.loads(re.findall(r'\{\s*"input_i"[\s\S]*?\}',measured)[-1]);assert -17<=float(m['input_i'])<=-15 and float(m['input_tp'])<=-1
  state.update(status='complete-awaiting-current-mixed-ASR',endedAt=now(),exitCode=0,outputs={x:sh(O/x) for x in ['final-mix.wav','final-mix.m4a']},loudness=m,sourceAudioUsed=False,sourceAudioReason='Acquired source tracks mix third-party presentation narration/music; current approved source contract excludes them. No clean effects stem was fabricated.',musicOriginalFileAcquisition='pending-browser-security-policy-block',humanListening='pending',finalMixedAsrApproved=False)
  wr(O/'mix-execution.json',state)
 except BaseException as e:
  state.update(status='failed',error=repr(e),endedAt=now());wr(O/'mix-execution.json',state);raise
if __name__=='__main__':main()

"""Resume only final normalization/encode after loudnorm sample-rate trim bug."""
import pathlib,json,hashlib,datetime,subprocess,os,re
import soundfile as sf,psutil
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/beginner-revision-v1'
FF='C:/Users/eazuo/miniconda3/envs/renderformer/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 assert rd(P/'production/checkpoint.json')['beginnerRevision']['privateUploadAuthorized']
 assert not (O/'local-mix-tail-resume.json').exists()
 plan=rd(O/'plan.json');mix=rd(O/'mix-execution.json');bad=sf.info(O/mix['currentWav']);assert bad.frames==plan['frames']*200 and bad.samplerate==48000
 state=dict(startedAt=now(),status='running',pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),cpuThreads=2,gpuJobs=0,reason='loudnorm dynamically resamples to192k; old atrim end_sample intended for48k truncated atonequarter. Explicit aresample=48000 before trim. Retain full voice/premix and previous measurement.',badOutputPreserved=mix['currentWav'],steps=[])
 def save():wr(O/'local-mix-tail-resume.json',state)
 def run(label,args):
  cmd=[FF,'-hide_banner','-nostdin','-n','-threads','2',*args];log=O/(label+'.log');state['active']=dict(label=label,command=cmd,log=log.relative_to(R).as_posix());save()
  with log.open('w') as f:
   ch=subprocess.Popen(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);state['active']['pid']=ch.pid;save();rc=ch.wait()
  state['steps'].append(dict(label=label,exitCode=rc));save();assert rc==0
  return log.read_text()
 save()
 try:
  measured=json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}',(O/'local-final-measure.log').read_text())[-1])
  filt=f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:offset={measured['target_offset']}:linear=true,volume=-0.5dB,aresample=48000,atrim=end_sample={plan['frames']*800}"
  wav=O/'final-mix-current.wav';aac=O/'final-mix-current.m4a'
  run('current-final-normalize',['-i',str(O/'premix-local-corrected.wav'),'-af',filt,'-ar','48000','-ac','2','-c:a','pcm_s24le',str(wav)])
  info=sf.info(wav);assert info.frames==plan['frames']*800 and info.samplerate==48000
  run('current-final-aac',['-i',str(wav),'-c:a','aac','-b:a','192k','-ar','48000',str(aac)])
  result=json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}',run('current-final-loudness',['-i',str(aac),'-af','loudnorm=I=-16:TP=-2:LRA=11:print_format=json','-f','null','-']))[-1]);assert -18<=float(result['input_i'])<=-14 and float(result['input_tp'])<=-1.5,result
  decoded=O/'final-aac-current-decoded.wav';run('current-decode-aac',['-i',str(aac),'-ar','48000','-c:a','pcm_f32le',str(decoded)])
  di=sf.info(decoded);assert 0<=di.frames-info.frames<1024
  state.update(status='complete-awaiting-level-rereview',exitCode=0,endedAt=now(),active=None,loudness=result,wavSamples=info.frames,aacDecodedSamples=di.frames,outputs={n.name:sha(n) for n in [wav,aac]});save()
  mix.update(currentWav=wav.name,currentAac=aac.name,currentDecodedAac=decoded.name,loudness=result,outputs=state['outputs'],localMixTailResume='local-mix-tail-resume.json',finalMixedAsrApproved=False);wr(O/'mix-execution.json',mix);print(json.dumps(dict(status=state['status'],wavSamples=info.frames,loudness=result)))
 except BaseException as e:state.update(status='failed',error=repr(e),endedAt=now());save();raise
if __name__=='__main__':main()

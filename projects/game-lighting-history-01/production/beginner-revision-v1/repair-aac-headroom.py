"""Keep the completed mix, lower only its final master by0.5dB for AAC peak margin."""
import pathlib,json,hashlib,subprocess,datetime,os,re,psutil
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/beginner-revision-v1'
FF='C:/Users/eazuo/miniconda3/envs/renderformer/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 assert rd(P/'production/checkpoint.json')['beginnerRevision']['privateUploadAuthorized']
 prior=rd(O/'mix-execution.json');assert prior['status']=='failed' and prior['steps'][-1]['label']=='final-loudness'
 assert not psutil.pid_exists(prior['pid']) or psutil.Process(prior['pid']).create_time()!=prior['createTime']
 assert not (O/'mix-execution-first-failure.json').exists();wr(O/'mix-execution-first-failure.json',prior)
 plan=rd(O/'plan.json');state={**prior,'status':'running-peak-repair','priorExecution':'mix-execution-first-failure.json','pid':os.getpid(),'createTime':psutil.Process().create_time(),'command':psutil.Process().cmdline(),'repairStartedAt':now(),'repairReason':'AAC true peak -1.19dBTP exceeded -1.5 while integrated loudness -16.06 was valid. Preserve normalization/mix; final constant -0.5dB and exact ending sample trim only.','retainedPremasterSha256':sha(O/'final-mix.wav')}
 def save():wr(O/'mix-execution.json',state)
 def run(label,args):
  cmd=[FF,'-hide_banner','-nostdin','-n','-threads','2',*args];log=O/(label+'.log');state['active']=dict(label=label,command=cmd,log=log.relative_to(R).as_posix());save()
  with log.open('w') as f:ch=subprocess.Popen(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);state['active']['pid']=ch.pid;save();rc=ch.wait()
  state['steps'].append(dict(label=label,command=cmd,exitCode=rc,log=log.relative_to(R).as_posix()));save();assert rc==0;return log.read_text()
 try:
  run('peak-safe-wav',['-i',str(O/'final-mix.wav'),'-af',f"volume=-0.5dB,atrim=end_sample={plan['frames']*800}",'-c:a','pcm_s24le',str(O/'final-mix-peak-safe.wav')])
  run('peak-safe-aac',['-i',str(O/'final-mix-peak-safe.wav'),'-c:a','aac','-b:a','192k','-ar','48000',str(O/'final-mix-peak-safe.m4a')])
  txt=run('peak-safe-loudness',['-i',str(O/'final-mix-peak-safe.m4a'),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']);m=json.loads(re.findall(r'\{\s*"input_i"[\s\S]*?\}',txt)[-1]);assert -17<=float(m['input_i'])<=-15 and float(m['input_tp'])<=-1.5,m
  run('decode-aac-diagnostic',['-i',str(O/'final-mix-peak-safe.m4a'),'-ar','48000','-c:a','pcm_f32le',str(O/'final-aac-decoded.wav')])
  state.update(status='complete-awaiting-current-mixed-ASR',endedAt=now(),exitCode=0,active=None,error=None,outputs={n:sha(O/n) for n in ['final-mix-peak-safe.wav','final-mix-peak-safe.m4a']},currentWav='final-mix-peak-safe.wav',currentAac='final-mix-peak-safe.m4a',loudness=m,finalMixedAsrApproved=False,humanListening='pending',sourceAudioUsed=False,sourceAudioReason='Source recordings contain inseparable presenter narration/music; previous source-audio exclusions retained.',originalMusicAcquisition='pending',constantFinalGainDb=-.5);save()
 except BaseException as e:state.update(status='failed',error=repr(e),endedAt=now());save();raise
if __name__=='__main__':main()

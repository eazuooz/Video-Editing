"""One finite continuation: wait for this TTS identity, then current source ASR.

This is not a recurring task and does not generate another video. It never
resumes TTS, touches a foreign lease, starts Unity, or advances past source ASR.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys,time
import psutil
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v6_voice_render',H/'voice-render.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
def main():
 selected=v.read(v.R/'shared/publishing/video-production-control.json')
 assert selected['selectedVideo']==v.P.name and selected['newProductionAuthorization']['fullProductionAuthorized']
 initial=v.read(v.O/'tts-execution.json');identity=initial['coordinator'];token=initial['token'];me=psutil.Process()
 record=dict(scope='One finite current TTS→sourceASR continuation only',ttsCoordinator=identity,ttsLeaseToken=token,
  coordinator=dict(pid=me.pid,createTime=me.create_time()),startedAt=time.time(),status='waiting-current-tts')
 receipt=v.O/'voice-continuation.json';v.save(receipt,record)
 while True:
  v.selected()
  try:owner=psutil.Process(identity['pid']);same=abs(owner.create_time()-identity['createTime'])<.02 and owner.is_running()
  except psutil.NoSuchProcess:same=False
  if not same:break
  time.sleep(5)
 final=v.read(v.O/'tts-execution.json');assert final['token']==token and final['status']=='complete' and final['returnCode']==0,'TTS failed; preserve completed PCM and do not start another stage'
 v.validate();assert not v.LEASE.exists(),'Existing lease must remain untouched; no ASR concurrency'
 current=v.read(v.R/'shared/publishing/video-production-control.json')
 assert current['selectedVideo']==v.P.name and current['newProductionAuthorization']['fullProductionAuthorized']
 record.update(status='starting-authorized-current-source-asr',ttsCompletedAt=final['endedAt']);v.save(receipt,record)
 with (v.O/'voice-continuation-asr-parent.log').open('ab') as log:
  child=subprocess.Popen([sys.executable,'-u','-X','utf8',str(H/'voice-review.py'),'--gpu-approved'],cwd=v.R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  record.update(asrParentPid=child.pid);v.save(receipt,record);code=child.wait()
 record.update(status='source-asr-complete-direct-review-pending' if code==0 else 'source-asr-failed',asrReturnCode=code,endedAt=time.time());v.save(receipt,record)
 assert code==0,'Inspect source ASR logs; no automatic retry'
 print('Current41-sourceASR complete. Stop before alignment/Unity until actual full-text direct review.',flush=True)
if __name__=='__main__':main()

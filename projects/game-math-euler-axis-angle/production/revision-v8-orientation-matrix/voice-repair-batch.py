"""Finite two-candidate m07L02 repair slot with a bounded manual selection gap."""
from pathlib import Path
import argparse,importlib.util,json,subprocess,sys,time,uuid
import psutil
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_repair_batch_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
def main():
 p=argparse.ArgumentParser();p.add_argument('--gpu-approved',action='store_true');p.add_argument('--alias-only',action='store_true');x=p.parse_args();assert x.gpu_approved
 plan=c.validate();selection=c.read(H/'voice-retake-input.json');assert len(selection['paragraphs'])==1 and selection['paragraphs'][0]['scene']=='m07'and selection['paragraphs'][0]['line']==2
 assert selection['sourceReceiptSha256']==c.sha(c.O/'tts-current.json');assert not c.LEASE.exists(),'Preserve existing finite GPU lease'
 before=c.wait_memory(plan['resources']['tts']['minimumFreeMiB']);me=psutil.Process();token=str(uuid.uuid4());state=dict(project=c.P.name,revision='orientation-matrix-v8',token=token,
  coordinator=dict(pid=me.pid,createTime=me.create_time()),purpose='One m07L02 1/2=0.5 pronunciation-alias candidate→ASR→selection→changedsceneASR'if x.alias_only else'm07L02 at most2 complete-paragraph QA candidates→candidateASR→manualselection→onechangedsceneASR',
  state='running',startedAt=time.time(),gpuBefore=before,retakeInputSha256=c.sha(H/'voice-retake-input.json'),sourceReceiptSha256=selection['sourceReceiptSha256'],foreignProcessesChanged=False,phases=[])
 with c.LEASE.open('x',encoding='utf8')as f:json.dump(state,f)
 child=None;success=False
 def phase(name,script,*args):
  nonlocal child
  c.validate();entry=dict(name=name,implementationSha256=c.sha(H/script),startedAt=time.time());state['state']=name;state['phases'].append(entry);c.save(c.LEASE,state)
  with(c.O/(name+'-worker.log')).open('ab')as log:
   child=subprocess.Popen([sys.executable,'-u','-X','utf8',str(H/script),'--worker',token,*args],cwd=c.R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
   entry['workerPid']=child.pid;c.save(c.O/'repair-execution.json',state);entry['returnCode']=child.wait();entry['endedAt']=time.time();c.save(c.O/'repair-execution.json',state)
  assert entry['returnCode']==0,'Preserve outputs and inspect actual finite repair failure'
 try:
  phase('alias-tts'if x.alias_only else'repair-tts','voice-alias-render.py'if x.alias_only else'voice-retake.py')
  phase('alias-candidate-asr'if x.alias_only else'repair-candidate-asr','voice-repair-asr.py','--mode','alias'if x.alias_only else'candidates')
  state['state']='awaiting-manual-candidate-selection-models-unloaded';state['selectionDeadline']=time.time()+600;c.save(c.LEASE,state);c.save(c.O/'repair-execution.json',state)
  while not(c.O/'repair-selection.json').exists():
   assert time.time()<state['selectionDeadline'],'Finite manual-selection window expired; candidates preserved';c.selected();time.sleep(2)
  chosen=c.read(c.O/'repair-selection.json');assert chosen['token']==token and chosen['selectedCandidate']and chosen['sourceReceiptSha256']==c.sha(c.O/'tts-current.json')
  phase('repair-changed-scene-asr','voice-repair-asr.py','--mode','current');success=True
 finally:
  live=child is not None and child.poll()is None;state.update(state='complete'if success else'owned-worker-still-running'if live else'failed',endedAt=time.time());c.save(c.O/'repair-execution.json',state)
  if c.LEASE.exists()and c.read(c.LEASE).get('token')==token:
   if live:c.save(c.LEASE,state)
   else:c.LEASE.unlink()
if __name__=='__main__':main()

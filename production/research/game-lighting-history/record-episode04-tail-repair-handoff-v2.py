"""Save actual lease/session identities without asserting synthesized output."""
from pathlib import Path
import datetime,hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3];lease=ROOT/'shared/output/GPU_HANDOFF.json'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def live(i):
 try:
  p=psutil.Process(i['pid'])
  return abs(p.create_time()-i['createTime'])<.01 and p.cmdline()==i['command']
 except psutil.NoSuchProcess:return False
def main():
 h=read(lease)
 if h['project']!='game-lighting-history-04' or 'render-episode04-additive-tail-repair-v2.py' not in ' '.join(h['ttsCommand']):raise RuntimeError('Own exact scoped handoff required')
 if not live(h['coordinator']):raise RuntimeError('Lease coordinator identity not live')
 tts_path=ROOT/'projects/game-lighting-history-04/production/additive-tail-repair-execution-v2.json'
 actual=read(tts_path) if tts_path.exists() else None
 event=dict(observedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),session=38924,leaseToken=h['token'],leaseState=h['state'],actualCoordinator=h['coordinator'],coordinatorIdentityLive=True,researchOwner=h['queueOwner'],researchIdentityLive=live(h['queueOwner']),originalResearchJob=h['originalStatus'],actualTtsExecution=actual,ownGpuTtsRunning=h['state']=='tts_running',generationComplete=False,finalApproved=False)
 target=ROOT/'projects/game-lighting-history-04/production/additive-tail-repair-session-v2.json'
 temp=target.with_name(target.name+'.writing-'+str(os.getpid()));temp.write_text(json.dumps(event,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(temp,target)
 checkpoint=ROOT/'production/research/game-lighting-history/checkpoint.json';c=read(checkpoint);c['updatedAt']=event['observedAt'];c['stage']='episode04-scoped-two-tail-repairs-'+h['state'];c['episode04AdditiveNarration']['scopedRepairSession']=event;c['ownedJobsRunning']=[dict(session=38924,kind='cooperative-two-addition-tail-repair',actualCoordinator=h['coordinator'],state=h['state'])];c['ownedGpuJobs']=1 if event['ownGpuTtsRunning'] else 0
 temp=checkpoint.with_name(checkpoint.name+'.writing-'+str(os.getpid()));temp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(temp,checkpoint)
 print(json.dumps(dict(session=38924,state=h['state'],coordinator=h['coordinator']['pid'],ownGpuRunning=event['ownGpuTtsRunning'],ttsExecutionCreated=actual is not None)))
if __name__=='__main__':main()

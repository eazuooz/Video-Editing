from pathlib import Path
import datetime,hashlib,json,os,psutil
R=Path(__file__).resolve().parents[3]
def read(p):return json.loads(p.read_text('utf-8-sig'))
leasePath=R/'shared/output/GPU_HANDOFF.json'
lease=read(leasePath)
if lease['project']!='game-lighting-history-04' or 'render-physical-framing-v49.py' not in ' '.join(lease['ttsCommand']):raise RuntimeError('Preserve foreign lease')
identity=lease['coordinator'];proc=psutil.Process(identity['pid'])
if abs(proc.create_time()-identity['createTime'])>=.01:raise RuntimeError('Process identity changed')
record=dict(observedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),session=49437,state=lease['state'],token=lease['token'],coordinator=identity,coordinatorAlive=True,ttsCommand=lease['ttsCommand'],originalResearchOwner=lease['queueOwner'],originalResearchJob=lease['originalStatus']['job'],leaseHistory='shared/output/gpu-handoff/'+lease['token']+'.json',trainingInterrupted=False,ttsGenerationStarted=lease['state']=='tts_running',original111Regenerated=False,researchRestoreOwnedByCoordinator=True,next='Complete source action/cross-game comparison and scene preparation while current sealed research boundary is pending.')
p=R/'projects/game-lighting-history-04/production/physical-framing-handoff-observation-v49.json'
p.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=R/'production/research/game-lighting-history/checkpoint.json';j=read(cp)
j.update(updatedAt=record['observedAt'],episode04PhysicalFramingHandoffV49={**record,'record':str(p.relative_to(R)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},ownedActiveWork=dict(type='cooperative-research-boundary-and-native-review',session=49437,coordinatorPid=identity['pid'],coordinatorCreateTime=identity['createTime'],command=identity['command'],ownedCpuMediaWorkersRunning=0,ownedGpuWorkersRunning=0,state=lease['state'],next=record['next']))
tmp=cp.with_name(cp.name+'.writing-'+str(os.getpid()));tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,cp)
print(json.dumps({k:record[k] for k in ['session','state','coordinatorAlive','ttsGenerationStarted','originalResearchJob']}))

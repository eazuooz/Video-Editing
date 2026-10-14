from pathlib import Path
import hashlib,json,datetime,psutil
ROOT=Path(__file__).resolve().parents[3]
read=lambda p:json.loads((ROOT/p).read_text('utf-8-sig'))
history='shared/output/gpu-handoff/fe3d2438-816a-4afa-8ef7-8319ed1a3dfa.json'
h=read(history);assert h['project']=='game-lighting-history-04' and h['ttsExitCode']==1 and h['state']=='research_resume_verified'
target=ROOT/'projects/game-lighting-history-04/production/physical-framing-preflight-stop-v50.json'
assert not target.exists()
owner=h['resumedQueue']
try:
 p=psutil.Process(owner['pid']);live=abs(p.create_time()-owner['createTime'])<.01;command=p.cmdline() if live else None
except psutil.NoSuchProcess:live=False;command=None
foreign=read('shared/output/GPU_HANDOFF.json')
assert foreign['project']!='game-lighting-history-04' and foreign['state']=='tts_running'
state=dict(schemaVersion=1,observedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='pre-model-current-duplicate-input-change-rejected',history=history,historySha256=hashlib.sha256((ROOT/history).read_bytes()).hexdigest(),actualTtsExitCode=1,executionStateCreated=(ROOT/'projects/game-lighting-history-04/production/physical-framing-tts-execution-v49.json').exists(),generationStarted=False,newChunks=0,original111Regenerated=False,completedResearchJob=h['completedJobEvidence'],researchResumeVerified=True,resumeVerificationScope='Own coordinator verified its restored queue at16:27:58. A later foreign TTS coordinator has now normally stopped that queue again; the earlier PID is not presently alive.',resumedQueue=owner,earlierResumedQueueStillAlive=live,currentResumedCommand=command,foreignCurrentGpuLease=foreign['project'],foreignLeaseToken=foreign['token'],next='Directly reread changed inventory and publishing inputs; refresh current distinct evidence. Retry only this unstarted five-paragraph batch through normal cooperative handoff after the current foreign lease. Preserve its original111 PCM and all foreign work.')
target.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=ROOT/'production/research/game-lighting-history/checkpoint.json';c=read(str(cp.relative_to(ROOT)))
c['episode04PhysicalFramingPreflightStopV50']={k:state[k] for k in ['status','generationStarted','newChunks','original111Regenerated','researchResumeVerified','next']};c['episode04PhysicalFramingPreflightStopV50']['record']=str(target.relative_to(ROOT)).replace('\\','/')
c['ownedActiveWork']={'status':'no-active-owned-gpu-or-media-worker','next':state['next']};c['updatedAt']=state['observedAt']
tmp=cp.with_suffix('.v50.tmp');tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(cp)
print(json.dumps({k:state[k] for k in ['status','generationStarted','researchResumeVerified','foreignCurrentGpuLease']}))

"""Snapshot actual running current-AAC worker and completed mix; no worker launch."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,psutil,subprocess
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1';R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'resource-and-annotation-handoff-v23.json';assert not out.exists()
m=read(O/'current34-mix-execution-v2.json');s=read(O/'current34-mixed-whole-asr-execution-v1.json');ss=read(O/'current34-mixed-whole-asr-execution-v1.session.json')
assert m['actualExitObserved'] and m['actualOuterExitCode']==0 and m['workerDead'] and ss['sessionId']==88118
p=psutil.Process(s['pid']);assert abs(p.create_time()-s['createTime'])<.01 and p.cmdline()==s['commandLine'] and p.cwd()==s['cwd'] and p.is_running()
assert s['exitCode'] is None and s['gpuJobs']==0
proof=read(O/'narration-07b-guide-repair-execution-v1.json')
for r in proof['protectedInputs']+proof['results']:assert sha(ROOT/r['path'])==r['sha256']
motion=read(R/'current17-main-promotion-v1.json')
for r in motion['otherProtectedInputs']:assert sha(ROOT/r['path'])==r['sha256']
cim=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','ffmpeg.exe','node.exe') } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],text=True,encoding='utf-8',errors='replace')
research=Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json');rs=read(research)
assert rs['status']=='complete_pending_visual_review' and rs['completed']==rs['total']==1088
assert not psutil.pid_exists(75876) or psutil.Process(75876).create_time()!=1791735347.4583836
at=datetime.now(timezone.utc).isoformat()
data=dict(recordedAt=at,previousHandoff='resource-and-annotation-handoff-v22.json',orientation79ProtectedShaMatched=True,motionOther70ProtectedShaMatched=True,currentWholeWorker=dict(pid=s['pid'],createTime=s['createTime'],commandLine=s['commandLine'],cwd=s['cwd'],sessionId=88118,initialChunk='1eef35',status=s['status'],completed=s['completed'],total=34,currentlyAlive=True,cpuThreads=2,gpuJobs=0),
 orientation=dict(baselineVideoId='6-kP65hrZcI',currentPlan='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/current34-measured-timing-plan-v1.json',bodyFrames=65197,actualFrames=26079,explanationFrames=39118,ratioErrorFrames=.2,totalFrames=65917,seconds=1098.6166666666666,sourceRatioPlanOnly=True,mixExecution='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/current34-mix-execution-v2.json',mixActualSession=30519,mixActualCompletion='3b583f',mixActualExitCode=0,mixWorkerDead=True,all34RawPcmSamplesExactlyPlaced=True,all24BaselineDistributedPcmBytesMatched=True,noBgm=True,noSourceAudio=True,AACIntegratedLufs=-16.06,AACTruePeakDbtp=-2.70,currentMixedAudioApproved=False,tracked02a03b07b10b02aextBoundedReviewsComplete=True,remainingVisuals=['01b projected overview','baseline01/24 depth review/repair','eight baseline actual scenes final narrated tracked guides'],whole34ExpectedComparisonPending=True,independent180Pending=True,finalCaptionsPixelsDeliveryPrivateSettingsGitSchedulePending=True),
 motion=dict(actualVideoId='lXjDBqONLWs',productionSettingsGitScheduleVerified=True,oldVideoId='mBDd9VzSTkA',oldDeleted=False,deletionActionTimeConfirmationPending=True,repeatQuestion=False),
 completedResearch=dict(status=rs['status'],completed=1088,total=1088,pid75876CurrentlyAlive=False,statusSha256=sha(research),restarted=False,visualReviewApproved=False),
 currentResource=dict(cpuLoadPercent=psutil.cpu_percent(interval=2),freePhysicalMemoryKiB=psutil.virtual_memory().available//1024,gpuObservation=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip(),cimActual=cim),researchManipulations=0,newImageGit=0,
 next='Reuse actual whole34 session88118 and exact command/create/state. Observe actual outer exit, close via record-orientation-current34-worker-v1.py --mode whole with actual session/exit/completion; directly compare all34 expected/current full texts. Prepare/review180 complete current AAC paragraphs with exact76 PCM placement boundaries; run one CPU2 context worker only after closure/freshresource. Render pending overview/baseline guides serially, current captions/chapters/end/final pair/pixels/4files/private/settings/Git/actual schedule, then action-time confirmed exact obsolete deletion. Continue actual future slots through normal-transform-UV then pause; no Sakurai6/new lecture.')
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
qp=B/'queue.json';old=qp.read_bytes();q=read(qp);q['latestHandoff']=out.relative_to(ROOT).as_posix();q['updatedAt']=at;assert qp.read_bytes()==old
qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(handoff=out.relative_to(ROOT).as_posix(),whole34Alive=True,pid=s['pid'],completed=s['completed'],mixActualExit=0,protected79=True,researchComplete1088=True)))

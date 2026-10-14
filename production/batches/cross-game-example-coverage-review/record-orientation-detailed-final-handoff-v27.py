"""Record current detailed QA/pair/pixel identity without changing foreign work."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,v):
 t=p.with_name(p.name+'.handoff-writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def identity(s):
 try:
  p=psutil.Process(s['pid']);same=abs(p.create_time()-s['createTime'])<.01
  if same:assert p.cmdline()==s['commandLine'] and p.cwd()==s['cwd']
  alive=same and p.is_running()
 except psutil.NoSuchProcess:alive=False
 cim=subprocess.check_output(['powershell','-NoProfile','-Command',f"Get-CimInstance Win32_Process -Filter 'ProcessId={s['pid']}' | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],text=True,encoding='utf-8',errors='replace')
 return dict(pid=s['pid'],createTime=s['createTime'],commandLine=s['commandLine'],cwd=s['cwd'],sessionId=s['sessionId'],sameIdentityAliveAtObservation=alive,actualCim=cim)
proof=read(O/'narration-07b-guide-repair-execution-v1.json')
for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
reviews=[]
for name,checks in [
 ('current34-overview-direct-review-v5.json',['all110SamplesDirectlyRead','normalPlaybackReviewed']),
 ('current34-detailed-explanations-sampled-direct-review-v1.json',['all605SamplesDirectlyRead','all109BoardsDirectlyRead']),
 ('current34-detailed-explanations-normal-direct-review-v1.json',['all17NormalStartEndObserved']),
 ('current34-baseline-guides-direct-review-v1.json',['all562SamplesDirectlyRead','normalPlaybackEndpointsReviewedAll8']),
 ('current34-mixed-detailed-direct-review-v1.json',['all172SamplesDirectlyRead','all3NormalStartEndObserved'])]:
 p=O/name;s=read(p);assert all(s[k] for k in checks);reviews.append(dict(path=rel(p),sha256=sha(p),verifiedTrueFields=checks))
pairp=O/'current34-final-pair-execution-v3.json';pair=read(pairp)
assert pair['actualOuterExitCode']==0 and pair['workerDead'] and pair['frames']==65917
for x in pair['pair']:assert sha(ROOT/x['path'])==x['sha256'] and x['wholeDecodeExitCode']==0 and x['identicalReviewedWholeAacPackets']
pixelp=O/'current34-pair-pixel-execution-v2.json';pixel=read(pixelp)
pixelid=identity(pixel)
now=datetime.now(timezone.utc).isoformat();out=R/'resource-and-annotation-handoff-v27.json';assert not out.exists()
previous=R/'resource-and-annotation-handoff-v26.json'
data=dict(recordedAt=now,previousHandoff=rel(previous),previousHandoffSha256=sha(previous),currentProject='game-math-orientation-matrices',currentOwnedWorker=dict(state=rel(pixelp),stateSha256AtObservation=sha(pixelp),statusAtObservation=pixel['status'],identity=pixelid,actualOuterExitCode=pixel.get('actualOuterExitCode'),workerDead=pixel.get('workerDead',False)),pair=dict(execution=rel(pairp),executionSha256=sha(pairp),actualSession=pair['actualSession'],actualOuterExitCode=0,actualCompletion=pair['completionChunk'],workerDead=True,frames=65917,seconds=65917/60,allPts1500=True,bothWholeDecode0=True,identicalReviewedAACPackets=True,bodyMeasured=pair['bodyMeasured']),completedDirectReviews=reviews,subjectPolicy='shared/publishing/illustrative-subject-detail-policy.json',subjectPolicySha256=sha(ROOT/'shared/publishing/illustrative-subject-detail-policy.json'),all79ProtectedUnchanged=True,repairCandidateUnchanged=True,newTts=0,newAsr=0,newMix=0,newServer=0,newImageGit=0,researchChanges=0,final244PixelsApproved=False,mainPromotion=False,fourOutputsCollected=False,newUploadId=None,publishingComplete=False,gitDeliveryComplete=False,actualReplacementSchedule=False,obsoleteDeleted=False,stopBoundary='Complete authorized revisions through game-math-normal-transform-uv then pause task and owned continuation; no new lectures or deferred Sakurai6.',next='Reuse actual pixelV2 session/state/command/create and record actual exit. Then read all final244cue/37cut/76PCM/selected detailed moving guide/overview/cat/member absolutePTS samples; actual normal1x playback. Current detailed samples/endpoints are bounded, not every intermediate frame or whole listening. Only after final QA explicitly promote main, collect4files, single private captioned upload/settings/selectiveGit/currentStudio09schedule replacement; corresponding obsolete deletion remains action-time confirmation pending. Do not repeat completed TTS/ASR/mix/detail renders/guide extraction/replays; preserve foreign work.')
save(out,data)
cp=read(O/'latest-checkpoint.json');cp.update(latestHandoff=rel(out));save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';raw=qp.read_bytes();q=read(qp);q['currentOrientationReview']['latestHandoff']=rel(out);assert qp.read_bytes()==raw;save(qp,q)
print(json.dumps(dict(handoff=rel(out),pairActualExit=0,pixelSession=pixel['sessionId'],pixelAlive=pixelid['sameIdentityAliveAtObservation'],protected79=True,finalPixels=False)))

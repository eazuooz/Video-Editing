"""Record current owned rendering and the user's detailed-subject policy."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,subprocess,psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,v):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
out=R/'resource-and-annotation-handoff-v25.json';assert not out.exists()
proof=rd(O/'narration-07b-guide-repair-execution-v1.json')
for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
render=O/'current34-detailed-header-repair-render-execution-v2.json';s=rd(render)
ss=rd(O/'current34-detailed-header-repair-render-execution-v2.session.json')
assert ss['sessionId']==1557 and ss['initialChunk']=='ffbde4'
p=psutil.Process(s['pid']);assert abs(p.create_time()-s['createTime'])<.01 and p.cmdline()==s['commandLine'] and p.cwd()==s['cwd']
cim=subprocess.check_output(['powershell','-NoProfile','-Command',f'Get-CimInstance Win32_Process -Filter "ProcessId={s["pid"]}" | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3'],text=True,encoding='utf-8',errors='replace')
overview=O/'current34-overview-direct-review-v5.json';v=rd(overview)
assert v['all110SamplesDirectlyRead'] and v['normalPlaybackReviewed']
first=O/'current34-detailed-explanation-render-execution-v1.json';f=rd(first)
assert f['actualOuterExitCode']==0 and f['workerDead'] and len(f['scenes'])==17
partial=O/'current34-guides-partial-direct-review-v1.json'
policy=ROOT/'shared/publishing/illustrative-subject-detail-policy.json'
next_steps='Reuse actual1557 header-repair worker; after actual outer exit record closure, inspect all11 corrected baseline scene samples and six preserved V1 revision scene samples/normal playback. Complete remaining guides14/17/20/23 (288samples74boards; normal endpoints already observed). Bind a NEW current34 assembly version to detailed overviewV5, repaired baselineV2 and detailed revisionV1; old generic-subject assembly V1 must not run. Retain18storage and19code as genuine geometric/code subjects. Then244 final cue/cut/moving pixels, technical pairQA, main promotion, fourfiles/private settings/Git/saved schedule replacement. No new TTS/ASR/mix.'
data=dict(recordedAt=now(),previousHandoff=rel(R/'resource-and-annotation-handoff-v24.json'),latestUserEvidence=rd(policy)['userEvidence'],ruleFiles=[dict(path=rel(p),sha256=sha(p)) for p in [ROOT/'AGENTS.md',ROOT/'docs/VIDEO_VISUAL_STYLE.md',ROOT/'docs/VIDEO_WORKFLOW.md',policy]],orientation79ProtectedShaMatched=True,repairCandidateShaMatched=True,
 overview=dict(review=rel(overview),reviewSha256=sha(overview),actualSession=65738,actualCompletion='b7972f',actualClosure='1d4da6',directSamples=110,boards=20,normalEndpoints3=True,scope='Detailed subjects and selected motion; not all intervening frames or final244 captions.'),
 detailed17V1=dict(execution=rel(first),executionSha256=sha(first),actualSession=64072,actualCompletion='3382ed',actualClosure='935b05',actualOuterExitCode=0,workerDead=True,complete17RenderOutputs=True,all17MovingSamplesReviewed=False,headerHeldReview=rel(O/'detailed-header-layout-held-review-v1.json'),directlyReadRepresentatives=['shared/output/unpublished-teaching-clarity-revision/orientation/current34-detailed-explanations-v1/scene-12/frame-015.png','shared/output/unpublished-teaching-clarity-revision/orientation/current34-detailed-explanations-v1/scene-03/frame-005.png'],directlyReadBoards=['shared/output/unpublished-teaching-clarity-revision/orientation/current34-detailed-explanations-v1/scene-12/board-02.png','shared/output/unpublished-teaching-clarity-revision/orientation/current34-detailed-explanations-v1/scene-12/board-03.png']),
 currentOwnedWorker=dict(state=rel(render),sessionId=1557,initialChunk='ffbde4',registration='db7ca8',pid=s['pid'],createTime=s['createTime'],commandLine=s['commandLine'],cwd=s['cwd'],aliveAtObservation=p.is_running(),currentScene=s.get('currentScene'),completedScenes=len(s['scenes']),cimActual=cim,cpuThreads=2,gpuJobs=0),
 partialGuideReview=dict(path=rel(partial),sha256=sha(partial),directScenes=['02','05','08','11'],samples=274,boards=70,remainingScenes=['14','17','20','23'],remainingSamples=288,remainingBoards=74,normalEndpoints8AlreadyObserved=True),
 currentMixedReview=rel(O/'current34-mixed-complete-direct-review-v1.json'),currentCaptionReview=rel(O/'current34-caption-timing-direct-review-v1.json'),currentCaptionCount=244,whole34AndIndependent180Closed=True,currentMixedHumanListeningApproved=False,
 finalAssemblyApproved=False,finalCaptionPixelsApproved=False,mainPromotion=False,newOrientationId=None,newImageGit=0,newTts=0,newAsr=0,newMix=0,researchChanges=0,foreignIndexChanges=0,automation24='ACTIVE',scopeBoundary='Finish authorized revisions through game-math-normal-transform-uv; then pause this task/owned continuation. No new lectures or six Sakurai productions.',next=next_steps)
save(out,data)
cp_path=O/'latest-checkpoint.json';cp=rd(cp_path);cp.update(recordedAt=now(),detailedSubjectPolicy=rel(policy),detailedOverviewReview=rel(overview),detailed17OriginalClosure=rel(first),detailedHeaderRepairState=rel(render),guidePartialReview=rel(partial),latestHandoff=rel(out),detailedExplanationVisualApproved=False);save(cp_path,cp)
qp=B/'queue.json';old=qp.read_bytes();q=rd(qp);q['currentOrientationReview'].update(detailedSubjectPolicy=rel(policy),detailedOverviewReview=rel(overview),detailedHeaderRepairState=rel(render),guidePartialReview=rel(partial),latestHandoff=rel(out));q['updatedAt']=now();assert qp.read_bytes()==old;save(qp,q)
print(json.dumps(dict(recorded=rel(out),ownSession=1557,pid=s['pid'],createTime=s['createTime'],alive=p.is_running(),completedScenes=len(s['scenes']),all79ProtectedUnchanged=True,finalPixels=False)))

"""Seal actual closed execution and bounded directly read navigation pixels."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,os,subprocess,psutil
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).parent;B=ROOT/'projects/limited-color-world/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat();rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()
def save(p,d):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
sp=P/'navigation-targets-execution-v7.json';d=read(sp);assert d['exitCode']==0 and d['totalUniqueSampleCount']==20 and d['totalBoards']==4
try: assert abs(psutil.Process(d['pid']).create_time()-d['createTime'])>.01
except psutil.NoSuchProcess:pass
assert all(c['exitCode']==0 and c['status']=='closed' for c in d['children'])
for field in ['protectedInputs','protectedOriginal8Pcm']:
 assert all(sha(ROOT/p)==h for p,h in d[field].items()),field
for c in d['cuts']:
 for s in c['samples']:
  assert s['pts']==s['nativeFrame']*256 and sha(ROOT/s['path'])==s['sha256'] and sha(ROOT/s['captionTestPath'])==s['captionTestSha256']
 for board in c['boards']:assert sha(ROOT/board['path'])==board['sha256']
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
check=subprocess.run([node,'scripts/review-video-duplicates.cjs','limited-color-world','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8');assert check.returncode==0,check.stdout+check.stderr
d.update(actualExitObserved=True,actualOuterExitCode=0,actualOuterExitToolObservation='aecf24',actualOuterSessionId=45008,status='closed-bounded-direct-pixel-review-complete',allPixelsDirectlyRead=True)
save(sp,d)
session=P/'navigation-targets-execution-v7.session.json';assert not session.exists()
save(session,dict(recordedAt=now(),sessionId=45008,launchTool='16362a',exitTool='aecf24',actualOuterExitCode=0,pid=d['pid'],createTime=d['createTime'],commandLine=d['commandLine'],cwd=d['cwd'],liveCimObservationClaim=False,identityBasis='Worker startup command/cwd/creation plus actual tool completion. Earlier recorder0347d8 saw already closed PID and wrote no session file; no later live observation claimed.',status='closed'))
rp=P/'navigation-targets-direct-review-v7.json';assert not rp.exists()
observations={
 'town-entry-navigation':'First/last boundaries show character moving left/up along the outlined stone path toward the tree. From192.5 turquoise painting also begins; label navigation and painting, not exclusively walking. House/tree outlines and hatch remain visible under the120px upward crop; important route and actor stay above the two-line fixed caption placeholder. No dialogue modal/wipe is visible in the selected samples.',
 'interior-door-navigation':'The first384.0–384.5 samples show the character standing at the doorway. Exclude that stationary lead. Adopt385.0–386.0 only: the actor moves up/left between outlined shelves and tables toward the NPC; ColaQ interaction bubble appears, but no dialogue modal or wipe is present in reviewed boundaries. Name the interior walk, not entering a door, painting or a raised platform. Important actor and route clear the fixed-caption placeholder.'}
save(rp,dict(schemaVersion=7,slug='limited-color-world',recordedAt=now(),execution=rel(sp),executionSha256=sha(sp),session=rel(session),actualExitTool='aecf24',actualOuterExitCode=0,all20SamplesAnd4BoardsDirectlyRead=True,allHashesAndNativePtsVerified=True,boards=[b for c in d['cuts'] for b in c['boards']],observations=observations,acceptedBoundedIntervals=[dict(key='town-entry-navigation',startFrame=11400,endFrameExclusive=11580),dict(key='interior-outline-walk',startFrame=23100,endFrameExclusive=23160)],excludedStationaryLead=[23040,23100],boundedNativeAndPlaceholderFramingApproved=True,wholeContinuousNativeViewingApproved=False,finalTrackedAnnotationReviewApproved=False,finalCueUiApproved=False,publicRightsApproved=False,researchManipulated=False,gitImagesOrMediaAdded=0))
old=P/'source-action-bank-v2.json';bank=copy.deepcopy(read(old));dest=P/'source-action-bank-v3.json';assert not dest.exists();sources={x['sourceKey']:x for x in bank['sources']}
for c in d['cuts']:
 key=c['key'];a,b=(11400,11580) if key=='town-entry-navigation' else (23100,23160);label='町の道:輪郭をたどって移動・塗る' if key=='town-entry-navigation' else '室内:家具の境界の間を移動'
 label='마을: 윤곽을 따라 이동하고 칠하기' if key=='town-entry-navigation' else '실내: 가구의 경계 사이로 이동'
 bank['windows'].append(dict(key=key if key=='town-entry-navigation' else 'interior-outline-walk',sourceKey=c['source'],sourceSha256=sources[c['source']]['sourceSha256'],startFrame=a,endFrameExclusive=b,startPts=a*256,endPtsExclusive=b*256,timeBase='1/15360',frameRate='60/1',durationSeconds=(b-a)/60,framingUpPixels=120,sameFrameBottomBlurPixels=120,boundaryDirectReviewApproved=True,placeholderFramingSampleReviewApproved=True,normalSourcePlaybackBasis='Verified native60fps/absolutePTS; selected boundary/interior pixels read. Continuous final playback pending.',provisionalInsertion='generic-outline-navigation',visibleAction=observations[key],viewerFocus=label,diagramConnection='A generic outline/foreground navigation statement only; not a house-specific pattern or platform-height claim.',observation=observations[key],onScreenObjectLabel=label,normalPlaybackRate=1,loop=False,slowdown=False,sourceAudioUse=False,selectedForNarrationPlanning=True,finalUseDurationSeconds=None,allFinalCueUiApproved=False,finalTrackedAnnotationReviewApproved=False,allContinuousFramesReviewed=False))
for sk in sources:
 intervals=sorted((x['startFrame'],x['endFrameExclusive']) for x in bank['windows'] if x['sourceKey']==sk)
 assert all(a[1]<=b[0] for a,b in zip(intervals,intervals[1:]))
total=sum(x['endFrameExclusive']-x['startFrame'] for x in bank['windows']);assert total==8715
bank.update(schemaVersion=3,recordedAt=now(),status='bounded-33-window-source-bank-before-measured-allocation',baselineBank=dict(path=rel(old),sha256=sha(old)),maximumUniqueSeconds=total/60,maximumUniqueNativeFrames=total,currentDistinctCheck=dict(exitCode=0,stdout=check.stdout),adoptionScope='31 preserved plus4s of two newly reviewed navigation windows. Bounded native/placeholder planning only; all current user clarity/flow/annotation and final media gates remain pending.',sourceAdoptionApproved=True,finalSourceAllocationApproved=False,actualBodyRatioApproved=False,allFinalPixelsApproved=False,wholeContinuousViewingOrListeningApproved=False)
bank['proofs'].append(dict(path=rel(rp),sha256=sha(rp)));bank['exclusions'].append('Native384–385 stationary doorway lead excluded; only385–386 interior navigation may enter actual allocation.')
save(dest,bank);candidate=ROOT/'projects/limited-color-world/sources/game-candidates-v3.json';assert not candidate.exists();save(candidate,bank)
cp=read(B/'latest-checkpoint.json');cp.update(recordedAt=now(),stage='current11voice-and-bounded33window-bank-ready-clarity-flow-annotation-planning',sourceBankV3=rel(dest),sourceBankV3Sha256=sha(dest),maximumUniqueActionSeconds=total/60,ownedJob={**cp['ownedJob'],'sessionId':45008,'actualOuterExitCode':0,'actualExitTool':'aecf24','workerExpectedRunning':False},nextAction='Apply latest user overview/coherent-flow/Sakurai-comparison/first-time-gameplay/tracked-math-highlight requirements. Preserve11PCM, reviewed ASR and bank history. Measured allocation and final mixed/pixels/QA/collection/upload remain pending.')
save(B/'latest-checkpoint.json',cp)
print(json.dumps(dict(review=rel(rp),bank=rel(dest),sha256=sha(dest),windows=33,maximumUniqueSeconds=total/60,finalApproval=False)))

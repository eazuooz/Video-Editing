"""Closed finalV5 delivery handoff;verify78 protected inputs after intentional promotion."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'));rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,v):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
out=R/'resource-and-annotation-handoff-v29.json';assert not out.exists()
promotion=rd(O/'current34-main-promotion-v1.json')
assert sha(ROOT/promotion['currentMain']['path'])==promotion['currentMain']['sha256']
assert sha(ROOT/promotion['baselineMain']['path'])==promotion['baselineMain']['sha256']
for f in promotion['otherProtectedInputs']+promotion['repairCandidates']:assert sha(ROOT/f['path'])==f['sha256']
owned=[]
for p in psutil.process_iter(['pid','name','cmdline']):
 try:
  cmd=' '.join(p.info['cmdline'] or [])
  if (p.info['name'] or '').lower() in ('python.exe','node.exe','ffmpeg.exe') and p.pid!=os.getpid() and 'cross-game-example-coverage-review' in cmd and any(t in cmd for t in ['render-orientation','review-orientation','extract-orientation','build-orientation','assemble-orientation','collect-orientation','render-motion','review-motion','extract-motion']):owned.append(p.pid)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
assert not owned
research=Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json')
assert sha(research)=='bbeac85c5f493baec614eeb5fae13f15d8b9b913f58631dce2d2ee211f07b0b8'
files=['current34-final-pair-execution-v5.json','current34-pair-pixel-execution-v4.json',
       'current34-final-v5-pixels-partial-direct-review-v1.json','current34-final-normal-direct-review-v5.json',
       'current34-final-technical-and-pixel-direct-review-v5.json','current34-main-promotion-v1.json',
       'current34-four-output-collection-verification-v1.json','current34-output-collection-execution-v1.json',
       'current-studio-baseline-readonly-v1.json','publishing/youtube-upload-v1.json']
data=dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),stage='orientation-current34-finalV5-delivery-closed-private-upload-next',
 actualPairSession=91761,pairCompletion='55be94',pairClosure='6683f7',pairWorkerDead=True,
 actualPixelSession=15422,pixelCompletion='2d67ba',pixelClosure='26a83b',pixelWorkerDead=True,
 newFinalPixelsDirectlyRead=118,newFinalBoardsDirectlyRead=30,inheritedExactPriorPixels=3052,totalSelectedFinalPixels=3170,
 currentFinalNormalTab='115',normalStart=.146694,normalEnd=1098.616667,normalRate=1,normalMuted=True,normalStartEndActuallyObserved=True,normalReplayRequired=False,
 finalTechnicalQaPassed=True,final244SelectedCuePixelsReviewed=True,finalRatioApproved=True,
 ratio=dict(bodyFrames=65197,actualFrames=26078,explanationFrames=39119,errorFrames=-.8,contract='legacylecture40actual60ex/noBGM'),
 mainIntentionallyPromoted=True,originalMainExactBackup=True,other78ProtectedInputsUnchanged=True,repairCandidateUnchanged=True,
 doNotRunOld79IncludingMainGuard=True,postPromotionGuard=rel(O/'current34-main-promotion-v1.json'),
 actualCollectionSession=43370,collectionCompletion='2021fb',collectionClosure='6987d0',collectorWorkerDead=True,fourOutputsVerified=True,
 sharedRebuildIndexBytesPreserved=True,foreignRebuildsPreserved=63,activeOwnedWorkers=0,
 newPrivateUploadStarted=False,newActualVideoId=None,settingsVerified=False,gitDelivered=False,scheduleReplacementVerified=False,obsoleteDeleted=False,
 baselineVideoId='6-kP65hrZcI',baselineActualStudioTab='116',baselineActualSchedule='2026-10-13 09:00 GMT+0900',baselineChanged=False,
 motionCompletedVideoId='lXjDBqONLWs',motionOldDelete=dict(videoId='mBDd9VzSTkA',questionAskedOnce=True,answerReceived=False,deletePerformed=False),
 detailedSubjectRuleReaffirmed=True,newTts=0,newAsr=0,newMix=0,newRenderRequired=False,newImageGit=0,researchChanged=False,
 humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,
 boundRecords=[dict(path=rel(O/f),sha256=sha(O/f)) for f in files],
 next='Use existingStudio116 baseline readonly and one reviewed captioned output selection privately;recordactualID;manualKOEN/localizedEN/card/memberend/possible settings/CCoff1080p60/save-reopen;selectiveGit;currentStudio09slot savedreopen replacement. Only then correspondingobsolete deletion with required action-time confirmation. Preserve priorpendingmBDd question;no repeat.',
 continuationBoundary='RemainACTIVE through normal-transform-UV final3D delivery and actualschedule replacement;then pause taskownedcontinuation. No newlectures/Sakurai6.')
save(out,data)
for cp_path in [O/'latest-checkpoint.json',R/'latest-checkpoint.json']:
 cp=rd(cp_path);cp.update(recordedAt=data['recordedAt'],latestHandoff=rel(out))
 if cp_path.parent==O:cp.update(next=data['next'],postPromotionGuard=data['postPromotionGuard'],doNotRunOld79IncludingMainGuard=True)
 save(cp_path,cp)
qp=B/'queue.json';raw=qp.read_bytes();q=rd(qp);q['currentOrientationReview'].update(latestHandoff=rel(out),postPromotionGuard=data['postPromotionGuard'],doNotRunOld79IncludingMainGuard=True,next=data['next']);q['updatedAt']=data['recordedAt'];assert qp.read_bytes()==raw;save(qp,q)
print(json.dumps(dict(handoff=rel(out),activeOwnedWorkers=0,protectedOthers=78,fourOutputsVerified=True,researchUnchanged=True,newUploadStarted=False)))

"""Seal new lighting04-3 full content review and actual CUA observations."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
inv=read(ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json');old=read(R/'duplicate-before-refresh-v10.json')
before={x['path']:x['sha256'] for x in old['inputFiles']};changed=[x for x in inv['inputFiles'] if before.get(x['path'])!=x['sha256']]
assert len(changed)==5 and len(inv['existingProjects'])==88 and len(inv['inputFiles'])==506
assert all(x['path'].startswith('projects/game-lighting-history-04-3/') for x in changed)
for x in changed:assert sha(ROOT/x['path'])==x['sha256']
receipt=read(ROOT/'projects/game-lighting-history-04-3/publishing/youtube-upload.json')
assert receipt['actualVideoId']=='ydW9Glmh0nM'
proof=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),previousReview='duplicate-content-and-studio-direct-review-v9.json',previousReviewSha256=sha(R/'duplicate-content-and-studio-direct-review-v9.json'),inventoryDigest=inv['inputsDigest'],inventoryProjectCount=88,inventoryInputCount=506,changedInputs=changed,allChangedContentsReviewed=True,
 fullReadEvidence=['c3f32d manifest and README whole; receipt final tail','13-chapter/caption missing middle recovered by separate KO36..48 read','EN0..39 and40..end whole narration reads','receipt first200, second200, final tail reads recover first truncated combined receipt'],
 findings=['Lighting04-3 teaches reconstruction/display generation, exposure/tone mapping, focus and actual RenderDoc/resource inspection. Its four-game surface comparisons differ from motion camera/aim/input/locomotion choices. Entire independent KO/EN scenes and claims compared.',
 'Lighting receipt describes completed private delivery and unscheduled physical-series order. This duplicate audit does not independently approve its pixels, whole listening, rights or GPU restoration.',
 'CUA97 actual whole Korean title/description directly matches prepared receipt. SD and HD complete; Save disabled; current private state. No foreign settings/file mutation.',
 'CUA98 current motion full title/description read. SD/HD complete and Save disabled. Actual visibility modal has Private selected and schedule collapsed. Current private state supersedes historical October12 reservation; no saved future schedule asserted and no privacy/date changed. Historical original09KST slot retained as planning reference only.'],
 studioWholeReads=[dict(videoId='ydW9Glmh0nM',actualTab=97,title=receipt['titleKo'],descriptionKo=receipt['descriptionKo'],descriptionSha256=hashlib.sha256(receipt['descriptionKo'].encode()).hexdigest(),wholeDescriptionCompared=True,privacy='private',sdHdComplete=True,saveDisabled=True,actualObservations='CUA AX and readonly contenteditable text; no external write'),dict(videoId='mBDd9VzSTkA',actualTab=98,title='게임 멀미와 카메라 설계: 화면 움직임을 선택하게 만들기',wholeDescriptionRead=True,privacy='private',privateRadioSelected=True,scheduleCollapsed=True,sdHdComplete=True,saveDisabled=True,currentSavedFutureScheduleVerified=False)],
 verdict='distinct',currentDuplicateCheckPassed=False,foreignQualityOrRightsApproved=False,foreignFileOrPlatformMutations=0)
out=R/'duplicate-content-and-studio-direct-review-v10.json';assert not out.exists();save(out,proof)
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=proof['reviewedAt'],currentDuplicateReview=out.name,currentDuplicateCheckPassed=False,currentBaselineStudioPrivacy='private',currentBaselineScheduleVerified=False,historicalOriginalSchedulePreserved=True);save(R/'latest-checkpoint.json',cp)
print(json.dumps(dict(changed=5,projects=88,inputs=506,currentMotionPrivate=True,currentCheckRequired=True)))

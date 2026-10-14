"""Seal actual full content comparisons and read-only current Studio evidence."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'duplicate-content-and-studio-direct-review-v7.json'
assert not out.exists()
partial=read(R/'duplicate-content-partial-direct-review-v8.json')
reviewed={x['path']:x['reviewedSha256'] for x in partial['completeReviewedInputs']}
reviewed.update({x['path']:x['sha256'] for x in partial['remainingWholeContentReads']})
reviewed['projects/game-math-quaternion-calculations-v3/project.json']='714805b438ed2c02291a3670d327947c504eb8ef7e1983989fa84c5eb3b606a9'
report=read(ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json')
baseline={x['path']:x['sha256'] for x in read(R/'duplicate-before-refresh-v6.json')['inputFiles']}
changed=[x for x in report['inputFiles'] if baseline.get(x['path'])!=x['sha256']]
assert len(changed)==24
for item in changed:
    assert reviewed.get(item['path'])==item['sha256'],item['path']
    assert sha(ROOT/item['path'])==item['sha256'],item['path']
studio=[]
for p in sorted(R.glob('current-studio-*-whole-v7.json')):
    item=read(p)
    assert item['wholeTitleExactlyMatchesReceipt'] and item['wholeDescriptionExactlyMatchesReceipt'],p
    assert item['scheduled'] and item['sd'] and item['hd'] and item['saveDisabled'],p
    studio.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),
        slug=item['slug'],videoId=item['id'],wholeDescriptionChars=len(item['description']),observedAt=item['observedAt']))
assert len(studio)==9
deleted=R/'current-studio-historical-polygon-deleted-v7.ax.txt'
assert '업로더가 삭제한 동영상입니다.' in deleted.read_text('utf-8')
proof=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),
    previousReview=partial['previousPartialReview'],partialReview=partial['previousPartialReview'],
    inventoryDigest=report['inputsDigest'],inventoryProjectCount=len(report['existingProjects']),
    inventoryInputCount=len(report['inputFiles']),changedInputs=changed,
    completeReviewedInputs=[dict(path=x['path'],sha256=x['sha256'],wholeContentReviewed=True) for x in changed],
    contentReadMethod='Full bilingual scripts/manifests/plans were directly read in bounded outputs. All changed receipt properties were read. Exact equal subtrees and exact description-body plus footer repetitions reference the fully read camera-projection receipt; no truncation counts as completion.',
    additionalReadOutputs=['da43dc','f8380d','69871f','93fc9b','862250','96c702','7a3e5a','bc414f','97e72c','11d8a0','a41cf0'],
    studioWholeReads=studio,historicalDeletionRead=dict(path=deleted.relative_to(ROOT).as_posix(),sha256=sha(deleted),deletionPerformedByThisTask=False),
    findings=[
      'Camera frustum concerns viewport/pixel aspect/FOV versus dolly/clipping/orthographic mapping; camera-projection follows local/world/camera/clip/divide/viewport coordinate stages. Motion concerns input/aim/view/locomotion choices and reversible settings, not these renderer calculations.',
      'Depth and w, normal construction and inverse-transpose/UV addressing, and radiometry/rendering equation have separate viewer questions and chapter claims. Shared game buildings and fixed captions do not make them duplicate episodes.',
      'Centers and partition are the explicitly split replacement of old triangulation. Centroid/incenter/circumcenter and boundary tests precede fan versus ear clipping and validity/quality. They are not motion-camera option design. Current nine Studio descriptions exactly match the whole currently read receipts; no foreign settings changed.',
      'Foundations teaches imaginary/complex representation, axis/half-angle, norm, q/-q and inverse. Calculations teaches ordered Hamilton composition, current-target delta, endpoint angle and two-sided vector rotation. Whole new bilingual additions compare Riders Republic, Trailmakers, Space Engineers and Besiege and are not a motion or comfort tutorial.',
      'The newer calculations manifest adds prepared publishing description chapters and current local refined-v3 master review. Its new actual ID remains null/private-upload pending. Reading those records does not independently approve foreign pixels, audio or rights.',
      'Old polygon ID L7SXFwn4i2k is already deleted; the receipt has historical retained/pending wording alongside its later authoritative deletion record. Actual watch message agrees. No deletion is repeated.',
      'The baseline motion receipt nests KO metadata under metadata.ko. The earlier generic flat-field comparison returned false; corrected comparison against the actual nested fields is exact. This was a review-helper schema correction, not a platform metadata change.'
    ],verdict='distinct',allChangedContentsReviewed=True,currentWholeStudioReviewComplete=True,
    currentDuplicateCheckPassed=False,foreignCompletionOrRightsApproved=False,
    foreignFileOrPlatformMutations=0,newVoiceRequestStarted=False,newPcmCount=0)
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(path=out.relative_to(ROOT).as_posix(),changedInputs=len(changed),studioWholeReads=len(studio),digest=report['inputsDigest'],distinctContentDecision=True,currentCheckStillRequired=True)))

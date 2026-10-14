"""Seal five new whole content reads and two current read-only Studio pages."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'duplicate-content-and-studio-direct-review-v8.json'
assert not out.exists()
report=read(ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json')
old=read(R/'duplicate-before-refresh-v8.json')
hashes={x['path']:x['sha256'] for x in old['inputFiles']}
changed=[x for x in report['inputFiles'] if hashes.get(x['path'])!=x['sha256']]
assert len(changed)==5 and len(report['existingProjects'])==87 and len(report['inputFiles'])==499
for row in changed:assert sha(ROOT/row['path'])==row['sha256'],row['path']
studio=[]
for part in ['foundations','calculations']:
    slug=f'game-math-quaternion-{part}-v3'
    p=R/f'current-studio-{part}-v3-whole-v8.json';ui=read(p)
    manifest=read(ROOT/f'projects/{slug}/project.json')
    description=ROOT/manifest['paths']['publishingKo']
    assert ui['title']==manifest['titles']['ko']
    assert ui['description'].strip()==description.read_text('utf-8-sig').strip()
    assert '비공개' in ui['ax'] and '표준 화질 완료' in ui['ax'] and '고화질 완료' in ui['ax']
    assert 'button (disabled) 저장' in ui['ax']
    studio.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),videoId=ui['videoId'],
        title=ui['title'],observedAt=ui['observedAt'],wholeDescriptionCompared=True,
        preparedDescriptionPath=description.relative_to(ROOT).as_posix(),preparedDescriptionSha256=sha(description),
        private=True,sdHd=True,saveDisabled=True,platformMutations=0))
proof=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),
    previousReview='duplicate-content-and-studio-direct-review-v7.json',previousReviewSha256=sha(R/'duplicate-content-and-studio-direct-review-v7.json'),
    inventoryDigest=report['inputsDigest'],inventoryProjectCount=87,inventoryInputCount=499,
    changedInputs=changed,allChangedContentsReviewed=True,fullReadChunks=['23f0b6','09af34','06674a','53dd55','2231e6'],
    fullNewScripts=dict(scenesEachLanguage=8,paragraphsEachLanguage=21),
    studioWholeReads=studio,currentWholeStudioReviewComplete=True,
    findings=[
        'New interpolation additions separate an explicitly defined SLERP orientation path from linear or squared time progression. Aircraft body and wing directions motivate two-vector orientation checks, matrix columns, orthonormality and reflection determinant checks. Eight full bilingual scenes/21 paragraphs per language are different from motion input/aim/locomotion design and reversible comfort options.',
        'Changed quaternion manifests now contain actual private uploads wreXZkEtLqA and Rck2eL8VtqM with prepared source-link exceptions and settings records. Whole current Studio titles/descriptions exactly match the prepared descriptions. Both are private with SD/HD and disabled Save; foundations had platform review pending, calculations showed dash. This does not approve foreign completion, pixels or rights.',
        'The previously read full quaternion narration and broader inventory remain unchanged in this recorded diff. No new motion PCM or voice request was made.'
    ],verdict='distinct',currentDuplicateCheckPassed=False,foreignQualityOrRightsApproved=False,
    foreignFileOrPlatformMutations=0,newVoiceRequestStarted=False,newPcmCount=0)
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(changedInputs=5,projects=87,inputs=499,digest=report['inputsDigest'],currentCheckStillRequired=True)))

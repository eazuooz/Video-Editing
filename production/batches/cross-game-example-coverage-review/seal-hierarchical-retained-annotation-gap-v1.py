"""A bounded new-policy annotation audit; historical technical QA remains preserved."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os

ROOT=Path(__file__).resolve().parents[3]
H=ROOT/'projects/hierarchical-game-outlines'
V=H/'revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=V/'retained-gameplay-annotation-gap-audit-v1.json';assert not out.exists()
idx_path=H/'production/visual-depth-v1/encoded-pixels-local/index.json';idx=read(idx_path)
plan=read(H/'production/final-v1/plan.json');samples=[s for b in idx['boards'] for s in b['frames']]
guard=read(V/'baseline-preservation-v1.json')
master_guard=[r for r in guard['protectedInputs'] if r['sha256']==idx['videoSha256']]
assert len(master_guard)==1
selected=[]
for sc in plan['scenes']:
    if sc['classification']!='actual':continue
    sample=min([s for s in samples if sc['startFrame']<=s['frame']<sc['startFrame']+sc['frames']],
        key=lambda s:abs(s['frame']-(sc['startFrame']+sc['frames']/2)))
    assert sha(ROOT/sample['file'])==sample['sha256']
    selected.append(dict(scene=sc['id'],title=sc['title'],sample=sample,fullResolutionDirectlyViewed=True,
        visibleFeatures='Original gameplay/UI, version label and burned bottom caption; native colored rails are source graphics.',
        ownNarratedTrackedAnnotationObserved=False,entireSceneAnnotationAuditApproved=False))
first=next(s for s in samples if s['frame']==328);assert sha(ROOT/first['file'])==first['sha256']
assert len(selected)==6
record=dict(recordedAt=datetime.now(timezone.utc).isoformat(),purpose='New current unpublished on-footage annotation requirement; no historical decode/caption/pair QA repeated.',
    existingPixelIndex=dict(path=idx_path.relative_to(ROOT).as_posix(),sha256=sha(idx_path),masterSha256=idx['videoSha256']),
    matchingProtectedMaster=master_guard[0],representativeSceneSamples=selected,
    additionalScene01Sample=dict(sample=first,fullResolutionDirectlyViewed=True,
        finding='Round ride/queue instruction panel visible without our narrated target/condition marker.'),
    totalBoundedRepresentativeFrames=7,wholeContinuousFramesDirectlyReviewed=False,
    inference='These7representatives evidence missing own target/condition annotations at specific points in all6actual scenes; they do not prove the state of every other frame.',
    originalScriptClaimsPcmAndOrderPreserved=True,existingSilentFilesPreserved=True,
    historicalTechnicalQaInvalidated=False,currentNewPolicyAnnotationApproval=False,
    requiredScope=[
        'Audit every relevant original Museum paragraph/cut against its source object and actual voice/cue timing.',
        'Add editable red target lines/role-colored labelled shape guides only where the target is directly visible; match camera/object screen geometry and hide when occluded or behind important UI.',
        'Distinguish native red/green rails from our overlay. No measured world axes, actual developer outline/engine hierarchy or hidden UI inferred.',
        'Keep original good explanation,12PCM/all60KOEN paragraphs,46native-cut order and original lengths. New annotated variants preserve original files; explanation pieces do not need a remake for this annotation gap.',
        'Preserve fixed captions960/970 and readable gameplay controls/version labels. Any composition change requires new direct encoded pixels; no caption relocation.',
        'Review newly rendered moving annotations/current final cue pixels after measured additions; source inventory/static representatives alone do not approve them.'
    ],newProductionRenderStarted=False,allFourGameTeachingApproved=False,
    next='Finish current additional sourceV2 and new native499point review; write actual-selected causal additions, measured annotation/cut plan and only necessary current variants. Do not rerun completed source QA/pair/TTS solely for this record.')
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
cp_path=V/'latest-checkpoint.json';raw=cp_path.read_bytes();cp=read(cp_path)
cp.update(recordedAt=record['recordedAt'],retainedGameplayAnnotationGapAudit=out.relative_to(ROOT).as_posix(),
    retainedActualSceneAnnotationApproval=False,causalInsertionOutline='projects/hierarchical-game-outlines/revision-teaching-clarity-v1/causal-insertion-outline-preparation-v1.json')
assert cp_path.read_bytes()==raw;cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(dict(boundedNewPolicyRepresentatives=7,retainedActualScenes=6,ownedTrackedAnnotationGap=True,
    historicalTechnicalQaRepeated=False,originalPcmOrderLengthPreserved=True)))

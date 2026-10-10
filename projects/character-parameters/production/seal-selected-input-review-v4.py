"""Seal the manually read targeted repair, retaining earlier unchanged review."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
pf=BASE/'selected-input-preflight-v4.json';p=read(pf);old=BASE/'selected-input-direct-review-v3.json';v3=read(old)
notes=BASE/'selected-input-direct-notes-v4.json';n=read(notes);dest=BASE/'selected-input-direct-review-v4.json'
assert not dest.exists(),'Preserve completed seal'
assert v3['allBoardsDirectlyRead'] and v3['allPlannedSamplesDirectlyRead']
assert not n['unresolvedDefects']
assert sorted(b for g in n['groups'] for b in g['boards'])==list(range(1,56))
assert len(p['samples'])==845 and len(p['boards'])==55 and sum(len(b['sampleFrames'])for b in p['boards'])==325
assert p['changedSamples']==325 and p['reusedSamples']==520
assert sha(ROOT/p['previousPreflight'])==p['previousPreflightSha256']
for r in [*p['samples'],*p['boards'],*p['segments']]:assert sha(ROOT/r['path'])==r['sha256'],r['path']
assert all(r['pts']==r['frame']*1500 for r in p['samples'])
assert sha(ROOT/p['bodyPath'])==p['bodySha256']
assert p['wholeBodyDecodeExitCode']==p['extractionExitCode']==0 and p['allBodyPtsVerified'] and p['allSamplePtsVerified']
diagnostic=BASE/'hud-source-diagnostic-direct-review-v4.json'
r=dict(schemaVersion=4,reviewedAt=datetime.now(timezone.utc).isoformat(),preflight=pf.relative_to(ROOT).as_posix(),preflightSha256=sha(pf),
 all845SampleHashesVerified=True,all55BoardHashesVerified=True,all41SegmentHashesVerified=True,bodySha256=p['bodySha256'],
 changedSamplesDirectlyRead=325,changedBoardsDirectlyRead=55,reusedSamplesDirectlyReadPreviously=520,
 earlierDirectReview=old.relative_to(ROOT).as_posix(),earlierDirectReviewSha256=sha(old),
 targetedManualNotes=notes.relative_to(ROOT).as_posix(),targetedManualNotesSha256=sha(notes),groups=n['groups'],
 sourceDiagnostic=diagnostic.relative_to(ROOT).as_posix(),sourceDiagnosticSha256=sha(diagnostic),
 diagnosticCorrection='Earlier bottom-HUD-crop interpretation was corrected using six original native frames: source-inherited102 bottom clipping atf6674 remains; original digit top margins are preserved by full sourcey620..720. No missing source pixels invented.',
 sourceLimitations=['Original source transient102 bottom truncation atbodyf6674 is inherited.','Independent archival match cuts do not prove uninterrupted action, universal balance or optimal strategy.'],
 unresolvedDefects=[],allBoardsDirectlyRead=True,allPlannedSamplesDirectlyRead=True,allInputCaptionPixelsReviewed=True,sourceAllocationApproved=True,inputPixelApproval=True,
 approvalScope='All planned input caption/scene samples:325 changed plus520 previously reviewed unchanged pixels; source allocation and measured timeline. Final encoded pixels and current mixed-ASR remain pending.',
 allContinuousFramesReviewed=False,allFinalPixels=False,finalMixedAsrApproved=False,humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,qa=False,collected=False,private=False,rasterGitAdditions=0,mediaGitAdditions=0)
dest.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(path=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),changedSamples=325,reusedSamples=520,inputPixelApproval=True,allFinalPixels=False)))

"""Add two directly read, hash-matched files to the pending content review."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'duplicate-content-partial-direct-review-v8.json'
assert not out.exists()
proof=read(R/'duplicate-content-partial-direct-review-v7.json')
additional={
 'projects/game-math-quaternion-foundations-v3/project.json':'7ef1c94cb63aeac2d86c59708795d0a2126593d939e6cca4776c19d09d564213',
 'projects/game-math-camera-frustum/publishing/youtube-upload.json':'1d3778d84acb507075a25f78cf140c6634121474ae217ac01b2ad80901fbdff3',
}
for path,expected in additional.items():
    assert sha(ROOT/path)==expected,path
    proof['completeReviewedInputs'].append(dict(path=path,reviewedSha256=expected,currentSha256=expected,
        currentBytesMatchReviewed=True,wholeContentDirectlyRead=True,foreignCompletionApproved=False))
proof['remainingWholeContentReads']=[x for x in proof['remainingWholeContentReads'] if x['path'] not in additional]
assert len(proof['completeReviewedInputs'])==16 and len(proof['remainingWholeContentReads'])==8
proof['previousPartialReview']='duplicate-content-partial-direct-review-v7.json'
proof['reviewedAt']=datetime.now(timezone.utc).isoformat()
proof['additionalWholeReadOutputs']=['bd8f03','6bcbc0','959eee','a79791']
proof['additionalFindings']=[
 'Foundation manifest finalRender/revisionOf/preservation was reread separately after the truncated multi-file output. All22 root properties accounted for; manifest pending publishing remains distinct from local technical approval.',
 'Frustum full receipt describes viewport/pixel aspect, FOV/zoom/dolly, clipping and orthographic calculations. It is distinct from motion camera/aim/locomotion option design. Current scheduled date Nov8 matches the visible current future list; old Nov6 record is history.',
 'Eight other full changed receipts and current whole edit descriptions remain pending. Current duplicate gate remains false; no dependent voice request made.'
]
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
cp_path=R/'latest-checkpoint.json'
q_path=ROOT/'production/batches/cross-game-example-coverage-review/queue.json'
cp_bytes,q_bytes=cp_path.read_bytes(),q_path.read_bytes()
cp,q=read(cp_path),read(q_path)
next_step=('Finish eight remaining changed whole publishing receipts and actual whole current Studio review, '
    'then currentdistinct/check. Reuse the16 complete hash-bound reads in partial-v8 when unchanged. '
    'ObserverV10 completed31954/exit0 stable20s at23:20 is historical eligibility; make one fresh resource '
    'version referencingV10 immediately before one new-version TTS request after the duplicate gate passes. '
    'Require currentidentity/no foreignlease/stable20s/68SHA; preserve coordinator20s/600s guard and exact '
    'success-failure research restoration. No V5 execution against false resourceV6. Preserve original Oct12 slot.')
cp.update(recordedAt=proof['reviewedAt'],currentDuplicateReviewPending=out.name,next=next_step)
q['updatedAt']=proof['reviewedAt']
q['currentMotionReview'].update(currentDuplicateReviewPending=out.relative_to(ROOT).as_posix(),next=next_step)
assert cp_path.read_bytes()==cp_bytes and q_path.read_bytes()==q_bytes
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
q_path.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(completeReads=16,pendingWholeReceipts=8,currentDuplicatePassed=False,newPcm=0)))

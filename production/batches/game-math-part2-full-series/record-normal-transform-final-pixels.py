"""Seal actually viewed current final pixels; keep human/public reviews pending."""
from pathlib import Path
import json,hashlib,datetime,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent;slug='game-math-normal-transform-uv'
P=R/'projects'/slug/'production';Q=R/'shared/output'/slug/'qa'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert '--changed-current-sheets-directly-viewed' in sys.argv
qa=read(P/'qa.json');beats=read(Q/'final-beats/generated-samples.json');ob=read(Q/'observation-samples.json');cmp=read(Q/'subject-repair-image-comparison.json');boundary=read(Q/'subject-boundary-samples.json')
current=qa['videos']['videoBurnedCaptions']['sha256']
assert current==sha(R/qa['videos']['videoBurnedCaptions']['path'])==beats['videoSha256']==ob['videoSha256']==cmp['currentVideoSha256']==boundary['videoSha256']
assert qa['fullDecodePassed'] and qa['captionCount']==156 and qa['frames']==44760 and qa['bodyFrames']==44040 and qa['actualFrames']==17616 and qa['explanationFrames']==26424 and qa['ratioErrorFrames']==0
assert qa['koEnMatchingTimes'] and all(v['audioPacketMd5']=='MD5=2e710692bfbd4e73964f09b682f56e4e' for v in qa['videos'].values())
assert len(beats['records'])==8 and sum(len(x['samples']) for x in beats['records'])==51
assert len(ob['samples'])==83 and len(ob['sheets'])==21
images=sorted(Q.glob('caption-strips-*.jpg'))+sorted(Q.glob('composition-sheet-*.jpg'))+[R/x['path'] for x in beats['records']]+[R/x['path'] for x in ob['sheets']]
assert len(images)==41 and len(cmp['identicalPixelSheets'])+len(cmp['requiresFreshDirectView'])==41
old=read(R/cmp['oldReview'])
for p in cmp['identicalPixelSheets']:assert sha(R/p)==next(x['sha256'] for x in old['images'] if x['path']==p)
assert len(boundary['samples'])==10 and len(boundary['sheets'])==3
images += [R/x['path'] for x in boundary['sheets']]
assert all(sha(R/x['path'])==x['sha256'] for x in beats['records']+ob['sheets']+boundary['sheets'])
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
notes=[
 'All156 Korean caption cues directly inspected: previously viewed unchanged sheet hashes and fresh views of every changed current sheet. Fixed960,970; opaque white square box, black text/thin border, forest-green offset shadow; at most two readable lines. KO/EN cue times match.',
 'Original2-second cat introduction and10-second original membership profiles/names/badges/logo/coaching URL are preserved. Truncated original handles remain human review pending. Actual gameplay fills the screen; all8 explanation scenes have projected spatial faces and narration-timed comparisons on research-black-v1.',
 'All51 explanation beat states inspected. Tangent(1,-1)/normal(1,1) starts perpendicular. Scale diag(2,1) gives tangent(2,-1), naive normal(2,1), dot3. Normalization alone leaves3/sqrt5. Inverse transpose gives(.5,1), dot0, then unit(.447,.894). Only the correct pair has the right-angle marker; singular/reflection conventions retained.',
 'Asymmetric image numbers/cross/edges and explicit top-left v-down UV pins match the mapped coordinates. Central.25–.75 crop omits outside numbers; rotation u′=v,v′=1-u and flip1-u change lookup while preserving the projected plate geometry.',
 'Repeat floor(-.75)=-1 gives.25, unlike truncation. Clamp labels only original region and extends its edges; mirror alternates visibly. Unwrapped u0→2 is interpolated first; wrapping vertex endpoints first collapses u to0 while preserving v. Perspective correction and filtering remain separate prerequisites.',
 'All83 final actual-game subject/seam/source-boundary samples inspected, plus ten exact before/after switch and roof/container sentence frames. Roof begins398.366667s at cue88; container begins402.45s at cue89. Remaining roof and wall are revisited during generic address discussion. All original inspected intervals are used once at real-time speed. No proprietary normals, mesh, UVs or sampler modes are inferred from game pixels.',
 '44760 total frames/746seconds, body44040 with17616 actual-existing-game and26424 explanation: exact40:60. All13 WAV hashes and156 captions preserved through the source-only edit. Clean and captioned videos fully decode with identical original audio packet MD5. Narration-only mix, no BGM or source audio; silent branding/outro checked separately.'
]
review=dict(status='passed',reviewedAt=now,videoSha256=current,captionCuesChecked=156,explanationBeatsChecked=51,actualObservationSamplesChecked=83,additionalSubjectBoundarySamplesChecked=10,reviewMethod=f'All40 baseline sheets directly viewed and scene08 subject timing rejected. After repair,{len(cmp["identicalPixelSheets"])} sheets retain their directly viewed baseline SHA256; all{len(cmp["requiresFreshDirectView"])} changed/new current sheets and3 extra boundary sheets directly viewed afresh. No generation-only pass.',images=[dict(path=p.relative_to(R).as_posix(),sha256=sha(p)) for p in images],notes=notes,humanListening='pending',publicGameIpReview='pending')
write(P/'pixel-review.json',review)
final=dict(status='passed-agent-direct-review',review=f'projects/{slug}/production/pixel-review.json',videoSha256=current,reviewedAtUtc=now)
for record,path,status in [(beats,Q/'final-beats/generated-samples.json','passed-agent-direct-current-final-review'),(ob,Q/'observation-samples.json','passed-agent-direct-current-action-caption-review'),(boundary,Q/'subject-boundary-samples.json','passed-agent-direct-current-subject-boundary-review')]:
 record.update(status=status,reviewedAtUtc=now);write(path,record)
math=read(P/'math-verification.json');assert len(math['checks'])==11 and all(x['passed'] for x in math['checks']) and math['lessonSha256']==sha(B/'lessons'/f'{slug}.json')
math.update(passed=True,checkCount=11,finalRenderedPixels=final,narrationReviewSha256=sha(P/'narration-review.json'));write(P/'math-verification.json',math)
proof=read(P/'math-review.json');proof.update(status='passed-independent-numerical-and-final-pixel-review',passed=11,finalRenderedPixels=final);write(P/'math-review.json',proof)
repair=read(P/'gameplay-subject-timing-repair.json');repair.update(status='passed-preserved-source-only-repair-and-final-pixels',finalEncodedPixelReview=final);write(P/'gameplay-subject-timing-repair.json',repair)
look=read(P/'pre-tts-lookdev-review.json');look['currentFinalReview']=final;write(P/'pre-tts-lookdev-review.json',look)
print('Current156 captions/51 beats/83 action samples+10 boundary samples sealed after direct review.',flush=True)

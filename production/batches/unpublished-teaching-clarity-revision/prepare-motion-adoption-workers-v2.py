from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
for old,new in [('adopt-motion-reviewed-final-v1.py','adopt-motion-reviewed-final-v2.py'),('prepare-motion-publishing-v1.py','prepare-motion-publishing-v2.py'),('deliver-reviewed-motion-v1.cjs','deliver-reviewed-motion-v2.cjs')]:
    text=(B/old).read_text('utf-8-sig')
    text=text.replace('final-pair-execution-v1','final-pair-execution-v2').replace('final-pixel-direct-review-v1','final-pixel-direct-review-v2').replace('final-flow-playback-direct-review-v1','final-flow-playback-direct-review-v2')
    text=text.replace('allListedSamplesDirectlyRead','allListedPixelsDirectlyReviewedCurrentOrByteIdenticalPrior')
    if old.startswith('adopt-'):
        text=text.replace('assemble-motion-current-pair-v1.py','assemble-motion-current-pair-v2.py').replace('final-media-adoption-v1.json','final-media-adoption-v2.json').replace('baseline-records-before-adoption-v1','baseline-records-before-adoption-v2')
        text=text.replace("finalPixels=rel(R/'final-pixel-direct-review-v2.json'),","finalPixels=rel(R/'final-pixel-direct-review-v2.json'),visualRepairs=rel(R/'two-target-repair-direct-review-v3.json'),")
        text=text.replace('allListedFinalPixelsDirectlyReviewed=True,','allListedFinalPixelsDirectlyReviewedCurrentOrByteIdenticalPrior=True,')
    if old.endswith('.cjs'):
        text=text.replace('collection-private-preflight-v1.json','collection-private-preflight-v2.json')
    out=B/new;assert not out.exists();out.write_text(text,'utf-8')
print('Prepared currentV2 adoption/publishing/Git guards; no adoption, upload or Git delivery executed.')

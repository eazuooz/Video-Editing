from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
text=(B/'extract-motion-current-final-pixels-v1.py').read_text('utf-8-sig')
text=text.replace('final-pixels-v1','final-pixels-v2').replace('final-pair-execution-v1','final-pair-execution-v2').replace('final-pixel-execution-v1','final-pixel-execution-v2')
needle="        assert sha(source)==srcrow['sha256']\n        save(DEST/'index.json'"
replacement="""        priorIndex=read(ROOT/'shared/output/unpublished-teaching-clarity-revision/motion/final-pixels-v1/index.json')
        priorReview=read(R/'final-pixel-direct-review-v1.json');assert priorReview['allListedSamplesDirectlyRead']
        assert [v['frame'] for v in samples]==[v['frame'] for v in priorIndex['samples']]
        originalByFrame={v['frame']:v for v in priorIndex['samples']}
        for s in samples:
            old=originalByFrame[s['frame']];assert sha(ROOT/old['path'])==old['sha256']
            same=s['sha256']==old['sha256']
            repaired=(4843<=s['frame']<7181) or (20165<=s['frame']<20568)
            s.update(priorSamplePath=old['path'],priorSampleSha256=old['sha256'],decodedPngByteIdenticalToReviewedV1=same,
                targetRepairRegion=repaired,reusedPriorDirectPixelObservation=same and not repaired,
                currentDirectPixelReviewRequired=not same or repaired)
        for b in boards:
            b['currentDirectPixelReviewRequired']=any(samples[i-1]['currentDirectPixelReviewRequired'] for i in b['sampleIndices'])
            b['allSamplesDecodedByteIdenticalToReviewedV1']=all(samples[i-1]['reusedPriorDirectPixelObservation'] for i in b['sampleIndices'])
        save(DEST/'v1-decoded-sample-comparison.json',dict(source=rel(source),sourceSha256=srcrow['sha256'],
            priorSourceSha256=priorIndex['sourceSha256'],samples=len(samples),byteIdentical=sum(v['decodedPngByteIdenticalToReviewedV1'] for v in samples),
            reusedDirectPixelObservations=sum(v['reusedPriorDirectPixelObservation'] for v in samples),
            requireCurrentDirectReview=sum(v['currentDirectPixelReviewRequired'] for v in samples),
            currentBoardsRequired=[b for b in boards if b['currentDirectPixelReviewRequired']],
            allFinalPixelsApproved=False,newGitImages=0))
        assert sha(source)==srcrow['sha256']
        save(DEST/'index.json'"""
assert needle in text;text=text.replace(needle,replacement)
out=B/'extract-motion-current-final-pixels-v2.py';assert not out.exists();out.write_text(text,'utf-8')
print('Prepared currentV2 absolutePTS worker plus exact decodedPNG comparison; no extraction performed.')

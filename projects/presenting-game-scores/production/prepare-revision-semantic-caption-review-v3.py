"""Bind the directly read independent KO/EN text to the current measured SRTs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent/'revision-balatro60-v2';F=B/'final-v3'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cap=read(F/'captions.json');textreview=read(B/'caption-text-direct-review-v4.json');plan=read(F/'plan.json')
assert cap['allCurrentCueTextsDirectlyRead'] and cap['allInputCuePixelsReviewed'] and plan['allInputSegmentCaptionPixelsReviewed']
assert not (F/'semantic-caption-alignment-review-v3.json').exists()
rows=[]
for c in sorted(cap['chunks'],key=lambda x:x['startSeconds']):
    rows.append(dict(scene=c['scene'],paragraph=c['paragraph'],chunk=c['chunk'],ko=c['ko'],en=c['en'],
        start=round(c['startSeconds'],3),end=round(c['endSeconds'],3),
        koCues=[x['index'] for x in cap['ko'] if (x['scene'],x['paragraph'],x['chunk'])==(c['scene'],c['paragraph'],c['chunk'])],
        enCues=[x['index'] for x in cap['en'] if (x['scene'],x['paragraph'],x['chunk'])==(c['scene'],c['paragraph'],c['chunk'])]))
assert len(rows)==42
for lang,total in [('ko',175),('en',70)]:
    assert [n for r in rows for n in r[lang+'Cues']]==list(range(1,total+1))
    for r in rows:
        cues=[cap[lang][n-1] for n in r[lang+'Cues']]
        assert abs(cues[0]['startSeconds']-r['start'])<.001 and abs(cues[-1]['endSeconds']-r['end'])<.001
review=dict(schemaVersion=3,status='approved-semantic-paragraph-alignment',approved=True,manualSemanticReview=True,
    allParagraphTextsRetained=True,reviewedAt=datetime.now(timezone.utc).isoformat(),paragraphs=rows,
    captions=[dict(language=l,path=(F/f'presenting-game-scores.{l}.srt').relative_to(ROOT).as_posix(),
        sha256=sha(F/f'presenting-game-scores.{l}.srt'),cues=n) for l,n in [('ko',175),('en',70)]],
    priorDirectTextReview=(B/'caption-text-direct-review-v4.json').relative_to(ROOT).as_posix(),
    priorDirectTextReviewSha256=sha(B/'caption-text-direct-review-v4.json'),captionJsonSha256=sha(F/'captions.json'),
    planSha256=sha(F/'plan.json'),scope='Independent KO/EN literal text and measured semantic span alignment; final encoded-pixel QA remains separate.',
    allFinalPixels=False,collected=False,uploaded=False)
(F/'semantic-caption-alignment-review-v3.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(semanticChunks=42,ko=175,en=70,alignmentApproved=True,allFinalPixels=False)))

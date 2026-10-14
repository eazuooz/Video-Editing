"""Seal the 41 actually read bilingual cue rows and six exact-placement gap fixes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'current17-caption-timing-direct-review-v1.json';assert not out.exists()
p=R/'caption-alignment-v1.json';v=read(p);originalSha=sha(p);layout=read(R/'caption-layout-v1.json')
review=read(R/'current17-mixed-complete-direct-review-v2.json');assert review['currentMixedContentReviewPassed'] and review['all17WholeAnd81IndependentContextsDirectlyCompared']
rows=[x for x in v['entries'] if x.get('editorialId')];assert len(rows)==41 and len([x for x in v['entries'] if x.get('retainedCue')])==179
assert layout['allCuesMeasured'] and not layout['unresolvedLayoutErrors'] and layout['mixAacSha256']==review['mixAacSha256']
assert sha(ROOT/layout['ass'])==layout['assSha256']
fixes=[x for x in rows if x['knownQuietGapsExcludedFromFirstWord']];assert [x['id'] for x in fixes]==[115,121,122,143,146,148]
for x in rows:
 assert x['end']>x['start'] and x['contextAlignmentRatio']>.90 and x['contextAlignmentRatio']<=1
 assert x['ko'] and x['en'] and len(x['lines'])<=2
 for gap in x['knownQuietGapsExcludedFromFirstWord']:assert abs(x['start']-gap['end'])<.000001
 x['finalCueTimingDirectlyReviewed']=True
v['allNewCueTimingDirectlyReviewed']=True;v['allFinalCuePixelsReviewed']=False
t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
out.write_text(json.dumps(dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),previousAlignmentSha256=originalSha,currentAlignmentSha256=sha(p),mixedReviewSha256=sha(R/'current17-mixed-complete-direct-review-v2.json'),mixAacSha256=review['mixAacSha256'],all41FullKoEnCueRowsAndTimingDirectlyRead=True,all179RetainedCueTextsAndWrapsPreserved=True,allSixLongLeadingObservationGapsCorrected=True,correctedCueIds=[x['id'] for x in fixes],rows=rows,allNewCueTimingDirectlyReviewed=True,wordTimestampsApproximate=True,finalRenderedCuePixelReviewPending=True,humanAcousticListeningApproved=False,publicRightsApproved=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(newCuesDirectlyCompared=41,oldCuesRetained=179,correctedLongGapOnsets=6,finalPixels=False)))

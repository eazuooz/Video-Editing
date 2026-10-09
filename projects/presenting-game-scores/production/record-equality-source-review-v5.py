"""Seal the 91 native samples and 16 boards actually read during source review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
e=read(B/'equality-claim-source-extraction-v5.json')
assert e['exitCode']==e['actualOuterExitCode']==0 and e['outerExitDirectlyObserved']
assert e['sampleCount']==91 and e['boardCount']==16 and e['exactNativePtsVerified']
for r in e['samples']+e['boards']:assert sha(ROOT/r['path'])==r['sha256']
p=B/'equality-claim-source-direct-review-v5.json';assert not p.exists()
j=dict(recordedAt=datetime.now(timezone.utc).isoformat(),source=e['source'],sourceSha256=e['sourceSha256'],
 candidateNativeFrames=[2250,2725],candidateSeconds=[90,109],nativeTimebase='1/25000',nativePtsStep=1000,
 directlyReadSamples=[dict(r,directlyRead=True) for r in e['samples']],
 directlyReadBoards=[dict(r,index=i,directlyRead=True) for i,r in enumerate(e['boards'],1)],
 observations=['90s LINES9/11; 90.4s12/11; first observed equality92.28s12/12.',
 'At both claim cues33/34, mapped native92.883..96.117s, samples show12/12 with unequal SCORE values2500/1502,2502/1508,2508/1514,2514/1518.',
 '96.8s13/12;98.32s13/13; guide starts100.145s13/13. Later14/13,15/13, ending15/14. Guide asks comparison, not persistent equality.',
 'All91 samples preserve continuous normal-speed piece placement/clears, SCORE/LINES/central difference, two boards and upper UI. Fixed bottom caption region remains on same-frame blur fill.'],
 claimSampleMapping='ceil from final60fps offsets to native25fps candidate; actual source PTS individually verified, not browser endpoint timing',
 normalSpeed=True,loop=False,slowdown=False,sourceAudio=False,sourceSampleActionAndFramingApproved=True,
 wholeContinuousNativeFrameReview=False,allFinalPixels=False,finalEncodedCaptionReviewApproved=False,
 humanListeningApproved=False,publicRightsApproved=False,imagesLocalOnly=True,newGitImages=0)
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(samples=91,boards=16,sourceSamplesApproved=True,allFinalPixels=False)))

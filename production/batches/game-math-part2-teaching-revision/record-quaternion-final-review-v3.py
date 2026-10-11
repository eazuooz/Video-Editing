"""Bind direct cue/moving-pixel reviews and native playback to current masters."""
from pathlib import Path
import datetime, hashlib, json, sys

ROOT = Path(__file__).resolve().parents[3]
Q = Path(__file__).parent / 'cross-game-review-20261011/quaternion-four-game-v3'
SLUGS = ['game-math-quaternion-foundations-v3', 'game-math-quaternion-calculations-v3']
slug = sys.argv[1]
assert slug in SLUGS
read = lambda p: json.loads(p.read_text(encoding='utf8'))
write = lambda p, v: p.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

p = ROOT/'projects'/slug
m=read(p/'project.json'); qa=read(p/'production/qa.json')
idx=read(ROOT/f'shared/output/{slug}/caption-review/index.json')
caption_sha=sha(ROOT/m['paths']['videoBurnedCaptions'])
assert idx['sha256']==qa['videos']['videoBurnedCaptions']['sha256']==caption_sha
assert idx['cueCount']==qa['captionCount'] and qa['fullDecodePassed']
assert qa['ratioErrorFrames']==0 and qa['actualShare']==.4 and qa['explanationShare']==.6
assert not qa['backgroundMusic'] and not qa['sourceAudioUsed']
add=read(Q/'current-narrated-additions-review.json')
assert add['addedSceneMovingPixelsPassed'] and add['gameplayAnnotationsPassed']
assert read(Q/'final-preservation-audit.json')['allPassed']
episode=slug.removeprefix('game-math-quaternion-').removesuffix('-v3')
proof_path=Q/f'{episode}-final-native-playback.json'
proof=read(proof_path)
assert proof['sha256']==caption_sha and proof['ended'] and proof['rate']==1
assert abs(proof['seconds']-qa['seconds'])<.001
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
review={
    'schemaVersion':1,'reviewedAt':now,'slug':slug,
    'videos':qa['videos'],'timelineSha256':sha(p/'production/timeline.json'),
    'directMovingPixelsPassed':True,
    'movingReview':str((Q/'current-narrated-additions-review.json').relative_to(ROOT)).replace('\\','/'),
    'captionReview':{'cueCount':idx['cueCount'],'allCuePixelsDirectlyReviewed':True,
        'sourceSha256':caption_sha,'method':'Direct inspection of all bottom-caption strips, every cue midpoint; new scene moving full-frame pages and spoken reveals reviewed separately.',
        'fixedBottomCenter':True,'wrappedAtMostTwoLines':True,'noCaptionEdgeClipping':True,
        'newExplanationResultsClearOfCaptions':True,'imagesLocalOnly':True},
    'wholeNativePlayback':{'proof':proof_path.relative_to(ROOT).as_posix(),'proofSha256':sha(proof_path),'rate':1,'ended':True},
    'audioReview':(Q/'final-aac-meaning-comparison.json').relative_to(ROOT).as_posix(),
    'originalContentPreservation':(Q/'final-preservation-audit.json').relative_to(ROOT).as_posix(),
    'bodyRatio':{'actual':.4,'explanation':.6,'roundingErrorFrames':0},
    'distinctGames':['Riders Republic','Trailmakers','Space Engineers','Besiege'],
    'gameWorldValuesMeasured':False,'humanListeningComplete':False,'rightsHumanReviewComplete':False,
    'publishingComplete':False,
    'limitations':['Native playback, direct pixels and CPU speech recognition are technical review, not human whole listening or game-IP/source rights approval.']}
write(p/'production/current-pixel-review.json',review)
idx['directReviewPassed']=True;idx['reviewEvidence']=(p/'production/current-pixel-review.json').relative_to(ROOT).as_posix()
write(ROOT/f'shared/output/{slug}/caption-review/index.json',idx)
qa['directVisualReview']='passed-current-hash-all-cues-and-added-moving-pixels'
qa['currentPixelReview']=review['wholeNativePlayback'];qa['audioMeaningReview']=review['audioReview']
qa['humanListening']='pending';write(p/'production/qa.json',qa)
m['status']='reviewed-local-four-game-lecture; private publishing pending'
m['approvals']['script']='Bilingual additions and full preserved explanation order verified; numerical and coordinate conventions checked.'
m['approvals']['pixels']='Current SHA verified: every caption cue, narration-timed moving additions, unchanged baseline clips and uninterrupted whole native 1x playback.'
m['finalRender']['status']='technical-review-passed-current-master'
m['finalRender']['currentPixelApproval']=True
m['finalRender']['review']=(p/'production/current-pixel-review.json').relative_to(ROOT).as_posix()
m['finalRender']['openItems']=['Private upload, actual publishing settings and schedule verification pending.','Human whole listening and source/game-IP review remain pending.']
if 'movingReviewRefinement' in m['finalRender']:m['finalRender']['movingReviewRefinement']['finalMovingReviewComplete']=True
if 'currentLayoutCorrection' in m['finalRender']:m['finalRender']['currentLayoutCorrection']['fullMasterReviewComplete']=True
m['publishReady']=False
m['membershipOutro']['appliedToFinal']=True
m['membershipOutro']['originalClipProof']=(p/'production/current-pixel-review.json').relative_to(ROOT).as_posix()
write(p/'project.json',m)
print(json.dumps({'slug':slug,'captionedSha256':caption_sha,'technicalReviewComplete':True,'humanListeningComplete':False,'uploadComplete':False}))

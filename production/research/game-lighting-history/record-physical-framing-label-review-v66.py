"""Record only the twenty source boards actually read by the reviewer."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
root = Path(__file__).resolve().parents[3]
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(root).as_posix()
stamp = datetime.now(timezone.utc).isoformat()
p = root / 'production/research/game-lighting-history/local/episode04-physical-framing-label-qa-v66/execution.json'
ex = read(p)
assert ex['status'] == 'encoded-samples-ready' and len(ex['items']) == 74 and len(ex['boards']) == 20
assert [sum(b['source']==s for b in ex['boards']) for s in ['clean','captioned']] == [8,12]
for b in ex['boards']:
    assert sha(root / b['path']) == b['sha256']
build_path = root / 'projects/game-lighting-history-04/production/physical-framing-label-review-build-v65.json'
build = read(build_path)
assert build['frames']==2314 and build['captionCues']==11 and build['identicalAacPayloadAndPtsAndDuration']
assert all(x['wholeDecode']['exitCode']==0 for x in build['outputs'])
record = {
    'reviewedAt':stamp, 'scope':'Two repaired physical-framing source scenes only',
    'build':{'path':rel(build_path),'sha256':sha(build_path)},
    'extraction':{'path':rel(p),'sha256':sha(p)},
    'boards':[{**b,'directlyViewed':True} for b in ex['boards']],
    'cleanFramesDirectlyRead':29,'captionedFramesDirectlyRead':45,
    'all20BoardsDirectlyRead':True,'all11CueFirstMiddleLastAndAdjacentSamplesDirectlyRead':True,
    'fixedBottomCaptionPlacementPassed':True,'captionWrappingPassed':True,
    'thinSurfaceNameplateClearInAllSampledStagePixels':True,
    'diagramCaptionOverlapDetected':False,
    'retainedPriorScenes':['part1-overview','part1-conclusion','part3-overview'],
    'priorReview':'projects/game-lighting-history-04/production/physical-framing-encoded-direct-review-v63.json',
    'sourceSceneSamplePixelsPassed':True,
    'allMovingPixelsReviewed':False,'allFinalPixelsReviewed':False,
    'finalMixedAsrApproved':False,'wholeEpisode60to40Approved':False,
    'qaApproved':False,'collected':False,'uploaded':False,
    'humanWholeListening':'pending','newGitImages':0
}
dest = root / 'projects/game-lighting-history-04/production/physical-framing-label-direct-review-v66.json'
assert not dest.exists()
dest.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
cp = root / 'production/research/game-lighting-history/checkpoint.json';j=read(cp)
j['episode04PhysicalFramingLabelDirectPixelsV66']={'review':rel(dest),'status':'source-sample-pixels-passed','all20BoardsDirectlyRead':True,'repairedScenes':2,'retainedEncodedScenes':3,'allFinalPixelsReviewed':False}
j['ownedActiveWork']={'type':'native-game-comparison-and-additive-teaching-preparation','status':'preparing','cpuThreads':0,'gpuJobs':0,'next':'Review the NBA replacement source and expand exact normal-speed guided gameplay/engine cuts; preserve existing PCM and all approved explanation duration.'}
j['updatedAt']=stamp
tmp=cp.with_suffix('.physical-label-review-v66.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(cp)
print('Twenty source boards recorded; full-motion/final episode/upload gates remain false.')

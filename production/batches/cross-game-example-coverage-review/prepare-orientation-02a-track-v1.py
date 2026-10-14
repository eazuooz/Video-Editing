"""Write observed image anchors and measured, unreleased scene timing."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(O/'additional-bank-native-v3/manifest.json');review=read(O/'additional-bank-native-direct-review-v3.json')
assert review['all36DisplayedNativeSamplesDirectlyRead'] and review['all8BoardsDirectlyRead']
# Coordinates read from the displayed 640x360 tiles; each image fills its tile.
# The point is a manually chosen torso image feature, never a physical centroid.
xy=[(317,228),(324,211),(322,213),(321,214),(327,208),(327,194),(322,199),
    None,None,None,None,(329,157),(350,144),(362,157),(351,176),(342,189),
    None,None,None,(310,202),(316,200),(295,195),(313,180),(320,179),(325,177),(334,181),
    None,None,None,None,None,(337,197),(342,199),(336,201),(342,203),(342,202)]
assert len(xy)==len(m['samples'])==36
anchors=[]
for s,p in zip(m['samples'],xy):
    assert sha(ROOT/s['path'])==s['sha256']
    anchors.append(dict(sourceFrame=s['nativeFrame'],sourcePts=s['pts'],
        inspectedImage=s['path'],inspectedImageSha256=s['sha256'],
        visible=p is not None,screenPoint=None if p is None else [p[0]*3,p[1]*3]))
voice=read(O/'additions-whole-asr-v1/02a.json')
assert sha(ROOT/voice['sourcePath'])==voice['sourceSha256']
out=O/'02a-observation-track-plan-v1.json';assert not out.exists()
data=dict(preparedAt=datetime.now(timezone.utc).isoformat(),sceneId='02a',source=m['sources'][0]['sourcePath'],
    sourceSha256=m['sources'][0]['sourceSha256'],nativeIn=4770,nativeOutExclusive=5802,
    nativeFrames=1032,sceneFrames=1033,roundingHoldFrames=1,roundingHoldIsLoopQuota=False,
    coordinateBasis='Directly inspected 640x360 displayed tile coordinates multiplied by3 into native1920x1080. Underlying native audit images1280x720.',
    anchors=anchors,hideSeconds=[[83,85],[87.5,89],[92.5,95]],
    interpolation='Only between two visible adjacent image observations, without crossing a hidden bracket. Linear screen interpolation requires encoded-pixel review.',
    reveals=dict(characterFocus=4.22,torsoPoint=5.44,screenDisplacement=7.16,bodyTiltFocus=8.72,redLineDefinition=11.72,notEngineCoordinates=14.78),
    voice=dict(path=voice['sourcePath'],sha256=voice['sourceSha256'],samples=voice['sourceSamples'],sampleRate=24000),
    asrEvidence=dict(path=(O/'additions-whole-asr-v1/02a.json').relative_to(ROOT).as_posix(),sha256=sha(O/'additions-whole-asr-v1/02a.json')),
    screenOnly=True,physicalCentroid=False,engineWorldAxes=False,rigidRollMeasurement=False,
    actualRenderApproved=False,allBetweenFramesApproved=False,finalCueApproved=False,finalRatioApproved=False,newImageGit=0)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(anchors=36,visible=sum(x['visible'] for x in anchors),sceneFrames=1033,preparedOnly=True)))

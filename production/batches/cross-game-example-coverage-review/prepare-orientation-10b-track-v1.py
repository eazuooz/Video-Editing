"""Measured10b plan: distinct preview rotation, placement and size-selection cuts."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,wave
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(O/'cross-game-native-v1/manifest.json');s=next(x for x in m['sources'] if x['game']=='space-engineers');samples={x['nativeFrame']:x for x in m['samples'] if '/space-engineers/' in x['path']}
voice=ROOT/'shared/output/narration/game-math-orientation-matrices/cross-game-repair-batch-v1/chunks/10b-scene.wav'
with wave.open(str(voice),'rb') as w:assert w.getframerate()==24000 and w.getnframes()==760320
assert sha(voice)=='22c0d09672798d8eb5de6da5da05641fa4a426b69f3088b33a5afdf355e6eca4'
# Manually observed green preview bounds in displayed640x360 tiles. Original source coordinates are tile*3.
# Horizontal/vertical description refers to the screen appearance, not engine/world axes.
features={
 172:((290,146,360,216),(320,156,320,208)),172.2:((290,146,360,216),(320,156,320,208)),172.4:((290,146,360,216),(320,156,320,208)),172.6:((290,146,360,216),(320,156,320,208)),172.8:((290,146,360,216),(320,156,320,208)),
 173:((290,146,360,216),(320,156,320,208)),173.2:((290,146,360,216),(320,156,320,208)),173.4:((290,146,360,216),(320,156,320,208)),173.5:((290,146,360,216),(320,156,320,208)),173.6:None,
 173.8:((284,164,364,207),(292,185,355,185)),174:((284,164,364,207),(292,185,355,185)),174.2:None,
 174.4:((290,146,360,216),(320,156,320,208)),174.5:((290,146,360,216),(320,156,320,208)),174.6:((290,146,360,216),(320,156,320,208)),174.8:((290,146,360,216),(320,156,320,208)),
 177.4:((265,143,376,224),(278,189,359,189)),177.5:((265,143,376,224),(278,189,359,189)),177.6:None,
 177.8:((265,108,373,242),(354,125,354,211)),178:((265,108,373,242),(354,125,354,211)),178.2:None,
 178.4:((266,140,376,225),(350,154,350,206)),178.5:((266,140,376,225),(350,154,350,206)),178.6:((266,140,376,225),(350,154,350,206)),178.8:None,
 178.98333333333332:None,179:None,179.5:None,
 180:((263,157,368,264),(354,169,354,235)),180.5:((263,157,368,264),(354,169,354,235)),181:((263,157,368,264),(354,169,354,235)),181.5:None
}
anchors=[]
for sec,features0 in features.items():
 frame=round(sec*60);x=samples[frame];assert sha(ROOT/x['path'])==x['sha256']
 anchors.append(dict(sourceFrame=frame,sourcePts=x['pts'],path=x['path'],sha256=x['sha256'],visible=features0 is not None,bounds=None if features0 is None else [v*3 for v in features0[0]],line=None if features0 is None else [v*3 for v in features0[1]]))
segments=[dict(frameIn=0,frameOut=380,classification='explanation',kind='projected-flight-to-placement'),dict(frameIn=380,frameOut=647,classification='explanation',kind='full-source-ui-context',freezeNative=10320),dict(frameIn=647,frameOut=886,classification='explanation',kind='frozen-preview-prerequisite',freezeNative=10320),dict(frameIn=886,frameOut=1045,classification='actual',kind='small-preview-rotation',nativeIn=10320,nativeOutExclusive=10479),dict(frameIn=1045,frameOut=1276,classification='actual',kind='separate-placement-action',nativeIn=10644,nativeOutExclusive=10875),dict(frameIn=1276,frameOut=1308,classification='explanation',kind='announce-separate-size-comparison'),dict(frameIn=1308,frameOut=1428,classification='actual',kind='separate-size-selection',nativeIn=10500,nativeOutExclusive=10620),dict(frameIn=1428,frameOut=1901,classification='explanation',kind='projected-shared-reference')]
assert sum(x['frameOut']-x['frameIn'] for x in segments)==1901
intervals=sorted((x['nativeIn'],x['nativeOutExclusive']) for x in segments if x['classification']=='actual');assert all(a[1]<=b[0] for a,b in zip(intervals,intervals[1:]))
p=O/'10b-observation-track-plan-v1.json';assert not p.exists()
d=dict(preparedAt=datetime.now(timezone.utc).isoformat(),sceneId='10b',source=s['sourcePath'],sourceSha256=s['sourceSha256'],sourceTimeBase='1/15360',sourcePtsStep=256,frames=1901,sceneSeconds=1901/60,voice=dict(path=voice.relative_to(ROOT).as_posix(),sha256=sha(voice),samples=760320,sampleRate=24000),voicePlacement=[dict(sourceStartSample=0,sourceEndSample=760320,sceneStartSample=0)],segments=segments,classification=dict(actualFrames=510,explanationFrames=1391),anchors=anchors,
 coordinateBasis='Manual640x360 board coordinates x3 to original1920x1080; source audit PNG1280x720. Moving crop is x320,y255,w1280,h720 scaled1.5. No lift; same-frame blur footer y900..1080.',sourceCrop1920=[320,255,1280,720],
 hideSourceSeconds=[[173.6,173.8],[174.2,174.4],[177.6,177.8],[178.1,178.4],[178.8,180]],interpolationMaxNativeFrames=31,
 voiceLandmarks=dict(p2=6.34,p3=10.78,p4=14.76,verticalWord=15.5,horizontalWord=15.9,rotateWord=16.3,chosenPose=17.4,actualPart=18.74,placementWord=19.66,comparison=20.68,p5=21.8,p6=24.88,sharedAxes=28.9,sharedReference=29.36),
 findings=['Full-source frozen UI/key context precedes enlarged preview; screenshot key labels do not prove actual keys pressed.','Small preview shows vertical/horizontal changes. A distinct later action shows preview pose then solid placed part; cuts explicitly labelled separate intervals.','At native10728..10739 preview/solid transition is an observation bracket, not an exact first placement frame. Orange next-preview overlap hides guides until native10800.','Size-selection sequence uses full source framing and separate label; apparent camera changes are not claimed to be pure rotation or a measured scale factor.','Red line describes the visible long feature; teal bounds locate the selected preview/solid part. Both are screen observations, not engine/world axes.','Frozen source analysis and projected illustrative models are explanation; only unique normal-speed action intervals count as actual.'],
 sourceReviews=['cross-game-native-direct-review-v1.json','space-enlarged-static-direct-review-v3.json'],allMovingPixelsApproved=False,narrationTimedApproved=False,finalRatioApproved=False,finalCueApproved=False,engineWorldAxes=False,physicalCentroid=False,newImageGit=0)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(preparedOnly=True,frames=1901,actualFrames=510,explanationFrames=1391,anchors=len(anchors))))

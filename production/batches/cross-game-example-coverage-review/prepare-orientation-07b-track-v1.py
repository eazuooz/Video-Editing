"""Manual visible aircraft features and measured, byte-preserving voice placement."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,wave,struct
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(O/'cross-game-native-v1/manifest.json');s=next(x for x in m['sources'] if x['game']=='trailmakers');samples={x['nativeFrame']:x for x in m['samples'] if '/trailmakers/' in x['path']}
# 640x360 displayed tiles, directly read: nose, tail, two upper-wing endpoints.
# Null/hidden features never receive a fabricated geometry estimate.
features={
675:((380,238),(258,206),(249,239),(357,178)),675.5:((379,224),(264,220),(244,258),(358,174)),
676:((373,253),(269,214),(257,273),(353,165)),676.5:((372,252),(270,219),(252,264),(355,170)),
677:((376,258),(270,226),(250,277),(354,176)),677.5:((374,230),(277,218),(251,252),(354,170)),
678:((365,219),(280,218),(256,249),(345,168)),678.5:((367,230),(280,219),(251,259),(350,173)),
679:((373,242),(282,220),(246,272),(362,168)),679.5:((370,240),(278,225),(246,261),(355,177)),
680:((373,235),(270,214),(253,256),(351,171)),680.5:((372,226),(269,226),(266,265),(343,169)),
681:((371,228),(262,235),(283,282),(337,166)),684.5:None,
685:((286,234),(343,212),(268,190),(378,202)),685.5:((298,232),(346,208),(255,196),(382,197)),
686:((314,229),(330,210),(254,219),(378,187)),686.5:((314,226),(335,208),(253,231),(369,179)),
687:((315,246),(340,220),(248,251),(365,195)),687.5:((315,231),(333,208),(244,224),(373,177)),
688:None,688.5:None,689:None,689.5:((285,224),(351,213),(306,194),(323,234)),
690:((285,216),(370,216),(295,187),(326,209)),690.5:((285,218),(369,216),(299,188),(337,209)),
691:((286,224),(367,216),(295,190),(336,210)),691.5:((283,231),(365,215),(302,185),(322,217)),
692:((282,225),(367,223),(278,229),(324,182)),692.5:((300,212),(367,225),(250,201),(369,183)),
693:((304,211),(367,235),(252,195),(374,192)),693.5:((312,210),(350,241),(255,193),(375,194)),
694:((312,210),(350,241),(255,193),(375,194)),694.5:((315,210),(350,241),(251,193),(377,193)),
695:((319,207),(337,230),(250,188),(382,195)),695.5:((316,208),(314,231),(254,191),(386,193)),
696:((324,232),(329,205),(254,237),(366,174)),696.5:((320,229),(329,205),(249,246),(357,176)),
697:((320,224),(327,203),(250,246),(355,176)),697.5:((316,236),(326,196),(249,242),(354,165)),
698:((317,236),(327,196),(254,243),(356,168)),698.5:((309,239),(328,204),(266,234),(346,169)),
699:((302,232),(348,215),(316,177),(328,221)),699.5:((285,225),(352,216),(305,167),(330,210)),
699.9833333333333:None}
anchors=[]
for sec,points in features.items():
 frame=round(sec*60);x=samples[frame];assert sha(ROOT/x['path'])==x['sha256']
 a=dict(sourceFrame=frame,sourcePts=x['pts'],path=x['path'],sha256=x['sha256'],visible=points is not None)
 for key,p in zip(('nose','tail','wingA','wingB'),points or (None,)*4):a[key]=None if p is None else [v*3 for v in p]
 anchors.append(a)
voice=ROOT/'shared/output/narration/game-math-orientation-matrices/07b-guide-repair-v1/repair/07b-last-paragraph-spliced-v1.wav'
with wave.open(str(voice),'rb') as w:
 assert w.getframerate()==24000 and w.getnframes()==689400
 pcm=w.readframes(w.getnframes())
assert sha(voice)=='777cb46d8f71caf58a11813a9821c8bd1323ed114c56f4c6a7cddecc17c13f84'
pause=506520;assert all(v[0]==0 for v in struct.iter_unpack('<h',pcm[pause*2:(pause+2400)*2]))
segments=[]
def add(a,b,c,kind,ni=None,no=None):
 x=dict(frameIn=a,frameOut=b,classification=c,kind=kind)
 if c=='actual':assert no-ni==b-a;x.update(nativeIn=ni,nativeOutExclusive=no)
 segments.append(x)
add(0,390,'actual','takeoff',40080,40470)
add(390,583,'actual','side-view',40500,40693)
add(583,742,'actual','next-view-return',41070,41229)
add(742,1003,'explanation','front-wing-model')
add(1003,1144,'actual','front-view',41229,41370)
add(1144,1266,'actual','side-view',41400,41522)
add(1266,1474,'actual','related-level-observation',41522,41730)
add(1474,1622,'actual','related-bank-observation',41760,41908)
add(1622,1789,'actual','camera-side-observation',40693,40860)
add(1789,1891,'actual','camera-other-observation',41908,42010)
add(1891,2080,'explanation','separate-ninety-degree-model')
intervals=sorted((x['nativeIn'],x['nativeOutExclusive']) for x in segments if x['classification']=='actual')
assert all(a[1]<=b[0] for a,b in zip(intervals,intervals[1:]))
p=O/'07b-observation-track-plan-v1.json';assert not p.exists()
d=dict(preparedAt=datetime.now(timezone.utc).isoformat(),sceneId='07b',source=s['sourcePath'],sourceSha256=s['sourceSha256'],sourceTimeBase='1/15360',sourcePtsStep=256,frames=2080,sceneSeconds=2080/60,
voice=dict(path=voice.relative_to(ROOT).as_posix(),sha256=sha(voice),samples=689400,sampleRate=24000),voicePlacement=[dict(sourceStartSample=0,sourceEndSample=pause,sceneStartSample=0),dict(sourceStartSample=pause,sourceEndSample=689400,sceneStartSample=pause+142400)],
observationPause=dict(sourceVoiceSample=pause,sourceVoiceSeconds=21.105,addedFrames=356,addedSamples=142400,seconds=356/60,quietPeak=0,reason='Compare unique normal-speed level and banked passes after both screen guides have been explained; then explicitly compare the different camera views.'),
segments=segments,classification=dict(actualFrames=1630,explanationFrames=450),anchors=anchors,coordinateBasis='640x360 displayed native tile x3 to source1920x1080; audit PNG1280x720.',
interpolation='Adjacent visible observations only; null endpoint hides both guides, no tracking across a cut or hidden bracket.',hideSourceSeconds=[[684.5,685],[687.85,689.35],[699.8,700.1666666667]],
voiceLandmarks=dict(p3Start=7.78,wingsScene=8.76,nextViewScene=9.72,levelReturnScene=[10.94,12.08],p4Start=12.38,frontScene=13.1,blueScene=14.2,wingScene=14.82,bothScene=15.72,p5Start=16.98,p6Start=27.1383333333,screenGuideScene=29.4533333333,separateMathScene=31.5133333333),
sourceBoundaryEvidence=['cross-game-native-direct-review-v1.json','additional-bank-native-direct-review-v1.json'],projectedModelIsExplanation=True,screenGuidesOnly=True,physicalCentroid=False,engineWorldAxes=False,rigidRollMeasurement=False,actualRenderApproved=False,finalRatioApproved=False,finalCueApproved=False,newImageGit=0)
assert sum(x['frameOut']-x['frameIn'] for x in segments)==2080
assert sum(x['frameOut']-x['frameIn'] for x in segments if x['classification']=='actual')==1630
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(preparedOnly=True,anchors=len(anchors),frames=2080,actualFrames=1630,explanationFrames=450,addedObservation=356/60)))

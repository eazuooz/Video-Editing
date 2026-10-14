"""Observed screen anchors, paragraph/native timing, and byte-preserving pause plan."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,wave
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(O/'cross-game-native-v1/manifest.json');s=next(x for x in m['sources'] if x['game']=='descenders')
ss=[x for x in m['samples'] if '/descenders/' in x['path']]
# Directly read head/hip features in displayed 640x360 native tiles.
# These observations are not a measured rigid bike frame or world axis.
pairs=[[(286,163),(303,207)],[(301,161),(308,204)],[(302,162),(308,211)],[(302,164),(314,210)],[(294,167),(310,212)],
 [(278,166),(305,207)],[(298,161),(309,207)],[(296,162),(309,213)],[(314,159),(313,214)],[(317,161),(314,208)],
 [(355,161),(331,207)],[(370,168),(349,216)],[(342,155),(329,217)],[(322,146),(322,211)],[(298,147),(309,207)],
 [(267,155),(288,205)],[(314,148),(315,211)],[(293,147),(310,209)],[(308,143),(310,212)],[(331,149),(329,214)],
 [(321,148),(323,216)],[(321,153),(322,208)],[(328,145),(319,218)],None,None,
 [(321,184),(319,244)],[(321,184),(319,244)],[(329,179),(322,232)],[(342,147),(332,210)],[(316,147),(315,207)],
 None,[(316,171),(321,209)],[(333,222),(320,264)],[(324,145),(325,205)],[(314,146),(313,208)],
 [(338,152),(323,211)],[(346,162),(325,213)],[(351,156),(331,207)],[(342,147),(326,207)],[(352,153),(336,218)],
 [(369,160),(341,216)],[(358,165),(342,216)],[(350,149),(333,210)],[(345,150),(326,205)],[(337,129),(329,208)],
 None,None,None,None,None,[(327,169),(315,224)],[(323,185),(316,246)],[(321,213),(320,276)]]
assert len(pairs)==53
anchors=[]
for x,pair in zip(ss[:53],pairs):
 assert sha(ROOT/x['path'])==x['sha256']
 anchors.append(dict(sourceFrame=x['nativeFrame'],sourcePts=x['pts'],head=None if pair is None else [v*3 for v in pair[0]],hip=None if pair is None else [v*3 for v in pair[1]],visible=pair is not None,path=x['path'],sha256=x['sha256']))
voice=ROOT/'shared/output/narration/game-math-orientation-matrices/cross-game-repair-batch-v1/chunks/03b-scene.wav'
with wave.open(str(voice),'rb') as w:
 assert w.getframerate()==24000 and w.getnframes()==531840
 pcm=w.readframes(w.getnframes())
# The low-amplitude inter-paragraph gap; never cut inside a word.
pause_sample=390960
quiet=pcm[390720*2:391200*2]
import struct
assert max(abs(x[0]) for x in struct.iter_unpack('<h',quiet))<=22
out=O/'03b-observation-track-plan-v1.json';assert not out.exists()
d=dict(preparedAt=datetime.now(timezone.utc).isoformat(),sceneId='03b',source=s['sourcePath'],sourceSha256=s['sourceSha256'],sourceTimeBase='1/15360',sourcePtsStep=256,
 frames=1636,sceneSeconds=1636/60,voice=dict(path=voice.relative_to(ROOT).as_posix(),sha256=sha(voice),samples=531840,sampleRate=24000),
 voicePlacement=[dict(sourceStartSample=0,sourceEndSample=pause_sample,sceneStartSample=0),dict(sourceStartSample=pause_sample,sourceEndSample=531840,sceneStartSample=pause_sample+122400)],
 observationPause=dict(sourceVoiceSample=pause_sample,sourceVoiceSeconds=16.29,addedFrames=306,addedSamples=122400,seconds=5.1,quietGapPeak=22,reason='Observe a second unique flip/landing at normal speed after the narrated first landing, then compare front/up in a separate explanatory model.'),
 segments=[dict(frameIn=0,frameOut=220,classification='explanation',kind='projected-bike-model',claim='Position and orientation are separate quantities; illustrative model.'),
 dict(frameIn=220,frameOut=664,classification='actual',nativeIn=40800,nativeOutExclusive=41244,kind='road',claim='Curved road: screen location and visible body inclination differ.'),
 dict(frameIn=664,frameOut=964,classification='actual',nativeIn=41337,nativeOutExclusive=41637,kind='first-jump',claim='Approach, inverted wheels, upright before landing; maps narrated p4.'),
 dict(frameIn=964,frameOut=1270,classification='actual',nativeIn=41640,nativeOutExclusive=41946,kind='second-jump-observation',claim='A second unique jump demonstrates the same wheel-up/wheel-down change. Explicit separate-jump label; no replay.'),
 dict(frameIn=1270,frameOut=1636,classification='explanation',kind='projected-bike-model',claim='Separately animated model: front and up rotate together; movement direction alone is insufficient.')],
 classification=dict(actualFrames=1050,explanationFrames=586),anchors=anchors,coordinateBasis='640x360 displayed native tile x3 to source1920x1080; underlying audit PNG1280x720.',
 interpolation='Adjacent visible head/hip observations only; no interpolation across rapid flips or null feature brackets.',hideSourceSeconds=[[691.1,692.4833333333333],[694,695],[697.9,698.8]],
 voiceLandmarks=dict(p3Start=6.84,p4Start=11.06,inversionPhrase=[12.66,13.56],backDownPhrase=[14.28,15.2],firstLandingEnd=16.04,p5SceneStart=21.42,frontScene=25.14,upScene=25.5),
 projectedModelIsExplanation=True,screenGuidesOnly=True,physicalCentroid=False,engineWorldAxes=False,rigidRollMeasurement=False,actualRenderApproved=False,finalRatioApproved=False,finalCueApproved=False,newImageGit=0)
assert sum(x['frameOut']-x['frameIn'] for x in d['segments'])==1636
intervals=sorted((x['nativeIn'],x['nativeOutExclusive']) for x in d['segments'] if x['classification']=='actual')
assert all(a[1]<=b[0] for a,b in zip(intervals,intervals[1:]))
out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(preparedOnly=True,anchors=53,frames=1636,actualFrames=1050,explanationFrames=586,pauseAt=16.29,addedObservation=5.1)))

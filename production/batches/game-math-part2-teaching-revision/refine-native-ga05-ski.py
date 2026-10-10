"""Retain correct approved new voice; show only directly observed ski landmarks."""
from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'ga05old-landmarks.json';d=read(p);assert d.get('nativeFrameTimestampCorrection')
archive=B/'baselines/landmark-drafts-before-native-time-fix/ga05old-after-time-correction-before-native-refinement.json'
if not archive.exists():shutil.copy2(p,archive)
# Native source frame times = the original reference labels plus14/60.
# White back emblem and coat base are image landmarks, not calibrated axes.
points=[(169.25,291,217,286,294),(169.75,278,177,279,242),(170.25,268,176,279,249),(170.75,267,182,264,267),(171.25,260,222,291,278),(171.75,256,222,281,296),(174.25,300,199,298,274),(174.75,316,198,312,263),(175.25,304,205,303,261),(175.75,310,187,311,247)]
ski={170.25:[[293,275],[309,323]],170.75:[[222,315],[268,295]],171.25:[[296,289],[313,334]],171.75:[[211,335],[267,312]],174.25:[[315,294],[304,326]],174.75:[[350,281],[357,313]],175.25:[[321,288],[314,334]],175.75:[[324,267],[318,306]]}
d['keyframes']=[]
for label,ux,uy,lx,ly in points:
 k={'t':round(label+14/60,9),'authoringLabelTime':label,'upper':[ux,uy],'lower':[lx,ly]}
 if label in ski:k['wheel']=ski[label]
 d['keyframes'].append(k)
d['hideIntervals']=[[172.4,174.35]];d['meaning']='Directly viewed native white back emblem/coat-base and visible longitudinal ski segments. Two skis/poles verified in enlarged native175.25 and170.25. No world/engine measurement.'
d['movingPixelApproval']=False;write(p,d)
p=B/'quaternion-annotation-tracks.json';r=read(p);r['scenes']['GA05'].update(showWheel=True,blueLabel='보이는 스키 선',blueAtLine=1,blueHideSourceIntervals=[[170.5,171.1],[172.2,174.35]])
r['all25ActualScenesReady']=False;write(p,r)
# Exact native180.1 was still a gray get-up. Resume after that transition.
p=B/'quaternion-source-corrections-v5.json';c=read(p);s=next(x for x in c['scenes'] if x['id']=='GA05');s['intervals'][2]=[181.8,187];s['maximumSeconds']=sum(b-a for a,b in s['intervals']);s['selectionReason']+=' Native-time correction: gray get-up visible180.1; resume at181.8. Same allocated real-time frame count fits the remaining5.2s.';write(p,c)
slug='game-math-quaternion-foundations-v2';p=ROOT/f'projects/{slug}/production/timeline.json';t=read(p);s=next(x for x in t['scenes'] if x['id']=='GA05')
s['cut']['sourceSegments'][2].update({'in':181.8,'maxSeconds':5.2});s['cut']['segments'][2].update({'in':181.8,'maxSeconds':5.2});s['cut']['maximumSeconds']=c['scenes'][[x['id'] for x in c['scenes']].index('GA05')]['maximumSeconds']
assert s['cut']['segments'][2]['frames']/60<=5.2;write(p,t)
p=ROOT/f'projects/{slug}/production/lesson.json';l=read(p);s=next(x for x in l['scenes'] if x['id']=='GA05');s.update(intervals=c['scenes'][[x['id'] for x in c['scenes']].index('GA05')]['intervals'],maximumSeconds=49.05,maxSeconds=49.05);write(p,l)
write(B/'quaternion-ga05-native-refinement.json',{'originalV4VoiceRetained':True,'v7BoardRetakeRejected':True,'sceneFramesUnchanged':2673,'wholeEpisodeFramesUnchanged':72630,'actualExplanationShareUnchanged':[.4,.6],'grayRecoveryExcluded':[[179.1,181.8]],'nativeSkiLandmarksAdded':8,'finalMovingReview':False})
print('Correct ski voice retained; native source boundary and editable blue ski observations fixed without retiming the episode.')

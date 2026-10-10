"""Remove native crash/recovery in a new insertion, retaining its measured slot."""
from pathlib import Path
import json,copy
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=ROOT/'projects/game-math-quaternion-foundations-v2/production/timeline.json';t=read(p);s=next(x for x in t['scenes'] if x['id']=='GA08')
cut=s['cut'];first=copy.deepcopy(cut['segments'][0]);remaining=s['frames']-first['frames'];assert remaining>720
cut['sourceSegments']=[{'in':460,'maxSeconds':7,'startsAtLine':0},{'in':475,'maxSeconds':12,'startsAtLine':1},{'in':490,'maxSeconds':7,'startsAtLine':None}]
cut['segments']=[first,{'in':475,'maxSeconds':12,'startsAtLine':1,'frames':720,'seconds':12,'sourceGroupStartsAtLine':1},{'in':490,'maxSeconds':7,'startsAtLine':None,'frames':remaining-720,'seconds':(remaining-720)/60,'sourceGroupStartsAtLine':None}]
cut['maximumSeconds']=26;assert sum(x['frames'] for x in cut['segments'])==s['frames'];write(p,t)
p=ROOT/'projects/game-math-quaternion-foundations-v2/production/lesson.json';d=read(p);s=next(x for x in d['scenes'] if x['id']=='GA08');s.update(intervals=[[460,467],[475,487],[490,497]],maximumSeconds=26,maxSeconds=26,sourceGroupStartsAtLines=[0,1,None]);write(p,d)
p=B/'quaternion-source-corrections-v5.json';d=read(p);s=next(x for x in d['scenes'] if x['id']=='GA08');s.update(intervals=[[460,467],[475,487],[490,497]],maximumSeconds=26,sourceGroupStartsAtLines=[0,1,None]);s['selectionReason']+=' Exact native488–489 frames show crash/get-up and blurred recovery. Exclude487–490, resume clear flight490. Keep the same1487-frame slot with a distinct-excerpt label; no loop, slowdown or narration change.';d['comparison'].append({'id':'GA08-native-recovery','rejected':[487,490],'reason':'Exact native frame readback exposes grayscale get-up488 and ghost recovery489. Clear flight resumes490.','chosenSubintervals':[[460,467],[475,487],[490,497]],'fullCurrentMovingReviewPassed':False});write(p,d)
# These particular ten manually corrected ski landmarks were directly read
# from enlarged native frames. The generic detector rejects occluded hips and
# has insufficient coverage here, so preserve the precise observed draft.
p=B/'quaternion-annotation-tracks.json';r=read(p)
s=r['scenes']['GA05'];s['landmarkSources']=[x.replace('/dense-body-tracks/ga05old-landmarks.json','/ga05old-landmarks.json') for x in s['landmarkSources']];s['manualSkiLandmarksRetained']='Ten directly viewed native coat/ski anchors; CPU detector2D hips unsuitable in this occluded segment.';write(p,r)
write(B/'quaternion-ga08-native-recovery-exclusion.json',{'excludedNativeIntervals':[[487,490]],'sceneFramesRetained':1487,'ratioAndVoiceUnchanged':True,'originalBaselineFootagePreserved':True,'nativeEvidence':'shared/output/game-math-part2-teaching-revision/landmark-authoring/GA08-native-tail','movingPixelReview':False})
print('Excluded new-cut recovery without changing duration, voice or the40:60 ratio.')

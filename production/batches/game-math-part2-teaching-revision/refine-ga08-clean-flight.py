"""Observed native flight replacements; fixed measured voice and timeline."""
from pathlib import Path
import json,copy
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
intervals=[[460,460+494/60],[471.2,473.5],[475,487],[490,492.25]]
p=ROOT/'projects/game-math-quaternion-foundations-v2/production/timeline.json';t=read(p);s=next(x for x in t['scenes'] if x['id']=='GA08')
cut=s['cut'];cut['sourceSegments']=[{'in':a,'maxSeconds':b-a,'startsAtLine':line} for (a,b),line in zip(intervals,[0,1,None,None])]
cut['segments']=[{'in':a,'maxSeconds':b-a,'startsAtLine':line,'frames':frames,'seconds':frames/60,'sourceGroupStartsAtLine':line} for (a,b),line,frames in zip(intervals,[0,1,None,None],[494,138,720,135])]
cut['maximumSeconds']=sum(b-a for a,b in intervals);assert sum(x['frames'] for x in cut['segments'])==s['frames']==1487;write(p,t)
for p in [ROOT/'projects/game-math-quaternion-foundations-v2/production/lesson.json',B/'quaternion-source-corrections-v5.json']:
 d=read(p);s=next(x for x in d['scenes'] if x['id']=='GA08');s.update(intervals=intervals,maximumSeconds=cut['maximumSeconds'],maxSeconds=cut['maximumSeconds'],sourceGroupStartsAtLines=[0,1,None,None])
 if 'selectionReason' in s:s['selectionReason']='Exact native frames of baseline source4Odvp_TIeQU show clear first flight through468.23 and last flight through492.2; CHECKPOINT MISSED appears at492.4 and ghosting at492.8, so end the last excerpt at492.25. Also exclude473.5–475 and487–490 recovery. Preserve1487frames, original voice and explicit separate-excerpt labels. New moving playback remains pending.'
 write(p,d)
draft=read(B/'ga08-landmarks.json');extra=copy.deepcopy(draft);extra.update(id='GA08-native-clean-flight',interval=[471.2,473.5],hideIntervals=[],reviewStatus='Coordinates directly read from exact native0.2s authoring frames; moving pixels pending')
points=[(471.2,130,274,427,274),(471.4,125,284,427,282),(471.6,140,288,438,283),(471.8,170,285,442,280),(472,175,280,449,273),(472.2,175,274,443,265),(472.4,165,256,441,254),(472.6,160,248,428,260),(472.8,164,245,429,269),(473,180,240,427,273),(473.2,196,243,418,276),(473.4,205,251,412,276)]
extra['keyframes']=[{'t':time,'left':[lx,ly],'right':[rx,ry]} for time,lx,ly,rx,ry in points];write(B/'ga08-clean-flight-landmarks.json',extra)
p=B/'quaternion-annotation-tracks.json';r=read(p);r['scenes']['GA08']['landmarkSources']=['production/batches/game-math-part2-teaching-revision/ga08-landmarks.json','production/batches/game-math-part2-teaching-revision/ga08-clean-flight-landmarks.json']
r['scenes']['GA07']['blueHideSourceIntervals']=[[70,80]];r['scenes']['GA07']['blueVisibilityReason']='The narrated wheel comparison is retained during61.5–70; hide the sparse wheel draft after70 where direct rendered pixels show drift. Dense torso continues.'
write(p,r)
write(B/'quaternion-native-final-cut-refinement.json',{'scene':'GA08','sourceId':'4Odvp_TIeQU','chosenIntervals':intervals,'rejectedIntervals':[[470,471.2],[473.5,475],[487,490],[492.25,497]],'nativeEvidence':['shared/output/game-math-part2-teaching-revision/landmark-authoring/GA08-flight-clean','shared/output/game-math-part2-teaching-revision/landmark-authoring/GA08-old-first-tail','shared/output/game-math-part2-teaching-revision/landmark-authoring/GA08-old-flight-tail'],'excludedMisleadingEvidence':'GA08-flight-tail was generated from a different source_dw9jjRpanA and must not validate this cut','ratioAndNarrationUnchanged':True,'movingPixelReview':False,'GA07wheelDriftHidden':[70,80]})
print('Retained fixed1487frames; removed native recovery from the new flight insertion; wheel drift hidden.')

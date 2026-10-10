"""Reject visually incorrect color detections; retain only inspected body portions."""
from pathlib import Path
import json, hashlib, datetime
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
old='33acbad6b7980c3d56f952e66cb9f7614f683e1e4fcc315b2d852a9067c1e29f'
P=ROOT/'projects/game-math-bounds-transform-v2'
rejection={'reviewedAt':datetime.datetime.now().astimezone().isoformat(),'sha256':old,'approval':False,'failures':[{'scene':'13','localTimes':[0,10,33],'reason':'Blue-color component attached to foreground gun or empty ground; not the narrated selected body.'},{'scene':'16','localTimes':[2,13.5,27.5,31.5,38],'reason':'Color component attached to ground, timber, or sky; a color match is insufficient evidence of a body landmark.'}],'directlyViewedProof':'moving-pixel-review and quarter-second track-fine-review local sheets','correction':'Retain only directly inspected short visible body windows. All uncertain intervals hidden; no claim of continuous tracking. Narration, source action, timeline and original material unchanged.'}
write(P/'production/rejected-annotation-review-33ac.json',rejection)
valid={'13':[[26,26.5],[33.6,34]],'16':[[28,29.25],[30,30.5]]}
records=[]
for ident,intervals in valid.items():
 path=B/'lines-tracks'/f'{ident}.json';d=read(path)
 assert not d.get('visuallyReviewedVisibleWindows'),'Do not overwrite an already narrowed track.'
 write(ROOT/'shared/output/game-math-bounds-transform-v2/track-fine-review'/f'rejected-original-track-{ident}.json',d)
 original=hashlib.sha256(path.read_bytes()).hexdigest()
 d['keyframes']=[x for x in d['keyframes'] if any(a-1e-8<=x['t']<=z+1e-8 for a,z in intervals)]
 d['visuallyReviewedVisibleWindows']=intervals;d['automaticComponentCountIsApproval']=False
 d['selectionDefinition']='A briefly visible portion of the selected body, not all limbs, hidden edges, or engine collision data. Different observations separated by hidden intervals.'
 d['selectionReview']={'rejectedFinalSha256':old,'priorTrackSha256':original,'fineSampleSeconds':.25,'rejectedIntervalsHidden':True,'currentMovingRenderReview':'pending'}
 write(path,d);records.append({'scene':ident,'visibleWindows':intervals,'retainedSourceObservations':len(d['keyframes']),'priorTrackSha256':original,'currentTrackSha256':hashlib.sha256(path.read_bytes()).hexdigest()})
write(P/'production/annotation-correction-plan.json',{'rejectedFinalSha256':old,'records':records,'narrationAndTimelineUnchanged':True,'currentMovingPixelsDirectlyReviewed':False})
m=read(P/'project.json');m['finalRender']['currentPixelApproval']=False;write(P/'project.json',m)
print('Rejected components removed; render and moving review still required:',records)

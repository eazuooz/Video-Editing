"""Use directly compared continuous outcomes; never add logos or repeat cuts."""
from pathlib import Path
import json,datetime,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
changes={
 'game-math-plane-distances-v2':{'PG01':[[14,49],[16,35.8]],'PG03':[[18,31.6],[66,86]]},
 'game-math-triangle-addresses-v2':{'PG04':[[19.5,35.5],[36.5,55.5],[33.5,40.95]],'PG06':[[55.5,70],[72.3,81],[82.2,91.5]],'PG07':[[49,60],[62.75,74.5],[78,84.5]]}
}
records=[]
for slug,edits in changes.items():
 p=ROOT/f'projects/{slug}/production/lesson.json';d=read(p)
 for s in d['scenes']:
  if s['id'] not in edits:continue
  before=s['intervals'];s['intervals']=edits[s['id']];s['maximumSeconds']=sum(z-a for a,z in s['intervals'])
  if s['id']=='PG06':
   s['segmentSourceIds']=['portal2-steam-5790']*3
   s['sourceGroupStartsAtLines']=[0,1,None]
  records.append({'slug':slug,'scene':s['id'],'before':before,'after':s['intervals'],'originalNarrationPreserved':True})
 write(p,d)
review={
 'observedAt':datetime.datetime.now().astimezone().isoformat(),'changes':records,
 'pixelEvidence':'shared/output/game-math-part2-teaching-revision/planes-capacity-review',
 'directlyViewedPages':['faith-review.jpg','panels-review.jpg','coop-review.jpg','gel-review.jpg','vents-review.jpg'],
 'reasons':{
  'faith':'34–35.8 finishes the continuous traversal onto the far platform and shows the exit/check result. Reject35.9 onward because the Portal logo starts; no transition animation counts as actual gameplay.',
  'panels':'30.5–31.6 continues the same lifting panel and exposes the surface edge and robot underneath. Reject31.8 onward transition/logo; no inferred engine normal or mesh.',
  'coop':'33.5 starts the same launch shot before lift-off; finish40.95 before the close-up button shot. Reject32.5–33.3 unrelated character close-up and41+ different button/ceiling shots.',
  'gel':'First episode retains one continuous14–49 bounce/return interval, including the near platform and camera return. Second episode starts49 to preserve a distinct49–60 surface/next-position observation, without source overlap.',
  'vents':'72.3–74.5 approaches through the portal into the same bright room;80–80.8 offers an unobscured floor-grid comparison while its corners are narrated. Omit81–82.2 rapid pan and explicitly identify the next source cut.90.5–91.5 shows the robot visibly lifted off the floor beneath the device. Reject91.8 onward logo transition; do not imply a single tracked robot across several repeated device arrivals.'},
 'nativeSourceWholePlayback':'These unchanged source SHA files were already played end-to-end at1x; the additional boundaries and transitions are directly compared in the listed dense pixel pages.',
 'noFootageSpeedChangesLoopsFreezes':True,'movingOverlayApproval':False,'humanRightsReviewComplete':False
}
write(B/'planes-capacity-source-review.json',review)
print(json.dumps(records))

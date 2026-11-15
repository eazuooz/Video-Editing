import json,sys
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 plan=read(HERE/'plan.json');cpath=ROOT/'shared/publishing/video-production-control.json';c=read(cpath)
 c['explicitMathRemainingBatch20261104']['gameSubjectRevision20261115']=dict(scope=plan['scope'],userRequest=plan['userRequest'],plan=str((HERE/'plan.json').relative_to(ROOT)),status='authoring-and-internal-sample-QA',upload=False,automation=False,humanReviewed=False,baseline='teaching-sync-v2 preserved',checkedAt=datetime.now(timezone.utc).isoformat())
 save(cpath,c)
 audit=read(HERE/'scene-audit.json')
 for row in audit['rows']:
  row['status']='midpoint-picture-and-narration-reviewed; changed-motion-QA-pending'
  row['reviewMethod']='Actual existing encoded scene midpoint reviewed on scene-indexed contact sheets; no claim of full playback from a midpoint.'
  eid=row['episode']
  row['decision']='Preserve necessary abstract geometry and the existing real-game windows; add subject continuity only where it explains the narrated mechanism.'
  if eid in ('M24','M25','M26') and row['motionSubject']=='robot':row['decision']='Replace visible generic robot using an inspected actual-game image on the same analytic position; preserve scalar/independent-diagram visibility and current formula overlays.'
  if eid=='M22':row['decision']='Replace unrelated knight portrait with actual Mario image; preserve independently calculated arm/surface experiment. Screenshot does not claim measured Mario skin weights.'
  if eid=='M23':row['decision']='Replace decorative knight portrait with actual Townscaper subject image; preserve rasterizer, matrices, surface diagrams and canonical formulas.'
  if eid=='M21':row['decision']='Retain the user-selected material sphere, shader-driven vectors and game windows. No unrelated robot remains and a Mario cutout would obscure surface shading.'
  if eid=='M27' and row['scene']=='010':row['decision']='Preserve this explicit spoken robot-in-an-elevator thought experiment; do not silently show Mario while narration identifies a robot. Distinguish it from the replaceable motion stand-ins.'
 audit['actualMidpointPictureReview']=True;audit['actualFullMotionReview']=False;save(HERE/'scene-audit.json',audit)
 save(HERE/'checkpoint.json',dict(scope=plan['scope'],status='authoring-and-sample-QA',completedFinalMasters=[],next='Encode and inspect representative actual-Mario motion/arm/pipeline samples, then serialized local renders.',upload=False,humanReviewed=False))
if __name__=='__main__':main()

from pathlib import Path
import audio_pipeline as ap,video_pipeline as vp
from build_cut_plan import tracked
H=Path(__file__).resolve().parent;L=H.parent/'local/fighters-v3';R=H.parents[3]
p=ap.read(H/'edit-plan.json')
for c in p['cuts']:
 if c.get('unrealCapture'):
  receipt=L/'unreal'/f"{c['id']}-capture.json";j=ap.read(receipt);assert j['status']=='complete' and j['frames']==c['frames']
  c['unrealCapture']=ap.artifact(receipt);c['renderedSource']=j['movie'];c['renderedSourceSha256']=j['movieSha256']
 if c.get('playbackSpeed',1)!=1:
  if c['id'] in {'A02-F12','A02-F32'}:
   c['sourceStart']={'A02-F12':67.3,'A02-F32':244.2}[c['id']];c['sourceEndExclusive']=c['sourceStart']+c['frames']/60*.25
   c['marks']=[tracked(c,'punch' if c['id']=='A02-F12' else 'spin','')]
   c['timingDecision']='Place the observed arm raise/takeoff immediately beside its spoken target/action clause; retain preparatory native frames during the slow-replay introduction.'
  for m in c['marks']:
   m['label']={'A02-F12':'팔·몸통','A02-F13':'팔·몸통','A02-F22':'실루엣','A02-F23':'실루엣','A02-F32':'회전','A02-F33':'회전'}[c['id']];m['labelPosition']=[32,720]
  ref=next(r for r in p['cuts'] if r['id']==c['normalSpeedReference']);assert ref['endFrame']<=c['startFrame'] and ref['sourceFile']==c['sourceFile'] and ref['playbackSpeed']==1
vp.validate_plan(p);ap.save(H/'edit-plan.json',p)
ap.save(H/'annotation-review.json',{'status':'source-bound-red-tracking-rectangles','captionProtectedRect':p['captionProtectedRect'],'labelLocation':'black left gutter, away from game HUD','nativeFirstReferences':[{'cut':c['id'],'reference':c['normalSpeedReference']} for c in p['cuts'] if c.get('normalSpeedReference')],'sourceFramesReviewed':['kof-shermie-67.5-69.5-0.1.jpg','kof-shermie-245-252-0.25.jpg','gg-giovanna-55-63-0.2.jpg'],'noDetectorOrHitboxMeasurementClaim':True,'fullFinalPixels':'pending'})
print('Six completed Unreal captures bound; six slow-motion labels cleared from the HUD')

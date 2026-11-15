"""Compare two complete, actually recorded facing-direction guard poses."""
from common import *
import visuals as v,render,sys

def main(preview=False):
 original=v.SOURCES['dee-right'];v.SOURCES['dee-right']=(original[0],14,14.7,original[3],(250,220,850,1050))
 plan=read(HERE/'plan.json');e=next(e for e in plan['episodes'] if e['id']=='A13')
 for s in e['studyDefinitions'].values():
  s.update(localIn=14,localOut=14.7,detailCrop=[250,220,850,1050],rendererAdapter=str(Path(__file__)),rendererAdapterSha256=sha(__file__))
 studies=read(HERE/'source-studies.json')
 for s in studies['studies']:
  if s['episode']=='A13':s.update(localIn=14,localOut=14.7,detailCrop=[250,220,850,1050],rendererAdapter=str(Path(__file__)),sourceWindowEvidence=str(WORK/'A13/idle-candidates/guard-candidates.jpg'))
 save(HERE/'source-studies.json',studies)
 e['queuedVisualEnhancement']=dict(stage='previewed-pending-encode',reason='Use the inspected14.0–14.7s right-facing guard instead of a cropped recovery. Compare it with the existing29.4–30.1s left-facing guard; both full figures remain visible. No whole-video flip.',sourceEvidence=str(WORK/'A13/idle-candidates/guard-candidates.jpg'),audioChanged=False)
 save(HERE/'plan.json',plan);v.prepare_banks()
 if preview:
  span=next(s for s in e['replacementSpans'] if s['key']=='mirror');old=span['start']+30
  im=v.draw('A13',e,dict(span,mode='analysis',nativeLeadCompleted=True,newFrame=old),30,old)
  im.save(WORK/'A13/guard-comparison-preview.png');im.resize((375,211)).save(WORK/'A13/guard-comparison-preview-mobile.png');return
 render.render_episode(e)
 plan=read(HERE/'plan.json');next(e for e in plan['episodes'] if e['id']=='A13')['queuedVisualEnhancement']['stage']='encoded-awaiting-internal-review';save(HERE/'plan.json',plan)
if __name__=='__main__':main('--preview' in sys.argv)

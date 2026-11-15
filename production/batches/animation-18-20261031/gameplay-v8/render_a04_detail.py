"""A04-only detail adapter; preserve other running episode renderers."""
from common import *
import visuals,render,sys
CROP=(760,340,1240,660)
original_timing=visuals.timing

def enlarged_timing(im,bank,u,key,ep):
 if ep!='A04':return original_timing(im,bank,u,key,ep)
 original=visuals.SOURCES[bank];visuals.SOURCES[bank]=(*original[:4],CROP)
 try:return original_timing(im,bank,u,key,ep)
 finally:visuals.SOURCES[bank]=original
visuals.timing=enlarged_timing

def main(preview=False):
 plan=read(HERE/'plan.json');e=next(e for e in plan['episodes'] if e['id']=='A04')
 s=e['studyDefinitions']['anticipation'];s.update(timingDetailCrop=list(CROP),rendererAdapter=str(Path(__file__)),rendererAdapterSha256=sha(__file__))
 e['queuedVisualEnhancement']=dict(stage='previewed-pending-encode',reason='The final375px comparison needs a larger player/weapon view. Tighten only timing comparisons; native whole-action/context views retain their original crop.',preview=str(WORK/'A04/enlarged-timing-preview.png'))
 save(HERE/'plan.json',plan)
 if preview:
  span=next(x for x in e['replacementSpans'] if x['key']=='anticipation' and x['mode']!='native');n=span['start']+53
  image=visuals.draw('A04',e,dict(span,mode='analysis',nativeLeadCompleted=True,newFrame=n),53,n)
  image.save(WORK/'A04/enlarged-timing-preview.png');image.resize((375,211)).save(WORK/'A04/enlarged-timing-preview-mobile.png');return
 render.render_episode(e)
 plan=read(HERE/'plan.json');next(e for e in plan['episodes'] if e['id']=='A04')['queuedVisualEnhancement']['stage']='encoded-awaiting-internal-review';save(HERE/'plan.json',plan)
if __name__=='__main__':main('--preview' in sys.argv)

"""A14-only missing mathematical minus glyph correction; preserve all audio."""
from common import *
import visuals as v,render,sys
original_text=v.text
def text(d,xy,s,*args,**kwargs):
 return original_text(d,xy,s.replace('1−w','1 - w'),*args,**kwargs)
v.text=text
def main(preview=False):
 plan=read(HERE/'plan.json');e=next(e for e in plan['episodes'] if e['id']=='A14')
 e['studyDefinitions']['blend'].update(rendererAdapter=str(Path(__file__)),rendererAdapterSha256=sha(__file__))
 e['queuedVisualEnhancement']=dict(stage='previewed-pending-encode',reason='Encoded QA found the U+2212 minus absent in the selected display font. Use the equivalent supported ASCII minus in (1 - w), retaining the same calculation, speech and timing.',audioChanged=False)
 save(HERE/'plan.json',plan)
 if preview:
  s=next(s for s in e['replacementSpans'] if s['key']=='blend');n=s['start']+45
  im=v.draw('A14',e,dict(s,mode='analysis',nativeLeadCompleted=True,newFrame=n),45,n)
  im.save(WORK/'A14/formula-glyph-preview.png');return
 render.render_episode(e)
 plan=read(HERE/'plan.json');next(e for e in plan['episodes'] if e['id']=='A14')['queuedVisualEnhancement']['stage']='encoded-awaiting-internal-review';save(HERE/'plan.json',plan)
if __name__=='__main__':main('--preview' in sys.argv)

"""Use a weapon-neutral label beside Lance footage; retain the same diagram."""
from common import *
import visuals as v,render
original_text=v.text
def text(d,xy,s,*args,**kwargs):
 return original_text(d,xy,s.replace('같은 검 경로','같은 무기 경로'),*args,**kwargs)
v.text=text
def main():
 plan=read(HERE/'plan.json');e=next(e for e in plan['episodes'] if e['id']=='A16')
 e['studyDefinitions']['range'].update(rendererAdapter=str(Path(__file__)),rendererAdapterSha256=sha(__file__))
 e['queuedVisualEnhancement']=dict(stage='pending-encode',reason='Name the abstract path 무기 경로 consistently with the adjacent Lance example, rather than 검 경로. Model, audio, timing and existing checks otherwise unchanged.',audioChanged=False)
 save(HERE/'plan.json',plan);render.render_episode(e)
 plan=read(HERE/'plan.json');next(e for e in plan['episodes'] if e['id']=='A16')['queuedVisualEnhancement']['stage']='encoded-awaiting-internal-review';save(HERE/'plan.json',plan)
if __name__=='__main__':main()

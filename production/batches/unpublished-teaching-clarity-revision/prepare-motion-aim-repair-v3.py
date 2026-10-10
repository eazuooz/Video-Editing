from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
MC=ROOT/'motion-canvas/src/projects/motion-sickness-games/teaching-clarity-v1'
src=MC/'scene02-explanation-v2.tsx';dest=MC/'scene02-explanation-v3.tsx';assert not dest.exists()
text=src.read_text('utf-8')
text=text.replace("angle: ()=>number, color: string) =>", "angle: ()=>number, color: string, distance: ()=>number = () => Math.hypot(370,80)) =>")
text=text.replace('X()+240*Math.cos(angle()), 20+240*Math.sin(angle()), 40','X()+distance()*Math.cos(angle()), 20+distance()*Math.sin(angle()), 70')
text=text.replace('camera(-590,()=>-.2+.6*u(2),P.blue)','camera(-590,()=>-.8+(Math.atan2(-80,370)+.8)*u(2),P.blue)')
text=text.replace('camera(()=>310+24*Math.sin(t()*4),()=>.4+.09*Math.sin(t()*4),P.red)', 'camera(()=>310+24*Math.sin(t()*4),()=>Math.atan2(-80,370-24*Math.sin(t()*4))+.045*Math.sin(t()*4),P.red,()=>Math.hypot(370-24*Math.sin(t()*4),80))')
text=text.replace('[[340,120,65],[520,120,65]]','[[286,120,65],[334,120,65]]')
assert text!=src.read_text('utf-8') and '240*Math' not in text
dest.write_text(text,'utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=dict(schemaVersion=1,status='prepared-only-scene02-target-direction-repair',sourceHeldReview='two-target-held-observation-v2.json',sources=[dict(id='02',source=dest.relative_to(ROOT).as_posix(),frames=2338,sha256=sha(dest))],goalReuse=dict(id='06b',path='shared/output/unpublished-teaching-clarity-revision/motion/two-target-repair-v2/scene-06b.mp4',sha256='542232598e0461d3268c03e3e1df204751aa8c213b1aad70ccb393a085d9cb08'),originalV2SourcePreservedSha256=sha(src),pcmAudioCaptionsTimingChanged=False,allFinalPixelsApproved=False)
(R/'targeted-visual-repair-plan-v3.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
worker=(B/'render-motion-two-targets-v2.cjs').read_text('utf-8').replace('two-target-repair-v2','aim-target-repair-v3').replace('targeted-visual-repair-plan-v2.json','targeted-visual-repair-plan-v3.json').replace('two-target-render-execution-v2.json','aim-target-render-execution-v3.json').replace('rendering-only-two-held-targets','rendering-only-scene02-target-direction').replace('rendered-two-targets-pending-current-captioned-pixels','rendered-scene02-target-direction-pending-current-captioned-pixels')
assert not (B/'render-motion-aim-target-v3.cjs').exists();(B/'render-motion-aim-target-v3.cjs').write_text(worker,'utf-8')
print(json.dumps(dict(prepared=True,newTtsOrAsr=0,onlyScene02=True)))

"""Prepare scoped CPU workers only; do not launch rendering or an ASR model."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
old=ROOT/'production/batches/unpublished-teaching-clarity-revision'
R='projects/motion-sickness-games/production/revision-cross-game-four-v1'
def once(s,a,b):assert s.count(a)==1,a;return s.replace(a,b,1)
s=(old/'render-motion-two-targets-v2.cjs').read_text('utf-8-sig')
s=s.replace('projects/motion-sickness-games/production/revision-teaching-clarity-v1',R)
s=s.replace('shared/output/unpublished-teaching-clarity-revision/motion/two-target-repair-v2','shared/output/cross-game-example-coverage/motion/structural-prototypes-v1')
s=s.replace('targeted-visual-repair-plan-v2.json','structural-prototype-plan-v1.json')
s=s.replace('narration-tts-waiting-v1.json','narration-tts-waiting-v2.json')
s=s.replace('two-target-render-execution-v2.json','structural-prototype-render-execution-v1.json')
s=s.replace('rendering-only-two-held-targets','rendering-three-silent-structural-prototypes')
s=s.replace('rendered-two-targets-pending-current-captioned-pixels','rendered-three-silent-prototypes-awaiting-direct-structural-pixel-review')
s=s.replace('pcmOrAudioOrCaptionsOrGameplayChanged:false','pcmOrAudioOrCaptionsOrGameplayChanged:false,measuredNarrationTimed:false,finalTimingApproved:false')
p=B/'render-motion-four-structural-prototypes-v1.cjs';assert not p.exists();p.write_text(s,'utf-8')
s=(old/'review-orientation-additive-voice-v2.py').read_text('utf-8-sig')
s=s.replace('projects/game-math-orientation-matrices/revision-teaching-clarity-v1',R)
s=s.replace('game-math-orientation-matrices','motion-sickness-games')
s=s.replace("len(tts['results'])==6","len(tts['results'])==3")
s=s.replace("len(script['scenes'])==6 and sum(len(x['lines']) for x in script['scenes'])==22","len(script['scenes'])==3 and sum(len(x['lines']) for x in script['scenes'])==15")
s=s.replace("len(plan['contexts'])==22","len(plan['contexts'])==15")
s=s.replace('shared/output/unpublished-teaching-clarity-revision/orientation/additive-contexts-v1','shared/output/cross-game-example-coverage/motion/additive-contexts-v1')
s=s.replace('original24PCM','original14PCM')
a="    qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)\n    item=next(x for x in q['items'] if x['slug']=='motion-sickness-games')\n    item.update(status=cp['stage'],currentExecution=cp['ownedJob'],actualReplacementVideoId=None)\n    q['execution'].update(currentSlug='motion-sickness-games',stage=cp['stage'],ownedJob=cp['ownedJob'],next=cp['next'])\n"
b="    qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)\n    q['currentMotionReview'].update(status=cp['stage'],ownedJob=cp['ownedJob'],actualReplacementVideoId=None,next=cp['next'])\n"
s=once(s,a,b)
p=B/'review-motion-four-additive-voice-v1.py';assert not p.exists();p.write_text(s,'utf-8')
print('Scoped CPU2 prototype and3whole/15complete-context ASR workers prepared; execution/model0.')

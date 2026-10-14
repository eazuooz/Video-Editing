"""Prepare read-only restoration verification and serial CPU ASR, without models."""
from pathlib import Path
import py_compile
B=Path(__file__).resolve().parent
src=(B/'verify-motion-voice-resume-v1.py').read_text('utf8')
replacements={
    "projects/motion-sickness-games/production/revision-teaching-clarity-v1":"projects/game-math-orientation-matrices/revision-teaching-clarity-v1",
    "assert args.session_id == 83518, 'Use only the original serialized request session.'":"session = read(R/'narration-tts-session-v1.json')\nassert args.session_id == session['sessionId'] == 18332, 'Use only the actual original serialized request session.'",
    "state['total'] == 2":"state['total'] == 6",
    "{'00a', '06b'}":"{'02a','06a','09a','13a','16a','21a'}",
    "history['project'] == 'motion-sickness-games'":"history['project'] == 'game-math-orientation-matrices'",
    "allTwoCurrentPcmHashesMatched=True, all26ProtectedInputsMatched=True":"allSixCurrentPcmHashesMatched=True, all47ProtectedInputsMatched=True",
    "original12PcmRegenerated=0":"original24PcmRegenerated=0",
    "Actual two-scene exit0":"Actual six-scene exit0"}
for old,new in replacements.items():
    assert old in src,old
    src=src.replace(old,new)
dest=B/'verify-orientation-voice-resume-v1.py';assert not dest.exists();dest.write_text(src,'utf8');py_compile.compile(str(dest),doraise=True)
src=(B/'review-motion-additive-voice-v1.py').read_text('utf8')
replacements={
    "projects/motion-sickness-games/production/revision-teaching-clarity-v1":"projects/game-math-orientation-matrices/revision-teaching-clarity-v1",
    "tts['actualOuterSession']==83518 and len(tts['results'])==2":"tts['actualOuterSession']==18332 and len(tts['results'])==6",
    "len(script['scenes'])==2 and sum(len(x['lines']) for x in script['scenes'])==6":"len(script['scenes'])==6 and sum(len(x['lines']) for x in script['scenes'])==22",
    "len(plan['contexts'])==6":"len(plan['contexts'])==22",
    "slug='motion-sickness-games'":"slug='game-math-orientation-matrices'",
    "original12PCM":"original24PCM",
    "x['slug']=='motion-sickness-games'":"x['slug']=='game-math-orientation-matrices'",
    "currentSlug='motion-sickness-games'":"currentSlug='game-math-orientation-matrices'",
    "shared/output/unpublished-teaching-clarity-revision/motion/additive-contexts-v1":"shared/output/unpublished-teaching-clarity-revision/orientation/additive-contexts-v1"}
for old,new in replacements.items():
    assert old in src,old
    src=src.replace(old,new)
dest=B/'review-orientation-additive-voice-v1.py';assert not dest.exists();dest.write_text(src,'utf8');py_compile.compile(str(dest),doraise=True)
print('Prepared actual-session restoration verifier and serial CPU2 whole6/independent22 ASR; model/audio job0.')

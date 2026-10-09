"""Prepare guarded CPU2 review workers, without loading models or altering audio."""
from pathlib import Path
P=Path(__file__).parent
src=(P/'review-revision-voice-v1.py').read_text('utf-8')
for a,b in [('narration-tts-execution-v2.json','narration-tts-execution-v3.json'),('research-handoff-verification-v2.json','research-handoff-verification-v3.json'),('narration-tts-request-v1.json','narration-tts-request-v3.json'),('==11','==2'),('>=11','>=5'),('>=5','>=1'),("f'voice-{a.mode}-asr-execution-v1.json'","f'voice-{a.mode}-asr-execution-v3.json'"),("f'voice-{a.mode}-asr-v1'","f'voice-{a.mode}-asr-v3'"),("f'voice-{a.mode}-asr-v1.log'","f'voice-{a.mode}-asr-v3.log'"),("f'voice-{a.mode}-asr-session-v1.json'","f'voice-{a.mode}-asr-session-v3.json'"),("f'voice-{a.mode}-asr-plan-v1.json'","f'voice-{a.mode}-asr-plan-v3.json'"),('voice-whole-asr-execution-v1.json','voice-whole-asr-execution-v3.json'),('revision-balatro60-v2/voice-contexts-v1','revision-balatro60-v2/voice-contexts-v3')]:src=src.replace(a,b)
# Explicit counts keep contexts complete and the single repaired join independent.
src=src.replace("assert len(inputs)>=1 if a.mode=='contexts' else len(inputs)>=1","assert len(inputs)==5 if a.mode=='contexts' else len(inputs)==1")
dst=P/'review-revision-voice-v3.py';assert not dst.exists();dst.write_text(src,'utf-8')
src=(P/'record-revision-asr-session-v1.py').read_text('utf-8').replace("f'voice-{a.mode}-asr-execution-v1.json'","f'voice-{a.mode}-asr-execution-v3.json'").replace("f'voice-{a.mode}-asr-session-v1.json'","f'voice-{a.mode}-asr-session-v3.json'")
dst=P/'record-revision-asr-session-v3.py';assert not dst.exists();dst.write_text(src,'utf-8')
import py_compile
for name in ['render-balatro60-revision-voice-v3.py','verify-revision-voice-research-resume-v3.py','review-revision-voice-v3.py','record-revision-asr-session-v3.py']:py_compile.compile(str(P/name),doraise=True)
print('Prepared-only: guarded whole2, complete sentence5, exact repaired join1 CPU2 workers. Models0.')

"""Create a scoped verifier from the successful original research verifier."""
from pathlib import Path
import py_compile
BASE=Path(__file__).resolve().parent
source=(BASE/'verify-own-voice-research-resume-v2.py').read_text('utf-8-sig')
changes={
 "BASE/'narration-tts-session-v2.json'":"BASE/'voice-clarity-v2/session.json'",
 "BASE/'narration-tts-execution-v2.json'":"BASE/'voice-clarity-v2/execution.json'",
 "len(state['results'])==state['total']==12":"len(state['results'])==state['total']==2",
 "allTwelveCurrentPcmHashesMatched=True":"allTwoReplacementPcmHashesMatched=True",
 "BASE/'research-handoff-verification-v2.json'":"BASE/'voice-clarity-v2/research-resume-verification.json'",
 "Actual twelve-scene voice exit0":"Actual two-paragraph voice exit0"
}
for a,b in changes.items():
 assert source.count(a)==1,(a,source.count(a));source=source.replace(a,b)
marker="for r in state['results']:assert sha(ROOT/r['path'])==r['sha256']"
assert source.count(marker)==1
source=source.replace(marker,marker+"\nrequest=read(BASE/'voice-clarity-v2/request.json')\nfor row in request['protectedInputs']:assert sha(ROOT/row['path'])==row['sha256'],row['path']")
p=BASE/'verify-voice-clarity-research-resume-v2.py';assert not p.exists()
p.write_text(source,'utf-8');py_compile.compile(str(p),doraise=True)
print('Scoped verifier compiled. Prepared only; no process/control/state verification executed.')

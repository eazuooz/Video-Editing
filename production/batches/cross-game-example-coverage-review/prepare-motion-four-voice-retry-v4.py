"""Prepare versioned request/verifier after v3 closed before model load."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
S=ROOT/'production/batches/cross-game-example-coverage-review'
source=(S/'render-motion-four-additions-v3.py').read_text('utf-8-sig')
source=source.replace('narration-tts-execution-v3','narration-tts-execution-v4').replace('narration-tts-session-v3','narration-tts-session-v4').replace('narration-tts-waiting-v3','narration-tts-waiting-v4')
source=source.replace("failed=read(R/'research-handoff-premodel-failure-verification-v2.json')","failed=read(R/'research-handoff-premodel-timeout-verification-v3.json')")
needle="assert failed['restorationVerified'] and failed['newPcmCount']==0"
assert source.count(needle)==1
source=source.replace(needle,needle+"\nretry=read(R/'voice-retry-resource-verification-v4.json')\nassert retry['foreignRestorationVerified'] and retry['stableGpuIdle20SecondsVerified'] and retry['all68ProtectedHashesMatched']\nassert (datetime.now(timezone.utc)-datetime.fromisoformat(retry['observedAt'])).total_seconds()<240, 'Read fresh resources before another voice request.'")
target=S/'render-motion-four-additions-v4.py';assert not target.exists();target.write_text(source,'utf-8')
v=(S/'verify-motion-four-voice-resume-v3.py').read_text('utf-8-sig')
v=v.replace('narration-tts-session-v3','narration-tts-session-v4').replace('narration-tts-execution-v3','narration-tts-execution-v4').replace('research-handoff-verification-v3','research-handoff-verification-v4')
target=S/'verify-motion-four-voice-resume-v4.py';assert not target.exists();target.write_text(v,'utf-8')
print('V4 request/verifier prepared; model/lease/PCM creation0. Execution requires fresh stable-GPU evidence.')

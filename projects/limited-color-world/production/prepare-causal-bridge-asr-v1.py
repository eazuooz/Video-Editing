from pathlib import Path
import hashlib
P=Path(__file__).resolve().parent
source=(P/'review-current-voice-v1.py').read_text('utf-8')
replacements={
 "current-{args.mode}":"causal-bridge-{args.mode}",
 "narration-tts-execution-v1.json":"causal-bridge-tts-execution-v1.json",
 "research-handoff-verification-v1.json":"causal-bridge-research-handoff-verification-v1.json",
 "narration-tts-request-v1.json":"causal-bridge-tts-request-v1.json",
 "len(tts['results']) == 8":"len(tts['results']) == 3",
 "script/narration.ko.json":"script/causal-bridges.v1.ko.json",
 "script/narration.en.json":"script/causal-bridges.v1.en.json",
 "len(script['scenes']) == 8":"len(script['scenes']) == 3",
 "sum(len(x['lines']) for x in script['scenes']) == 24":"sum(len(x['lines']) for x in script['scenes']) == 3",
 "current-whole-asr-execution-v1.json":"causal-bridge-whole-asr-execution-v1.json",
 "current-independent-context-plan-v1.json":"causal-bridge-independent-context-plan-v1.json",
 "current-targeted-leading-context-plan-v1.json":"causal-bridge-targeted-leading-context-plan-v1.json",
 "len(plan['contexts']) >= 8":"len(plan['contexts']) == 3",
 "current-eight-voice-{args.mode}-CPU-ASR":"causal-three-bridge-voice-{args.mode}-CPU-ASR",
 "Read every complete recognized text against the current script and PCM":"Read every new bridge complete recognized text against its current script and PCM; preserve original8PCM/32ASR"
}
for a,b in replacements.items():assert a in source,a;source=source.replace(a,b)
# A bridge request protects retained PCM and immutable content, not execution
# logs. Full and isolated padded paragraph readings are separate transcriptions.
target=P/'review-causal-bridge-voice-v1.py';assert not target.exists();target.write_text(source,'utf-8')
print(hashlib.sha256(target.read_bytes()).hexdigest())

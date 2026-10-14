"""Prepare fresh resource reference and exact one-item closure verifier; no synthesis."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
observer=B/'observe-orientation-07b-guide-voice-resource-v2.py';assert not observer.exists()
text=(B/'observe-orientation-07b-guide-voice-resource-v1.py').read_text('utf-8').replace('resource-before-07b-guide-repair-voice-v1','resource-before-07b-guide-repair-voice-v2')
observer.write_text(text,'utf-8')
wrapper=B/'render-orientation-07b-guide-repair-v1.py';assert not (O/'narration-07b-guide-repair-execution-v1.json').exists()
text=wrapper.read_text('utf-8').replace('resource-before-07b-guide-repair-voice-v1','resource-before-07b-guide-repair-voice-v2').replace('Four additive scenes and one exact paragraph candidate; preserve original PCM.','One newly clarified observation-guide paragraph candidate; preserve original PCM.').replace('compare allfive currentwhole PCM and19independent contexts','compare this one candidate and the complete current07b splice/seam')
wrapper.write_text(text,'utf-8')
verifier=B/'verify-orientation-07b-guide-voice-exit-v1.py';assert not verifier.exists()
text=(B/'verify-orientation-cross-game-voice-exit-v1.py').read_text('utf-8')
for a,b in [('narration-cross-game-repair','narration-07b-guide-repair'),('cross-game-repair-voice-closure','07b-guide-repair-voice-closure'),('resource-before-cross-game-repair-voice-v1','resource-before-07b-guide-repair-voice-v2'),('cross-game-repair-owned-idle-guard','07b-guide-repair-owned-idle-guard'),("state['total']==5","state['total']==1"),("len(state['results'])==5","len(state['results'])==1"),('five-items-voice-closed-awaiting-current-ASR','one-guide-candidate-closed-awaiting-current-ASR'),('crossGameVoiceClosure=out.relative_to(ROOT).as_posix()','guideCandidateVoiceClosure=out.relative_to(ROOT).as_posix()'),("cp['crossGameVoiceClosure']","cp['guideCandidateVoiceClosure']"),('crossGameVoiceClosure=','guideCandidateVoiceClosure='),('Fresh CPU resource then wholefive currentPCM ASR once; directly compare allfulltext and prepare19 complete independent contexts. Original24+6PCM unchanged;21r adoption remains false.','FreshCPU resource then onecandidate wholeASR once; if complete, make separate07b splice preserving firstfive paragraphs bytes and review currentwhole+complete seam once. Candidate adoption/finalmixed approval remain false.')]:text=text.replace(a,b)
verifier.write_text(text,'utf-8')
print('PreparedV2 readonly observer / never-run1item wrapper exactV2 resource / one-item closure verifier. Modelrequest0.')

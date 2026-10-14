"""Prepare a scoped copy of the established owned handoff/verification wrappers."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
OLD = ROOT / 'production/batches/unpublished-teaching-clarity-revision'
R = 'projects/motion-sickness-games/production/revision-cross-game-four-v1'

def replace_once(s, old, new):
    assert s.count(old) == 1, old
    return s.replace(old, new, 1)

s = (OLD / 'render-orientation-additions-v2.py').read_text('utf-8-sig')
s = s.replace('projects/game-math-orientation-matrices/revision-teaching-clarity-v1', R)
s = s.replace('game-math-orientation-matrices', 'motion-sickness-games')
s = replace_once(s, 'import argparse,hashlib,json,os,sys,time,traceback', 'import argparse,hashlib,json,os,sys,time,traceback,subprocess')
s = replace_once(s,
    "failed=read(R/'narration-tts-execution-v1.json'); restored=read(R/'research-handoff-verification-v1.json')\nassert failed['actualOuterExitCode']==1 and failed['actualOuterSession']==18332 and failed['results']==[] and restored['restorationVerified']\n",
    "NODE=ROOT/'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'\nNODE=Path('C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')\ndef current_duplicate_check():\n    subprocess.run([str(NODE),'scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],cwd=ROOT,check=True)\ncurrent_duplicate_check()\n")
s = s.replace("narration-tts-execution-v2.json", "narration-tts-execution-v1.json")
s = s.replace("narration-tts-session-v2.json", "narration-tts-session-v1.json")
s = s.replace("narration-tts-waiting-v2.json", "narration-tts-waiting-v1.json")
s = replace_once(s, "assert request['total']==6 and request['paragraphs']==22", "assert request['total']==3 and request['paragraphs']==15")
s = replace_once(s,
    "bank=read(R/'source-selection-preflight-v2.json')\nassert bank['sourceSelectionPreflightApproved'] and bank['maximumUniqueFrames']==21370\nassert bank['all16NormalPlaybackWindowsExecuted'] and not bank['entireFinalPixelsApproved']",
    "bank=read(R/'sources/source-action-bank-v1.json')\nassert bank['sourcePlanningApproved'] and len(bank['actions'])==8\nassert not bank['finalCutAllocationApproved'] and not bank['finalCueAndMovingAnnotationApproval']")
s = replace_once(s,
    "ROOT/request['scriptReview'],R/'source-selection-preflight-v2.json',\n    R/'causal-flow-and-annotation-plan-v1.json',R/'observation-pilot-direct-review-v4.json',R/'observation-point-keyframes-v3.json'",
    "ROOT/request['scriptReview'],R/'sources/source-action-bank-v1.json',\n    R/'causal-flow-and-annotation-plan-v1.json',R/'native-and-clearance-direct-review-v1.json',\n    R/'planning/game-example-coverage.json',R/'sources/game-candidates.json'")
s = replace_once(s, "for x in protected: assert sha(ROOT/x['path'])==x['sha256'],x['path']\nlease=read(leasePath)",
    "for x in protected: assert sha(ROOT/x['path'])==x['sha256'],x['path']\ncurrent_duplicate_check()\nlease=read(leasePath)")
s = s.replace('total=6,results=[]', 'total=3,results=[]')
s = s.replace('total=6,exitCode=', 'total=3,exitCode=')
s = s.replace("assert len(state['results'])==6", "assert len(state['results'])==3")
s = s.replace('original24PcmRegenerated=0', 'original14PcmRegenerated=0')
s = s.replace('Prepared6newbridges/22pairedparagraphs;24approvedPCM preserved.', 'Prepared3newcomparisons/15pairedparagraphs;14approvedPCM preserved.')
s = s.replace('Six bridges measured; original24PCM preserved.', 'Three comparisons measured; original14PCM preserved.')
s = s.replace('serialized-six-bridges-request-before-model', 'serialized-three-comparisons-request-before-model')
s = s.replace('six-bridges-measured-awaiting-whole-current-ASR-and-research-resume', 'three-comparisons-measured-awaiting-whole-current-ASR-and-research-resume')
s = s.replace('six whole current-PCM ASR texts', 'three whole current-PCM ASR texts')
s = s.replace('Six approved additive bridges', 'Three approved additive comparisons')
s = s.replace("NODE=ROOT/'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'\n", '')
assert 'orientation' not in s.lower() and '18332' not in s and '24Pcm' not in s
target = B / 'render-motion-four-additions-v1.py'
assert not target.exists()
target.write_text(s, 'utf-8')

v = (OLD / 'verify-orientation-voice-resume-v2.py').read_text('utf-8-sig')
v = v.replace('projects/game-math-orientation-matrices/revision-teaching-clarity-v1', R)
v = v.replace('game-math-orientation-matrices', 'motion-sickness-games')
v = v.replace('narration-tts-session-v2.json', 'narration-tts-session-v1.json')
v = v.replace('narration-tts-execution-v2.json', 'narration-tts-execution-v1.json')
v = v.replace('research-handoff-verification-v2.json', 'research-handoff-verification-v1.json')
v = replace_once(v, "expected_ids={'02a','06a','09a','13a','16a','21a'}", "expected_ids={'07b','08b','11b'}")
v = replace_once(v, "assert state['total']==6 and len(state['protectedInputs'])==47", "assert state['total']==3 and len(state['protectedInputs'])==68")
v = v.replace("len(state['results'])==6", "len(state['results'])==3")
v = v.replace('allSixCurrentPcmHashesMatched', 'allThreeCurrentPcmHashesMatched')
v = v.replace('all47ProtectedInputsMatched', 'all68ProtectedInputsMatched')
v = v.replace('original24PcmRegenerated', 'original14PcmRegenerated')
assert 'orientation' not in v.lower()
target = B / 'verify-motion-four-voice-resume-v1.py'
assert not target.exists()
target.write_text(v, 'utf-8')
print('Prepared single3PCM wrapper and actual-exit/owned-research verification only; model/GPU/process0.')

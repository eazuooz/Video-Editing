"""Prepare one guarded six-bridge worker. This does not start TTS."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
p = B/'render-orientation-additions-v1.py'
assert not p.exists(), 'Inspect an existing worker and its actual session before any retry.'
s = (B/'render-motion-additions-v1.py').read_text('utf-8-sig')
s = s.replace('Two approved additive scenes', 'Six approved additive bridges')
s = s.replace('projects/motion-sickness-games/production/revision-teaching-clarity-v1',
              'projects/game-math-orientation-matrices/revision-teaching-clarity-v1')
s = s.replace('motion-sickness-games', 'game-math-orientation-matrices')
s = s.replace("request['total']==2 and request['paragraphs']==6", "request['total']==6 and request['paragraphs']==22")
s = s.replace("bank=read(R/'sources/source-action-bank-v1.json')\nassert bank['sourceSelectionPreflightApproved'] and bank['maximumUniqueFrames']==1515",
    "bank=read(R/'source-selection-preflight-v2.json')\nassert bank['sourceSelectionPreflightApproved'] and bank['maximumUniqueFrames']==21370\nassert bank['all16NormalPlaybackWindowsExecuted'] and not bank['entireFinalPixelsApproved']")
s = s.replace("REQUEST,R/'tts-manifest-v1.json',R/'script/additions.ko.json',R/'script/additions.en.json',\n    R/'script/narration.ko.json',R/'script/narration.en.json',R/'paired-script-direct-review-v1.json',\n    R/'sources/source-action-bank-v1.json',R/'sources/native-source-direct-review-v1.json'",
    "REQUEST,R/'tts-manifest-v1.json',R/'script/additions.ko.json',R/'script/additions.en.json',\n    R/'paired-additive-script-direct-review-v1.json',R/'source-selection-preflight-v2.json',\n    R/'causal-flow-and-annotation-plan-v1.json',R/'observation-pilot-direct-review-v4.json',R/'observation-point-keyframes-v3.json'")
s = s.replace("review=read(ROOT/request['scriptReview'])", "review=read(ROOT/request['scriptReview'])")
s = s.replace('Prepared2newscenes/6pairedparagraphs;12approvedPCM preserved.', 'Prepared6newbridges/22pairedparagraphs;24approvedPCM preserved.')
s = s.replace('serialized-two-additions', 'serialized-six-bridges')
s = s.replace('whole2plusindependent6', 'whole6pluscomplete-independent-contexts')
s = s.replace("total=2", "total=6")
s = s.replace("len(state['results'])==2", "len(state['results'])==6")
s = s.replace('original12PcmRegenerated', 'original24PcmRegenerated')
s = s.replace('two-additions-measured', 'six-bridges-measured')
s = s.replace('Two additions measured; original12PCM preserved.', 'Six bridges measured; original24PCM preserved.')
# This project's paired-review path differs from the motion revision.
s = s.replace("R/'paired-script-direct-review-v1.json'", "R/'paired-additive-script-direct-review-v1.json'")
s = s.replace("scriptReview\'])", "scriptReview\'])")
assert "request['total']==6" in s and "maximumUniqueFrames']==21370" in s
assert "sources/source-action-bank-v1" not in s and "original12" not in s
p.write_text(s, 'utf-8')
print('Prepared single six-bridge worker; no state/model/GPU/research action.')

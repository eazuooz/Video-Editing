"""Prepare only; ASR must use corrected current37 text and actual selected PCM."""
from pathlib import Path
import ast
root=Path(__file__).resolve().parents[3]
source=root/'production/research/game-lighting-history/review-part1-guided-actions-v172.py'
target=root/'production/research/game-lighting-history/review-part1-selected-actions-v182.py'
if target.exists():raise RuntimeError('Preserve prepared current worker')
code=source.read_text('utf-8-sig')
changes={
 'part1-guided-actions-asr-execution-v172.json':'part1-selected-actions-asr-execution-v182.json',
 'local/part1-guided-actions-asr-v172':'local/part1-selected-actions-asr-v182',
 'part1-guided-actions-tts-request-v169.json':'part1-selected-current-tts-request-v181.json',
 'physical-part1-guided-actions.koen.v169.json':'physical-part1-guided-actions.koen.v175.json',
 'part1-guided-actions-tts-execution-v169.json':'part1-selected-current-tts-execution-v181.json',
 'part1-guided-actions-asr-plan-v172.json':'part1-selected-actions-asr-plan-v182.json',
 "['review-part1-guided-actions-v172.py','render-part1-guided-actions-v169.py','render-part1-scoped-tail-v173.py']":"['review-part1-selected-actions-v182.py','review-part1-guided-actions-v172.py','render-part1-guided-actions-v169.py','render-part1-scoped-repair-v176.py']"
}
for old,new in changes.items():
 if old not in code:raise RuntimeError('Missing binding '+old)
 code=code.replace(old,new)
needle=" if tts.get('requestSha256')!=sha(reqpath):raise RuntimeError('Selected execution is not bound to current37 request')\n"
code=code.replace(needle,needle+" if req['script']['path']!=rel(scriptpath) or req['script']['sha256']!=sha(scriptpath):raise RuntimeError('Current corrected full37 script mismatch')\n")
ast.parse(code);target.write_text(code,'utf-8')
print('Prepared corrected37 whole/context CPU2 recognizer only; no model or ASR started.')

"""Prepare a guarded CPU worker only. It does not recognize or change PCM."""
from pathlib import Path
import ast

root = Path(__file__).resolve().parents[3]
source = root / 'production/research/game-lighting-history/review-guided-actions-v76.py'
target = root / 'production/research/game-lighting-history/review-part1-guided-actions-v172.py'
if target.exists():
    raise RuntimeError('Preserve prepared worker')
code = source.read_text('utf-8-sig')
start = code.index(' if INCLUDE_HOGWARTS:\n')
end = code.index(' def previous(identifier):\n', start)
code = code[:start] + code[end:]
code = code.replace("INCLUDE_HOGWARTS='--include-hogwarts' in sys.argv\n", '')
code = code.replace("STATE=BASE/('guided-observation-asr-execution-v88.json' if INCLUDE_HOGWARTS else 'guided-actions-asr-execution-v76.json')", "STATE=BASE/'part1-guided-actions-asr-execution-v172.json'")
code = code.replace("FOLDER=BASE/('local/guided-observation-asr-v88' if INCLUDE_HOGWARTS else 'local/guided-actions-asr-v76')", "FOLDER=BASE/'local/part1-guided-actions-asr-v172'")
code = code.replace('part3-guided-actions-tts-request-v69.json', 'part1-guided-actions-tts-request-v169.json')
code = code.replace('physical-part3-guided-actions.koen.v69.json', 'physical-part1-guided-actions.koen.v169.json')
code = code.replace('part3-guided-actions-tts-execution-v69.json', 'part1-guided-actions-tts-execution-v169.json')
code = code.replace("  target=BASE/('guided-observation-asr-plan-v88.json' if INCLUDE_HOGWARTS else 'guided-actions-asr-plan-v76.json')", "  target=BASE/'part1-guided-actions-asr-plan-v172.json'")
code = code.replace("['review-guided-actions-v76.py','render-part3-guided-actions-v69.py','render-guided-tail-repair-v83.py','render-hogwarts-observation-v85.py','render-guided-followup-batch-v87.py']", "['review-part1-guided-actions-v172.py','render-part1-guided-actions-v169.py','render-part1-scoped-tail-v173.py']")
# The same PID can later identify an unrelated process. Resume requires both a
# recorded end and a current identity comparison, never a PID-only decision.
needle = "  if not prior.get('endedAt'):raise RuntimeError('Observe ended previous worker before resume')\n"
addition = """  identity=prior.get('actualIdentity',{})
  if psutil.pid_exists(identity.get('pid',-1)):
   old=psutil.Process(identity['pid'])
   if abs(old.create_time()-identity.get('createTime',0))<0.001 and old.cmdline()==identity.get('command'):
    raise RuntimeError('Recorded previous worker is still alive; do not duplicate recognition')
"""
if needle not in code:
    raise RuntimeError('Expected resume gate missing')
code = code.replace(needle, needle + addition)
code = code.replace("plan=dict(preparedAt=stamp(),request=", "plan=dict(physicalPart='game-lighting-history-04-1',preparedAt=stamp(),request=")
ast.parse(code)
target.write_text(code, 'utf-8')
print('Prepared one CPU2/GPU0 worker:37 whole +37 complete neighbouring contexts; not started')

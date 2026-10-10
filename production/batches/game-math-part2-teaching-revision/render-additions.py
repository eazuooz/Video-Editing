"""Run only explicitly authorized additive narration under the existing GPU guard."""
from pathlib import Path
import json,runpy,sys
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
q=json.loads((B/'queue.json').read_text(encoding='utf8'))
if q['execution']['mode']!='active' or q['execution']['currentSlug']!='game-math-quaternion-operations':
 raise SystemExit('Current additive revision is not authorized to run; preserve its checkpoint.')
audit=json.loads((B/'quaternion-pretts-math-audit.json').read_text(encoding='utf8'))
assert audit['originalSceneOrderAndAllFieldsExact'] and audit['originalContractExact'] and all(x['passed'] for x in audit['checks'])
sys.path.insert(0,str(ROOT/'production/batches/game-math-part2-full-series'))
runpy.run_path(str(ROOT/'production/batches/game-math-part2-full-series/render-voice.py'),run_name='__main__')

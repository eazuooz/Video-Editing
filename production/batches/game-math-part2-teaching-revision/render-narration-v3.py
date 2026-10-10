"""Authorized new material only, using the same cooperative GPU/voice renderer."""
from pathlib import Path
import json,runpy,sys,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug='game-math-quaternion-teaching-additions-v3'
q=json.loads((B/'queue.json').read_text(encoding='utf8'))
assert q['execution']['mode']=='active' and q['execution']['currentSlug']=='game-math-quaternion-operations'
assert sys.argv[sys.argv.index('--project')+1]==slug
audit=json.loads((B/'quaternion-v3-pretts-audit.json').read_text(encoding='utf8'))
assert audit['originalAuditPreserved'] and not audit['baseline26ScenesAnd155KoLinesChanged']
for lang,sha in audit['scriptSha256'].items():
    assert hashlib.sha256((ROOT/f'projects/{slug}/script/narration.{lang}.json').read_bytes()).hexdigest()==sha
sys.path.insert(0,str(ROOT/'production/batches/game-math-part2-full-series'))
runpy.run_path(str(ROOT/'production/batches/game-math-part2-full-series/render-voice.py'),run_name='__main__')

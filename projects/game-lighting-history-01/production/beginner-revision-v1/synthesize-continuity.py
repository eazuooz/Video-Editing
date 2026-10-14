"""One batch of approved-voice transition takes; never rebuild baseline PCM."""
import pathlib,sys,runpy,json,hashlib
R=pathlib.Path(__file__).resolve().parents[4];H=pathlib.Path(__file__).parent
runpy.run_path(str(H/'production-authority.py'))['require_selected_production']()
d=json.loads((H/'current-policy-changes.json').read_text(encoding='utf8'))
for lang in ['ko','en']:
 assert hashlib.sha256((R/f'projects/game-lighting-history-01/script/continuity-v2.{lang}.json').read_bytes()).hexdigest()==d['scriptHashes'][lang]
sys.path.insert(0,str(R/'qwen3-tts'))
import render_narration as renderer
repair='--repair' in sys.argv
renderer.configure_project('game-lighting-history-01',(H/('continuity-repair-tts.project.json' if repair else 'continuity-tts.project.json')).relative_to(R).as_posix())
renderer.load_tts_dependencies();renderer.torch.set_num_threads(4);renderer.torch.manual_seed(20261015)
items=renderer.build_render_items(renderer.load_jobs())
assert len(items)==(4 if repair else 14)
if repair:
 from dataclasses import replace
 renderer.torch.manual_seed(202610151)
 items=[replace(x,text=x.text.replace('퀘이크','Quake')) for x in items]
# Existing takes are never regenerated merely because a tail heuristic flags them.
items=[x for x in items if not x.path.exists()]
renderer.MAX_RENDER_ATTEMPTS=1
renderer.render_chunks(items,1)

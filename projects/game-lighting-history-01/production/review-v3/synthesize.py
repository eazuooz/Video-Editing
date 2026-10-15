"""Render only the eight selected RNM explanation paragraphs."""
import pathlib,sys,runpy,json
R=pathlib.Path(__file__).resolve().parents[4];H=pathlib.Path(__file__).parent
runpy.run_path(str(H.parent/'beginner-revision-v1/production-authority.py'))['require_selected_production']()
d=json.loads((H/'design.json').read_text(encoding='utf8'));assert d['quality']['scriptKoEnReviewed']
sys.path.insert(0,str(R/'qwen3-tts'))
import render_narration as renderer
renderer.configure_project('game-lighting-history-01',(H/'tts.project.json').relative_to(R).as_posix())
renderer.load_tts_dependencies();renderer.torch.set_num_threads(4);renderer.torch.manual_seed(202610152)
items=renderer.build_render_items(renderer.load_jobs());assert len(items)==8
items=[x for x in items if not x.path.exists()]
renderer.MAX_RENDER_ATTEMPTS=1
renderer.render_chunks(items,1)

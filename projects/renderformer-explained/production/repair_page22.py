"""Preserve v1; render a complete replacement take for the suspected missing opening."""
from pathlib import Path
import sys
from dataclasses import replace
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'qwen3-tts'))
import render_narration as tts
tts.configure_project('renderformer-explained')
tts.load_tts_dependencies()
tts.torch.set_num_threads(4)
target=ROOT/'shared/output/narration/renderformer-explained/qwen3-1.7b-balanced-v2-repair'
target.mkdir(exist_ok=True)
items=[replace(i,path=target/'22-scene.wav') for i in tts.build_render_items(tts.load_jobs()) if i.key.startswith('22-')]
assert len(items)==1
tts.render_chunks(items,1)

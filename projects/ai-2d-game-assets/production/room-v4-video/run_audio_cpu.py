"""One new paragraph, same approved voice/model, no GPU or global guard change."""
from pathlib import Path
import os,sys,runpy
os.environ['OMP_NUM_THREADS']='4';os.environ['MKL_NUM_THREADS']='4'
import torch
torch.set_num_threads(4);torch.set_num_interop_threads(1)
R=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(R/'qwen3-tts'))
sys.argv=[str(R/'qwen3-tts/render_narration.py'),'--project','ai-2d-game-assets','--manifest','projects/ai-2d-game-assets/production/room-v4-video/tts-manifest.json','--batch-size','1','--device','cpu']
runpy.run_path(str(R/'qwen3-tts/render_narration.py'),run_name='__main__')

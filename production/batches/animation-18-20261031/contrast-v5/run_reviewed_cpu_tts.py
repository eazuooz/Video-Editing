"""Same approved voice on bounded CPU while foreign GPU activity is present."""
from pathlib import Path
import os,sys,runpy
os.environ['OMP_NUM_THREADS']='4';os.environ['MKL_NUM_THREADS']='4'
import torch
set_threads=torch.set_num_threads
torch.set_num_threads=lambda n:set_threads(min(4,n))
torch.set_num_threads(4);torch.set_num_interop_threads(1)
H=Path(__file__).resolve().parent;R=H.parents[3];sys.path.insert(0,str(R/'qwen3-tts'))
sys.argv=[str(R/'qwen3-tts/render_narration.py'),'--project','animation-contrast-v5','--manifest',(H/'narration/released-tts-manifest.json').relative_to(R).as_posix(),'--batch-size','1','--device','cpu']
runpy.run_path(str(R/'qwen3-tts/render_narration.py'),run_name='__main__')

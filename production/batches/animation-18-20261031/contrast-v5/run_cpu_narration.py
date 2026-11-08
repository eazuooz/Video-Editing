"""CPU fallback for source-verified changes, preserving other editor/GPU work."""
from pathlib import Path
import os,sys,runpy,json
os.environ['OMP_NUM_THREADS']='4';os.environ['MKL_NUM_THREADS']='4'
import torch
torch.set_num_threads(4);torch.set_num_interop_threads(1)
H=Path(__file__).resolve().parent;R=H.parents[3]
c=json.loads((R/'shared/publishing/video-production-control.json').read_text('utf-8-sig'))['animationContrastRevision20261108']
assert c['fullLocalProductionAuthorized'] and c['candidateUserApproval']['text']=='이 목록으로 진행'
sys.path.insert(0,str(R/'qwen3-tts'))
sys.argv=[str(R/'qwen3-tts/render_narration.py'),'--project','animation-contrast-v5',
          '--manifest',(H/'narration/tts-manifest.json').relative_to(R).as_posix(),'--batch-size','1','--device','cpu']
runpy.run_path(str(R/'qwen3-tts/render_narration.py'),run_name='__main__')

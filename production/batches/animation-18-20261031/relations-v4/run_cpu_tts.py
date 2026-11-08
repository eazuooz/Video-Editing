"""Run the approved shared Qwen entrypoint without altering its global defaults."""
from pathlib import Path
import runpy,sys,torch,os
H=Path(__file__).resolve().parent;R=H.parents[3]
assert '--device' in sys.argv and sys.argv[sys.argv.index('--device')+1]=='cpu'
os.environ.update(OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4')
set_threads=torch.set_num_threads
torch.set_num_threads=lambda count:set_threads(min(int(count),4))
torch.set_num_threads(4)
target=R/'qwen3-tts/render_narration.py'
sys.path.insert(0,str(target.parent));sys.argv=[str(target),*sys.argv[1:]]
runpy.run_path(str(target),run_name='__main__')

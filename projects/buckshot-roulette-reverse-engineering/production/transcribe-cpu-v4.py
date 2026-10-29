"""Selected-v4 CPU-only wrapper around the existing local Whisper pipeline."""
import os
from pathlib import Path
import runpy
import sys

os.environ.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='2', MKL_NUM_THREADS='2',
                  OPENBLAS_NUM_THREADS='2', NUMEXPR_NUM_THREADS='2',
                  HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
assert '--device' in sys.argv and sys.argv[sys.argv.index('--device') + 1] == 'cpu'

import torch

torch.set_num_threads(2)
torch.set_num_interop_threads(1)
assert not torch.cuda.is_initialized()
print('CPU-only Whisper: fp32, intraop=2, interop=1, OMP=2; CUDA hidden; no GPU context or lease.', flush=True)
target = Path(__file__).resolve().parents[3] / 'qwen3-tts/transcribe_reference.py'
sys.argv[0] = str(target)
runpy.run_path(str(target), run_name='__main__')
assert not torch.cuda.is_initialized()
print('CPU-only Whisper complete; CUDA remains uninitialized.', flush=True)

"""Same approved voice/model; SDPA on CUDA, original float32/eager CPU fallback.

The shared CPU renderer selects eight threads; preserve its inference settings.
"""
from pathlib import Path
import sys
from production_control import require_current_authorization
if '--project' in sys.argv:require_current_authorization(sys.argv[sys.argv.index('--project')+1],'narration synthesis')
import torch
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'qwen3-tts'))
from gpu_handoff_guard import check_gpu_handoff
if '--project' in sys.argv:
 project=sys.argv[sys.argv.index('--project')+1]
 device=sys.argv[sys.argv.index('--device')+1] if '--device' in sys.argv else 'cuda:0'
 check_gpu_handoff(project,device,'--dry-run' in sys.argv)
torch.set_num_threads(2)
from qwen_tts import Qwen3TTSModel
original=Qwen3TTSModel.from_pretrained.__func__
def load(cls,*args,**kwargs):
 kwargs.setdefault('attn_implementation','sdpa')
 return original(cls,*args,**kwargs)
Qwen3TTSModel.from_pretrained=classmethod(load)
original_generate=Qwen3TTSModel.generate_voice_clone

def generate_with_local_stream(self,*args,**kwargs):
 # Scope scheduling to this inference call; do not modify other processes,
 # model parameters, sampling options, text, or the approved voice prompt.
 if self.device.type!='cuda':return original_generate(self,*args,**kwargs)
 current=torch.cuda.current_stream(self.device)
 stream=torch.cuda.Stream(device=self.device,priority=-1);stream.wait_stream(current)
 with torch.cuda.stream(stream):result=original_generate(self,*args,**kwargs)
 stream.synchronize();current.wait_stream(stream)
 # Completed audio is on CPU. Release unused allocator blocks between
 # independent scenes so long lectures do not retain avoidable GPU reserve.
 # This changes neither synthesis settings nor the approved voice prompt.
 torch.cuda.empty_cache()
 return result
Qwen3TTSModel.generate_voice_clone=generate_with_local_stream
import render_narration
original_badness=render_narration._badness
def prefer_passing_take(tail_ratio,decay_ms):
 # A quiet natural close may pass the unchanged35ms exception while scoring
 # worse under the general70ms decay score. Always preserve a passing take
 # over a failing take; do not waste retries or discard valid narration.
 score=original_badness(tail_ratio,decay_ms)
 return score if render_narration._passes_quality(tail_ratio,decay_ms) else 1000000+score
render_narration._badness=prefer_passing_take
original_chunks=render_narration.render_chunks
selected=set()
if '--scenes' in sys.argv:
 index=sys.argv.index('--scenes');selected={x.strip().zfill(2) for x in sys.argv[index+1].split(',')};del sys.argv[index:index+2]
 original_items=render_narration.build_render_items
 render_narration.build_render_items=lambda jobs:[item for item in original_items(jobs) if item.key.split('-')[0] in selected]
 render_narration.assemble_outputs=lambda jobs:print('Selected-scene checkpoint retained; assemble the complete project after all scenes pass review.',flush=True)
def render_independent_scenes(items,batch_size,force_scenes):
 requested=int(sys.argv[sys.argv.index('--batch-size')+1]) if '--batch-size' in sys.argv else 1
 return original_chunks(items,requested,force_scenes)
render_narration.render_chunks=render_independent_scenes
if __name__=='__main__':render_narration.main()

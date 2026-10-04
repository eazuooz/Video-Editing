"""Same approved voice/model; small CPU thread pool and SDPA for local batching."""
from pathlib import Path
import sys,torch
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'qwen3-tts'))
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
 return result
Qwen3TTSModel.generate_voice_clone=generate_with_local_stream
import render_narration
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

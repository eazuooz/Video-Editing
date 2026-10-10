"""Only reviewed episodes2–4 under the single cooperative batch lease."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'qwen3-tts'))
if '--project' not in sys.argv: raise SystemExit('Explicit reviewed episode required')
PROJECT=sys.argv[sys.argv.index('--project')+1]
if PROJECT not in ['game-lighting-history-02','game-lighting-history-03','game-lighting-history-04']:
    raise SystemExit('Unreviewed episode scope')
review=json.loads((ROOT/f'projects/{PROJECT}/production/script-input-review-v1.json').read_text(encoding='utf-8'))
if not all(review.get(k) is True for k in ['fullScriptDirectReread','allKoEnTextDirectlyReviewed','finalTtsInputWritten','overviewMatchesActualBody']):
    raise SystemExit('Full bilingual input/overview review required before model allocation')
for lang in ['ko','en']:
    path=ROOT/f'projects/{PROJECT}/script/narration.{lang}.json'
    if hashlib.sha256(path.read_bytes()).hexdigest()!=review['finalInputHashes'][lang]:
        raise SystemExit('Reviewed script changed; preserve chunks and rereview')
checked=subprocess.run(['node','scripts/review-video-duplicates.cjs',PROJECT,'--candidate-file',
                        f'production/research/game-lighting-history/candidate-{PROJECT[-2:]}.json','--check'],
                       cwd=ROOT,capture_output=True,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
print(checked.stdout,end='',flush=True)
if checked.returncode:
    print(checked.stderr,end='',file=sys.stderr,flush=True);raise SystemExit(checked.returncode)
device=sys.argv[sys.argv.index('--device')+1] if '--device' in sys.argv else 'cuda:0'
dry='--dry-run' in sys.argv
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff
check_gpu_tts_hold(PROJECT,device,dry)
schedule_gpu_handoff(PROJECT,device,dry)
import render_narration
if not dry:
    import torch
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(2)
    original_loader=Qwen3TTSModel.from_pretrained.__func__
    def load(cls,*args,**kwargs):
        kwargs.setdefault('attn_implementation','sdpa')
        return original_loader(cls,*args,**kwargs)
    Qwen3TTSModel.from_pretrained=classmethod(load)
    original_generate=Qwen3TTSModel.generate_voice_clone
    def generate(self,*args,**kwargs):
        if self.device.type!='cuda': return original_generate(self,*args,**kwargs)
        current=torch.cuda.current_stream(self.device)
        stream=torch.cuda.Stream(device=self.device,priority=-1);stream.wait_stream(current)
        with torch.cuda.stream(stream): result=original_generate(self,*args,**kwargs)
        stream.synchronize();current.wait_stream(stream);torch.cuda.empty_cache()
        return result
    Qwen3TTSModel.generate_voice_clone=generate
    original_badness=render_narration._badness
    def prefer_passing(tail,decay):
        score=original_badness(tail,decay)
        return score if render_narration._passes_quality(tail,decay) else 1000000+score
    render_narration._badness=prefer_passing
if __name__=='__main__': render_narration.main()

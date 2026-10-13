"""Episode1: approved shared renderer with scoped SDPA and cooperative lease.

This entry point never pauses or terminates arbitrary research processes.
The shared handoff waits for the current run to seal and restores the queue.
"""
from pathlib import Path
import hashlib, json, subprocess, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'qwen3-tts'))
PROJECT = 'game-lighting-history-01'
if '--project' not in sys.argv or sys.argv[sys.argv.index('--project')+1] != PROJECT:
    raise SystemExit('This reviewed input belongs only to episode1')
review_path = f'projects/{PROJECT}/production/script-source-wording-review-v4.json'
if '--manifest' in sys.argv:
    manifest_path = ROOT/sys.argv[sys.argv.index('--manifest')+1]
    manifest_input = json.loads(manifest_path.read_text(encoding='utf-8'))
    requested_review = manifest_input.get('voiceRepair', {}).get('scriptReview')
    if requested_review:
        if requested_review != f'projects/{PROJECT}/production/script-source-wording-review-v5.json':
            raise SystemExit('Unknown scoped input review; inspect before synthesis')
        review_path = requested_review
review = json.loads((ROOT/review_path).read_text(encoding='utf-8'))
if not review['fullScriptDirectReread'] or not review['finalTtsInputWritten']:
    raise SystemExit('Direct source/script review is required before synthesis')
for lang in ['ko','en']:
    f = ROOT/f'projects/{PROJECT}/script/narration.{lang}.json'
    if hashlib.sha256(f.read_bytes()).hexdigest() != review['finalInputHashes'][lang]:
        raise SystemExit('Reviewed script changed; preserve checkpoints and rereview')
checked = subprocess.run(['node', 'scripts/review-video-duplicates.cjs', PROJECT,
                         '--candidate-file', f'projects/{PROJECT}/production/local/current-candidate.json', '--check'],
                        cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                        creationflags=subprocess.CREATE_NO_WINDOW)
print(checked.stdout, end='', flush=True)
if checked.returncode:
    print(checked.stderr, end='', file=sys.stderr, flush=True)
    raise SystemExit(checked.returncode)
device = sys.argv[sys.argv.index('--device')+1] if '--device' in sys.argv else 'cuda:0'
dry = '--dry-run' in sys.argv
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff
check_gpu_tts_hold(PROJECT, device, dry)
schedule_gpu_handoff(PROJECT, device, dry)
import render_narration

if not dry:
    # Same model, clone prompt, text and sampling parameters as shared renderer.
    import torch
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(2)
    original_loader = Qwen3TTSModel.from_pretrained.__func__
    def load(cls, *args, **kwargs):
        kwargs.setdefault('attn_implementation', 'sdpa')
        return original_loader(cls, *args, **kwargs)
    Qwen3TTSModel.from_pretrained = classmethod(load)
    original_generate = Qwen3TTSModel.generate_voice_clone
    def generate_with_released_cache(self, *args, **kwargs):
        if self.device.type != 'cuda':
            return original_generate(self, *args, **kwargs)
        current = torch.cuda.current_stream(self.device)
        stream = torch.cuda.Stream(device=self.device, priority=-1)
        stream.wait_stream(current)
        with torch.cuda.stream(stream):
            result = original_generate(self, *args, **kwargs)
        stream.synchronize();current.wait_stream(stream);torch.cuda.empty_cache()
        return result
    Qwen3TTSModel.generate_voice_clone = generate_with_released_cache
    original_badness = render_narration._badness
    def prefer_passing_take(tail, decay):
        score = original_badness(tail, decay)
        return score if render_narration._passes_quality(tail, decay) else 1000000+score
    render_narration._badness = prefer_passing_take

if __name__ == '__main__':
    render_narration.main()

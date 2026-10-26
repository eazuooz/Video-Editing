"""Add opt-in GPU ASR only to the six new, unrendered batch runtimes."""
from pathlib import Path
import ast
R=Path(__file__).resolve().parents[3]
SLUGS=['limited-color-world','computer-controlled-players','in-game-cutscenes','start-with-climax','kind-to-beginners','respect-player-time']
WRAPPER='''@contextmanager
def batch_asr_lease(device):
    lease=Path('C:/Users/1/.codex/video-production/design-finish-six-20261026/heavy-job.lock.json')
    lease.parent.mkdir(parents=True,exist_ok=True)
    observed=None
    if device=='cuda':
        result=subprocess.run(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
        free,util=(int(x.strip()) for x in result.stdout.strip().splitlines()[0].split(','))
        if free<6000 or util>25:raise ValueError('GPU occupied; preserve foreign work and retry at an idle boundary')
        observed={'memoryFreeMiB':free,'utilizationPercent':util,'observedAt':now()}
    with lease.open('x',encoding='utf8') as handle:
        json.dump({'owner':'root','pid':os.getpid(),'slug':SLUG,'kind':'full unprompted ASR','device':device,'startedAt':now(),'resourceObservation':observed},handle)
    try:yield
    finally:
        if lease.exists() and read(lease).get('pid')==os.getpid():lease.unlink()


def full_asr(audio_path,cache_path,*,final=False):
    device=os.environ.get('VIDEO_BATCH_ASR_DEVICE','cpu')
    if device not in ['cpu','cuda']:raise ValueError('Explicit cpu/cuda ASR device required')
    if Path(cache_path).exists():return _full_asr(audio_path,cache_path,final=final,device=device)
    with batch_asr_lease(device):return _full_asr(audio_path,cache_path,final=final,device=device)


'''
for slug in SLUGS:
 p=R/'projects'/slug/'production/batch-v1/audio_pipeline.py'
 text=p.read_text('utf-8-sig')
 if 'def batch_asr_lease(' in text:continue
 tree=ast.parse(text);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='full_asr')
 lines=text.splitlines(keepends=True);old=''.join(lines[node.lineno-1:node.end_lineno])
 changed=old.replace('def full_asr(audio_path, cache_path, *, final=False):','def _full_asr(audio_path, cache_path, *, final=False, device="cpu"):')
 changed=changed.replace('recorded.get("device") != "cpu"','recorded.get("device") not in ["cpu","cuda"]')
 changed=changed.replace("full, unprompted CPU recognition contract","full, unprompted recognition contract")
 changed=changed.replace('"device": "cpu"','"device": device')
 changed=changed.replace('dtype=torch.float32,','dtype=torch.float16 if device=="cuda" else torch.float32,')
 changed=changed.replace('dtype=torch.float32, device="cpu")','dtype=torch.float32, device=0 if device=="cuda" else "cpu")')
 changed=changed.replace('dtype=torch.float16 if device=="cuda" else torch.float32, device="cpu")','dtype=torch.float16 if device=="cuda" else torch.float32, device=0 if device=="cuda" else "cpu")')
 changed=changed.replace('print("Recognizing the complete current audio once on CPU4, without a supplied prompt", flush=True)','print(f"Recognizing the complete current audio once on {device}, without a supplied prompt", flush=True)')
 updated=''.join(lines[:node.lineno-1])+WRAPPER+changed+''.join(lines[node.end_lineno:])
 updated=updated.replace('No stage generates TTS, downloads a model, claims human listening, touches a GPU,','No stage generates TTS, downloads a model, claims human listening,')
 updated=updated.replace('Invoke stages explicitly; importing this module does no work.','Invoke stages explicitly; importing this module does no work.\nGPU ASR is opt-in (VIDEO_BATCH_ASR_DEVICE=cuda), resource-checked and serialized for this batch only.')
 ast.parse(updated);p.write_text(updated,'utf8')
 print(slug,'opt-in GPU ASR patched; CPU remains default')

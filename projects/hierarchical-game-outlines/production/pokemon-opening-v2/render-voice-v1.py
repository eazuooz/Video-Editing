"""One selected five-changed-request narration request; no automatic regeneration."""
import atexit
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
STATE = OUT / 'voice-execution-v1.json'
RESEARCH = Path('C:/Users/eazuo/renderformer/tmp/gi_ao_runtime_steady_20261013/status.json')
BASE = ROOT / 'projects/hierarchical-game-outlines/project.json'
BASE_SHA = '45bae8b008d8f34e562bd868e3a71f1220a61338b18e433d19be6c1adb1c8c5b'

def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, obj): Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def identity(p):
    try: return dict(pid=p.pid, createTime=p.create_time(), command=p.cmdline(), cwd=p.cwd())
    except (psutil.NoSuchProcess, psutil.AccessDenied): return None

sys.stdout.reconfigure(encoding='utf-8')
control=json.loads((ROOT/'shared/publishing/video-production-control.json').read_text(encoding='utf-8'))
assert control['selectedVideo']=='hierarchical-game-outlines' and control['newProductionAuthorization']['fullProductionAuthorized']
assert json.loads((OUT/'script-review.json').read_text(encoding='utf-8'))['scriptFinalized']
if STATE.exists(): raise SystemExit('Existing request must be resumed from actual state; duplicate execution forbidden')
assert sha(BASE) == BASE_SHA, 'Baseline changed; inspect before generating'
assert json.loads((OUT/'white-preflight-direct-review.json').read_text(encoding='utf-8'))['preflightPixelsApproved']
assert not list((OUT/'generated-narration/chunks').glob('*.wav')), 'Preserve existing narration'
subprocess.run(['node', 'scripts/review-video-duplicates.cjs', 'hierarchical-game-outlines', '--check'], cwd=ROOT, check=True)
me = psutil.Process()
state = dict(status='resource-observation', startedAt=now(), worker=identity(me), baselineSha256=BASE_SHA,
             scriptSha256=sha(OUT/'narration.ko.json'), manifestSha256=sha(OUT/'voice-manifest.json'),
             modelLoaded=False, completed=[], humanListeningApproved=False, publicRightsApproved=False)
write(STATE, state)
try:
    research = json.loads(RESEARCH.read_text(encoding='utf-8-sig'))
    assert research.get('status') == 'complete_pending_visual_review', 'Research not complete; preserve it'
    foreign = []
    for p in psutil.process_iter():
        ident = identity(p)
        if not ident or p.pid in [me.pid, *[a.pid for a in me.parents()]]: continue
        command = ' '.join(ident['command']).lower()
        if any(x in command for x in ['gpu_queue.py', 'render_narration.py', 'render-voice-v1.py', 'tts-handoff', 'gpu-handoff.py', 'train_gi_ao', 'gi_ao_runtime_steady']):
            foreign.append(ident)
    assert not foreign, f'Foreign GPU owner must finish without intervention: {foreign}'
    lease = ROOT/'shared/output/GPU_HANDOFF.json'
    assert not lease.exists(), 'Preserve foreign handoff'
    resource = dict(at=now(), worker=identity(me), researchStatus=research, researchSha256=sha(RESEARCH),
                    cpuPercent=psutil.cpu_percent(interval=1), availableRam=psutil.virtual_memory().available,
                    matchingForeignProcesses=foreign, gpuSamples=[], stable20seconds=False)
    started = time.monotonic(); stable = None
    while time.monotonic()-started < 600:
        raw = subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'], text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        free, util = map(int,raw.splitlines()[0].replace(' ','').split(','))
        good = free >= 18000 and util < 15 and not lease.exists()
        resource['gpuSamples'].append(dict(at=now(),freeMiB=free,utilization=util,eligible=good))
        if good and stable is None: stable=time.monotonic()
        elif not good: stable=None
        if stable is not None and time.monotonic()-stable >= 20:
            resource['stable20seconds']=True; break
        write(OUT/'voice-resource-v1.json',resource)
        time.sleep(2)
    write(OUT/'voice-resource-v1.json',resource)
    assert resource['stable20seconds'], 'No stable GPU window; no request/model allocated'
    sys.path.insert(0,str(ROOT/'qwen3-tts'))
    from gpu_tts_hold import check_gpu_tts_hold
    from gpu_handoff_guard import schedule_gpu_handoff, check_gpu_handoff
    check_gpu_tts_hold('hierarchical-game-outlines','cuda:0')
    schedule_gpu_handoff('hierarchical-game-outlines','cuda:0')
    check_gpu_handoff('hierarchical-game-outlines','cuda:0')
    state.update(status='tts_running',lease=json.loads(lease.read_text(encoding='utf-8-sig')),updatedAt=now())
    write(STATE,state)
    import render_narration as rn
    rn.configure_project('hierarchical-game-outlines', (OUT/'voice-manifest.json').relative_to(ROOT).as_posix())
    rn.load_tts_dependencies()
    rn.torch.set_num_threads(2)
    rn.torch.set_num_interop_threads(1)
    original = rn.Qwen3TTSModel.from_pretrained
    def load(*args, **kwargs):
        kwargs['attn_implementation']='sdpa'
        result=original(*args,**kwargs)
        state.update(modelLoaded=True,updatedAt=now());write(STATE,state)
        generate=result.generate_voice_clone
        def observed(*a,**k):
            state.update(activeText=k.get('text'), updatedAt=now());write(STATE,state)
            return generate(*a,**k)
        result.generate_voice_clone=observed
        return result
    rn.Qwen3TTSModel.from_pretrained=load
    items=rn.build_render_items(rn.load_jobs())
    assert len(items)==5 and rn.MAX_RENDER_ATTEMPTS==1
    rn.render_chunks(items,batch_size=1)
    for item in items:
        info=rn.sf.info(item.path)
        state['completed'].append(dict(key=item.key,path=item.path.relative_to(ROOT).as_posix(),
                                      samples=info.frames,sampleRate=info.samplerate,seconds=info.duration,sha256=sha(item.path)))
    assert sha(BASE)==BASE_SHA
    state.update(status='generated-pending-current-asr',endedAt=now(),baselinePreserved=True)
    write(STATE,state)
    print(json.dumps(dict(status=state['status'],scenes=len(state['completed']),seconds=sum(x['seconds'] for x in state['completed'])),ensure_ascii=False),flush=True)
except BaseException as e:
    state.update(status='failed',error=repr(e),endedAt=now(),baselinePreserved=sha(BASE)==BASE_SHA)
    write(STATE,state)
    raise

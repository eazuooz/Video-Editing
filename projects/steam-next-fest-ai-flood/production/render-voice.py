"""Bounded GPU-only Qwen3-TTS scene batch for steam-next-fest-ai-flood.
Cooperative handoff: runs only when no foreign python/TTS job holds the GPU,
with >=9000MiB free and an 8192MiB allocator cap; never terminates other
applications and never falls back to CPU."""
from pathlib import Path
import datetime, json, os, psutil, subprocess, sys, time, uuid
R = Path(__file__).resolve().parents[3]
P = R / 'projects/steam-next-fest-ai-flood'
L = P / 'production/local/edit'
LEASE = R / 'shared/output/GPU_HANDOFF.json'
L.mkdir(parents=True, exist_ok=True)
def read(p): return json.loads(p.read_text(encoding='utf8'))
def save(p, v): p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
def gpu():
    raw = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free,memory.total,utilization.gpu', '--format=csv,noheader,nounits'], text=True)
    return [int(x.strip()) for x in raw.splitlines()[0].split(',')]
plan = read(P / 'planning/production-plan.json')
assert 'production-authorized' in plan['approvals']['videoSelection']['status'], plan['approvals']['videoSelection']['status']
assert 'tts' in plan['approvals']['videoSelection']['authorizedScope']
assert not LEASE.exists(), 'Preserve existing GPU lease'
me = psutil.Process()
family = {p.pid for p in [me, *me.parents()]}
# Foreign GPU compute (not idle helper interpreters) is what must stay untouched.
apps = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid,process_name', '--format=csv,noheader'], text=True)
foreign = [row for row in apps.splitlines() if 'python' in row.lower() and int(row.split(',')[0]) not in family]
assert not foreign, ('Other GPU compute remains untouched; wait for its boundary', foreign)
before = gpu()
# User confirmed the GPU is free (2026-10-20 "gpu 지금 비어있어"); editors hold display memory, so run bounded to the free pool.
MIN_FREE = 8192
assert before[0] >= MIN_FREE, ('Bounded profile needs at least 8192MiB free', before)
CAP = min(8192, before[0] - 700)
token = str(uuid.uuid4())
state = dict(schemaVersion=1, token=token, project=P.name, state='gpu_granted_to_tts', requestedAt=time.time(),
             coordinator={'pid': me.pid, 'createTime': me.create_time()},
             gpuBeforeTts={'freeMiB': before[0], 'totalMiB': before[1], 'utilization': before[2]},
             foreignProcessesPaused=[], userEvidence='gpu 지금 비어있어 (2026-10-20)', allocatorLimitMiB=CAP,
             profile='bf16-scene-batch1-bounded-8GiB', generations=[])
with LEASE.open('x', encoding='utf8') as f: json.dump(state, f, indent=2)
receipt = L / 'tts-gpu-coordination.json'
save(receipt, state)
code = 1
try:
    sys.path.insert(0, str(R / 'qwen3-tts'))
    import torch
    torch.cuda.set_per_process_memory_fraction(CAP * 1024 * 1024 / torch.cuda.get_device_properties(0).total_memory, 0)
    import render_narration as worker
    worker.configure_project(P.name)
    worker.load_tts_dependencies()
    generate = worker.Qwen3TTSModel.generate_voice_clone
    def measured(self, *args, **kwargs):
        torch.cuda.reset_peak_memory_stats()
        result = generate(self, *args, **kwargs)
        state['generations'].append({'at': time.time(), 'peakAllocatedMiB': round(torch.cuda.max_memory_allocated() / 2**20), 'freeMiB': gpu()[0]})
        save(receipt, state)
        return result
    worker.Qwen3TTSModel.generate_voice_clone = measured
    force = sys.argv[1] if len(sys.argv) > 1 else ''
    sys.argv = ['render_narration.py', '--project', P.name, '--batch-size', '1'] + (['--force-scenes', force] if force else [])
    worker.main()
    code = 0
    state.update(state='finished', finishedAt=time.time(), exitCode=0)
except BaseException as e:
    state.update(state='failed', finishedAt=time.time(), error=repr(e))
    raise
finally:
    save(receipt, state)
    if LEASE.exists() and read(LEASE).get('token') == token: LEASE.unlink()
sys.exit(code)

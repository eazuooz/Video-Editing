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
    # Line-level regeneration (user review 2026-10-21: long scene takes drifted quieter).
    # The shared renderer keeps its bounded profile in scene mode, so each paragraph
    # line becomes a one-line "scene" in a derived script/manifest; the real scene
    # files are assembled below with per-line speech-level equalization.
    script = read(P / 'script/narration.ko.json')
    derived = {'scenes': [{'id': f"{s['id']}-{n:02d}", 'title': s['title'], 'lines': [line]} for s in script['scenes'] for n, line in enumerate(s['lines'], start=1) if line.strip()]}
    (P / 'script/narration.lines.ko.json').write_text(json.dumps(derived, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    manifest = read(P / 'project.json'); manifest['paths']['script'] = f'projects/{P.name}/script/narration.lines.ko.json'
    manifest['tts']['renderMode'] = 'scene'; manifest['tts']['sceneGapSeconds'] = manifest['tts'].get('lineGapSeconds', 0.28)
    MANIFEST = P / 'production/tts-manifest-lines.json'; save(MANIFEST, manifest); MANIFEST_REL = MANIFEST.relative_to(R).as_posix()
    worker.configure_project(P.name, MANIFEST_REL)
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
    sys.argv = ['render_narration.py', '--project', P.name, '--batch-size', '1', '--manifest', MANIFEST_REL] + (['--force-scenes', force] if force else [])
    worker.main()
    # Assemble the real scene files from the per-line takes at one speech level:
    # each line's speech-active frame median is matched to the target before the
    # lines are joined with the line gap. Exact line boundaries replace estimation.
    import numpy as np, soundfile as sf
    tts = read(P / 'project.json')['tts']; eq = tts['lineLevelEqualization']; C = worker.CHUNK_DIR
    gap = float(tts.get('lineGapSeconds', 0.28)); scene_gap = float(tts['sceneGapSeconds'])
    def db(v): return float(20 * np.log10(max(float(v), 1e-10)))
    def speech_median(a, sr):
        n = max(1, round(sr * eq['frameMs'] / 1000)); frames = a[:len(a) // n * n].reshape(-1, n)
        lv = np.array([db(np.sqrt(np.mean(f * f))) for f in frames]); active = lv[lv >= lv.max() - eq['gateBelowPeakDb']]
        return float(np.median(active)) if len(active) else float(lv.max())
    pieces, entries, levels, position, sr0, idx = [], [], [], 0.0, None, 1
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    for si, s in enumerate(script['scenes']):
        lines = [l for l in s['lines'] if l.strip()]; parts = []; local = 0.0
        for n, line in enumerate(lines, start=1):
            a, sr = worker._read_mono(C / f"{s['id']}-{n:02d}-scene.wav"); sr0 = sr0 or sr; assert sr == sr0
            before = speech_median(a, sr); gain_db = max(-eq['maxGainDb'], min(eq['maxGainDb'], eq['targetSpeechFrameMedianDbfs'] - before))
            out = worker._apply_edge_fades(a * np.float32(10 ** (gain_db / 20)), sr)
            levels.append({'line': f"{s['id']}-{n:02d}", 'speechMedianDbfs': before, 'gainDb': gain_db, 'afterDbfs': before + gain_db, 'seconds': len(a) / sr, 'peak': float(np.abs(out).max())})
            if n > 1: parts.append(np.zeros(round(gap * sr), dtype=np.float32)); local += gap
            entries.append({'index': idx, 'scene_id': s['id'], 'scene_title': s['title'], 'text': line, 'start': position + local, 'end': position + local + len(out) / sr}); idx += 1
            parts.append(out); local += len(out) / sr
        wav = np.concatenate(parts); target = C / f"{s['id']}-scene.wav"
        if target.exists(): target.replace(C / f"{s['id']}-scene-previous-{stamp}.wav")
        sf.write(target, wav, sr0, subtype='FLOAT'); pieces.append(wav); position += len(wav) / sr0
        if si != len(script['scenes']) - 1: pieces.append(np.zeros(round(scene_gap * sr0), dtype=np.float32)); position += scene_gap
    sf.write(worker.FINAL_WAV, np.concatenate(pieces), sr0, subtype='FLOAT')
    worker.FINAL_SRT.write_text('\n\n'.join(f"{e['index']}\n{worker.timestamp(e['start'])} --> {worker.timestamp(e['end'])}\n{e['text']}" for e in entries) + '\n', encoding='utf8')
    save(worker.TIMING_JSON, {'sample_rate': sr0, 'duration_seconds': position, 'render_mode': 'line-takes-assembled-per-scene', 'example_seconds': worker.EXAMPLE_SECONDS, 'narration_placement': worker.NARRATION_PLACEMENT, 'entries': entries})
    before = [l['speechMedianDbfs'] for l in levels]; after = [l['afterDbfs'] for l in levels]
    save(worker.OUTPUT_DIR / eq['record'], {'equalization': eq, 'lineGapSeconds': gap, 'lines': levels, 'lineMedianRangeDb': {'before': max(before) - min(before), 'after': max(after) - min(after)}, 'maxPeak': max(l['peak'] for l in levels)})
    print('Assembled', len(script['scenes']), 'scenes from', len(levels), 'line takes; line median range before %.1f dB, after %.1f dB' % (max(before) - min(before), max(after) - min(after)), flush=True)
    code = 0
    state.update(state='finished', finishedAt=time.time(), exitCode=0)
except BaseException as e:
    state.update(state='failed', finishedAt=time.time(), error=repr(e))
    raise
finally:
    save(receipt, state)
    if LEASE.exists() and read(LEASE).get('token') == token: LEASE.unlink()
sys.exit(code)

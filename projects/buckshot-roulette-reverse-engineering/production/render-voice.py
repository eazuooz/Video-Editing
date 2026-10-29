"""Buckshot's selected, paragraph-level own-voice render. Default is no-GPU preflight.

Root coordinator must explicitly pass --synthesize after capture/render GPU work
has finished. No paid services, app termination, or unrelated queue mutation.
"""
from pathlib import Path
import argparse
import atexit
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
SLUG = PROJECT.name
MANIFEST = PROJECT / 'production/tts-manifest.json'
LEASE = ROOT / 'shared/output/GPU_HANDOFF.json'
CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def command_output(command):
    return subprocess.check_output(command, text=True, creationflags=CREATE_NO_WINDOW)

def unity_import_worker(info, process):
    """Recognize Unity's own idle import helpers without printing license args."""
    import re
    import psutil
    args = [str(a).lower() for a in info.get('cmdline') or []]
    if (info.get('name') or '').lower() != 'unity.exe' or not all(flag in args for flag in ['-batchmode','-adb2','-noupm']):
        return False
    def value(arguments,flag):
        return arguments[arguments.index(flag)+1] if flag in arguments and arguments.index(flag)+1 < len(arguments) else None
    if not re.fullmatch(r'assetimportworkerhw\d+', value(args,'-name') or ''):
        return False
    try:
        parent = process.parent()
        if parent is None or parent.name().lower() != 'unity.exe':
            return False
        parent_args = [str(a).lower() for a in parent.cmdline()]
        return (parent.exe().lower() == (info.get('exe') or process.exe()).lower()
                and '-batchmode' not in parent_args
                and value(args,'-projectpath') is not None
                and value(parent_args,'-projectpath') is not None
                and Path(value(args,'-projectpath')).resolve() == Path(value(parent_args,'-projectpath')).resolve())
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--synthesize', action='store_true', help='Root-coordinated actual GPU synthesis, after source/script review')
    parser.add_argument('--allow-idle-editors', action='store_true', help='Selected Buckshot root choice: preserve inspected idle editor windows, require10GiBfree/util<=40, cap allocator7.5GiB; never permit render/compute jobs')
    parser.add_argument('--check-resources', action='store_true', help='Inspect resource guard and record baseline only; never load a model or take GPU lease')
    args = parser.parse_args()
    manifest = read(MANIFEST)
    script = read(ROOT / manifest['paths']['script'])
    english = read(ROOT / manifest['paths']['scriptEn'])
    assert manifest['slug'] == script['slug'] == english['slug'] == SLUG
    assert [(s['id'], len(s['lines'])) for s in script['scenes']] == [(s['id'], len(s['lines'])) for s in english['scenes']]
    authorization = read(ROOT / 'shared/publishing/video-production-control.json')['scopedSetupAuthorizations'][SLUG]
    assert authorization['productionAllowedNow'] is True and authorization['projectPath'] == f'projects/{SLUG}'
    derived = {'scenes': [{'id': f"{s['id']}-{n:02d}", 'title': s['title'], 'lines': [line]} for s in script['scenes'] for n, line in enumerate(s['lines'], 1) if line.strip()]}
    derived_path = PROJECT / 'production/local/audio-v1/narration.lines.ko.json'
    save(derived_path, derived)
    render_manifest = json.loads(json.dumps(manifest))
    render_manifest['paths']['script'] = derived_path.relative_to(ROOT).as_posix()
    render_path = PROJECT / 'production/local/audio-v1/render-manifest.json'
    save(render_path, render_manifest)
    sys.path.insert(0, str(ROOT / 'qwen3-tts'))
    import render_narration as worker
    worker.configure_project(SLUG, render_path.relative_to(ROOT).as_posix())
    jobs = worker.load_jobs()
    if not args.synthesize and not args.check_resources:
        worker_args = [sys.executable, '-X', 'utf8', str(ROOT / 'qwen3-tts/render_narration.py'), '--project', SLUG, '--manifest', render_path.relative_to(ROOT).as_posix(), '--batch-size', '1', '--dry-run']
        subprocess.run(worker_args, cwd=ROOT, check=True, creationflags=CREATE_NO_WINDOW)
        print(json.dumps({'status': 'preflight-passed-no-synthesis', 'paragraphTakes': len(jobs), 'sourceCharacters': sum(len(j.text) for j in jobs), 'gpuLoaded': False}))
        return
    import psutil
    me = psutil.Process()
    family = {p.pid for p in [me, *me.parents()]}
    assert not LEASE.exists(), 'Existing GPU lease preserved; root must coordinate next boundary.'
    blocked = []
    baseline = []
    process_names = {}
    gui_allow = {'explorer.exe', 'chrome.exe', 'msedge.exe', 'msedgewebview2.exe', 'shellhost.exe', 'shellexperiencehost.exe', 'searchhost.exe', 'startmenuexperiencehost.exe', 'applicationframehost.exe', 'textinputhost.exe', 'runtimebroker.exe', 'dwm.exe', 'codex.exe', 'steam.exe', 'steamwebhelper.exe', 'obs64.exe', 'discord.exe', 'nvidia overlay.exe', 'nvidia share.exe', 'windowsterminal.exe'}
    # Root inspected the signed/installed executable paths for these exact
    # WDDM desktop rows. This is one production's baseline, not a global rule.
    gui_allow.update({'crossdeviceresume.exe','phoneexperiencehost.exe','mmgaserver.exe','systemsettings.exe','microsoftsecurityapp.exe','snippingtool.exe','edgegameassist.exe','chatgpt.exe','codex-computer-use-swift.exe','codex-computer-use.exe','radeonsoftware.exe','amdrssrcext.exe','logioptionsplus_agent.exe','icue.exe','parsecd.exe','razerappengine.exe','razer synapse.exe','battle.net.exe','icloudhome.exe','icloudphotos.exe','unity hub.exe','claude.exe','onedrive.exe','obs-browser-page.exe'})
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        info = proc.info
        if info['pid'] in family:
            continue
        name = (info['name'] or '').lower()
        exe = (info['exe'] or '').replace('\\', '/').lower()
        process_names[info['pid']] = name
        arguments = [str(a).lower() for a in (info['cmdline'] or [])]
        joined = ' '.join(arguments)
        hub = name == 'unity.exe' and exe.endswith('/unity hub/resources/unity.exe') and 'serve' in arguments
        import_worker = args.allow_idle_editors and unity_import_worker(info, proc)
        editor = not hub and (name in ['unity.exe', 'unrealeditor.exe', 'blender.exe'] or name.startswith('godot'))
        batch_flags = [flag for flag in ['--write-movie', '--headless', '--background', '-b', '-batchmode', '-moviepipeline', '-render', '--render'] if any(a == flag or (flag == '-moviepipeline' and a.startswith(flag)) or (flag == '-render' and a.startswith('-renderoffscreen')) for a in arguments)]
        actual_game = name in ['buckshot roulette.exe', 'buckshot roulette_windows.exe', 'monsterhunterwilds.exe', 'd2r.exe', 'diablo ii.exe']
        compute = name.startswith(('python', 'ffmpeg'))
        reason = 'actual-game' if actual_game else 'foreign-compute-process' if compute else 'editor-background-render' if editor and batch_flags and not import_worker else 'editor-not-explicitly-allowed' if editor and not args.allow_idle_editors else None
        if reason:
            blocked.append({'pid': info['pid'], 'name': info['name'], 'reason': reason, 'batchFlags': batch_flags})
        if editor or actual_game or compute:
            baseline.append({'pid': info['pid'], 'name': info['name'], 'editor': editor, 'batchFlags': batch_flags, 'verifiedUnityImportWorker': import_worker, 'disposition': reason or ('preserved-Unity-import-worker' if import_worker else 'preserved-visible-editor')})
        if hub or import_worker or (editor and args.allow_idle_editors and not batch_flags):
            gui_allow.add(name)
    assert not blocked, ('Actual game/editor/render apps remain; preserve and let root finish them', blocked)
    apps = command_output(['nvidia-smi', '--query-compute-apps=pid,process_name', '--format=csv,noheader'])
    # Windows WDDM rows include ordinary GPU-using windows. Classify their
    # inspected process identity instead of calling every row a CUDA batch.
    foreign = []
    observed_gpu_rows = []
    for line in apps.splitlines():
        if not line.strip() or not line.split(',')[0].strip().isdigit():
            continue
        pid = int(line.split(',')[0])
        if pid in family:
            continue
        name = process_names.get(pid, Path(line.split(',', 1)[1].strip()).name.lower())
        allowed = args.allow_idle_editors and name in gui_allow
        observed_gpu_rows.append({'pid': pid, 'name': name, 'classification': 'inspected-GUI-preserved' if allowed else 'unclassified-foreign-GPU-process'})
        if not allowed:
            foreign.append({'pid': pid, 'name': name})
    assert not foreign, ('Foreign GPU compute remains untouched', foreign)
    samples = []
    for sample_index in range(3):
        free, total, utilization = [int(v.strip()) for v in command_output(['nvidia-smi', '--query-gpu=memory.free,memory.total,utilization.gpu', '--format=csv,noheader,nounits']).splitlines()[0].split(',')]
        samples.append({'freeMiB': free, 'totalMiB': total, 'utilization': utilization})
        if sample_index < 2:
            time.sleep(1)
    minimum_free, maximum_utilization = (10240, 40) if args.allow_idle_editors else (8192, 14)
    assert all(s['freeMiB'] >= minimum_free and s['utilization'] <= maximum_utilization for s in samples), ('Insufficient inspected GPU capacity; existing windows/jobs preserved', samples)
    free = min(s['freeMiB'] for s in samples)
    if args.check_resources and not args.synthesize:
        preflight = {'status':'resource-preflight-passed-no-synthesis','checkedAt':time.time(),'project':SLUG,'rootScope':'selected Buckshot documentary only','allowIdleEditors':args.allow_idle_editors,'baselineProcesses':baseline,'observedGpuRows':observed_gpu_rows,'gpuSamples':samples,'allocatorCapMiBIfStarted':min(7680 if args.allow_idle_editors else 8192,free-700),'gpuModelLoaded':False,'gpuLeaseCreated':False,'foreignProcessesChanged':False}
        save(worker.OUTPUT_DIR/'resource-preflight.json',preflight)
        print(json.dumps({'status':preflight['status'],'gpuSamples':samples,'baselineProcesses':len(baseline),'gpuRows':len(observed_gpu_rows),'gpuModelLoaded':False},ensure_ascii=False))
        return
    inputs = {name: digest(ROOT / manifest['paths'][name]) for name in ['script', 'scriptEn']}
    inputs.update(reference=digest(ROOT / manifest['tts']['reference']), referenceText=digest(ROOT / manifest['tts']['referenceText']), manifest=digest(MANIFEST))
    input_record = worker.OUTPUT_DIR / 'render-inputs.json'
    if input_record.exists():
        assert read(input_record)['sha256'] == inputs, 'Inputs changed: preserve previous takes and select a new audio revision before rendering.'
    save(input_record, {'sha256': inputs, 'rawTakesPreserved': True})
    state = {'schemaVersion': 1, 'project': SLUG, 'token': str(uuid.uuid4()), 'state': 'gpu_granted_to_tts', 'requestedAt': time.time(), 'coordinator': {'pid': me.pid, 'createTime': me.create_time()}, 'foreignProcessesPaused': [], 'rootExplicitInvocation': '--synthesize' + (' --allow-idle-editors' if args.allow_idle_editors else ''), 'selectedProjectResourceChoice': 'Inspected idle GUI editors preserved; require10GiBfree/util<=40; block actual games, background renders and foreign Python/FFmpeg compute' if args.allow_idle_editors else 'Default exclusive idle resource guard', 'baselineProcesses': baseline, 'observedGpuRows': observed_gpu_rows, 'gpuSamples': samples, 'gpuBeforeTts': {'freeMiB': free, 'totalMiB': total, 'utilization': utilization}, 'allocatorCapMiB': min(7680 if args.allow_idle_editors else 8192, free - 700), 'generations': []}
    LEASE.parent.mkdir(parents=True, exist_ok=True)
    with LEASE.open('x', encoding='utf-8') as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)
    receipt = worker.OUTPUT_DIR / 'tts-gpu-coordination.json'
    save(receipt, state)
    def release_at_exit():
        if LEASE.exists() and read(LEASE).get('token') == state['token']:
            LEASE.unlink()
    atexit.register(release_at_exit)
    try:
        import torch
        torch.cuda.set_per_process_memory_fraction(state['allocatorCapMiB'] / total, 0)
        worker.load_tts_dependencies()
        original_generate = worker.Qwen3TTSModel.generate_voice_clone
        def measured(model, *a, **kw):
            torch.cuda.reset_peak_memory_stats()
            result = original_generate(model, *a, **kw)
            state['generations'].append({'at': time.time(), 'peakAllocatedMiB': round(torch.cuda.max_memory_allocated() / 2**20)})
            save(receipt, state)
            return result
        worker.Qwen3TTSModel.generate_voice_clone = measured
        items = worker.build_render_items(jobs)
        # Never replace an existing raw take because of a tail heuristic. Actual
        # ASR/listening review decides retakes, in an additive output revision.
        for item in items:
            if item.path.exists():
                assert worker.valid_wav(item.path), f'Inspect invalid existing raw take, preserved: {item.path}'
        worker.render_chunks([item for item in items if not item.path.exists()], 1, set())
        import numpy as np
        import soundfile as sf
        eq = manifest['tts']['lineLevelEqualization']
        gap = manifest['tts']['lineGapSeconds']
        scene_gap = manifest['tts']['sceneGapSeconds']
        pieces, entries, levels = [], [], []
        position, sr0 = 0.0, None
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        def speech_level(samples, sr):
            length = max(1, round(sr * eq['frameMs'] / 1000))
            assert len(samples) >= length, 'Empty/too-short take must be inspected.'
            frames = samples[:len(samples)//length*length].reshape(-1, length)
            rms = np.sqrt(np.mean(frames * frames, axis=1))
            db = 20 * np.log10(np.maximum(rms, 1e-10))
            active = db[db >= db.max() - eq['gateBelowPeakDb']]
            return float(np.median(active))
        for si, scene in enumerate(script['scenes']):
            local = 0.0
            parts = []
            for n, text in enumerate(scene['lines'], 1):
                raw = worker.CHUNK_DIR / f"{scene['id']}-{n:02d}-scene.wav"
                samples, sr = worker._read_mono(raw)
                sr0 = sr0 or sr
                assert sr == sr0
                before = speech_level(samples, sr)
                gain_db = max(-eq['maxGainDb'], min(eq['maxGainDb'], eq['targetSpeechFrameMedianDbfs'] - before))
                levelled = worker._apply_edge_fades(samples * np.float32(10**(gain_db/20)), sr)
                if n > 1:
                    parts.append(np.zeros(round(gap*sr), dtype=np.float32)); local += gap
                seconds = len(levelled)/sr
                entries.append({'index': len(entries)+1, 'scene_id': scene['id'], 'scene_title': scene['title'], 'paragraph': n, 'text': text, 'display_text': scene.get('displayLines', scene['lines'])[n-1], 'text_en': english['scenes'][si]['lines'][n-1], 'start': position+local, 'end': position+local+seconds})
                levels.append({'id': f"{scene['id']}-{n:02d}", 'rawSha256': digest(raw), 'beforeMedianDbfs': before, 'gainDb': gain_db, 'afterMedianDbfs': speech_level(levelled, sr), 'peak': float(np.abs(levelled).max()), 'seconds': seconds})
                parts.append(levelled); local += seconds
            scene_wav = np.concatenate(parts)
            target = worker.OUTPUT_DIR / 'scenes' / f"{scene['id']}.wav"
            target.parent.mkdir(exist_ok=True)
            if target.exists():
                target.rename(target.with_name(f'{target.stem}-previous-{stamp}.wav'))
            sf.write(target, scene_wav, sr0, subtype='FLOAT')
            pieces.append(scene_wav); position += len(scene_wav)/sr0
            if si < len(script['scenes'])-1:
                pieces.append(np.zeros(round(scene_gap*sr0), dtype=np.float32)); position += scene_gap
        for output in [worker.FINAL_WAV, worker.FINAL_SRT, worker.TIMING_JSON, worker.OUTPUT_DIR / 'narration.en.srt']:
            if output.exists():
                output.rename(output.with_name(f'{output.stem}-previous-{stamp}{output.suffix}'))
        sf.write(worker.FINAL_WAV, np.concatenate(pieces), sr0, subtype='FLOAT')
        save(worker.TIMING_JSON, {'sample_rate': sr0, 'duration_seconds': position, 'render_mode': 'paragraph-takes-with-active-level-normalization', 'narration_placement': worker.NARRATION_PLACEMENT, 'entries': entries, 'paceListening': 'pending'})
        for language, key, path in [('ko', 'display_text', worker.FINAL_SRT), ('en', 'text_en', worker.OUTPUT_DIR / 'narration.en.srt')]:
            # Paragraph SRT is timing evidence. Final on-screen captions still require clause segmentation.
            path.write_text('\n\n'.join(f"{entry['index']}\n{worker.timestamp(entry['start'])} --> {worker.timestamp(entry['end'])}\n{entry[key]}" for entry in entries)+'\n', encoding='utf-8')
        save(worker.OUTPUT_DIR / eq['record'], {'equalization': eq, 'lines': levels, 'allRawPcmPreserved': True, 'voiceSha256': digest(worker.FINAL_WAV), 'sourceFullAsr': 'pending', 'finalMixAsr': 'pending', 'humanListening': False, 'maxPeak': max(row['peak'] for row in levels)})
        state.update(state='finished', finishedAt=time.time(), exitCode=0, durationSeconds=position)
        print(json.dumps({'status': 'generated-requires-audio-review', 'seconds': position, 'paragraphs': len(entries), 'wav': str(worker.FINAL_WAV)}, ensure_ascii=False))
    except BaseException as error:
        state.update(state='failed', finishedAt=time.time(), error=repr(error))
        raise
    finally:
        save(receipt, state)
        # Model can retain CUDA allocations until process exit. Keep the lease until atexit.

if __name__ == '__main__':
    main()

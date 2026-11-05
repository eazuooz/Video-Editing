"""Finite M21–M33 batch paragraph-level approved-voice renderer. Default is no-GPU preflight.

Root passes --project and --synthesize after source/script/footage review and resource checks. No paid services, app termination, or unrelated queue mutation.
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
BOOT = argparse.ArgumentParser(add_help=False)
BOOT.add_argument('--project', required=True)
BOOT.add_argument('--manifest')
BOOTARGS, _ = BOOT.parse_known_args()
SLUG = BOOTARGS.project
if not __import__('re').fullmatch(r'game-math-[a-z0-9-]+', SLUG):
    raise ValueError('Invalid selected math project')
PROJECT = ROOT / 'projects' / SLUG
MANIFEST = (ROOT / BOOTARGS.manifest).resolve() if BOOTARGS.manifest else PROJECT / 'production/tts-manifest.json'
assert MANIFEST.is_relative_to(PROJECT/'production'), 'Alternate manifest must belong to this selected project'
LEASE = ROOT / 'shared/output/GPU_HANDOFF.json'
CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verified_cpu_research(arguments):
    """Allow only the inspected CPU Whisper job, never arbitrary Python work.

    Its exact source uses pipeline(device=-1), float32, four CPU threads and
    no CUDA calls. The separate NVIDIA inventory below must still be empty
    of this PID before a synthesis job can start.
    """
    path = ROOT / 'projects/unreal-engine-6-verse-gameplay/production/research_source.py'
    if not path.is_file() or digest(path) != 'bf9ab30630f0a7e054b444779123ad3f7e25648bec2af77f66bd3b69f79a3f06':
        return False
    return any(Path(a).resolve() == path.resolve() for a in arguments if a.lower().endswith('.py'))

def command_output(command):
    return subprocess.check_output(command, text=True, creationflags=CREATE_NO_WINDOW)

def passive_python_host(proc, arguments):
    """Recognise a waiting coordinator, without granting its child a GPU exemption.

    WDDM process registration, utilization/free-memory sampling, game/render
    detection and exclusive file acquisition are checked independently below.
    A program doing CPU work or loading any compute/graphics library stays blocked.
    """
    import psutil
    def evidence():
        cpu=proc.cpu_times()
        modules=(Path(m.path).name.lower() for m in proc.memory_maps())
        gpu_tokens=('cuda','cublas','cudnn','torch','onnxruntime','vulkan','d3d11','d3d12','directml','nvencode')
        if any(any(t in m for t in gpu_tokens) for m in modules):
            return None
        return (cpu.user+cpu.system,proc.num_threads())
    try:
        paths=[Path(a).resolve() for a in arguments if a.lower().endswith('.py')]
        coordinator=ROOT/'production/batches/animation-18-20261031/finish_queue.py'
        known=(paths==[coordinator] and digest(coordinator).lower()=='f669dceda8b56fe5929367733663b86eab768cfdd7e4e370f0a507ba8720888c')
        idle_input=(arguments[1:] in (['-X','utf8','-'],['-u','-X','utf8','-']) and time.time()-proc.create_time()>90)
        if not (known or idle_input):return False
        before=evidence()
        if before is None or before[0]>2.5 or before[1]>4:return False
        time.sleep(.25)
        return before==evidence()
    except (OSError,psutil.Error,ValueError):
        return False

def verified_waiting_math_worker(process, arguments):
    """Admit this finite batch's idle coordinators, never their render children.

    Exact workspace entrypoint + output scope + PID/start-time + waiting state
    are required. The exclusive lease and independent GPU inventory still apply.
    """
    try:
        scripts = [Path(x).resolve() for x in arguments if x.lower().endswith('.py')]
        if len(scripts) != 1:
            return False
        selected = scripts[0]
        batch = ROOT / 'production/batches/game-math-remaining-20261104'
        m21 = ROOT / 'projects/game-math-shading-lights/production'
        def value(flag):
            return arguments[arguments.index(flag)+1] if flag in arguments else None
        statefile = None
        if selected==(batch/'part2/finish_lesson.py').resolve():
            ep=arguments[-1]
            if not __import__('re').fullmatch(r'M(?:2[3-9]|3[0-3])',ep):return False
            if digest(selected)!='f2d5adca3d7a7aeb8d99168edea5f3edc769931a9d9ee21ab58a95880b0d139b':return False
            lane=read(batch/'local/part2-20261106/lanes'/f'{ep}.json')
            # This exact program dispatches a separate process for every job.
            # Its children, WDDM registrations and memory load are still checked.
            return (lane.get('active') and lane.get('episode')==ep and lane.get('pid')==process.pid
                    and abs(lane.get('createTime',0)-process.create_time())<.1)
        if selected in [(batch/'finish-selected-voice.py').resolve(), (batch/'finish-word-review.py').resolve()]:
            slug = value('--project')
            if slug not in read(ROOT/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']['projectSlugs']:
                return False
            if selected.name=='finish-selected-voice.py' and value('--manifest'):
                source_manifest=(ROOT/value('--manifest')).resolve()
                if not source_manifest.is_relative_to(ROOT/'projects'/slug/'production'):return False
                audio_dir=(ROOT/read(source_manifest)['tts']['outputDir']).resolve()
            else:audio_dir=ROOT/'projects'/slug/'production/local'/(value('--audio-revision') or 'audio-v1')
            if not audio_dir.is_relative_to(ROOT/'projects'/slug/'production/local'):return False
            statefile = audio_dir/('finite-worker.json' if selected.name=='finish-selected-voice.py' else 'finite-word-review.json')
        elif selected in [(m21/'run-capture-queue.py').resolve(), (m21/'compose-lecture.py').resolve(), (batch/'run-module-preflight.py').resolve(), (batch/'run-module-render.py').resolve(), (batch/'compose-module.py').resolve()]:
            queue = Path(value('--queue')).resolve()
            if not queue.is_relative_to(ROOT/'projects'):
                return False
            statefile = queue.parent/('composite/worker.json' if selected.name in {'compose-lecture.py','compose-module.py'} else 'progress.json')
        elif selected == (batch/'run-prepared-module-queues.py').resolve():
            statefile=batch/'module-queue-worker.json'
        elif selected == (batch/'finish-remaining-speech.py').resolve() and '--run' in arguments:
            statefile=batch/'local/remaining-speech-worker.json'
        elif selected == (batch/'finish-module-candidates.py').resolve() and '--run' in arguments:
            statefile=batch/'local/finish-module-candidates.json'
            if '--repaired-episode' in arguments:
                ep=value('--repaired-episode');rev=value('--audio-revision')
                if not __import__('re').fullmatch(r'[mM](?:2[2-9]|3[0-3])',ep or '') or not __import__('re').fullmatch(r'(?:[2-9]|1[0-2])',rev or ''):return False
                statefile=statefile.with_name('finish-'+ep.lower()+'-audio-v'+rev+'.json')
        elif selected == (batch/'finish-m21-media-qa.py').resolve():
            revision=value('--revision') or 'render-v3'
            if not __import__('re').fullmatch(r'render-v\d+',revision):return False
            statefile=m21/'local'/revision/'finite-final-qa.json'
        elif selected == (batch/'review-final-mix.py').resolve():
            queue=Path(value('--queue')).resolve()
            if not queue.is_relative_to(ROOT/'projects'):return False
            statefile=queue.parent/'final-mix-review/worker.json'
        elif selected == (ROOT/'projects/game-math-skinning-normal-map/production/review-suspect-words.py').resolve():
            statefile=selected.parent/'local/audio-v1/review/targeted-context/worker.json'
        elif selected == (m21/'fix-audio-frame-tail.py').resolve():
            statefile=m21/'local/render-v4/composite/worker.json'
        elif selected == (m21/'unity-staging/run-preflight.py').resolve():
            folder = Path(value('--job-folder')).resolve()
            if not folder.is_relative_to(m21/'unity-staging'):
                return False
            statefile = folder/'progress.json'
        if statefile is None or not statefile.is_file():
            return False
        state = read(statefile)
        waiting=state.get('status') in {'waiting','waiting-for-idle-resources','waiting-for-current-voice','waiting-for-resource-boundary','waiting-for-m21-edit','waiting-for-encoded-master'}
        if selected == (batch/'run-prepared-module-queues.py').resolve() and state.get('status')=='running-one-preflight':
            import psutil
            child=psutil.Process(state['childPid'])
            waiting=child.ppid()==process.pid and verified_waiting_math_worker(child,child.cmdline())
        if selected in [(batch/'finish-remaining-speech.py').resolve(),(batch/'finish-module-candidates.py').resolve()] and state.get('status')=='waiting-for-finite-child':
            import psutil
            try:
                child=psutil.Process(state['childPid'])
                waiting=child.ppid()==process.pid and verified_waiting_math_worker(child,child.cmdline())
            except psutil.NoSuchProcess:
                waiting=False
        return (state.get('pid') == process.pid
                and abs(state.get('createTime',0)-process.create_time()) < .1
                and waiting)
    except (ValueError,TypeError,IndexError,KeyError,OSError):
        return False

def shared_capture_idle():
    library = ROOT / 'unity/VideoEditing/Library'
    status = library / 'AnimationGridV1.status.json'
    if not status.is_file() or list(library.glob('*.request')) or list(library.glob('*.request.json')):
        return False
    current = read(status)
    return (current.get('status')=='complete' and current.get('completed')==current.get('frames')
            and current.get('slug')=='animation-exaggeration')

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
                and ('-batchmode' not in parent_args or (shared_capture_idle() and Path(value(parent_args,'-projectpath') or '').resolve() == (ROOT/'unity/VideoEditing').resolve()))
                and value(args,'-projectpath') is not None
                and value(parent_args,'-projectpath') is not None
                and Path(value(args,'-projectpath')).resolve() == Path(value(parent_args,'-projectpath')).resolve())
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--manifest', help='Additive project-owned audio revision; preserves existing approved/raw PCM')
    parser.add_argument('--synthesize', action='store_true', help='Root-coordinated actual GPU synthesis, after source/script review')
    parser.add_argument('--allow-idle-editors', action='store_true', help='Selected Buckshot root choice: preserve inspected idle editor windows, require9GiBfree/util<=40, cap allocator7GiB; never permit render/compute jobs')
    parser.add_argument('--check-resources', action='store_true', help='Inspect resource guard and record baseline only; never load a model or take GPU lease')
    args = parser.parse_args()
    manifest = read(MANIFEST)
    script = read(ROOT / manifest['paths']['script'])
    english = read(ROOT / manifest['paths']['scriptEn'])
    assert manifest['slug'] == script['slug'] == english['slug'] == SLUG
    assert [(s['id'], len(s['lines'])) for s in script['scenes']] == [(s['id'], len(s['lines'])) for s in english['scenes']]
    authorization = read(ROOT / 'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
    assert authorization['productionAllowedNow'] is True and SLUG in authorization['projectSlugs']
    edition_path = PROJECT / 'planning/part2-delivery-edition.json'
    if edition_path.is_file() and (args.synthesize or args.check_resources):
        selected_output = read(edition_path)['audioRevision']
        if Path(manifest['tts']['outputDir']).name != selected_output:
            print('A newer speech edition owns this lecture. Earlier files are preserved.')
            raise SystemExit(88)
    plan = read(PROJECT / 'planning/production-plan.json')
    if args.synthesize:
        assert all(plan.get(k) is True for k in ['sourceFinal','narrationFinal','sceneBindingsFinal']), 'Finish actual source, narration and inspected gameplay binding before synthesis.'
    derived = {'scenes': [{'id': f"{s['id']}-{n:02d}", 'title': s['title'], 'lines': [line]} for s in script['scenes'] for n, line in enumerate(s['lines'], 1) if line.strip()]}
    audio_dir=(ROOT/manifest['tts']['outputDir']).resolve()
    assert audio_dir.is_relative_to(PROJECT/'production/local')
    derived_path = audio_dir / 'narration.lines.ko.json'
    save(derived_path, derived)
    render_manifest = json.loads(json.dumps(manifest))
    render_manifest['paths']['script'] = derived_path.relative_to(ROOT).as_posix()
    render_path = audio_dir / 'render-manifest.json'
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
        # Verified installed Epic launcher/web/overlay windows are desktop GUI,
        # not the Unreal editor or a launched game. Actual game/render checks
        # and the three GPU-capacity samples below still apply.
        epic_gui = {
            'epicgameslauncher.exe': '/epic games/launcher/portal/binaries/win64/epicgameslauncher.exe',
            'epicwebhelper.exe': '/epic games/launcher/engine/binaries/win64/epicwebhelper.exe',
        }
        if name == 'lockapp.exe' and exe == 'c:/windows/systemapps/microsoft.lockapp_cw5n1h2txyewy/lockapp.exe':
            gui_allow.add(name)
        if (name in epic_gui and exe.endswith(epic_gui[name])) or (name == 'eosoverlayrenderer-win64-shipping.exe' and '/epic games/epic online services/managedartifacts/' in exe):
            gui_allow.add(name)
        process_names[info['pid']] = name
        if SLUG in authorization['projectSlugs'] and exe=='c:/program files/windowsapps/microsoft.zunemusic_11.2609.11.0_x64__8wekyb3d8bbwe/microsoft.media.player.exe':
            gui_allow.add(name)  # local playback; capacity samples still required
        arguments = [str(a).lower() for a in (info['cmdline'] or [])]
        joined = ' '.join(arguments)
        hub = name == 'unity.exe' and exe.endswith('/unity hub/resources/unity.exe') and 'serve' in arguments
        idle_capture_server = False
        if name == 'unity.exe' and '-projectpath' in arguments and '-batchmode' in arguments:
            i = arguments.index('-projectpath')
            shared = ROOT / 'unity/VideoEditing'
            if i+1 < len(arguments) and Path(arguments[i+1]).resolve() == shared.resolve():
                status = shared / 'Library/AnimationGridV1.status.json'
                pending = list((shared/'Library').glob('*.request')) + list((shared/'Library').glob('*.request.json'))
                if status.is_file() and not pending:
                    current = read(status)
                    idle_capture_server = (current.get('status')=='complete' and current.get('completed')==current.get('frames') and current.get('slug')=='animation-exaggeration')
        if idle_capture_server and args.allow_idle_editors:
            gui_allow.add(name)

        import_worker = args.allow_idle_editors and unity_import_worker(info, proc)
        editor = not hub and (name in ['unity.exe', 'unrealeditor.exe', 'blender.exe'] or name.startswith('godot'))
        batch_flags = [flag for flag in ['--write-movie', '--headless', '--background', '-b', '-batchmode', '-moviepipeline', '-render', '--render'] if any(a == flag or (flag == '-moviepipeline' and a.startswith(flag)) or (flag == '-render' and a.startswith('-renderoffscreen')) for a in arguments)]
        actual_game = '/steamapps/common/' in exe or name in ['overwatch.exe','buckshot roulette.exe','buckshot roulette_windows.exe','monsterhunterwilds.exe','d2r.exe','diablo ii.exe']
        compute = name.startswith(('python', 'ffmpeg'))
        # Download/remux helpers are CPU I/O, not inference or video encoding.
        # Keep the GPU process inventory and headroom guard below unchanged.
        if name == 'ffmpeg.exe':
            codecs=[arguments[j+1] for j,a in enumerate(arguments[:-1]) if a in ('-c','-codec','-c:v','-c:a','-vcodec','-acodec')]
            if codecs and all(c=='copy' for c in codecs) and '-hwaccel' not in arguments:
                compute=False
        if name.startswith('python') and '-m' in arguments:
            module_at=arguments.index('-m')+1
            if module_at<len(arguments) and arguments[module_at] in ('yt_dlp','http.server'):
                compute=False
        cpu_research = name.startswith('python') and verified_cpu_research(arguments)
        # These exact read-only HTTP servers serve already-rendered local files.
        # Keep games, other Python workers, the WDDM PID check, load samples
        # and the exclusive lease unchanged. This finite math batch uses the same hosts.
        if compute and name.startswith('python') and SLUG in authorization['projectSlugs']:
            review_servers={
                'projects/shorts-doom-noise-alert/serve_review.py':('b0d9bcae8eea8e69106fe579729acacc42e09da91acf50bfa7cb0965f9f3e85b',{'9364'}),
                'production/batches/tech-ten-shorts-20261030/general-review/serve.py':('8a7fd9b973882c64005fa9228cde51b46b7b4dfff13ddffddebf6b43aca8171f',{'9358','9359'}),
            }
            if len(arguments)==6 and arguments[1:4]==['-x','utf8','-u']:
                for rel,(signature,ports) in review_servers.items():
                    path=(ROOT/rel).resolve()
                    if Path(arguments[4]).resolve()==path and arguments[5] in ports and digest(path)==signature:
                        compute=False
                        baseline.append({'pid':info['pid'],'disposition':'preserved-read-only-review-server','sourceSha256':signature})
        if cpu_research:
            compute=False
            baseline.append({'pid':info['pid'],'name':info['name'],'disposition':'preserved-verified-CPU-only-research','sourceSha256':'bf9ab30630f0a7e054b444779123ad3f7e25648bec2af77f66bd3b69f79a3f06'})
        if name.startswith('python') and verified_waiting_math_worker(proc, info.get('cmdline') or []):
            compute=False
            baseline.append({'pid':info['pid'],'name':info['name'],'disposition':'preserved-verified-waiting-finite-math-coordinator'})
        if compute and name.startswith('python') and passive_python_host(proc,info.get('cmdline') or []):
            compute=False
            baseline.append({'pid':info['pid'],'name':info['name'],'disposition':'preserved-passive-CPU-host-no-GPU-modules'})
        reason = 'actual-game' if actual_game else 'foreign-compute-process' if compute else 'editor-background-render' if editor and batch_flags and not import_worker and not idle_capture_server else 'editor-not-explicitly-allowed' if editor and not args.allow_idle_editors else None
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
    # A 7 GiB allocator cap leaves at least 2 GiB of measured free headroom.
    # The previous 10 GiB admission rule rejected otherwise idle launchers.
    minimum_free, maximum_utilization = (9216, 40) if args.allow_idle_editors else (8192, 14)
    assert all(s['freeMiB'] >= minimum_free and s['utilization'] <= maximum_utilization for s in samples), ('Insufficient inspected GPU capacity; existing windows/jobs preserved', samples)
    free = min(s['freeMiB'] for s in samples)
    if args.check_resources and not args.synthesize:
        preflight = {'status':'resource-preflight-passed-no-synthesis','checkedAt':time.time(),'project':SLUG,'rootScope':'explicit M21–M33 local review batch','allowIdleEditors':args.allow_idle_editors,'baselineProcesses':baseline,'observedGpuRows':observed_gpu_rows,'gpuSamples':samples,'allocatorCapMiBIfStarted':min(7168 if args.allow_idle_editors else 8192,free-700),'gpuModelLoaded':False,'gpuLeaseCreated':False,'foreignProcessesChanged':False}
        save(worker.OUTPUT_DIR/'resource-preflight.json',preflight)
        print(json.dumps({'status':preflight['status'],'gpuSamples':samples,'baselineProcesses':len(baseline),'gpuRows':len(observed_gpu_rows),'gpuModelLoaded':False},ensure_ascii=False))
        return
    inputs = {name: digest(ROOT / manifest['paths'][name]) for name in ['script', 'scriptEn']}
    inputs.update(reference=digest(ROOT / manifest['tts']['reference']), referenceText=digest(ROOT / manifest['tts']['referenceText']), manifest=digest(MANIFEST))
    input_record = worker.OUTPUT_DIR / 'render-inputs.json'
    if input_record.exists():
        assert read(input_record)['sha256'] == inputs, 'Inputs changed: preserve previous takes and select a new audio revision before rendering.'
    save(input_record, {'sha256': inputs, 'rawTakesPreserved': True})
    state = {'schemaVersion': 1, 'project': SLUG, 'token': str(uuid.uuid4()), 'state': 'gpu_granted_to_tts', 'requestedAt': time.time(), 'coordinator': {'pid': me.pid, 'createTime': me.create_time()}, 'foreignProcessesPaused': [], 'rootExplicitInvocation': '--synthesize' + (' --allow-idle-editors' if args.allow_idle_editors else ''), 'selectedProjectResourceChoice': 'Inspected idle GUI editors preserved; require9GiBfree/util<=40; block actual games, background renders and foreign Python/FFmpeg compute' if args.allow_idle_editors else 'Default exclusive idle resource guard', 'baselineProcesses': baseline, 'observedGpuRows': observed_gpu_rows, 'gpuSamples': samples, 'gpuBeforeTts': {'freeMiB': free, 'totalMiB': total, 'utilization': utilization}, 'allocatorCapMiB': min(7168 if args.allow_idle_editors else 8192, free - 700), 'generations': []}
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
        from paragraph_level import level_paragraph,speech_level
        for si, scene in enumerate(script['scenes']):
            local = 0.0
            parts = []
            for n, text in enumerate(scene['lines'], 1):
                raw = worker.CHUNK_DIR / f"{scene['id']}-{n:02d}-scene.wav"
                samples, sr = worker._read_mono(raw)
                sr0 = sr0 or sr
                assert sr == sr0
                levelled,before,gain_db=level_paragraph(samples,sr,eq,worker._apply_edge_fades)
                if n > 1:
                    parts.append(np.zeros(round(gap*sr), dtype=np.float32)); local += gap
                seconds = len(levelled)/sr
                entries.append({'index': len(entries)+1, 'scene_id': scene['id'], 'scene_title': scene['title'], 'paragraph': n, 'text': text, 'display_text': scene.get('displayLines', scene['lines'])[n-1], 'text_en': english['scenes'][si]['lines'][n-1], 'start': position+local, 'end': position+local+seconds})
                levels.append({'id': f"{scene['id']}-{n:02d}", 'rawSha256': digest(raw), 'beforeMedianDbfs': before, 'gainDb': gain_db, 'afterMedianDbfs': speech_level(levelled,sr,eq), 'peak': float(np.abs(levelled).max()), 'seconds': seconds})
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

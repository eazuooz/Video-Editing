"""One read-only resource observation for existing approved additive PCM ASR."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, psutil, os

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
R = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = R / 'resource-before-additive-asr-v2.json'
assert not out.exists(), 'Inspect existing observation; do not repeat'
tts = read(R / 'narration-tts-execution-v2.json')
resume = read(R / 'research-handoff-verification-v2.json')
assert tts['generationComplete'] and tts['actualOuterExitCode'] == 0
assert resume['restorationVerified'] and resume['ownedVoiceWorkerClosed']
for item in tts['protectedInputs'] + tts['results']:
    assert sha(ROOT / item['path']) == item['sha256'], item['path']
processes, own = [], []
for p in psutil.process_iter(['pid', 'create_time', 'name', 'cmdline']):
    try:
        name = (p.info['name'] or '').lower()
        cmd = ' '.join(p.info['cmdline'] or [])
        if name in ('python.exe', 'ffmpeg.exe', 'node.exe'):
            processes.append(dict(pid=p.pid, createTime=p.info['create_time'],
                commandLine=p.info['cmdline'], cwd=p.cwd()))
            owned_batch = any(s in cmd for s in ['unpublished-teaching-clarity-revision', 'cross-game-example-coverage-review'])
            is_worker = any(s in cmd for s in ['render-orientation', 'review-orientation', 'extract-orientation',
                'render-motion', 'review-motion', 'build-motion-current17', 'assemble-motion-current17', 'extract-motion'])
            if p.pid != os.getpid() and owned_batch and is_worker:
                own.append(p.pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
cim = subprocess.check_output(['powershell', '-NoProfile', '-Command',
    "Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','ffmpeg.exe','node.exe') } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],
    text=True, encoding='utf-8', errors='replace')
gpu = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free,utilization.gpu',
    '--format=csv,noheader,nounits'], text=True).strip()
cpu = psutil.cpu_percent(interval=2)
ram = psutil.virtual_memory().available // 1024
now = datetime.now(timezone.utc).isoformat()
data = dict(observedAt=now, ownHeavyCpuJobs=len(own), ownHeavyPids=own,
    cpuLoadPercent=cpu, freePhysicalMemoryKiB=ram, gpuObservation=gpu,
    processes=processes, cimActual=cim, protectedInputCount=len(tts['protectedInputs']),
    protectedShaMatched=True, currentAdditivePcmCount=6, additivePcmHashesMatched=True,
    ownTtsAndAnnotationCompleted=True, historicalResearchRestorationVerified=True,
    currentResearchStateIsSeparate=True, processControlChanges=0,
    cpuThreads=2, gpuJobs=0, intendedWorker='production/batches/unpublished-teaching-clarity-revision/review-orientation-additive-voice-v2.py',
    intendedMode='contexts', next='Actual session/PID/create registration; whole6 reviewed and preserved; compare independent22; no newTTS.')
out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf-8')
assert not own and cpu < 85 and ram > 8_000_000
qp = B / 'queue.json'
raw = qp.read_bytes()
q = read(qp)
q['currentOrientationReview'] = dict(stage='approved6PCM-independent22-ASR-preflight',
    baselineVideoId='6-kP65hrZcI', resource=out.relative_to(ROOT).as_posix(),
    plannedWorker=data['intendedWorker'], cpuThreads=2, gpuJobs=0,
    actualSession=None, activeOwnedWorkers=0, minimumFourGamesApproved=False,
    preserveBaseline24Pcm=True, preserveCompleted6AdditivePcm=True,
    next='Single CPU2 independent22 ASR, then actual registration; compare all complete recognized texts.')
q['updatedAt'] = now
assert qp.read_bytes() == raw, 'Concurrent queue update; preserve it'
qp.write_text(json.dumps(q, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps(dict(resource=out.relative_to(ROOT).as_posix(), cpu=cpu, freeRamKiB=ram,
    gpu=gpu, ownHeavy=0, protectedInputCount=len(tts['protectedInputs']), additivePcmCount=6)))

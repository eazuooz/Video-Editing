"""Fresh read-only CPU resource and current preservation check before acquisition."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import psutil

ROOT = Path(__file__).resolve().parents[3]
V = ROOT / 'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
out = V / 'source-cpu-resource-verification-v2.json'
assert not out.exists(), 'Do not repeat this observation; use a new version when needed'
def sha(p):
    digest = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()
baseline = read(V / 'baseline-preservation-v1.json')
for item in baseline['protectedInputs']:
    assert sha(ROOT / item['path']) == item['sha256'], item['path']
own = []
processes = []
observer = psutil.Process()
parents = {p.pid for p in observer.parents()}
for p in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
    try:
        if (p.info['name'] or '').lower() not in ['python.exe', 'node.exe', 'ffmpeg.exe']:
            continue
        item = dict(pid=p.pid, name=p.info['name'], command=p.info['cmdline'],
            createTime=p.info['create_time'], cwd=p.cwd())
        processes.append(item)
        command = ' '.join(p.info['cmdline'] or [])
        if (p.pid not in {os.getpid(), *parents} and 'hierarchical' in command
                and any(t in command for t in ['acquire-', 'render-', 'assemble-', 'extract-', 'generate-'])):
            own.append(item)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
assert not own, own
cim = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
    "Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','node.exe','ffmpeg.exe') } | Select-Object ProcessId,ParentProcessId,Name,CreationDate,CommandLine | ConvertTo-Json -Depth 4 -Compress"],
    cwd=ROOT, capture_output=True, encoding='utf-8', errors='replace')
assert cim.returncode == 0
(V / 'source-resource-v2.cim.json').write_text(cim.stdout, 'utf-8')
gpu = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu',
    '--format=csv,noheader,nounits'], capture_output=True, text=True)
assert gpu.returncode == 0, gpu.stderr
research = Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json')
assert sha(research) == 'bbeac85c5f493baec614eeb5fae13f15d8b9b913f58631dce2d2ee211f07b0b8'
index = ROOT / '.git/index'
git = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
entries = subprocess.check_output([git, 'ls-files', '--stage', '-z'], cwd=ROOT)
cpu = psutil.cpu_percent(interval=.3)
ram = psutil.virtual_memory().available
disk = psutil.disk_usage(str(ROOT)).free
assert cpu < 85 and ram > 6*1024**3 and disk > 8*1024**3, (cpu,ram,disk)
result = dict(schemaVersion=1, observedAt=datetime.now(timezone.utc).isoformat(),
    observer=dict(pid=os.getpid(), createTime=observer.create_time(), command=observer.cmdline(), cwd=observer.cwd()),
    cpuPercent=cpu, availableRamBytes=ram, availableDiskBytes=disk, gpuCsv=gpu.stdout.strip(),
    processIdentityEvidence=processes, cimEvidence='projects/hierarchical-game-outlines/revision-teaching-clarity-v1/source-resource-v2.cim.json',
    protectedInputsChecked=len(baseline['protectedInputs']), all49ProtectedInputsShaIdentical=True,
    currentOrientationMainSha256=sha(ROOT / 'projects/game-math-orientation-matrices/project.json'),
    completedResearchStatusSha256=sha(research), completedResearchManipulated=False,
    activeOwnedMediaWorkers=own, externalIndexSha256=sha(index),
    externalIndexEntriesSha256=hashlib.sha256(entries).hexdigest(),
    proposedJob='one additional clearer Timberborn developer stream;CPU2/GPU0;no model/TTS/render',
    cpuAcquisitionEligible=True, gpuTtsEligible=False, foreignProcessesChanged=False)
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps({k:result[k] for k in ['observedAt','cpuPercent','availableRamBytes','availableDiskBytes','gpuCsv','protectedInputsChecked','activeOwnedMediaWorkers','cpuAcquisitionEligible']}))

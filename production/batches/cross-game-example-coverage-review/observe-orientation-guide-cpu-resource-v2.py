"""One fresh read-only CPU/GPU/CIM observation; include final assembly workers."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess
import psutil
ROOT = Path(__file__).resolve().parents[3]
O = ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--version',type=int,required=True);a=ap.parse_args()
out=O/f'resource-before-guide-CPU-v{a.version}.json';assert not out.exists()
proof=read(O/'narration-07b-guide-repair-execution-v1.json')
assert proof['actualExitObserved'] and read(O/'07b-guide-repair-voice-closure-verification-v1.json')['restorationVerified']
for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
processes=[];own=[];ownPrefixes=['render-orientation','review-orientation','extract-orientation','build-orientation','assemble-orientation','render-motion','review-motion','build-motion-current17','assemble-motion-current17','extract-motion']
for p in psutil.process_iter(['pid','create_time','name','cmdline']):
    try:
        cmd=' '.join(p.info['cmdline'] or [])
        if (p.info['name'] or '').lower() in ['python.exe','ffmpeg.exe','node.exe']:
            processes.append(dict(pid=p.pid,createTime=p.info['create_time'],commandLine=p.info['cmdline'],cwd=p.cwd()))
            if p.pid!=os.getpid() and ('cross-game-example-coverage-review' in cmd or 'unpublished-teaching-clarity-revision' in cmd) and any(x in cmd for x in ownPrefixes):own.append(p.pid)
    except (psutil.NoSuchProcess,psutil.AccessDenied):pass
cim=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','ffmpeg.exe','node.exe') } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],text=True,encoding='utf-8',errors='replace')
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
cpu=psutil.cpu_percent(interval=2);ram=psutil.virtual_memory().available//1024
data=dict(observedAt=datetime.now(timezone.utc).isoformat(),ownHeavyJobs=len(own),ownHeavyPids=own,
    cpuLoadPercent=cpu,freePhysicalMemoryKiB=ram,processes=processes,cimActual=cim,gpuObservation=gpu,
    protectedShaMatched=True,protectedCount=len(proof['protectedInputs']),repairCandidateShaMatched=True,
    researchChanges=0,cpuThreads=2,gpuJobs=0,guardPassed=not own and cpu<85 and ram>8_000_000)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
assert data['guardPassed']
print(json.dumps(dict(resource=out.relative_to(ROOT).as_posix(),cpu=cpu,ramKiB=ram,ownHeavy=0,gpu=gpu,protected=len(proof['protectedInputs']))))

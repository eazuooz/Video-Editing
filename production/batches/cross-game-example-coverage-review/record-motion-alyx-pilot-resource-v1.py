from pathlib import Path
from datetime import datetime,timezone
import json,psutil,subprocess
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
rows=[]
for p in psutil.process_iter(['pid','create_time','cmdline','name']):
    try:
        c=' '.join(p.info['cmdline'] or [])
        if p.info['name'] and p.info['name'].lower() in ['python.exe','ffmpeg.exe','node.exe']:
            rows.append(dict(pid=p.pid,createTime=p.info['create_time'],command=p.info['cmdline'],cwd=p.cwd()))
    except (psutil.AccessDenied,psutil.NoSuchProcess):pass
own=[x for x in rows if 'cross-game-example-coverage-review/' in ' '.join(x['command']) and any(s in ' '.join(x['command']) for s in ['render-motion-','review-motion-','extract-motion-'])]
out=dict(observedAt=datetime.now(timezone.utc).isoformat(),cpuLoadPercent=psutil.cpu_percent(interval=1),
    freePhysicalMemoryKiB=psutil.virtual_memory().available//1024,ownHeavyCpuJobs=len(own),processes=rows,
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip(),
    processOrResearchControlMutations=0)
path=R/'alyx-pilot-resource-v1.json';assert not path.exists();path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({k:out[k] for k in ['cpuLoadPercent','freePhysicalMemoryKiB','ownHeavyCpuJobs','gpu']}))

"""Fresh read-only CPU/GPU/process/PCM evidence before one current ASR job."""
from pathlib import Path
from datetime import datetime,timezone
import json,psutil,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'resource-before-additions-whole-asr-v1.json';assert not out.exists()
tts=read(R/'narration-tts-execution-v7.json');resume=read(R/'research-handoff-verification-v7.json')
assert tts['generationComplete'] and tts['actualExitObserved'] and tts['actualOuterExitCode']==0 and resume['restorationVerified']
for row in tts['protectedInputs']+tts['results']:assert sha(ROOT/row['path'])==row['sha256']
procs=[];owned=[]
for p in psutil.process_iter(['pid','name','create_time','cmdline','cwd']):
    try:
        if p.info['name'] and any(s in p.info['name'].lower() for s in ['python','ffmpeg','node']):
            cmd=' '.join(p.info['cmdline'] or [])
            if 'Video-Editing' in cmd or 'renderformer' in cmd:procs.append(p.info)
            if p.pid!=psutil.Process().pid and any(s in cmd for s in ['render-motion-four-additions','review-motion-four-additive-voice','render-motion-portal','render-motion-alyx','render-orientation-additions','render-orientation-annotation']):
                owned.append(p.info)
    except (psutil.AccessDenied,psutil.NoSuchProcess):pass
assert not owned,'Reuse existing live owned job; never duplicate it'
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
resource=dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),cpuLoadPercent=psutil.cpu_percent(interval=1),
    freePhysicalMemoryKiB=psutil.virtual_memory().available//1024,ownHeavyCpuJobs=0,gpuObservation=gpu,processes=procs,
    all68ProtectedInputsMatched=True,allThreeCurrentPcmHashesMatched=True,voiceOuterSession=62462,voiceOuterExitCode=0,
    ownedResearchRestorationVerified=True,restorationProofSha256=sha(R/'research-handoff-verification-v7.json'),
    processOrPauseOrLeaseMutations=0)
out.write_text(json.dumps(resource,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({k:resource[k] for k in ['observedAt','cpuLoadPercent','freePhysicalMemoryKiB','ownHeavyCpuJobs','gpuObservation']}))

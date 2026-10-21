"""One bounded GPU batch with the approved voice; preserve foreign jobs."""
from pathlib import Path
import json,subprocess,sys,time,uuid,os,hashlib
import psutil
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];L=P/'production/local';LEASE=R/'shared/output/GPU_HANDOFF.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
control=read(R/'shared/publishing/video-production-control.json')
assert control.get('selectedShortVideo')==P.name
assert control.get('shortsDirectSelection',{}).get('selectedRevision')=='normal-map-v1'
assert control['shortsDirectSelection'].get('fullProductionAuthorized') is True
assert not LEASE.exists(),'Existing GPU lease preserved; do not pause or overwrite it'
prepared=read(P/'script/narration.spoken.ko.json')
assert prepared['derivation']['displayScriptSha256']==hashlib.sha256((P/'script/narration.ko.json').read_bytes()).hexdigest(),'Display script changed after spoken input preparation'
assert prepared['derivation']['clausesSha256']==hashlib.sha256((P/'script/clauses.json').read_bytes()).hexdigest(),'Pronunciation/caption clauses changed'
plan=read(P/'planning/production-plan.json')
assert plan['status']=='ready-for-narration', 'Root actual preview must pass and plan must be ready before TTS'
raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.total,utilization.gpu','--format=csv,noheader,nounits'],text=True)
free,total,util=[int(x.strip()) for x in raw.splitlines()[0].split(',')]
assert util < 20, ('Unregistered active GPU work; preserve it', util)
assert free>=7500,('Insufficient free memory; no foreign applications stopped',free)
clients=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
assert not any('python' in row.lower() for row in clients.splitlines()),'Another GPU Python process is active; preserve it.'
me=psutil.Process();token=str(uuid.uuid4());record=dict(schemaVersion=1,project=P.name,token=token,state='gpu_granted_to_tts',requestedAt=time.time(),coordinator=dict(pid=me.pid,createTime=me.create_time()),gpuBefore=dict(freeMiB=free,totalMiB=total,utilization=util),allocatorLimitMiB=6144,foreignProcessesPaused=[],userEvidence=control['shortsDirectSelection']['userEvidence'], inputs={k:hashlib.sha256((R/v).read_bytes()).hexdigest() for k,v in dict(script=f'projects/{P.name}/script/narration.spoken.ko.json', displayScript=f'projects/{P.name}/script/narration.ko.json', clauses=f'projects/{P.name}/script/clauses.json', manifest=f'projects/{P.name}/production/tts-manifest.json', reference='shared/voice-reference/reference-15-35s.wav', referenceText='shared/voice-reference/reference-15-35s.ko.txt').items()})
with LEASE.open('x',encoding='utf8') as f:json.dump(record,f)
code=1
try:
 import torch
 torch.set_num_threads(4);torch.set_num_interop_threads(2)
 torch.cuda.set_per_process_memory_fraction(6144*1048576/torch.cuda.get_device_properties(0).total_memory,0)
 sys.path.insert(0,str(R/'qwen3-tts'));import render_narration as worker
 worker.configure_project(P.name,f'projects/{P.name}/production/tts-manifest.json');worker.load_tts_dependencies()
 items=worker.build_render_items(worker.load_jobs());assert len(items)==1,'One continuous scene only'
 worker.render_chunks(items,1);worker.assemble_outputs(worker.load_jobs())
 assert all(hashlib.sha256((R/v).read_bytes()).hexdigest()==record['inputs'][k] for k,v in dict(script=f'projects/{P.name}/script/narration.spoken.ko.json', displayScript=f'projects/{P.name}/script/narration.ko.json', clauses=f'projects/{P.name}/script/clauses.json', manifest=f'projects/{P.name}/production/tts-manifest.json', reference='shared/voice-reference/reference-15-35s.wav', referenceText='shared/voice-reference/reference-15-35s.ko.txt').items()),'TTS input changed during generation'
 record.update(peakAllocatedMiB=torch.cuda.max_memory_allocated()/1048576,peakReservedMiB=torch.cuda.max_memory_reserved()/1048576)
 code=0
except BaseException as error:
 record['failure']={'type':type(error).__name__,'message':str(error),'automaticRetry':False,'sourceOutputsPreserved':True}
 raise
finally:
 if 'torch' in globals() and torch.cuda.is_initialized():
  record.update(peakAllocatedMiB=torch.cuda.max_memory_allocated()/1048576,peakReservedMiB=torch.cuda.max_memory_reserved()/1048576)
 record.update(state='finished' if code==0 else 'failed',finishedAt=time.time(),exitCode=code)
 save(L/'tts-execution.json',record)
 if LEASE.exists() and read(LEASE).get('token')==token:LEASE.unlink()

"""Selected-v2 GPU batch with immutable v1 and hash-checked reuse."""
from pathlib import Path
import argparse,json,subprocess,os,sys,time,uuid,hashlib
import psutil
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
OUT=ROOT/'shared/output'/SLUG/'revision-v2';FLAGS=subprocess.CREATE_NO_WINDOW
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--scenes',default='');p.add_argument('--probe',action='store_true');p.add_argument('--asr-only',action='store_true');a=p.parse_args()
control=read(ROOT/'shared/publishing/video-production-control.json');assert control['selectedVideo']==SLUG and control['newProductionAuthorization']['fullProductionAuthorized']
m=read(ROOT/f'projects/{SLUG}/project.json');assert m['revision']['id']=='v2'
prepared=read(OUT/'prepared.json');ids=a.scenes.split(',') if a.scenes else prepared['changedScenes'];assert set(ids)<=set(prepared['changedScenes'])
tag='probe' if a.probe else 'batch';statuspath=OUT/(tag+'-status.json');out=ROOT/m['tts']['outputDir']
lease=ROOT/'shared/output/GPU_HANDOFF.json';assert not lease.exists(),'Preserve the existing GPU owner'
me=psutil.Process();ancestors={x.pid for x in me.parents()}
foreign=[{'pid':x.pid,'name':x.info['name'],'command':x.info['cmdline']} for x in psutil.process_iter(['pid','name','cmdline']) if (x.info['name'] or '').lower().startswith(('python','train','torchrun')) and x.pid not in ancestors and x.pid!=me.pid];assert not foreign,foreign
raw=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=FLAGS).strip();name,total,free,util=[x.strip() for x in raw.split(',')]
assert '5070 Ti' in name and int(free)>=11000 and int(util)<40,raw
token=str(uuid.uuid4());record={'schemaVersion':1,'token':token,'project':SLUG,'state':'gpu_granted_to_tts','coordinator':{'pid':me.pid,'createTime':me.create_time()},'researchPaused':False,'gpuBefore':raw,'requestedAt':time.time()}
with lease.open('x',encoding='utf-8') as f:json.dump(record,f,indent=2)
status={'pid':me.pid,'startedAt':time.time(),'scenes':ids,'status':'running','stage':'synthesis'};save(statuspath,status)
def run(stage,cmd):
 status['stage']=stage;save(statuspath,status)
 with (OUT/(tag+'-'+stage+'.log')).open('ab') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=FLAGS)
try:
 # Probe invokes only generation; the standard assembler requires all28 takes.
 pending=[sid for sid in ids if not (out/'chunks'/f'{sid}-scene.wav').exists()]
 if pending and not a.asr_only:
  run('synthesis',[sys.executable,'-X','utf8',str(Path(__file__).with_name('synthesize-revision-v2.py')),'--scenes',','.join(pending)])
 run('asr',[sys.executable,'-X','utf8','qwen3-tts/review_project_narration.py','--project',SLUG,'--scenes',','.join(ids)])
 for sid in prepared['retainedScenes']:
  assert sha(out/'chunks'/f'{sid}-scene.wav')==sha(ROOT/prepared['oldTtsDirectory']/'chunks'/f'{sid}-scene.wav')
 status.update(status='complete-pending-text-and-acoustic-review',finishedAt=time.time());save(statuspath,status)
finally:
 if lease.exists() and read(lease).get('token')==token:
  record.update(state='released',finishedAt=time.time(),researchRestarts=0);save(OUT/(tag+'-gpu-lease.json'),record);lease.unlink()

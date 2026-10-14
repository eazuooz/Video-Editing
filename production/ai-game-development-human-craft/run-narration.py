"""Single selected-video narration job on the verified 16GB workstation.

Uses the shared lease protocol; does not pause/kill/restart other workloads.
The older idle guard's18GB threshold belongs to a different workstation.
This owner checks the current machine, reserves its GPU, and runs the standard
renderer as its descendant. Canonical caption text is never phoneticized.
"""
from pathlib import Path
import os,sys,json,time,uuid,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[2]
SLUG='ai-game-development-human-craft'
OUT=ROOT/'shared/output'/SLUG/'narration-job'
OUT.mkdir(parents=True,exist_ok=True)
FLAGS=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
def run(args): return subprocess.run(args,cwd=ROOT,check=True,creationflags=FLAGS)
if '--render-child' in sys.argv:
 sys.path.insert(0,str(ROOT/'qwen3-tts'))
 import render_narration as renderer
 from dataclasses import replace
 original=renderer.render_chunks
 pronunciations={'Wild Ox Studios':'와일드 옥스 스튜디오','Unity Spark':'유니티 스파크','UE6':'언리얼 엔진 식스','MCP':'엠씨피','UV':'유브이','UDK':'유디케이','NFT':'엔에프티','Verse':'버스','AI':'에이아이'}
 def spoken(items,batch_size,force_scenes=None):
  changed=[]
  for item in items:
   text=item.text
   for a,b in pronunciations.items():text=text.replace(a,b)
   changed.append(replace(item,text=text))
  return original(changed,batch_size,force_scenes)
 renderer.render_chunks=spoken
 sys.argv=['render_narration.py','--project',SLUG,'--batch-size','1']
 renderer.main()
 raise SystemExit(0)

import psutil
control=json.loads((ROOT/'shared/publishing/video-production-control.json').read_text(encoding='utf-8-sig'))
assert control['selectedVideo']==SLUG
assert control['newProductionAuthorization']['fullProductionAuthorized']
lease=ROOT/'shared/output/GPU_HANDOFF.json'
assert not lease.exists(),'Another GPU lease exists; preserve it.'
foreign=[p.pid for p in psutil.process_iter(['pid','name']) if (p.info['name'] or '').lower().startswith(('python','train','torchrun')) and p.pid!=os.getpid() and p.pid not in [x.pid for x in psutil.Process().parents()]]
assert not foreign,f'Other Python/training processes present: {foreign}; inspect before allocating.'
raw=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=FLAGS)
rows=raw.strip().splitlines();assert len(rows)==1
name,total,free,util=[x.strip() for x in rows[0].split(',')]
assert '5070 Ti' in name and int(total)>=16000 and int(free)>=11000 and int(util)<15,raw
me=psutil.Process();token=str(uuid.uuid4())
record=dict(schemaVersion=1,token=token,project=SLUG,state='gpu_granted_to_tts',requestedAt=time.time(),queueDir=None,idleGpu=True,coordinator=dict(pid=me.pid,createTime=me.create_time()),gpuBeforeTts=dict(name=name,totalMiB=int(total),freeMiB=int(free),utilization=int(util)),researchPaused=False)
with lease.open('x',encoding='utf-8') as f:json.dump(record,f,indent=2)
status={'startedAt':time.time(),'pid':me.pid,'gpuLeaseToken':token,'stage':'tts','status':'running'}
def save(): (OUT/'status.json').write_text(json.dumps(status,indent=2)+'\n',encoding='utf-8')
save()
try:
 run([sys.executable,'-X','utf8',str(Path(__file__).resolve()),'--render-child'])
 status['stage']='english-and-timing';save()
 run([sys.executable,'-X','utf8','qwen3-tts/build_translated_srt.py','--project',SLUG,'--language','en'])
 run([sys.executable,'-X','utf8','qwen3-tts/build_project_timing.py','--project',SLUG])
 status['stage']='full-narration-asr';save()
 m=json.loads((ROOT/f'projects/{SLUG}/project.json').read_text(encoding='utf-8'))
 wav=ROOT/m['paths']['narration'];review=wav.with_suffix('.asr-review.txt')
 if not review.exists():run([sys.executable,'-X','utf8','qwen3-tts/transcribe_reference.py',str(wav),'--output',str(review)])
 status.update(status='complete-pending-content-review',stage='done',wavSha256=hashlib.sha256(wav.read_bytes()).hexdigest());save()
except BaseException as e:
 status.update(status='failed',error=str(e));save();raise
finally:
 if lease.exists() and json.loads(lease.read_text(encoding='utf-8-sig')).get('token')==token:
  record.update(state='released',finishedAt=time.time(),researchRestarts=0)
  (OUT/'gpu-lease-receipt.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
  lease.unlink()

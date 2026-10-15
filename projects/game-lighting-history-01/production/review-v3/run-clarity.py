"""Acquire an idle GPU cooperatively for the selected8-take TTS and ASR batch."""
import datetime,json,os,pathlib,runpy,subprocess,sys,time,uuid
import psutil
R=pathlib.Path(__file__).resolve().parents[4];H=pathlib.Path(__file__).parent
repair=False
O=R/'projects/game-lighting-history-01/production/local/review-v3/clarity'
if repair:O=O/'repairs'
O.mkdir(parents=True,exist_ok=True)
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
runpy.run_path(str(H.parent/'beginner-revision-v1/production-authority.py'))['require_selected_production']()
lease=R/'shared/output/GPU_HANDOFF.json';assert not lease.exists(),'Existing GPU owner preserved.'
me=psutil.Process();ancestry={p.pid for p in me.parents()}|{me.pid}
foreign=[dict(pid=p.pid,name=p.info['name']) for p in psutil.process_iter(['pid','name']) if (p.info['name'] or '').lower().startswith(('python','train','torchrun')) and p.pid not in ancestry]
assert not foreign,foreign
raw=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).strip()
name,free,util=[v.strip() for v in raw.split(',')];assert int(free)>=11000 and int(util)<40,raw
token=str(uuid.uuid4());record=dict(token=token,project='game-lighting-history-01',state='gpu_granted_to_tts',coordinator=dict(pid=me.pid,createTime=me.create_time()),researchPaused=False,gpuBefore=raw)
with lease.open('x',encoding='utf8') as f:json.dump(record,f,indent=2)
state=dict(status='running',stage='synthesis',pid=me.pid,startedAt=time.time(),researchPaused=False,changedParagraphs=3,retainedPcmRegenerated=False)
def run(stage,cmd):
 state['stage']=stage;wr(O/'voice-execution.json',state)
 with (O/(stage+'.log')).open('ab') as log:subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
try:
 run('synthesis',[sys.executable,'-X','utf8',str(H/'synthesize-clarity.py')]+(['--repair'] if repair else []))
 cache=pathlib.Path('C:/Users/1/.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots')
 snapshots=[p for p in cache.iterdir() if (p/'model.safetensors').exists()];assert len(snapshots)==1
 run('source-asr',[sys.executable,'-X','utf8','qwen3-tts/review_project_narration.py','--project','game-lighting-history-01','--manifest',(H/'clarity-tts.project.json').relative_to(R).as_posix(),'--model',str(snapshots[0])])
 state.update(status='complete-pending-direct-review',finishedAt=time.time());wr(O/'voice-execution.json',state)
except BaseException as e:
 state.update(status='failed',error=repr(e),finishedAt=time.time());wr(O/'voice-execution.json',state);raise
finally:
 if lease.exists() and rd(lease).get('token')==token:
  record.update(state='released',finishedAt=time.time(),researchRestarts=0);wr(O/'voice-gpu-lease.json',record);lease.unlink()

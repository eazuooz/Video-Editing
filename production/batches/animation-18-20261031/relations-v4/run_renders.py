"""One finite render job; no scheduling, publishing or automatic next batch."""
from pathlib import Path
import json,sys,time,subprocess,hashlib,datetime,concurrent.futures,os
H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local';PY=R/'qwen3-tts/.venv/Scripts/python.exe'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
episodes=read(H/'planning/relations-plan.json')['episodes'];cpu='--cpu' in sys.argv;requested=[x for x in sys.argv[1:] if x!='--cpu'] or [e['id'] for e in episodes]
control=read(R/'shared/publishing/video-production-control.json')['animationRelationsRevision20261108'];assert control['renderAuthorized'] and all(id in control['episodes'] for id in requested)
reviews={e['id']:e for e in read(L/'text-review.json')};timing=read(L/'timing.json')
assert all(reviews[id]['directReview']=='complete-current-text' for id in requested)
if not cpu:
 sys.path.insert(0,str(R/'qwen3-tts'));from gpu_handoff_guard import schedule_gpu_handoff
 while True:
  try:schedule_gpu_handoff('animation-relations-v4-render','cuda:0',False,8192);break
  except SystemExit as err:print('Preserving current GPU owner:',err,flush=True);time.sleep(15)
else:
 os.environ.update(YAMYAM_RELATIONS_CPU='1',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4')
 print('CPU4-thread encoding; no GPU lease requested and other apps retained.',flush=True)
state={'startedAt':datetime.datetime.now().isoformat(),'requested':requested,'device':'cpu4' if cpu else 'gpu-serialized','assembled':[],'completed':[],'failures':[],'platformChanged':False};save(L/'render-worker.json',state)
pool=concurrent.futures.ThreadPoolExecutor(max_workers=1);verifications={}
def execute(script,id):
 logfile=L/(id+'-'+script+'.log')
 with logfile.open('w',encoding='utf-8') as log:result=subprocess.run([str(PY),'-X','utf8','-u',str(H/script),id],cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 result.check_returncode()
def collect_ready(wait=False):
 for key,future in list(verifications.items()):
  if not wait and not future.done():continue
  try:future.result();state['completed'].append(key);print(key,'technically verified',flush=True)
  except Exception as err:state['failures'].append({'id':key,'stage':'verification','error':repr(err)});print(key,'verification failed; inspect current log',flush=True)
  del verifications[key]
 save(L/'render-worker.json',state)
for id in requested:
 e=next(e for e in episodes if e['id']==id);O=R/'projects'/e['slug']/'production/local/relations-v4';assert (O/'relation.mp4').exists(),(id,'Timed relation render missing')
 try:
  execute('assemble.py',id);state['assembled'].append(id);print(id,'assembled',flush=True)
  # CPU-only decode/packet verification overlaps the next GPU encode, with one checker at a time.
  verifications[id]=pool.submit(execute,'verify_episode.py',id);collect_ready()
 except Exception as err:
  state['failures'].append({'id':id,'error':repr(err)});print(id,'FAILED; preserved outputs and continuing other authorized episodes',flush=True)
 save(L/'render-worker.json',state)
collect_ready(wait=True);pool.shutdown(wait=True)
state['finishedAt']=datetime.datetime.now().isoformat();save(L/'render-worker.json',state)
if state['failures']:raise SystemExit(2)
print('Finite render job complete. Encoded visual review and local delivery remain.',flush=True)

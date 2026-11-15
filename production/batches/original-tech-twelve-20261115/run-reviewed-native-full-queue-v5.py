from pathlib import Path
import importlib.util,json,subprocess,time,datetime
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');BASE=MEDIA/'reviewed-native-full-queue-v5';PYTHON=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
s=importlib.util.spec_from_file_location('full_queue_guard',HERE/'run-camera-native-v1.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.authority();worker=m.runtime.SingleWorker(path=BASE/'worker.json');child=None;results=[]
try:
 worker.acquire();BASE.mkdir(parents=True,exist_ok=True)
 for helper,case,slug,ver in [('run-bounded-native-v3.py','placement','shorts-horizon-gpu-placement','native-bounded-v3'),('run-streamed-native-v2.py','temporal','shorts-inside-temporal-antialiasing','native-stream-v2'),('run-streamed-native-v2.py','remaining-seven','remaining-seven','native-stream-v2')]:
  m.authority();accepted=MEDIA/slug/ver/'accepted-full.json'
  if not accepted.exists():
   m.save(BASE/'status.json',dict(status='finite-native-full-queue',current=case,results=results,newRecurringAutomation=False))
   with (BASE/(case+'.log')).open('w',encoding='utf8')as log:
    child=subprocess.Popen([str(PYTHON),'-u','-X','utf8',str(HERE/helper),'--case',case,'--execute','--mode','full','--wait-minutes','180'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=m.CREATE);worker.update(child=m.identity(child.pid));code=child.wait()
   assert code==0 and accepted.exists(),'Preserve incomplete native output; no automatic model retry'
  results.append(dict(case=case,proof=m.pin(accepted),fullVisualReviewPending=True));print(json.dumps(results[-1]),flush=True)
 m.save(BASE/'status.json',dict(status='full-source-capture-complete-review-pending',results=results,finalFilmsComplete=False))
finally:
 if worker.handle is not None:worker.close(remove=child is None or child.poll()is not None)

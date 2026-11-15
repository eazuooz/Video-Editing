from pathlib import Path
import importlib.util,json,subprocess,time,datetime
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PYTHON=ROOT/'qwen3-tts/.venv/Scripts/python.exe';MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');BASE=MEDIA/'camera-word-confirmation-v5'
s=importlib.util.spec_from_file_location('camera_word_full_guard',HERE/'run-bounded-native-v3.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.configure('lockon');m.authority();worker=m.runtime.SingleWorker(path=BASE/'worker.json');child=None
try:
 worker.acquire();deadline=time.monotonic()+180*60;last=None
 while True:
  m.authority();reason=m.busy()
  if reason is None:break
  if reason!=last:print(json.dumps(dict(status='CPU-only-wait-for-full-guard',reason=reason)),flush=True);last=reason
  if time.monotonic()>=deadline:raise TimeoutError('Finite guarded input confirmation deadline')
  time.sleep(10)
 argv=[str(PYTHON),'-u','-X','utf8',str(HERE/'run-camera-voice-repair-asr-v5.py'),'--project','shorts-mario64-lakitu-camera']
 BASE.mkdir(parents=True,exist_ok=True)
 with (BASE/'asr.log').open('w',encoding='utf8')as log:
  child=subprocess.Popen(argv+['--execute','--wait-minutes','15'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=m.native.CREATE);worker.update(child=m.native.identity(child.pid));code=child.wait()
 status=MEDIA/'shorts-mario64-lakitu-camera/asr-edit-v5/status.json';assert code==0 and m.read(status).get('modelCompleted'),'Preserve incomplete confirmation without retry'
 review=Path(m.read(status)['review']['path']);levels=review.parent/'levels.json'
 if not levels.exists():
  with (BASE/'levels.log').open('w',encoding='utf8')as log:
   child=subprocess.Popen(argv+['--levels'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=m.native.CREATE);worker.update(child=m.native.identity(child.pid));assert child.wait()==0
 m.save(BASE/'status.json',dict(status='word-confirmation-complete-content-review-pending',review=m.pin(review),levels=m.pin(levels),flags=m.read(levels)['flags'],modelInCoordinator=False));print(json.dumps(m.read(BASE/'status.json'),ensure_ascii=False),flush=True)
finally:
 if worker.handle is not None:worker.close(remove=child is None or child.poll()is not None)

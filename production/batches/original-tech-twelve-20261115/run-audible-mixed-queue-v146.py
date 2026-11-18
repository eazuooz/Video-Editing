"""Finite blind ASR of each newly completed audible mix; no repetition or retry."""
from pathlib import Path
import datetime,json,subprocess,time
H=Path(__file__).resolve().parent;ROOT=H.parents[2];PY=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
OUT=M/'camera-music-revision-v139/mixed-queue-v146'
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 OUT.mkdir(exist_ok=True);assert not(OUT/'launch.json').exists();save(OUT/'launch.json',dict(atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),finite=True,automaticRetry=False));records=[]
 for row in json.loads((H/'audible-bgm-baseline-bindings-v144.json').read_text('utf8'))['projects']:
  if row['order']==2:continue
  deadline=time.monotonic()+6*3600
  while not(M/row['slug']/'camera-music-v139/audio-mix-v144/audio-build.json').exists():
   completion=M/'camera-music-revision-v139/bgm-queue-v144/completion.json'
   if completion.exists():assert json.loads(completion.read_text('utf8'))['allElevenMixed'],'Prior mix stage ended incomplete'
   assert time.monotonic()<deadline;time.sleep(20)
  log=OUT/(row['slug']+'.log');assert not log.exists();print('Recognizing '+row['slug'],flush=True)
  with log.open('xb')as f:q=subprocess.run([str(PY),'-u','-X','utf8',str(H/'run-audible-mixed-asr-v146.py'),'--project',row['slug'],'--execute','--wait-minutes','15'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  records.append(dict(order=row['order'],slug=row['slug'],exitCode=q.returncode,log=str(log)));save(OUT/'progress.json',dict(projects=records))
  if q.returncode:break
 save(OUT/'completion.json',dict(projects=records,finiteQueueEnded=True,allElevenRecognized=len(records)==11 and all(x['exitCode']==0 for x in records),rootContentReviewRequired=True))
if __name__=='__main__':main()

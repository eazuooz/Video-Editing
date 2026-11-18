"""Finite eleven-file remux queue; each task reacquires the full guard."""
from pathlib import Path
import json,subprocess,time,datetime
H=Path(__file__).resolve().parent;ROOT=H.parents[2];PY=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');OUT=M/'camera-music-revision-v139/remux-queue-v155'
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 OUT.mkdir(exist_ok=True);assert not(OUT/'launch.json').exists();save(OUT/'launch.json',dict(atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),finite=True,automaticRetry=False));records=[]
 for row in json.loads((H/'batch.json').read_text('utf-8-sig'))['projects']:
  if row['order']==2:continue
  deadline=time.monotonic()+2*3600
  while not(M/row['slug']/'camera-music-v139/audio-mix-v144/mixed-content-review-v149.json').exists():
   assert time.monotonic()<deadline;time.sleep(20)
  log=OUT/(row['slug']+'.log');assert not log.exists();print('Remuxing '+row['slug'],flush=True)
  with log.open('xb')as f:q=subprocess.run([str(PY),'-u','-X','utf8',str(H/'run-audible-bgm-remux-v155.py'),'--project',row['slug'],'--execute','--wait-minutes','15'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  records.append(dict(order=row['order'],slug=row['slug'],exitCode=q.returncode,log=str(log)));save(OUT/'progress.json',dict(projects=records))
  if q.returncode:break
 save(OUT/'completion.json',dict(projects=records,allElevenComplete=len(records)==11 and all(x['exitCode']==0 for x in records),finiteQueueEnded=True))
if __name__=='__main__':main()

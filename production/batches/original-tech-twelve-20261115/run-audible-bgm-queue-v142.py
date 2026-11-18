"""Finite eleven unchanged-picture BGM remixes; Mario comparison follows separately."""
from pathlib import Path
import datetime,json,subprocess
H=Path(__file__).resolve().parent;ROOT=H.parents[2];PY=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
OUT=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/camera-music-revision-v139/bgm-queue-v142')
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 OUT.mkdir(exist_ok=True);assert not(OUT/'launch.json').exists();save(OUT/'launch.json',dict(atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),finite=True,automaticRetry=False));records=[]
 rows=json.loads((H/'audible-bgm-baseline-bindings-v142.json').read_text('utf8'))['projects']
 for row in rows:
  if row['order']==2:continue
  log=OUT/(row['slug']+'.log');assert not log.exists();print('Starting '+row['slug'],flush=True)
  with log.open('xb')as f:result=subprocess.run([str(PY),'-u','-X','utf8',str(H/'prepare-audible-bgm-remix-v142.py'),'--project',row['slug'],'--execute','--wait-minutes','15'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  records.append(dict(order=row['order'],slug=row['slug'],exitCode=result.returncode,log=str(log)));save(OUT/'progress.json',dict(projects=records))
  if result.returncode:break
 save(OUT/'completion.json',dict(projects=records,finiteQueueEnded=True,allElevenMixed=len(records)==11 and all(x['exitCode']==0 for x in records),independentAsrAndFinalOutputsStillRequired=True))
if __name__=='__main__':main()

"""Finite pilot and decoded QA only after root-recorded mixed-content review."""
from pathlib import Path
import datetime,json,subprocess,time
H=Path(__file__).resolve().parent;ROOT=H.parents[2];PY=ROOT/'qwen3-tts/.venv/Scripts/python.exe';M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');OUT=M/'clarity-revision-v83/pilot-queue-v113'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def run(slug,stage,script,args):
 log=OUT/(slug+'-'+stage+'.log');assert not log.exists();print(json.dumps(dict(project=slug,stage=stage,event='starting')),flush=True)
 with log.open('xb')as f:r=subprocess.run([str(PY),'-u','-X','utf8',str(H/script),'--project',slug,*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 return dict(stage=stage,exitCode=r.returncode,log=str(log))
def main():
 OUT.mkdir(parents=True,exist_ok=True);assert not(OUT/'launched.json').exists();save(OUT/'launched.json',dict(atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),finite=True,automaticRetry=False,automaticVisualApproval=False));records=[]
 for row in read(H/'selected-clarity-narration-preparation-v84.json')['projects']:
  slug=row['slug'];base=M/slug/'clarity-revision-v83';deadline=time.monotonic()+6*3600
  while not(base/'audio-mix-v95/mixed-content-review.json').exists():assert time.monotonic()<deadline;time.sleep(20)
  record=dict(slug=slug,stages=[])
  if slug=='shorts-journey-sand-sparkle':
   while not(base/'film-v95/pilot-proof.json').exists():assert time.monotonic()<deadline;time.sleep(15)
  elif not(base/'film-v95/pilot-proof.json').exists():
   result=run(slug,'pilot','run-clarity-film-v95.py',['--execute','--mode','pilot','--wait-minutes','180']);record['stages'].append(result)
   if result['exitCode']:records.append(record);save(OUT/'progress.json',dict(projects=records));continue
  if not(base/'film-v95/pilot-encoded-qa.json').exists():record['stages'].append(run(slug,'encoded-qa','verify-clarity-encoded-v95.py',['--mode','pilot']))
  records.append(record);save(OUT/'progress.json',dict(projects=records,rootVisualReviewRequired=True))
 save(OUT/'completion.json',dict(projects=records,finiteQueueEnded=True,rootVisualReviewRequired=True,finalFilmComplete=False))
if __name__=='__main__':main()

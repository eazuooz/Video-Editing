"""Prepare ready later lessons while explicit phrase repairs finish elsewhere."""
from pathlib import Path
import datetime,json,subprocess,time
H=Path(__file__).resolve().parent;ROOT=H.parents[2];PY=ROOT/'qwen3-tts/.venv/Scripts/python.exe';M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');OUT=M/'clarity-revision-v83/remaining-mix-queue-v117'
SLUGS=['shorts-doom-push-forward-healing','shorts-mariokart8-spin-boost','shorts-returnal-particle-tentacles','shorts-botw-chemistry-rules']
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def run(slug,stage,script,args):
 log=OUT/(slug+'-'+stage+'.log');assert not log.exists();print(json.dumps(dict(project=slug,stage=stage,event='starting')),flush=True)
 with log.open('xb')as f:r=subprocess.run([str(PY),'-u','-X','utf8',str(H/script),'--project',slug,*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 return dict(stage=stage,exitCode=r.returncode,log=str(log))
def main():
 OUT.mkdir(parents=True,exist_ok=True);assert not(OUT/'launched.json').exists();save(OUT/'launched.json',dict(atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),finite=True,automaticRetry=False,rootContentReviewRequired=True));records=[]
 for slug in SLUGS:
  deadline=time.monotonic()+4*3600;p=ROOT/'projects'/slug;record=dict(slug=slug,stages=[])
  while not(p/'production/accepted-voice-selection-v95.json').exists():assert time.monotonic()<deadline;time.sleep(20)
  if not(p/'production/film-inputs-v95.json').exists():
   r=run(slug,'film-plan','prepare-botw-clarity-film-v117.py'if'botw'in slug else'prepare-clarity-film-v95.py',[]);record['stages'].append(r)
   if r['exitCode']:records.append(record);save(OUT/'progress.json',dict(projects=records));continue
  for stage,script,args in [('mix','prepare-clarity-mix-v95.py',['--execute','--wait-minutes','180']),('mixed-asr','run-clarity-mixed-asr-v95.py',['--execute','--wait-minutes','15']),('mixed-inspection','review-clarity-mixed-audio-v95.py',[])]:
   assert not(M/slug/'clarity-revision-v83/audio-mix-v95/mixed-content-review.json').exists(),'Already reviewed; inspect orchestration before duplicate work'
   r=run(slug,stage,script,args);record['stages'].append(r)
   if r['exitCode']:record['hold']='Inspect exact stage; no automatic retry';break
  records.append(record);save(OUT/'progress.json',dict(projects=records,finalFilmComplete=False))
 save(OUT/'completion.json',dict(projects=records,finiteQueueEnded=True,rootContentReviewRequired=True))
if __name__=='__main__':main()

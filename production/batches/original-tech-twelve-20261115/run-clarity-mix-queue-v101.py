"""Finite source-bound mix preparation and blind mixed ASR, without auto approval."""
from pathlib import Path
import datetime,json,subprocess,time
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
OUT=M/'clarity-revision-v83/mix-queue-v101';PY=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def run(slug,stage,script,args):
 log=OUT/(slug+'-'+stage+'.log');assert not log.exists()
 print(json.dumps(dict(project=slug,stage=stage,event='starting')),flush=True)
 with log.open('xb')as f:r=subprocess.run([str(PY),'-u','-X','utf8',str(H/script),'--project',slug,*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 return dict(stage=stage,exitCode=r.returncode,log=str(log))
def main():
 OUT.mkdir(parents=True,exist_ok=True);assert not(OUT/'launched.json').exists()
 save(OUT/'launched.json',dict(atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),finite=True,automaticRetry=False,automaticContentApproval=False))
 records=[]
 for row in read(H/'selected-clarity-narration-preparation-v84.json')['projects']:
  slug=row['slug'];p=ROOT/'projects'/slug;record=dict(slug=slug,stages=[]);deadline=time.monotonic()+3*3600
  while not(p/'production/accepted-voice-selection-v95.json').exists():
   predecessor=M/'clarity-revision-v83/phrase-master-queue-v94/completion.json'
   assert not predecessor.exists(),'Master queue ended without this accepted voice; inspect exact result'
   assert time.monotonic()<deadline;time.sleep(20)
  if slug=='shorts-control-destruction-pipeline':
   while not(p/'production/film-inputs-v95.json').exists():
    assert time.monotonic()<deadline,'Awaiting separately observed Control source and bound film plan';time.sleep(20)
  elif not(p/'production/film-inputs-v95.json').exists():
   r=run(slug,'film-plan','prepare-clarity-film-v95.py',[]);record['stages'].append(r)
   if r['exitCode']:record['hold']='Film plan retained for review';records.append(record);save(OUT/'progress.json',dict(projects=records));continue
  for stage,script,args in [('mix','prepare-inside-clarity-mix-v95.py'if'inside'in slug else'prepare-clarity-mix-v95.py',['--execute','--wait-minutes','180']),('mixed-asr','run-clarity-mixed-asr-v95.py',['--execute','--wait-minutes','15']),('mixed-inspection','review-clarity-mixed-audio-v95.py',[])]:
   r=run(slug,stage,script,args);record['stages'].append(r)
   if r['exitCode']:record['hold']='Inspect exact stage; no automatic retry';break
  records.append(record);save(OUT/'progress.json',dict(projects=records,finalFilmComplete=False))
 save(OUT/'completion.json',dict(projects=records,finiteQueueEnded=True,contentApprovalPending=True,finalFilmComplete=False))
if __name__=='__main__':main()

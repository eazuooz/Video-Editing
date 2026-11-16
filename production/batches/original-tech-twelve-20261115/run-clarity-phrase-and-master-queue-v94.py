"""Finite continuation of this task: new phrases, then exact master QA.

Waits for the existing source queue to exit. Does not create a scheduler, retry
failed model jobs, approve listening, or advance into unreviewed film stages.
"""
from pathlib import Path
import datetime,json,subprocess,time
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
OUT=M/'clarity-revision-v83/phrase-master-queue-v94';PY=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
REPAIRS={'shorts-journey-sand-sparkle':'86','shorts-inside-temporal-antialiasing':'85','shorts-spiderman-swing-anchor':'85','shorts-returnal-particle-tentacles':'85','shorts-botw-chemistry-rules':'85'}
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def run(slug,stage,script,args):
 log=OUT/(slug+'-'+stage+'.log');assert not log.exists()
 print(json.dumps(dict(project=slug,stage=stage,event='starting',log=str(log))),flush=True)
 with log.open('xb')as f:r=subprocess.run([str(PY),'-u','-X','utf8',str(H/script),'--project',slug,*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 return dict(stage=stage,exitCode=r.returncode,log=str(log))
def main():
 OUT.mkdir(parents=True,exist_ok=True);assert not(OUT/'launched.json').exists()
 save(OUT/'launched.json',dict(atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),finite=True,newPhraseUnits=10,automaticRetry=False,filmOrUploadAuthorizedByThisQueue=False))
 predecessor=M/'clarity-revision-v83/source-queue-v84/completion.json';deadline=time.monotonic()+3*3600
 while not predecessor.exists():
  assert time.monotonic()<deadline,'Source queue still incomplete; no dependent work started';time.sleep(30)
 assert read(predecessor)['allSourceStagesExitedZero'],'Inspect the actual source failure; do not repeat it'
 repair_results=[]
 for slug,ver in REPAIRS.items():
  record=dict(slug=slug,stages=[])
  for stage,script,args in [('voice','run-selected-clarity-voice-v'+ver+'.py',['--execute','--wait-minutes','15']),('asr','run-selected-clarity-asr-v'+ver+'.py',['--execute','--wait-minutes','15']),('levels','run-selected-clarity-asr-v'+ver+'.py',['--levels'])]:
   r=run(slug,'phrase-'+stage,script,args);record['stages'].append(r)
   if r['exitCode']:break
  repair_results.append(record);save(OUT/'progress.json',dict(repairs=repair_results,masters=[],finalFilmComplete=False))
 masters=[]
 for row in read(H/'selected-clarity-narration-preparation-v84.json')['projects']:
  slug=row['slug'];ver=REPAIRS.get(slug,'84');record=dict(slug=slug,sourceVersion=ver,stages=[])
  if slug in REPAIRS and not all(s['exitCode']==0 for s in next(r for r in repair_results if r['slug']==slug)['stages']):record['hold']='Phrase execution failed; preserved';masters.append(record);continue
  master=M/slug/'voice-master-v95/voice-generation-complete-proof.json'
  if not master.exists():
   r=run(slug,'master-prepare','prepare-clarity-master-v95.py',['--source-version',ver]);record['stages'].append(r)
   if r['exitCode']:record['hold']='Raw unit trend or source validation hold';masters.append(record);continue
  for stage,script,args in [('asr','run-selected-clarity-master-asr-v95.py',['--execute','--wait-minutes','15']),('levels','run-selected-clarity-master-asr-v95.py',['--levels']),('review','review-clarity-master-v95.py',['--record'])]:
   r=run(slug,'master-'+stage,script,args);record['stages'].append(r)
   if r['exitCode']:record['hold']='Inspect exact '+stage+' hold; no automatic model retry';break
  masters.append(record);save(OUT/'progress.json',dict(repairs=repair_results,masters=masters,finalFilmComplete=False))
 save(OUT/'completion.json',dict(repairs=repair_results,masters=masters,finiteQueueEnded=True,masterTechnicalAccepted=sum((M/r['slug']/'voice-master-v95/technical-voice-review.json').exists()for r in masters),finalFilmComplete=False,humanApproval=False))
 print(json.dumps(dict(finiteQueueEnded=True,masterTechnicalAccepted=sum((M/r['slug']/'voice-master-v95/technical-voice-review.json').exists()for r in masters))),flush=True)
if __name__=='__main__':main()

"""Two explicit new phrase identities, then independent masters; no retries."""
from pathlib import Path
import datetime,json,subprocess
H=Path(__file__).resolve().parent;ROOT=H.parents[2];PY=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
OUT=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/clarity-revision-v83/final-phrase-queue-v111')
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def run(slug,stage,script,args):
 log=OUT/(slug+'-'+stage+'.log');assert not log.exists();print(json.dumps(dict(project=slug,stage=stage,event='starting')),flush=True)
 with log.open('xb')as f:r=subprocess.run([str(PY),'-u','-X','utf8',str(H/script),'--project',slug,*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 return dict(stage=stage,exitCode=r.returncode,log=str(log))
def main():
 OUT.mkdir(parents=True,exist_ok=True);assert not(OUT/'launched.json').exists();save(OUT/'launched.json',dict(atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),finite=True,automaticRetry=False,oldApprovedPcmPreserved=True));records=[]
 for slug,source,master in [('shorts-returnal-particle-tentacles','105','109'),('shorts-botw-chemistry-rules','106','110')]:
  row=dict(slug=slug,sourceVersion=source,masterVersion=master,stages=[])
  steps=[('voice','run-selected-clarity-voice-v'+source+'.py',['--execute','--wait-minutes','15']),('raw-asr','run-selected-clarity-asr-v'+source+'.py',['--execute','--wait-minutes','15']),('raw-levels','run-selected-clarity-asr-v'+source+'.py',['--levels']),('master','prepare-clarity-master-v'+master+'.py',['--source-version',source]),('master-asr','run-selected-clarity-master-asr-v'+master+'.py',['--execute','--wait-minutes','15']),('master-levels','run-selected-clarity-master-asr-v'+master+'.py',['--levels']),('master-review','review-clarity-master-v'+master+'.py',['--record'])]
  for stage,script,args in steps:
   r=run(slug,stage,script,args);row['stages'].append(r)
   if r['exitCode']:row['hold']='Inspect exact stage; no automatic repetition';break
  records.append(row);save(OUT/'progress.json',dict(projects=records,finalFilmComplete=False))
 save(OUT/'completion.json',dict(projects=records,finiteQueueEnded=True,finalFilmComplete=False,humanApproval=False))
if __name__=='__main__':main()

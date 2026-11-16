"""Finite source-voice/ASR jobs for the eight explicitly selected revisions."""
from pathlib import Path
import datetime,hashlib,json,subprocess,sys
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/clarity-revision-v83')
PY=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 out=M/'source-queue-v84';out.mkdir(parents=True,exist_ok=True)
 assert not(out/'launched.json').exists(),'One finite queue; inspect actual workers and evidence before continuation'
 selected=read(H/'selected-clarity-narration-preparation-v84.json')['projects']
 save(out/'launched.json',dict(atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),projects=[x['slug']for x in selected],finite=True,automaticRetry=False,platformActions=[]))
 results=[]
 for row in selected:
  slug=row['slug'];voice=M.parent/slug/'voice-repair-v84/voice-generation-complete-proof.json'
  commands=[('voice','run-selected-clarity-voice-v84.py',['--execute','--wait-minutes','15']),('asr','run-selected-clarity-asr-v84.py',['--execute','--wait-minutes','15']),('levels','run-selected-clarity-asr-v84.py',['--levels'])]
  record=dict(slug=slug,stages=[])
  for stage,script,extra in commands:
   if stage!='voice'and not voice.exists():record['hold']='Source voice not complete';break
   cmd=[str(PY),'-u','-X','utf8',str(H/script),'--project',slug,*extra]
   log=out/(slug+'-'+stage+'.log')
   print(json.dumps(dict(project=slug,stage=stage,event='starting',log=str(log))),flush=True)
   with log.open('xb')as f:r=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   record['stages'].append(dict(stage=stage,exitCode=r.returncode,log=str(log)))
   if r.returncode:record['hold']='Inspect preserved '+stage+' result';break
  results.append(record);save(out/'progress.json',dict(projects=results,finalFilmComplete=False,humanApproval=False))
  print(json.dumps(record),flush=True)
 save(out/'completion.json',dict(projects=results,finiteQueueEnded=True,allSourceStagesExitedZero=all(len(x['stages'])==3 and all(s['exitCode']==0 for s in x['stages'])for x in results),voiceAcceptancePending=True,finalFilmComplete=False,humanApproval=False))
if __name__=='__main__':main()

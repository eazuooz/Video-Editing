"""Seal a finite successor for the three unresolved voices; no new automation."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');RUN=MEDIA/'production-resume-20261115T055255Z'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def write(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def code(p,t):
 assert not p.exists(),p
 ast.parse(t);p.write_text(t,'utf8')
def main():
 t=(HERE/'run-finite-exact12-completion-v13.py').read_text('utf8');a=t.index('JOBS=');b=t.index('\ndef read(p):',a)
 jobs=[('shorts-control-destruction-pipeline',None,'run-additional-master-voice-repair-asr-v14.py','voice-master-v14','asr-master-v14')]+[(s,'run-clear-sentence-voice-repair-v15.py','run-clear-sentence-voice-repair-asr-v15.py','voice-repair-v15','asr-repair-v15')for s in ['shorts-doom-push-forward-healing','shorts-botw-chemistry-rules']]
 t=t[:a]+'JOBS='+repr(jobs)+'\n'+t[b:];t=t.replace('finite-exact12-completion-v13','finite-additional-completion-v16').replace('finite-completion-v13','finite-additional-completion-v16').replace('review-corrected-voice-captions-v13.py','review-corrected-voice-captions-v16.py').replace('bind-ready-film-inputs-v13.py','bind-ready-film-inputs-v15.py')
 path=HERE/'run-finite-additional-completion-v16.py';code(path,t)
 # Preserve the current source coordinator. Only its exact successor output
 # changes; no existing job, process or lease is stopped.
 t=(HERE/'run-source-phase-handoff-v13.py').read_text('utf8')
 t=t.replace('source-phase-handoff-v13','additional-phase-handoff-v16').replace('exact12-completion-readiness-v13.json','additional-completion-readiness-v16.json').replace('finite-lesson-completion-v9/worker.json','finite-exact12-completion-v13/worker.json').replace("new=MEDIA/'finite-exact12-completion-v13/worker.json'","new=MEDIA/'finite-additional-completion-v16/worker.json'").replace('run-finite-exact12-completion-v13.py','run-finite-additional-completion-v16.py')
 code(HERE/'run-additional-phase-handoff-v16.py',t)
 names=['run-finite-additional-completion-v16.py','run-additional-phase-handoff-v16.py','run-clear-sentence-voice-repair-v15.py','run-clear-sentence-voice-repair-asr-v15.py','run-additional-master-voice-repair-asr-v14.py','review-corrected-voice-captions-v16.py','bind-ready-film-inputs-v15.py','prepare-lesson-mix-v10.py','run-lesson-mixed-voice-repair-asr-v10.py','review-lesson-mixed-audio-v16.py','source-ordered-film-contracts-v15.json','clear-sentence-source-review-v15.json']
 write(RUN/'additional-completion-readiness-v16.json',dict(sourceInputs=[pin(HERE/n)for n in names],scope='Only Control master14 and one revised sentence each for DOOM/BOTW, after existing model owner exits normally. No repeats of completed source speech.',qualityThresholdsChanged=False,foreignProcessesChanged=False,newRecurringAutomation=False))
 print(json.dumps(dict(readiness=pin(RUN/'additional-completion-readiness-v16.json'),modelJobsStarted=False)))
if __name__=='__main__':main()

"""One finite foreground worker for this explicitly selected local revision."""
import sys,time,json,traceback
from subject_revision import *
import qa,progress
def main(ids):
 state=dict(scope=ids,pid=os.getpid(),status='running',encoded=[],failed=[]);save(HERE/'finite-worker.json',state)
 for eid in ids:
  if eid=='M21':continue
  e=EPISODES[eid];p=work(e)
  while not (p/'encoded.json').exists():
   try:
    state.update(current=eid,stage='encoding');save(HERE/'finite-worker.json',state);encode(e);break
   except Exception as error:
    reason=str(error)
    resource=any(x in reason for x in ('lease','batch job still running','Other media encode','Other model job','Game process still running','Other Unreal render','Shared lease'))
    if resource:
     state.update(stage='resource-wait',reason=reason);save(HERE/'finite-worker.json',state);time.sleep(2);continue
    state['failed'].append(dict(episode=eid,error=reason));save(HERE/'finite-worker.json',state);traceback.print_exc();break
  if (p/'encoded.json').exists():
   state.update(current=eid,stage='technical-and-picture-evidence');save(HERE/'finite-worker.json',state)
   try:
    if not (p/'technical-qa.json').exists():qa.technical(e)
    if not (p/'picture-evidence.json').exists():qa.pictures(e)
    state['encoded'].append(eid);print(eid,'encoded; technical checks passed; actual picture review pending',flush=True)
   except Exception as error:
    state['failed'].append(dict(episode=eid,stage='technical-and-picture-evidence',error=repr(error)));save(HERE/'finite-worker.json',state);traceback.print_exc()
  progress.update()
 state.update(status='encodes-ended-actual-picture-review-pending',stage='needs-internal-picture-review');save(HERE/'finite-worker.json',state)
if __name__=='__main__':main(sys.argv[1:] or [eid for eid in EPISODES if eid!='M21'])

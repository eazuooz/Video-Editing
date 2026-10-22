"""Finite partial recovery of verified original FHD slots, never a delivery pass."""
import os,sys
from datetime import datetime,timezone
from polish_common import *

selection={
 'M10':['10','LG04','13','16','LG06','LG07','21'],
 'M11':['02','05'],
 'M12':['11','17','19','21'],
 'M17':['05','08','14'],
}
job=B/'available-fhd-job.json'
def state(stage,**kw):
 save(job,{'pid':os.getpid(),'stage':stage,'updatedAt':datetime.now(timezone.utc).isoformat(),
  'selected':selection,'fullMasterReady':False,'newTts':False,'platformMutation':False,**kw})
try:
 for ident,scenes in selection.items():
  e=Episode(ident);e.authorized();state('restoring-selected-original-FHD',episode=ident)
  e.run([sys.executable,B/'restore-gameplay.py',ident,'--scenes',','.join(scenes)],'partial-original-fhd-restore.log')
  result=read(B/'gameplay-restoration-status.json')[ident]
  assert result['status']=='partial-gameplay-restored',result
  state('sampling-selected-original-FHD',episode=ident)
  e.run([sys.executable,B/'review-restored-sources.py',ident,'actual',*scenes],'partial-original-fhd-sample.log')
  print(ident,len(scenes),'original FHD slots restored; direct source/guide review pending',flush=True)
 state('finished-await-direct-source-inspection')
except Exception as exc:
 state('failed',error=str(exc)[-2000:]);raise

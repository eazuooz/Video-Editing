"""Finite encode/technical QA only after observed preflight; never approves pixels."""
import sys,datetime
from polish_common import *
ident=sys.argv[1];assert ident in ['M07','M08'];e=Episode(ident);e.authorized()
out=R/'shared/output/private-game-math-polish-20261022'
lock=out/f'fhd-polish-{ident}.lock';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
status=B/f'fhd-polish-{ident}-job.json'
def record(stage,**extra):
 save(status,{'pid':os.getpid(),'episode':ident,'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':stage,'newTts':False,'platformMutation':False,'visualApprovalGranted':False,**extra})
try:
 review=read(e.H/'moving-observed-guide-preflight.json');assert review['status']=='passed-selected-moving-preflight'
 assert review['compositionSha256']==sha(e.H/'composition-polish.json')
 assert read(e.H/'observed-guide-preflight.json')['assSha256']==sha(e.O/'composition-polish.ass')
 for script in ['assemble.py','technical-qa.py','review-final-pixels.py']:
  e.authorized();record('running',script=script)
  e.run([sys.executable,B/script,ident],'fhd-polish-'+script+'.log')
 e.run([sys.executable,B/'progress.py'],'fhd-polish-progress.log')
 record('technical-complete-await-direct-final-visual-review')
except Exception as error:
 record('failed',error=str(error)[-3000:]);raise
finally:
 if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()

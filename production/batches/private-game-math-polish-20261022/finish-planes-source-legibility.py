"""One finite explanation-only geometry job, guarded by its episode lock."""
import datetime
import sys
from polish_common import *

e=Episode(sys.argv[1]);assert e.id in ['M11','M12'];e.authorized()
lock=e.O/'source-legibility-worker.lock'
with lock.open('x',encoding='utf8') as f:f.write(str(os.getpid()))
path=B/f'source-legibility-{e.id}-job.json'
status={'pid':os.getpid(),'episode':e.id,'stage':'starting','newTts':False,
        'platformMutation':False,'fullMaster':False,'visualApprovalGranted':False,'statusFile':rel(path)}
try:
    for name in ['render-planes-legibility.py','review-planes-legibility.py']:
        e.authorized();status.update(stage=name,updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat());save(path,status)
        e.run([sys.executable,B/name,e.id],'source-legibility-worker-'+name+'.log')
        print(e.id,name,'completed',flush=True)
    status.update(stage='explanation-only-encoded-samples-await-direct-review',updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
except Exception as error:
    status.update(stage='failed',error=str(error)[-2500:],updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat());raise
finally:
    save(path,status)
    if lock.read_text(encoding='utf8')==str(os.getpid()):lock.unlink()

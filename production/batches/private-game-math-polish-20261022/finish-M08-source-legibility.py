"""Finite source-only M08 job; no gameplay, assembly, voice or platform work."""
import datetime
import sys
from polish_common import *

e = Episode('M08')
e.authorized()
lock = e.O/'source-legibility-worker.lock'
with lock.open('x', encoding='utf8') as f:
    f.write(str(os.getpid()))
status = {'pid':os.getpid(), 'episode':'M08', 'stage':'starting', 'newTts':False,
          'platformMutation':False, 'fullMaster':False, 'visualApprovalGranted':False,
          'statusFile':rel(B/'source-legibility-M08-job.json')}
try:
    for name in ['render-conversions-legibility.py','review-conversions-legibility.py']:
        e.authorized()
        status.update(stage=name, updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
        save(B/'source-legibility-M08-job.json',status)
        e.run([sys.executable,B/name],'source-legibility-worker-'+name+'.log')
        print('M08',name,'completed',flush=True)
    status.update(stage='explanation-only-encoded-samples-await-direct-review',
                  updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
except Exception as error:
    status.update(stage='failed', error=str(error)[-2500:],
                  updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
    raise
finally:
    save(B/'source-legibility-M08-job.json',status)
    if lock.read_text(encoding='utf8') == str(os.getpid()):
        lock.unlink()

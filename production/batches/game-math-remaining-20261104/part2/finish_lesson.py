"""One reserved lecture can finish while the main worker records a different lecture."""
import argparse
from datetime import datetime,timezone
import msvcrt
import os
import subprocess
import sys
import time
import psutil
from edition import BATCH,ROOT,read
from queue_state import PROJECTS,STATE,select
from status import store,refresh

def finish(ep):
    lane=STATE/'lanes';lane.mkdir(exist_ok=True)
    lockfile=lane/(ep+'.lock');receipt=lane/(ep+'.json')
    with lockfile.open('a+b') as lock:
        if not lock.tell():lock.write(b'1');lock.flush()
        lock.seek(0)
        try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        except OSError:return
        record=dict(episode=ep,pid=os.getpid(),createTime=psutil.Process().create_time(),active=True,at=datetime.now(timezone.utc).isoformat())
        store(receipt,record);previous=None
        try:
            while True:
                auth=read(ROOT/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
                assert auth['productionAllowedNow'] and PROJECTS[ep]['slug'] in auth['projectSlugs'] and not auth['upload']
                row=next(r for r in read(BATCH/'batch.json')['items'] if r['id']==ep)
                description,job=select(row)
                if description!=previous:
                    record.update(status=description,checkedAt=datetime.now(timezone.utc).isoformat());store(receipt,record)
                    refresh();print(ep,description,flush=True);previous=description
                if description.startswith(('4파일 생성','사용자 일괄')):return
                if not job:time.sleep(12);continue
                error=STATE/(ep+'-'+job['step']+'-error.json')
                if error.is_file():time.sleep(15);continue
                logfile=lane/(ep+'-'+job['step']+'.log')
                with logfile.open('a',encoding='utf8') as log:
                    rc=subprocess.run([job['exe'],*job['args']],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
                                      creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)).returncode
                if rc:store(error,dict(episode=ep,stage=job['step'],exitCode=rc,log=str(logfile)))
        finally:
            record.update(active=False,finishedAt=datetime.now(timezone.utc).isoformat());store(receipt,record)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('episode',choices=PROJECTS)
    finish(parser.parse_args().episode)

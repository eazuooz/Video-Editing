"""Finish the recorded picture corrections after the finite running job."""
import argparse
from datetime import datetime,timezone
import os
from pathlib import Path
import shutil
import subprocess
import sys

from inventory import ROOT,HERE,read,save,sha
from render_revision import guard,authorized,CREATE


def main(eid,archive_only=False):
    worker=read(HERE/'finite-worker.json')
    assert worker['status']=='finite-job-ended-review-pending'
    assert not guard().idle_reason(), 'Preserve active jobs'
    assert eid in ('M21','M22','M23','M24','M26')
    episode=next(e for e in read(HERE/'inventory.json')['episodes'] if e['id']==eid)
    authorized(episode)
    source=(ROOT/'projects'/episode['slug']/'production/local/teaching-sync-v2').resolve()
    output=(ROOT/'output'/(episode['slug']+'-teaching-sync-v2')).resolve()
    root=(Path(os.environ['LOCALAPPDATA'])/'YamyamCoding/VideoEditingScratch/teaching-sync-superseded').resolve()
    archive=(root/(eid+'-word-accurate-before-review-fix')).resolve()
    assert source.is_relative_to(ROOT.resolve()) and output.is_relative_to(ROOT.resolve())
    assert archive.is_relative_to(root) and archive!=root
    if not archive.exists():
        encoded=read(source/'encoded.json')
        for f in encoded['files'].values():assert sha(Path(f['path']))==f['sha256']
        archive.mkdir(parents=True)
        save(archive/'archive-receipt.json',dict(at=datetime.now(timezone.utc).isoformat(),encoded=encoded,
            oldProduction=str(source),oldOutput=str(output),archive=str(archive),baselineTouched=False,
            reason=read(HERE/'pending-encoded-corrections.json')['episodes'][eid]))
        shutil.move(str(source),str(archive/'production'));shutil.move(str(output),str(archive/'output'))
        records=read(HERE/'superseded-attempts.json')
        records[eid]=dict(episode=eid,archivedProduction=str(archive/'production'),archivedOutput=str(archive/'output'),
            previousAttempt=records.get(eid),encoded=encoded)
        save(HERE/'superseded-attempts.json',records)
    if archive_only:
        print(eid,'unapproved attempt preserved; internal sample stage can run',flush=True);return
    if not (source/'encoded.json').exists():
        subprocess.run([sys.executable,'-X','utf8',str(HERE/'render_revision.py'),eid,'--render'],cwd=ROOT,check=True,creationflags=CREATE)
    subprocess.run([sys.executable,'-X','utf8',str(HERE/'verify.py'),eid,'--pictures'],cwd=ROOT,check=True,creationflags=CREATE)
    subprocess.run([str(ROOT/'qwen3-tts/.venv/Scripts/python.exe'),'-X','utf8',str(HERE/'newmix.py'),eid],cwd=ROOT,check=True,creationflags=CREATE)
    d=read(HERE/'pending-encoded-corrections.json')
    d['episodes'][eid].update(status='resolved',actualEncodedPictureReview='pending',archive=str(archive),
        newCaptionedSha256=read(source/'encoded.json')['files']['captioned']['sha256'])
    save(HERE/'pending-encoded-corrections.json',d)
    worker=read(HERE/'finite-worker.json')
    resolved=[r for r in worker['failures'] if r['episode']==eid]
    worker['failures']=[r for r in worker['failures'] if r['episode']!=eid]
    worker.setdefault('resolvedFailures',[]).extend([dict(**r,resolution=str(source/'technical-qa.json')) for r in resolved])
    if eid not in worker['completed']:worker['completed'].append(eid)
    save(HERE/'finite-worker.json',worker)
    print(eid,'final correction encoded; final picture inspection remains separate',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('episodes',nargs='+');parser.add_argument('--archive-only',action='store_true')
    args=parser.parse_args()
    for eid in args.episodes:main(eid,args.archive_only)

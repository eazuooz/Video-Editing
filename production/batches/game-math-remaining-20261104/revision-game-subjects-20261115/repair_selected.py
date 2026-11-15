"""Finish two inspected corrections after the current finite worker releases work.

No process is interrupted. Existing renders and evidence remain archived locally.
"""
import time, traceback
import psutil
from subject_revision import *
import qa, progress


def resource_wait(error):
    return any(x in str(error) for x in ('lease','batch job still running','Other media encode','Other model job','Game process still running','Other Unreal render','Shared lease'))


def archive(e):
    p=work(e);enc=read(p/'encoded.json');folder=Path(enc['files']['clean']['path']).parent
    assert folder.resolve().is_relative_to(DEST.resolve())
    name='previous-encode-'+enc['files']['captioned']['sha256'][:10]
    target=folder/name;target.mkdir(exist_ok=True)
    assert target.resolve().is_relative_to(DEST.resolve())
    for f in enc['files'].values():
        source=Path(f['path']);destination=target/source.name
        assert source.resolve().parent==folder.resolve() and source.is_file()
        assert destination.resolve().is_relative_to(DEST.resolve()) and not destination.exists()
        shutil.move(source,destination)
    evidence=p/name;evidence.mkdir(exist_ok=True)
    assert evidence.resolve().is_relative_to((ROOT/'projects'/e['slug']).resolve())
    for filename in ('encoded.json','technical-qa.json','picture-evidence.json','qa.json','worker.json','subject-plan.json','resource-choice.json'):
        source=p/filename
        if source.exists():
            destination=evidence/filename
            assert not destination.exists() and destination.resolve().is_relative_to(p.resolve())
            shutil.move(source,destination)
    save(p/'preserved-previous-encode.json',dict(files=str(target),evidence=str(evidence),reason='Corrected actual encoded picture issues; no baseline or platform deletion.'))


def main():
    own=dict(pid=os.getpid(),status='waiting-for-current-finite-worker',scope=['M22','M24'])
    save(HERE/'repair-worker.json',own)
    finite=read(HERE/'finite-worker.json')
    while psutil.pid_exists(finite['pid']):time.sleep(20)
    for eid in own['scope']:
        e=EPISODES[eid];p=work(e);pending=read(HERE/'pending-corrections.json')
        if pending['episodes'][eid]['status']=='resolved':continue
        own.update(status='correcting',current=eid);save(HERE/'repair-worker.json',own)
        archive(e)
        while True:
            try:encode(e);break
            except RuntimeError as error:
                if not resource_wait(error):raise
                own.update(status='resource-wait',reason=str(error));save(HERE/'repair-worker.json',own);time.sleep(20)
        qa.technical(e);qa.pictures(e)
        pending=read(HERE/'pending-corrections.json');pending['episodes'][eid]['status']='encoded-picture-review-pending';save(HERE/'pending-corrections.json',pending)
        progress.update();print(eid,'correction encoded; actual final picture inspection pending',flush=True)
    own.update(status='encoded-needs-actual-picture-review');save(HERE/'repair-worker.json',own)


if __name__=='__main__':
    try:main()
    except BaseException as error:
        save(HERE/'repair-failure.json',dict(error=repr(error)));traceback.print_exc();raise

"""One explicitly selected thirteen-episode job, not an automation or new queue."""
import argparse
from datetime import datetime,timezone
import os
from pathlib import Path
import subprocess
import sys
import traceback

from inventory import HERE,ROOT,read,save
import render_revision as render
import verify
import progress


def now(): return datetime.now(timezone.utc).isoformat()


def main(ids,resume=False):
    assert len(ids)==len(set(ids)) and set(ids)<=set(f'M{i}' for i in range(21,34))
    records={e['id']:e for e in read(HERE/'inventory.json')['episodes']}
    state=dict(pid=os.getpid(),startedAt=now(),scope=ids,status='running',completed=[],failures=[],automation=False)
    path=HERE/'finite-worker.json'
    if resume:
        before=read(path);assert before['status']!='running', 'Preserve the running finite worker'
        assert not render.guard().idle_reason(), 'Preserve other active costly jobs'
        archive=HERE/('finite-worker-before-resume-'+now().replace(':','').replace('.','')+'.json')
        save(archive,before)
        state.update(completed=before.get('completed',[]),failures=[r for r in before.get('failures',[]) if r['episode'] not in ids],
            previousFailedForRetry=[r for r in before.get('failures',[]) if r['episode'] in ids],
            resolvedFailures=before.get('resolvedFailures',[]),previousRun=str(archive))
    save(path,state)
    for eid in ids:
        episode=records[eid];render.authorized(episode)
        try:render.validate_inputs()
        except AssertionError as error:
            state.update(status='preparation-changed-before-next-job',current=eid,stage='internal-preflight',detail=repr(error),updatedAt=now())
            save(path,state);print('Preserved current media; next job awaits corrected internal preflight',flush=True);return
        folder=ROOT/'projects'/episode['slug']/'production/local'/render.REVISION
        state.update(current=eid,stage='encode',updatedAt=now());save(path,state)
        try:
            if not (folder/'encoded.json').exists():
                # A partial existing movie is evidence of an interrupted job,
                # not permission to overwrite or start a duplicate encoder.
                subprocess.run([sys.executable,'-X','utf8',str(HERE/'render_revision.py'),eid,'--render'],
                    cwd=ROOT,check=True,creationflags=render.CREATE)
            progress.update()
            state.update(stage='technical-and-picture-QA',updatedAt=now());save(path,state)
            subprocess.run([sys.executable,'-X','utf8',str(HERE/'verify.py'),eid,'--pictures'],
                cwd=ROOT,check=True,creationflags=render.CREATE)
            progress.update()
            state.update(stage='audio-evidence',updatedAt=now());save(path,state)
            if read(folder/'encoded.json')['addedGameAudioIntervals']:
                log=folder/'mix-recognition.log'
                with log.open('a',encoding='utf8') as output:
                    subprocess.run([str(ROOT/'qwen3-tts/.venv/Scripts/python.exe'),'-X','utf8',str(HERE/'newmix.py'),eid],
                        cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,check=True,creationflags=render.CREATE)
            else:
                import newmix
                newmix.run(episode)
            state['completed'].append(eid)
            prior=[r for r in state.get('previousFailedForRetry',[]) if r['episode']==eid]
            state.setdefault('resolvedFailures',[]).extend([dict(**r,resolution=str(folder/'technical-qa.json')) for r in prior])
            state['previousFailedForRetry']=[r for r in state.get('previousFailedForRetry',[]) if r['episode']!=eid]
            print(eid,'encoded and technical checks complete; actual picture/mix review remains separate',flush=True)
        except BaseException as error:
            state['failures'].append(dict(episode=eid,error=repr(error),trace=traceback.format_exc()))
            print(eid,'FAILED',repr(error),flush=True)
            log=folder/(episode['slug']+'.clean.log')
            tail=log.read_text(encoding='utf8',errors='replace')[-6000:] if log.exists() else ''
            if any(message in tail for message in ('Padded dimensions cannot','Error reinitializing filters!')):
                state.update(stopReason='Shared picture filter requires internal correction before the next episode',updatedAt=now())
                save(path,state)
                break
            # Respect ownership and stopped authorization instead of repeatedly
            # probing or competing with an unrelated costly application.
            if render.guard().idle_reason():
                state.update(status='resource-boundary-stopped',updatedAt=now());save(path,state);return
        progress.update();state.update(updatedAt=now());save(path,state)
    state.update(status='finite-job-ended-review-pending',current=None,updatedAt=now());save(path,state)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('episodes',nargs='+');parser.add_argument('--resume',action='store_true')
    a=parser.parse_args();main(a.episodes,a.resume)

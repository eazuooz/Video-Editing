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


def main(ids):
    assert len(ids)==len(set(ids)) and set(ids)<=set(f'M{i}' for i in range(21,34))
    records={e['id']:e for e in read(HERE/'inventory.json')['episodes']}
    state=dict(pid=os.getpid(),startedAt=now(),scope=ids,status='running',completed=[],failures=[],automation=False)
    path=HERE/'finite-worker.json';save(path,state)
    for eid in ids:
        episode=records[eid];render.authorized(episode)
        folder=ROOT/'projects'/episode['slug']/'production/local'/render.REVISION
        state.update(current=eid,stage='encode',updatedAt=now());save(path,state)
        try:
            if not (folder/'encoded.json').exists():
                # A partial existing movie is evidence of an interrupted job,
                # not permission to overwrite or start a duplicate encoder.
                render.encode(episode)
            progress.update()
            state.update(stage='technical-and-picture-QA',updatedAt=now());save(path,state)
            verify.run(episode,True)
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
            print(eid,'encoded and technical checks complete; actual picture/mix review remains separate',flush=True)
        except BaseException as error:
            state['failures'].append(dict(episode=eid,error=repr(error),trace=traceback.format_exc()))
            print(eid,'FAILED',repr(error),flush=True)
            # Respect ownership and stopped authorization instead of repeatedly
            # probing or competing with an unrelated costly application.
            if render.guard().idle_reason():
                state.update(status='resource-boundary-stopped',updatedAt=now());save(path,state);return
        progress.update();state.update(updatedAt=now());save(path,state)
    state.update(status='finite-job-ended-review-pending',current=None,updatedAt=now());save(path,state)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('episodes',nargs='+');main(parser.parse_args().episodes)

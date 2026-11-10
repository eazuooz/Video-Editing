"""Finish verified local review files as speech and picture inputs become ready."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from plan_observations import BATCH, HERE, OUTPUT, PRIORITY, ROOT, WORK, load, save
from finish_review import RATE, voice_window


MEDIA = Path('C:/Users/1/Videos/YamyamProduction/animation-review-notes-20261110')


def invoke(executable, script, ep, log):
    with log.open('wb') as stream:
        subprocess.run([executable, '-X', 'utf8', '-u', str(HERE / script), ep], cwd=ROOT,
                       stdout=stream, stderr=subprocess.STDOUT, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--episodes', nargs='+')
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    plan_path = HERE / 'observation-plan.json'
    plan = load(plan_path)['episodes']
    scope = load(ROOT / 'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    ids = args.episodes or sorted(plan, key=lambda ep: (ep not in PRIORITY, ep))
    assert set(ids) <= set(plan) == set(scope['episodes']) and scope['renderAuthorized']
    path = WORK / 'delivery-queue.json'
    state = load(path) if path.exists() else {'done': {}, 'failed': {}}
    deadline = time.monotonic() + 5 * 3600
    while time.monotonic() < deadline:
        plan = load(plan_path)['episodes']
        waiting = {}
        for ep in ids:
            if (WORK / 'pause-after-episode.json').exists():
                return
            paths = [WORK / 'readback' / f'{q["id"]}.json' for q in plan[ep]]
            if not all(path.exists() for path in paths):
                waiting[ep] = 'observation audio readback'
                continue
            reads = [load(path) for path in paths]
            if any(row['ko'] != receipt['expected'] for row, receipt in zip(plan[ep], reads)):
                waiting[ep] = 'current wording needs readback'
                continue
            def does_not_fit(row, receipt):
                count = round(receipt['durationSeconds'] * RATE)
                a, b = voice_window(row, count)
                return count > b - a
            if any(does_not_fit(row, receipt) for row, receipt in zip(plan[ep], reads)):
                waiting[ep] = 'one or more lines need a shorter take'
                continue
            local = MEDIA / ep
            visual = local / 'new-pictures/manifest.json'
            capture = local / 'capture-receipt.json'
            if ep in ('A08', 'A11') and not capture.exists():
                waiting[ep] = 'Unreal capture'
                continue
            warrior = MEDIA / 'A08-motion/capture-receipt.json'
            if ep == 'A08' and not warrior.exists():
                waiting[ep] = 'Warrior I lean and return capture'
                continue
            input_paths = paths + [HERE / 'finish_review.py']
            if ep in PRIORITY:
                input_paths += [HERE / 'paint_replacements.py']
            if capture.exists():
                input_paths += [capture]
            if ep == 'A08':
                input_paths += [warrior]
            if visual.exists():
                input_paths += [visual]
            plan_bytes = json.dumps(plan[ep], sort_keys=True).encode()
            signature = hashlib.sha256(plan_bytes + b''.join(p.read_bytes() for p in input_paths)).hexdigest()
            proof = OUTPUT / ep / 'delivery.json'
            if state['done'].get(ep) == signature and proof.exists():
                continue
            if state['failed'].get(ep, {}).get('signature') == signature:
                waiting[ep] = state['failed'][ep]['log']
                continue
            state.update(active=ep, waiting=waiting)
            save(path, state)
            log = WORK / f'{ep}-final-output.log'
            try:
                if ep in PRIORITY and not visual.exists():
                    python = shutil.which('python')
                    assert python, 'The existing Python 3.12 plate renderer is required'
                    invoke(python, 'paint_replacements.py', ep, WORK / f'{ep}-picture-replacements.log')
                invoke(sys.executable, 'finish_review.py', ep, log)
                if visual.exists() and visual not in input_paths:
                    input_paths.append(visual)
                state['done'][ep] = hashlib.sha256(plan_bytes + b''.join(p.read_bytes() for p in input_paths)).hexdigest()
                state['failed'].pop(ep, None)
                print(ep, 'ready for sampled output review', flush=True)
            except subprocess.CalledProcessError:
                state['failed'][ep] = {'signature': signature, 'log': str(log)}
                waiting[ep] = str(log)
                print(ep, 'failed', log, flush=True)
            state['active'] = None
            save(path, state)
        state.update(active=None, waiting=waiting)
        save(path, state)
        if args.once or all(ep in state['done'] and ep not in waiting for ep in ids):
            return
        time.sleep(18)


if __name__ == '__main__':
    main()

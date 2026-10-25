"""Resume only the ten explicitly selected Shorts, one expensive job at a time.

This is a finite foreground production runner, not a recurring automation.
It preserves failed attempts and produces local review files only.
"""
from pathlib import Path
import argparse
import datetime
import importlib.util
import json
import os
import subprocess
import sys
import uuid

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parents[2]
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/distinctive-ten-shorts-20261025')
PYTHON = ROOT / 'qwen3-tts/.venv/Scripts/python.exe'

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def read(path):
    return json.loads(path.read_text(encoding='utf8'))

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    temporary.replace(path)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-order', type=int, default=1)
    parser.add_argument('--through-order', type=int, default=10)
    parser.add_argument('--retry-failed', action='store_true', help='Use only after inspecting and resolving the saved failure')
    args = parser.parse_args()
    rows = read(BATCH / 'batch.json')['projects']
    chosen = [r for r in rows if args.from_order <= r['order'] <= args.through_order]
    if not chosen:
        raise SystemExit('No explicitly selected projects in this range')
    sys.path.insert(0, str(BATCH))
    spec = importlib.util.spec_from_file_location('sequential_finalizer', BATCH / 'finish-ready-videos.py')
    finalizer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finalizer)
    finalizer.authorization()
    run_id = datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6]
    status_path = MEDIA / 'batch-local/sequential-status.json'
    status = dict(runId=run_id, startedAt=now(), finiteBatch=True,
                  userEvidence='게임 껐어~ GPU 사용해서 노이타부터 쇼츠 10편 제작 마저 진행해줘',
                  youtubeActions=False, driveActions=False, humanReview='pending', projects=[])
    environment = dict(os.environ, YAMYAM_ASR_DEVICE='cuda')
    for row in chosen:
        slug = row['slug']
        finalizer.authorization(slug)
        current = dict(slug=slug, order=row['order'], title=row['title'], status='starting', startedAt=now())
        status['projects'].append(current)
        write(status_path, status)
        for stage, command in (
            ('voice', [str(PYTHON), '-X', 'utf8', str(BATCH / 'generate-ready-voices.py'), '--slug', slug, '--wait-minutes', '180']),
            ('finalizer', [str(PYTHON), '-X', 'utf8', str(BATCH / 'finish-ready-videos.py'), '--execute', '--slug', slug, '--wait-minutes', '180'] + (['--retry-failed'] if args.retry_failed else [])),
        ):
            finalizer.authorization(slug)
            log = MEDIA / 'batch-local' / (run_id + '-' + slug + '-' + stage + '.log')
            current.update(status='running', stage=stage, log=str(log), updatedAt=now())
            write(status_path, status)
            print('START', slug, stage, flush=True)
            with log.open('x', encoding='utf8') as stream:
                result = subprocess.run(command, cwd=ROOT, env=environment, stdout=stream,
                                        stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
            current.update(exitCode=result.returncode, updatedAt=now())
            if result.returncode:
                current.update(status='needs-repair', reason='See retained stage log')
                break
            if stage == 'voice':
                voice = ROOT / 'projects' / slug / 'production/local/audio-v1/voice/narration.wav'
                if not voice.exists():
                    current.update(status='waiting-resource-or-prerequisite', reason='No complete PCM yet; preserved bounded wait')
                    break
            else:
                state = read(ROOT / 'projects' / slug / 'production/local/finite-finalizer-v1/state.json')
                current.update(status=state['status'], delivery=state.get('delivery'),
                               internalVisualReview='pending', internalListening='pending', humanReview='pending')
            write(status_path, status)
            print('END', slug, stage, result.returncode, flush=True)
        current['endedAt'] = now()
        write(status_path, status)
    status.update(endedAt=now(), status='finite-pass-finished',
                  completedFiles=sum(bool(r.get('delivery')) for r in status['projects']))
    write(status_path, status)
    print(json.dumps({'status':status['status'], 'generated':status['completedFiles'], 'projects':len(chosen)}, ensure_ascii=False), flush=True)
    return 0 if status['completedFiles'] == len(chosen) else 2

if __name__ == '__main__':
    raise SystemExit(main())

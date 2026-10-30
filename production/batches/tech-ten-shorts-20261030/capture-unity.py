"""Capture only current final-PCM Unity sections in the isolated owned project."""
from pathlib import Path
from contextlib import nullcontext
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import uuid

from batch_job_lock import SerialJobLock, inspect_lock
from scoped_context import BATCH, ROOT, MEDIA, make_context, read, sha, now


def own_lock(slug):
    existing = inspect_lock()
    if existing:
        import psutil
        ancestor_pids = {p.pid for p in psutil.Process().parents()}
        if (existing.get('ownerLive') is True and existing.get('pid') in ancestor_pids
                and existing.get('slug') == slug and existing.get('stage') == 'native-capture'):
            return nullcontext()
    return SerialJobLock(slug, 'native-capture')


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('slug'); args = parser.parse_args()
    ctx = make_context(args.slug); ctx['guard'](); ctx['assert_no_game_apps']()
    project = ctx['P']; timing_path = project / 'production/visual-timing.json'; timing = read(timing_path)
    voice_hash = sha(ctx['VOICE'])
    if timing != read(ctx['LOCAL'] / 'visual-timing.json') or timing['timingInputs']['voiceSha256'] != voice_hash:
        raise RuntimeError('Native capture requires exact same final-PCM timing.')
    sections = [s for s in timing['sections'] if s['kind'] == 'unity']
    if not sections: raise RuntimeError('No actual Unity sections selected.')
    capture = MEDIA / 'unity-capture'; output = ctx['LOCAL'].resolve() / 'unity-capture'
    receipt_path = output / 'native-receipt.json'; source = BATCH / 'unity-source'
    source_files = sorted(p for p in source.rglob('*') if p.is_file())
    source_hashes = {p.relative_to(source).as_posix(): sha(p) for p in source_files}
    source_digest = hashlib.sha256(json.dumps(source_hashes, sort_keys=True).encode()).hexdigest()
    provenance_path = output / 'input-receipt.json'
    provenance = {'voiceSha256': voice_hash, 'timingSha256': sha(timing_path),
                  'sourceCode': source_hashes, 'sourceTreeSha256': source_digest}
    if receipt_path.exists():
        old = read(receipt_path)
        if old.get('success') is not True or old.get('voiceSha256') != voice_hash or read(provenance_path) != provenance:
            raise RuntimeError('Existing native capture differs; preserve and version before retry.')
        for entry in old['artifacts']:
            if sha(entry['path']) != entry['sha256']: raise RuntimeError('Previous captured frame or scene changed.')
        print('Reused exact successful native capture.'); return
    if output.exists() and any(output.iterdir()): raise RuntimeError('Incomplete native output is preserved; inspect/version it before retry.')
    with own_lock(args.slug):
        ctx['assert_gpu_available']()
        if not (capture / 'ProjectSettings/ProjectVersion.txt').is_file():
            raise RuntimeError('The owned isolated Unity capture project has not been prepared.')
        snapshot = MEDIA / 'native-source-snapshots' / source_digest
        for relative, expected in source_hashes.items():
            original = source / relative; archived = snapshot / relative
            if sha(original) != expected: raise RuntimeError('Unity source changed during preflight; preserve current attempt.')
            archived.parent.mkdir(parents=True, exist_ok=True)
            if archived.exists():
                if sha(archived) != expected: raise RuntimeError('Archived native source snapshot changed.')
            else:
                with original.open('rb') as reader, archived.open('xb') as writer: shutil.copyfileobj(reader, writer)
                if sha(archived) != expected: raise RuntimeError('Native source changed while snapshotting.')
        destination = capture / 'Assets/VideoScenes/tech-ten-shorts-20261030'
        shutil.copytree(snapshot, destination, dirs_exist_ok=True)
        if any(sha(destination / relative) != expected for relative, expected in source_hashes.items()):
            raise RuntimeError('Isolated Unity source differs from the exact preserved snapshot.')
        output.mkdir(parents=True, exist_ok=True)
        provenance_path.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
        jobs = MEDIA / 'capture-jobs'; jobs.mkdir(exist_ok=True)
        token = uuid.uuid4().hex[:10]; job_path = jobs / (args.slug + '-actual-' + token + '.json')
        log_path = job_path.with_suffix('.log')
        job = {'topic': args.slug.removeprefix('shorts-'), 'mode': 'full', 'output': output.as_posix(),
               'timeline': timing_path.as_posix(), 'voiceSha256': voice_hash,
               'sceneVersion': 'source-' + source_digest[:12], 'stages': sorted({s['unityStage'] for s in sections})}
        job_path.write_text(json.dumps(job, indent=2) + '\n', encoding='utf8')
        exe = read(BATCH / 'gpu-authorization.json')['allowedExistingEditor']['executable']
        args_list = [exe, '-batchmode', '-projectPath', str(capture), '-executeMethod', 'Yamyam.TechTen.Editor.TechTenCapture.Run',
                     '-techTenJob', str(job_path), '-logFile', str(log_path)]
        print(json.dumps({'stage': 'native-capture', 'slug': args.slug, 'job': str(job_path), 'log': str(log_path)}, ensure_ascii=False), flush=True)
        lease = ROOT / 'shared/output/GPU_HANDOFF.json'
        import psutil
        lease_token = uuid.uuid4().hex
        lease_record = {'project': args.slug, 'revision': 'tech-ten-v1', 'state': 'native-unity-capture',
                        'token': lease_token, 'coordinator': {'pid': os.getpid(), 'createTime': psutil.Process().create_time()},
                        'startedAt': now(), 'voiceSha256': voice_hash, 'job': str(job_path), 'foreignProcessesPaused': []}
        with lease.open('x', encoding='utf8') as stream: json.dump(lease_record, stream, ensure_ascii=False)
        try:
            process = subprocess.run(args_list, cwd=capture, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        finally:
            if lease.exists() and read(lease).get('token') == lease_token:
                lease.unlink()  # Only this exact process-owned lease, never another job.
        if process.returncode or not receipt_path.exists():
            raise RuntimeError('Native capture failed; prior output and log preserved: ' + str(log_path))
        receipt = read(receipt_path)
        if receipt.get('success') is not True or receipt.get('voiceSha256') != voice_hash: raise RuntimeError('Native receipt lacks current exact PCM hash.')
        expected = sum(s['endFrame'] - s['startFrame'] for s in sections)
        frames = [entry for entry in receipt['artifacts'] if entry['path'].lower().endswith('.jpg')]
        if len(frames) != expected: raise RuntimeError('Native capture did not produce all exact current section frames.')
        for entry in receipt['artifacts']:
            if sha(entry['path']) != entry['sha256']: raise RuntimeError('Native result changed before acceptance.')
        print(json.dumps({'success': True, 'frames': len(frames), 'receipt': str(receipt_path)}, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()

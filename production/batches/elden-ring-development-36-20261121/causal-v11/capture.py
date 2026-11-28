"""Finite v11 native-Unity capture, with exact source identity and shared lease."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from make_approved_voice_v2 import read, save, sha, resource_guard
import make_library_unity_revision_v4 as library
from make_unity_revision_v3 import EDITOR

WORK = Path('D:/YamyamProduction/elden-ring-development-36-causal-v11')
READY = (2, 7, 8, 11, 12)

def inputs():
    plan = read(HERE / 'plan.json')
    assert plan['authorized'] and len(plan['scope']) == 36
    library.use_main_project()
    sources = {p.relative_to(library.PROJECT).as_posix(): sha(p)
               for p in library.SCENE_ROOT.rglob('*') if p.suffix in ('.cs', '.shader')}
    return dict(sources=sources, assetPlanSha256=sha(library.ASSET_PLAN),
                planSha256=sha(HERE / 'plan.json'), launcherSha256=sha(Path(__file__)))

def run(execute, selected):
    assert selected and all(i in READY for i in selected)
    cuts = [dict(id=f'{i:02}-{shot}', episode=i, shot=shot, frames=600,
                 speechStartFrame=5, speechEndFrame=590, pilotFrames=[90, 330, 550])
            for i in selected for shot in (1, 3)]
    identity = dict(inputs=inputs(), cuts=cuts, pilot=True, stage='design-pilot-before-voice-timing')
    fp = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    dest = WORK / fp[:12]
    guard = resource_guard()
    guard.OWNER = 'elden-ring-causal-v11'
    guard.PROTOCOL = 'elden-ring-causal-v11-native-capture'
    reason = guard.busy_reason()
    print(json.dumps(dict(fingerprint=fp, cuts=len(cuts), guard=reason, output=str(dest)), ensure_ascii=False), flush=True)
    if not execute or reason:
        return
    if (dest / 'pilot-complete.json').exists():
        proof = read(dest / 'pilot-complete.json')
        assert proof['fingerprint'] == fp
        for row in proof['captures']:
            assert sha(Path(row['receipt'])) == row['sha256']
        print('Exact completed pilot preserved; no rerun.', flush=True)
        return
    dest.mkdir(parents=True, exist_ok=True)
    save(dest / 'inputs.json', identity)
    worker = guard.SingleWorker(path=WORK / 'worker.json')
    worker.acquire()
    token = uuid.uuid4().hex
    lease = False
    child = None
    try:
        if reason := guard.busy_reason():
            raise RuntimeError(reason)
        guard.LEASE.parent.mkdir(parents=True, exist_ok=True)
        record = dict(protocol=guard.PROTOCOL, owner=guard.OWNER, token=token,
                      **guard.identity(), phase='reserved', child=None, fingerprint=fp, output=str(dest))
        with guard.LEASE.open('x', encoding='utf-8') as handle:
            json.dump(record, handle)
        lease = True
        worker.update(leaseToken=token)
        job = dict(output=str(dest / 'pilot'), ffmpeg=shutil.which('ffmpeg'), fingerprint=fp,
                   project=str(library.PROJECT), pilot=True, cuts=cuts,
                   assets=list(library.selected_assets().values()))
        save(dest / 'job.json', job)
        if reason := guard.busy_reason(own_token=token):
            raise RuntimeError(reason)
        record.update(phase='launching')
        save(guard.LEASE, record)
        log = dest / 'unity.log'
        cmd = [str(EDITOR), '-batchmode', '-force-d3d11', '-job-worker-count', '2',
               '-projectPath', str(library.PROJECT), '-executeMethod',
               'Yamyam.EldenRingLibraryLessons.CausalCaptureV11.Run', '-eldenFingerprint', fp,
               '-eldenOutput', str(dest), '-logFile', str(log)]
        child = subprocess.Popen(cmd, creationflags=guard.CREATE | getattr(subprocess, 'BELOW_NORMAL_PRIORITY_CLASS', 0),
                                 env={**os.environ, 'YAMYAM_ELDEN_CAUSAL_V11_JOB': str(dest / 'job.json')})
        record.update(phase='running', child=guard.identity(child.pid))
        worker.update(child=record['child'])
        save(guard.LEASE, record)
        save(dest / 'launch.json', dict(fingerprint=fp, child=record['child'], log=str(log)))
        if child.wait():
            raise RuntimeError(f'Unity design pilot failed; inspect {log}')
        rows=[]
        for cut in cuts:
            receipt=dest/'pilot'/cut['id']/'capture.json'
            r=read(receipt)
            assert r['fingerprint']==fp and r['pilot'] and r['frames']==cut['frames']
            assert r['scene'].startswith('Assets/VideoScenes/EldenRingDevelopment36/AssetLibraryV4/ScenesCausalV11/')
            images=sorted(receipt.parent.glob('frame-*.png'))
            assert len(images)==3
            rows.append(dict(id=cut['id'],receipt=str(receipt),sha256=sha(receipt),
                             images=[dict(path=str(p),sha256=sha(p)) for p in images]))
        save(dest/'pilot-complete.json', dict(fingerprint=fp,captures=rows,stage='design-pilot',
                                             finalTimedCapture=False,visualReview='pending'))
        print(f'Native pilot captured: {dest}',flush=True)
    finally:
        if child is None or child.poll() is not None:
            worker.update(child=None)
            if lease and guard.LEASE.exists():
                current=read(guard.LEASE)
                if guard.ours(current) and current['token']==token:
                    guard.LEASE.unlink()
        worker.close()

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--execute',action='store_true')
    p.add_argument('--episodes',nargs='+',type=int,default=list(READY))
    a=p.parse_args()
    run(a.execute,a.episodes)

"""Observe actual research GPU return after this complete TTS batch.

Read-only toward research and pause controls. This records completed synthesis
separately from content/listening, scene rendering and private-video delivery.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import time

import psutil

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/research/game-lighting-history'
TOKEN = '967d4ad1-fe14-4940-a548-67133be275de'
VERIFIED = BASE / 'remaining-tts-completion-verification-v1.json'
OUT = BASE / 'research-return-after-remaining-tts-v1.json'
QUEUE = Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008')


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, obj):
    t = p.with_name(p.name + '.tmp-' + str(os.getpid()))
    t.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for attempt in range(12):
        try:
            os.replace(t, p)
            return
        except PermissionError:
            if attempt == 11:
                raise
            time.sleep(.25)


def identity(p):
    return dict(pid=p.pid, createTime=p.create_time(), command=p.cmdline(), cwd=p.cwd(), exe=p.exe())


def main():
    if OUT.exists():
        raise RuntimeError('Preserve the actual return observation; do not repeat a completed watcher.')
    own = identity(psutil.Process())
    write(BASE / 'research-return-observer-execution-v1.json',
          dict(status='waiting-for-complete-batch-verification', startedAt=now(), actualIdentity=own,
               handoffToken=TOKEN, cudaAllocated=False, modifiesResearch=False))
    deadline = time.monotonic() + 43200
    while not VERIFIED.exists():
        if time.monotonic() > deadline:
            raise TimeoutError('Verification wait exceeded12hours; no completed TTS or resume claim.')
        producer = read(BASE / 'remaining-tts-execution-v1.json')
        if producer.get('status') in ('child-failed', 'input-preparation-timeout'):
            write(OUT, dict(observedAt=now(), status='TTS-failed-inspect-preserved-log',
                            producer=producer, allRequestedTtsProduced=False,
                            researchGpuProgressVerified=False, researchModifiedByObserver=False))
            return
        time.sleep(10)
    verification = read(VERIFIED)
    if verification.get('handoffToken') != TOKEN or not verification.get('allRequestedTtsProduced'):
        raise RuntimeError('Exact whole-batch verification required.')
    history_path = ROOT / 'shared/output/gpu-handoff' / (TOKEN + '.json')
    history = read(history_path)
    resumed = history.get('resumedQueue')
    record = dict(schemaVersion=1, observedAt=now(), handoffToken=TOKEN,
                  allRequestedTtsProduced=True, verifiedTtsEvidence=VERIFIED.relative_to(ROOT).as_posix(),
                  verifiedTtsEvidenceSha256=sha(VERIFIED),
                  researchGpuProgressVerified=False, researchModifiedByObserver=False,
                  pauseControlsModifiedByObserver=False, observer=own,
                  researchResumeMeaning='Continue original queue with saved completed markers; no mid-run optimizer/RNG resume from adapter-only weights.')
    deadline = time.monotonic() + 1800
    observations = []
    while True:
        status = read(QUEUE / 'status.json')
        snapshot = dict(observedAt=now(), status=status)
        try:
            owner = psutil.Process(status['owner_pid'])
            if not resumed or owner.pid != resumed['pid'] or abs(owner.create_time() - resumed['createTime']) >= .01:
                raise RuntimeError('Research owner differs from the actually resumed queue; preserve and inspect.')
            snapshot['queueIdentity'] = identity(owner)
            if status.get('status') == 'running' and status.get('child_pid'):
                child = psutil.Process(status['child_pid'])
                if owner.pid not in [p.pid for p in child.parents()]:
                    raise RuntimeError('Research child is not owned by the resumed queue.')
                snapshot['childIdentity'] = identity(child)
                listed = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid,process_name',
                                                  '--format=csv,noheader,nounits'], text=True,
                                                  creationflags=subprocess.CREATE_NO_WINDOW)
                gpu_pids = {int(line.split(',', 1)[0].strip()) for line in listed.splitlines()
                            if line.split(',', 1)[0].strip().isdigit()}
                children = {child.pid, *[p.pid for p in child.children(recursive=True)]}
                snapshot['researchGpuPidsObserved'] = sorted(children & gpu_pids)
                snapshot['gpu'] = subprocess.check_output(['nvidia-smi',
                    '--query-gpu=memory.used,memory.free,utilization.gpu', '--format=csv,noheader,nounits'],
                    text=True, creationflags=subprocess.CREATE_NO_WINDOW).strip()
                log = Path(status['log'])
                text = log.read_text(encoding='utf-8', errors='replace') if log.exists() else ''
                snapshot['log'] = str(log)
                snapshot['logBytes'] = log.stat().st_size if log.exists() else 0
                snapshot['actualLogTail'] = text[-5000:]
                previous = next((x for x in reversed(observations)
                                 if x.get('status', {}).get('job') == status.get('job')
                                 and x.get('childIdentity', {}).get('createTime') == child.create_time()), None)
                progressed = bool(previous and snapshot['logBytes'] > previous.get('logBytes', 0))
                snapshot['freshOwnedJobLogProgressObserved'] = progressed
                if snapshot['researchGpuPidsObserved'] and progressed:
                    record.update(status='all-requested-TTS-produced-research-GPU-running',
                                  researchGpuProgressVerified=True, actualResearch=snapshot)
                    observations.append(snapshot)
                    break
        except psutil.NoSuchProcess:
            snapshot['transition'] = 'Job changed while observed; inspect next actual status.'
        except KeyError:
            # stopped/waiting/complete status omits owner or child identity.
            pass
        observations.append(snapshot)
        if status.get('status') in ('failed', 'stopped', 'complete_pending_visual_review') or time.monotonic() > deadline:
            record.update(status='TTS-produced-research-return-awaiting-or-unavailable', actualResearch=snapshot)
            break
        time.sleep(10)
    record['observations'] = observations
    record['observedAt'] = now()
    record['currentNarrationApproved'] = False
    record['humanWholeListeningApproved'] = False
    record['finalMixedAsrApproved'] = False
    record['finalVideoProduced'] = False
    write(OUT, record)

    # The synthesis inputs stay frozen until ALL three children have exited and
    # the separate verifier has finished using those inputs.
    voice = read(BASE / 'remaining-voice-asr-execution-v1.json')
    for episode in verification['episodes']:
        slug = episode['slug']
        path = ROOT / 'projects' / slug / 'project.json'
        manifest = read(path)
        manifest['status'] = 'narration-produced-current-voice-review-pending'
        manifest['productionGates']['narrationProduced'] = True
        manifest['series'].update(measuredNarrationSeconds=episode['durationSeconds'], narrationTimingMeasured=True)
        entries = read(ROOT / episode['files']['.timing.json']['path'])['entries']
        overview = [e for e in entries if e['scene_id'] == entries[0]['scene_id']]
        manifest['editing']['openingOverview']['narrationSeconds'] = overview[-1]['end'] - overview[0]['start']
        manifest['productionState'].update(updatedAt=now(), ownedGpuJobs=0,
            ownedCpuAsrJobs=int(voice.get('status') in ('recognizing', 'loading-CPU-model')
                               and voice.get('currentEpisode') == slug),
            currentVoiceApproved=False, humanListeningApproved=False,
            narrationCompletionEvidence=VERIFIED.relative_to(ROOT).as_posix())
        write(path, manifest)
    plan = read(BASE / 'series-plan.json')
    for episode in plan['episodes']:
        current = next((e for e in verification['episodes'] if e['slug'] == episode['slug']), None)
        if current:
            episode.update(status='narration-produced-current-voice-review-pending', narrationProduced=True,
                           measuredNarrationSeconds=current['durationSeconds'], narrationTimingMeasured=True,
                           currentVoiceApproved=False, voiceCompletionEvidence=VERIFIED.relative_to(ROOT).as_posix())
        elif episode['slug'] == 'game-lighting-history-01':
            completion = read(ROOT / 'projects/game-lighting-history-01/production/tts-repair-completion-v4.json')
            episode.update(measuredNarrationSeconds=completion['audio']['durationSeconds'],
                           status='current-v4-voice-produced-direct-structural-review-listening-pending',
                           voiceRepairEvidence='projects/game-lighting-history-01/production/tts-repair-completion-v4.json',
                           narrationProduced=True, currentVoiceApproved=False)
    plan.update(updatedAt=now(), ownedGpuJobsRunning=0, allRequestedNarrationProduced=True,
                researchReturnEvidence=OUT.relative_to(ROOT).as_posix(), productionComplete=False)
    write(BASE / 'series-plan.json', plan)
    checkpoint = read(BASE / 'checkpoint.json')
    checkpoint['ownedJobHistory'].append(dict(recordedAt=now(), note='All remaining TTS children exited; original research returned separately from CPU ASR/listening/final video gates.',
                                              jobs=checkpoint.get('ownedJobsRunning', [])))
    checkpoint.update(stage=record['status'], updatedAt=now(), remainingTtsCompletion=VERIFIED.relative_to(ROOT).as_posix(),
                      researchReturnEvidence=OUT.relative_to(ROOT).as_posix(), researchGpuProgressVerified=record['researchGpuProgressVerified'],
                      next='Continue CPU-only current-audio direct review and caption/2.5D preparation. Keep research GPU priority; final mixing, rendered pixels and private deliveries are pending.')
    checkpoint['ownedJobsRunning'] = []
    identity_asr = voice.get('actualIdentity')
    if identity_asr:
        try:
            p = psutil.Process(identity_asr['pid'])
            if abs(p.create_time() - identity_asr['createTime']) < .01:
                checkpoint['ownedJobsRunning'].append(dict(kind='remaining-voice-CPU-recognizer',
                    **identity_asr, state=voice['status'], completedWindows=voice['completed'], expectedWindows=90,
                    cpuThreads=2, gpuJobs=0, sessionId=26892))
        except psutil.NoSuchProcess:
            pass
    write(BASE / 'checkpoint.json', checkpoint)
    write(BASE / 'research-return-observer-execution-v1.json',
          dict(status=record['status'], endedAt=now(), exitCode=0, actualIdentity=own,
               evidence=OUT.relative_to(ROOT).as_posix(), cudaAllocated=False, modifiesResearch=False))
    print(json.dumps(dict(status=record['status'], allRequestedTtsProduced=True,
                          researchGpuProgressVerified=record['researchGpuProgressVerified']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()

"""Record live waiting identity and prepared assets without final approval."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess, time
import psutil

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, x):
    tmp = p.with_name(p.name + f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(tmp, p)

ap = argparse.ArgumentParser(); ap.add_argument('--revision', type=int, default=2)
args = ap.parse_args(); assert args.revision >= 2
stamp = datetime.now(timezone.utc).isoformat()
session = read(BASE / 'narration-tts-session-v1.json')
worker = psutil.Process(session['pid'])
assert abs(worker.create_time() - session['createTime']) < .01
assert 'presenting-game-scores/production/render-voice-v1.py' in ' '.join(worker.cmdline())
assert worker.cwd().lower() == str(ROOT).lower()
request = read(BASE / 'narration-tts-request-v1.json')
for x in request['protectedInputs']:
    assert sha(ROOT / x['path']) == x['sha256'], x['path']
tts_path = BASE / 'narration-tts-execution-v1.json'
tts = read(tts_path) if tts_path.exists() else None
assert tts is None, 'TTS has started; preserve its newer actual execution and review that state instead.'
lease_path = ROOT / 'shared/output/GPU_HANDOFF.json'
lease = read(lease_path) if lease_path.exists() else None
proc_ids = [worker.pid, worker.ppid(), 63080, 27140]
if lease:
    proc_ids.append(lease['coordinator']['pid'])
    if lease.get('ttsOwner'):
        proc_ids.append(lease['ttsOwner']['pid'])
pid_string = ','.join(map(str, set(proc_ids + [50412])))
cim_cmd = f'Get-CimInstance Win32_Process | Where-Object {{ $_.ProcessId -in @({pid_string}) }} | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3 -Compress'
cim = subprocess.run(['pwsh', '-NoProfile', '-Command', cim_cmd], capture_output=True, text=True, encoding='utf-8', check=True)
gpu = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.free,utilization.gpu', '--format=csv,noheader,nounits'], capture_output=True, text=True, encoding='utf-8', check=True)
sources = ['black-structural-direct-review-v3.json', 'prepared-thumbnail-direct-review-v2.json', 'prepared-current-asr-v1.json', 'verify-own-voice-research-resume-v1.py', '../publishing/publishing-text-preparation-v1.json']
proof = dict(schemaVersion=2, slug='presenting-game-scores', observedAt=stamp,
    workerIdentity=dict(pid=worker.pid, createTime=worker.create_time(), commandLine=worker.cmdline(), cwd=worker.cwd(), sessionId=session['sessionId'], alive=True),
    actualCim=json.loads(cim.stdout), gpuMemoryUsedFreeMiBAndUtilizationCsv=gpu.stdout.strip(),
    currentLease=dict(project=lease.get('project'), token=lease.get('token'), state=lease.get('state'), coordinator=lease.get('coordinator'), ttsOwner=lease.get('ttsOwner')) if lease else None,
    ownModelLoaded=bool(tts), ownTtsStateCreated=bool(tts), protectedInputHashesMatched=len(request['protectedInputs']),
    preparedEvidence=[dict(path=(BASE / p).resolve().relative_to(ROOT).as_posix(), sha256=sha(BASE / p)) for p in sources],
    prototypeScope=dict(scenes=10, paragraphs=30, allReviewedPixels=78, selectedPrototypeSamples=72, directlyReadBoards=13, structuralPixelReviewApproved=True, measuredNarrationTimed=False),
    thumbnailPrepared=True, publishingTextPrepared=True, measuredChapterTimesPrepared=False,
    researchResumeVerifierPrepared=True, researchResumeVerifierExecuted=False, cpuAsrPrepared=True, cpuAsrExecuted=False,
    actualVoiceReviewApproved=False, finalTimingApproved=False, finalMixedAsrApproved=False, allFinalPixels=False,
    qaComplete=False, collected=False, actualVideoId=None, uploaded=False, privateSettingsVerified=False,
    ownResearchPauseOrProcessChanges=0, foreignLeaseOrPauseRemoval=0, imagesGitAdded=0, mediaGitAdded=0,
    nextAction='Inspect exact waiting worker/session and lease. After actual own TTS exit, verify owned lease closure and original research resume; then single CPU whole current-hash ASR, complete independent contexts and measured source allocation. Preserve completed structural/source work; no repeated synthesis or render.')
proof_name = f'prepared-handoff-resource-verification-v{args.revision}.json'
save(BASE / proof_name, proof)
c = read(BASE / 'latest-checkpoint.json')
c.update(recordedAt=stamp, latestResourceVerification='projects/presenting-game-scores/production/' + proof_name,
    thumbnailPreparation='projects/presenting-game-scores/production/prepared-thumbnail-direct-review-v2.json',
    publishingTextPreparation='projects/presenting-game-scores/publishing/publishing-text-preparation-v1.json', nextAction=proof['nextAction'])
save(BASE / 'latest-checkpoint.json', c)
queue_path = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(10):
    raw = queue_path.read_text('utf-8-sig'); q = json.loads(raw)
    item = next(x for x in q['items'] if x['slug'] == 'presenting-game-scores')
    item.update(latestResourceVerification=c['latestResourceVerification'], thumbnailPreparation=c['thumbnailPreparation'],
        publishingTextPreparation=c['publishingTextPreparation'], nextAction=proof['nextAction'])
    q['updatedAt'] = stamp
    if queue_path.read_text('utf-8-sig') == raw:
        save(queue_path, q); break
    time.sleep(.15)
else:
    raise RuntimeError('Concurrent queue writer; preserve separate proof and inspect actual queue')
print(json.dumps({k:proof[k] for k in ['observedAt', 'workerIdentity', 'ownTtsStateCreated', 'protectedInputHashesMatched', 'actualVoiceReviewApproved', 'uploaded', 'imagesGitAdded']}, ensure_ascii=False))

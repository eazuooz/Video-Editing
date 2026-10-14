"""Seal read paragraph results and snapshot the one live CPU worker."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess
import psutil

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
R = ROOT / 'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
now = lambda: datetime.now(timezone.utc).isoformat()

def save(p, data):
    tmp = p.with_name(p.name + '.writing')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(tmp, p)

out = R / 'resource-and-annotation-handoff-v24.json'
partial = O / 'current34-mixed-context-partial-direct-review-v1.json'
assert not out.exists() and not partial.exists()
s = read(O / 'current34-mixed-contexts-asr-execution-v1.json')
assert s['pid'] == 58900 and s['sessionId'] == 29301 and s['exitCode'] is None
p = psutil.Process(s['pid'])
assert p.is_running() and abs(p.create_time() - s['createTime']) < .01
assert p.cmdline() == s['commandLine'] and p.cwd() == s['cwd']
whole = read(O / 'current34-mixed-whole-asr-execution-v1.json')
assert whole['workerDead'] and whole['actualOuterExitCode'] == 0
whole_review = read(O / 'current34-mixed-whole-direct-review-v1.json')
assert whole_review['all34WholeTextsDirectlyCompared']
proof = read(O / 'narration-07b-guide-repair-execution-v1.json')
protected = proof['protectedInputs'] + proof['results']
for x in protected:
    assert sha(ROOT / x['path']) == x['sha256']
assert len(proof['protectedInputs']) == 79 and len(proof['results']) == 1
motion = read(R / 'current17-main-promotion-v1.json')
for x in motion['otherProtectedInputs']:
    assert sha(ROOT / x['path']) == x['sha256']
rows = []
for i, row in enumerate(s['results'][:45], 1):
    rp = O / 'current34-mixed-contexts-asr-v1' / (row['id'] + '.json')
    actual = read(rp)
    assert actual == row
    rows.append(dict(index=i, id=row['id'], expectedKo=row['expectedKo'],
                     currentText=row['text'], resultPath=rel(rp), resultSha256=sha(rp),
                     fullExpectedAndCurrentDirectlyRead=True,
                     firstThreeAndLastThreeWordsDirectlyRead=True,
                     readEvidence='6d2606' if i <= 22 else 'a13d92'))
assert len(rows) == 45 and rows[-1]['id'] == '06-p04'
notes = {
    '01-p03': '세/새 recognition alternative; pronunciation is pending.',
    '01b-p01': '배치에/배치의 particle alternative is unresolved.',
    '03-p05': '각변위 recovered in independent current AAC context after whole 각변인 alternative.',
    '04-p04': '좌표는/좌편은 recognition alternative; full clause and ending present.',
    '06a-p02': '어떤 자로 읽느냐/어떤 자료를 읽느냐 recognition alternative; not an audio repair approval.',
    '06a-p03': '방의 기준에서 recovered after whole 방에 기준해서 alternative.',
    '06-p04': '책은/최근 alternative persists; source convention remainder and complete ending present.'
}
save(partial, dict(recordedAt=now(), reviewedCount=45, total=180, rows=rows,
    recognitionNotes=notes,
    timingLimit='Leading word timestamps include preceding observation silence in baseline scenes. Use exact PCM placement/source cues, not recognizer zero, for final caption onset.',
    all180Reviewed=False, currentMixedAudioApproved=False,
    humanListeningApproved=False, humanPronunciationApproved=False,
    sourceAacSha256=s['mixAacSha256'], decodedAacSha256=s['decodedAacSha256']))
research = Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json')
rs = read(research)
assert rs['status'] == 'complete_pending_visual_review' and rs['completed'] == rs['total'] == 1088
assert not psutil.pid_exists(75876) or abs(psutil.Process(75876).create_time() - 1791735347.4583836) > .01
cim = subprocess.check_output(['powershell', '-NoProfile', '-Command',
    "Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','ffmpeg.exe','node.exe') } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],
    text=True, encoding='utf-8', errors='replace')
overview = read(O / 'current34-overview-render-execution-v3.json')
assert overview['actualOuterExitCode'] == 0 and overview['workerDead']
data = dict(recordedAt=now(), previousHandoff=rel(R / 'resource-and-annotation-handoff-v23.json'),
    orientation79ProtectedShaMatched=True, motionOther70ProtectedShaMatched=True,
    whole34Closed=dict(session=88118, completion='d32a4b', exitCode=0, workerDead=True,
        review=rel(O / 'current34-mixed-whole-direct-review-v1.json'), all34DirectlyCompared=True),
    currentContextWorker=dict(pid=p.pid, createTime=p.create_time(), commandLine=p.cmdline(), cwd=p.cwd(),
        sessionId=29301, initialChunk='807ae3', status=s['status'], completed=s['completed'], total=180,
        currentlyAlive=True, cpuThreads=2, gpuJobs=0,
        state=rel(O / 'current34-mixed-contexts-asr-execution-v1.json')),
    independentPlan=rel(O / 'current34-mixed-independent-context-plan-v1.json'),
    partialReview=rel(partial), partialReviewedCount=45,
    overviewV3=dict(session=35944, completion='3126e0', actualExitCode=0, workerDead=True,
        all110EncodedSamples20BoardsDirectlyRead=True,
        review=rel(O / 'current34-overview-sampled-held-review-v3.json'),
        held='Lower explanation note must clear fixed two-line captions.',
        preparedV4='production/batches/cross-game-example-coverage-review/render-orientation-overview-v4.py',
        preparedV4Executed=False),
    motion=dict(newId='lXjDBqONLWs', productionSettingsGitScheduleVerified=True,
        oldId='mBDd9VzSTkA', oldDeleted=False, actionTimeConfirmationPending=True, repeatQuestion=False),
    research=dict(status=rs['status'], completed=1088, total=1088, statusSha256=sha(research),
        originalPid75876Alive=False, restarted=False, visualReviewApproved=False),
    currentResource=dict(cpuLoadPercent=psutil.cpu_percent(interval=2),
        freePhysicalMemoryKiB=psutil.virtual_memory().available // 1024,
        gpuObservation=subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free,utilization.gpu',
            '--format=csv,noheader,nounits'], text=True).strip(), cimActual=cim),
    newTts=0, newMedia=0, researchManipulations=0, newImageGit=0,
    next='Reuse one live independent180 session29301/exact58900 command/create; actual outer exit then record closure. Preserve partial45 and compare only newly completed full paragraphs/edges. After closure and fresh resource render prepared overviewV4 once; review all new samples and normal playback. Prepare/render honest native-bounded baseline guides serially; no inferred world axes, arm axes or internal drift. Final current captions/chapters/end/pair/pixels/4files/private settings/selective Git/actual schedule remain pending. Continue through normal-transform-UV then pause; no Sakurai6/new lecture.')
save(out, data)
qp = B / 'queue.json'
before = qp.read_bytes(); q = read(qp)
q['latestHandoff'] = rel(out); q['updatedAt'] = now()
assert qp.read_bytes() == before
save(qp, q)
print(json.dumps(dict(handoff=rel(out), partial45=rel(partial), actualContextAlive=True,
    completed=s['completed'], total=180, protected79=True, whole34Closed=True, overviewV4PreparedOnly=True)))

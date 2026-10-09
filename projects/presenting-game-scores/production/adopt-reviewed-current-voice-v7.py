"""Adopt exact reviewed PCM for planning; keep final mix/pixels/private gates closed."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, copy, hashlib, json, os, psutil, subprocess, wave

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
PROJECT = BASE.parent
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
def save(p, data):
    t = p.with_name(p.name + '.recording')
    t.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(t, p)
def pcm(p):
    with wave.open(str(p), 'rb') as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, 24000)
        n = w.getnframes()
        return n, w.readframes(n)
def evidence(filename):
    p = BASE / filename
    d = read(p)
    assert d['allWholeTextsDirectlyCompared']
    for row in d['rows']:
        result = ROOT / row['path']
        assert result.exists()
        if 'sha256' in row:
            assert sha(result) == row['sha256']
    return dict(path=rel(p), sha256=sha(p))

ap = argparse.ArgumentParser()
ap.add_argument('--outer-exit-code', type=int, required=True)
ap.add_argument('--session-id', type=int, required=True)
args = ap.parse_args()
assert args.outer_exit_code == 0 and args.session_id == 80712
assert not (BASE / 'current-voice-selection-v7.json').exists(), 'Preserve adopted selection.'
node = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
dup = subprocess.run([node, 'scripts/review-video-duplicates.cjs', 'presenting-game-scores', '--check'],
                     cwd=ROOT, capture_output=True, text=True, encoding='utf-8', check=True)
request = read(BASE / 'named-guide-tts-request-v6.json')
for item in request['protectedInputs']:
    assert sha(ROOT / item['path']) == item['sha256'], item['path']
sp = BASE / 'named-guide-contexts-asr-execution-v6.json'
state = read(sp)
assert state['completed'] == state['total'] == 2 and state['exitCode'] == 0
try:
    assert abs(psutil.Process(state['pid']).create_time() - state['createTime']) >= .01
except psutil.NoSuchProcess:
    pass
stamp = datetime.now(timezone.utc).isoformat()
data = read(BASE / 'named-guide-contexts-asr-v6/asr.json')
assert data['complete'] and len(data['results']) == 2
notes = [
    'Entire new guide represented, including 먼저 and both complete sentences. Spacing/punctuation only. ASR ending8.44s extends0.24s into padded tail; not extra audible speech or a claimed precise phonetic endpoint.',
    'Entire original first paragraph and new guide represented. 먼저 is present after the exact PCM boundary. Ending12.94s extends0.425s into padded tail. Context-dependent timestamps are preserved; full current PCM and words were compared.'
]
rows = []
for d, note in zip(data['results'], notes):
    p = BASE / 'named-guide-contexts-asr-v6' / (d['id'] + '.json')
    assert read(p) == d and d['exactSourceSampleBytesMatched'] and not d['expectedWasRecognizerPrompt']
    assert sha(ROOT / d['sourcePath']) == d['sourceSha256']
    assert sha(ROOT / d['contextPath']) == d['contextSha256'] == d['audioSha256']
    rows.append(dict(id=d['id'], path=rel(p), sha256=sha(p), expectedKo=d['expectedKo'],
        actualText=d['text'], allExpectedAndEntireActualTextDirectlyRead=True,
        wordsAndFinalSoundDirectlyRead=True, finalSoundScope='Recognized ending text/timestamps; human listening pending',
        exactCurrentSourcePcmMatched=True, sourceSha256=d['sourceSha256'], contextSha256=d['contextSha256'],
        observation=note, noRecognizedSentenceOmission=True, noRecognizedSentenceRepetition=True,
        noRecognizedInventedGreeting=True))
proofp = BASE / 'named-guide-contexts-direct-review-v6.json'
assert not proofp.exists()
save(proofp, dict(schemaVersion=1, reviewedAt=stamp, rows=rows, completeContextCount=2,
    allWholeTextsDirectlyCompared=True, allIndependentContextsDirectlyCompared=True,
    allNewV6WindowsDirectlyCompared=3, namedGuideApprovedForUnmixedPlanning=True,
    humanListening='pending', humanPronunciation='pending', endingHeuristicUsedForApproval=False,
    actualOuterExitCode=0, sessionId=args.session_id, finalMixedAsrApproved=False))
state.update(actualExitObserved=True, actualOuterExitCode=0, actualOuterSessionId=args.session_id,
             actualWorkerAlive=False, actualExitObservedAt=stamp)
save(sp, state)
sessionp = sp.with_name(sp.stem + '.session.json')
assert not sessionp.exists()
save(sessionp, dict(schemaVersion=1, observedAt=stamp, pid=state['pid'], createTime=state['createTime'],
    sessionId=args.session_id, processIdentity=state['processIdentity'], workerExpectedRunning=False,
    actualExitObserved=True, exitCode=0, liveIdentityObservedAtRegistration=False,
    workerIdentitySource='Execution identity; completion drain returned actual outer exit0; matching PID/create no longer alive',
    initialRecorderAttempt=dict(exitCode=1, python='C:/Users/eazuo/miniconda3/python.exe',
        reason='psutil unavailable in base Python; no state or process mutation. Worker finished before corrected registration.'),
    cpuThreads=2, gpuJobs=0, processOrControlChanges=0))

original = {lang: read(PROJECT / f'script/narration.{lang}.json') for lang in ('ko', 'en')}
candidates = {lang: read(PROJECT / f'script/observation-candidates-v3.{lang}.json') for lang in ('ko', 'en')}
named = {lang: read(PROJECT / f'script/named-guide-repair-v6.{lang}.json') for lang in ('ko', 'en')}
o = {s['id']: s for s in original['ko']['scenes']}
c = {s['id']: s for s in candidates['ko']['scenes']}
g = named['ko']['scenes'][0]
order = [o['01-overview'], o['02-score-and-lines'], c['11-observe-separate-updates'],
    o['03-same-count'], c['12-observe-equal-quantity'], o['04-evaluation-weights'],
    c['13-observe-action-label'], o['05-events-and-total'], c['14-observe-notice-and-record'],
    o['06-relative-gap'], c['15-observe-equal-lines-gap'], c['16-observe-later-point-lead'],
    o['07-name-and-unit'], g, o['08-scoring-feedback'], o['09-feedback-hierarchy'],
    c['18-observe-stable-reading'], o['10-audit-and-close'], c['19-observe-reading-audit']]
selected_ids = [s['id'] for s in order]
assert len(selected_ids) == len(set(selected_ids)) == 19
proofs = [evidence(n) for n in ['current-whole-direct-review-v1.json', 'current-contexts-direct-review-v1.json',
    'observation-candidates-whole-direct-review-v3.json', 'observation-candidates-contexts-direct-review-v3.json',
    'observation-candidates-targets-direct-review-v3.json', 'named-guide-whole-direct-review-v6.json',
    'named-guide-contexts-direct-review-v6.json']]
joins = {x['id']: x for x in read(BASE / 'candidate-complete-joins-pcm-verification-v3.json')['joins']}
voice_rows = []
for s in order:
    sid = s['id']
    if sid in joins:
        join = joins[sid]
        path = ROOT / join['path']
        assert sha(path) == join['sha256']
        n, b = pcm(path)
        _, old = pcm(ROOT / join['originalPath'])
        _, fresh = pcm(ROOT / join['candidatePath'])
        assert b == old[:join['originalRetainedSamples'][1] * 2] + fresh
        scope = 'Exact original first two paragraphs + full reviewed candidate third paragraph; original text unchanged'
    else:
        folder = 'qwen3-named-guide-v6' if sid == g['id'] else 'qwen3-1.7b-balanced-v1' if sid in o else 'qwen3-observation-candidates-v3'
        path = ROOT / 'shared/output/narration/presenting-game-scores' / folder / 'chunks' / (sid + '-scene.wav')
        n, b = pcm(path)
        scope = 'Whole unchanged original scene' if sid in o else 'Whole directly compared independent guide'
    voice_rows.append(dict(id=sid, path=rel(path), sha256=sha(path), pcmSha256=hashlib.sha256(b).hexdigest(),
        samples=n, sampleRate=24000, seconds=n/24000, completeParagraphs=len(s['lines']), selectionScope=scope))
total_samples = sum(s['samples'] for s in voice_rows)
assert total_samples == 6388323
for lang in ('ko', 'en'):
    scenes = {s['id']: s for source in (original[lang], candidates[lang], named[lang]) for s in source['scenes']}
    current = dict(title=original[lang]['title'], language=lang, independentlyWritten=True,
                   scenes=[copy.deepcopy(scenes[sid]) for sid in selected_ids])
    assert sum(len(s['lines']) for s in current['scenes']) == 39
    for old in original[lang]['scenes']:
        assert next(s for s in current['scenes'] if s['id'] == old['id']) == old
    save(PROJECT / f'script/current-voice-v7.{lang}.json', current)
selection = dict(schemaVersion=1, adoptedAt=stamp, slug='presenting-game-scores', scenes=voice_rows,
    sceneOrder=selected_ids, scenesCount=19, paragraphsCount=39, originalParagraphsPreserved=30,
    exactOriginalKoEnScenesPreserved=True, originalChunksChanged=False, speechTrimmed=False,
    alteredSelectedPcmSamples=0, narrationSampleRate=24000, narrationSamples=total_samples,
    currentPcmSeconds=total_samples/24000, currentVoiceApproved=True,
    approvalScope='Unmixed full-content ASR and exact PCM planning selection; human listening/pronunciation and final mixed ASR still pending',
    reviewEvidence=proofs, completeOriginal04And08JoinEvidence=rel(BASE / 'candidate-complete-joins-pcm-verification-v3.json'),
    namedGuideSupersedesHeldIds=['17-observe-named-fields', '22-named-fields-guide-repair'],
    rejectedCandidate='23-evaluation-p3-particle-candidate; 배전표 recognition persists',
    pendingRecognitionDetails=['04 점수의/점수', '16 왼쪽의/왼쪽에', '06 경기 중의/중에'],
    pendingDetailsPolicy='Original written particles retained; full clauses/technical concepts represented. No claim of exact phonetic match or confirmed audible omission.',
    resolvedTechnicalTerms=['배점표 in v3 independent/full join', '기여/읽게 in v3 independent/full join', '먼저 in v6 whole/independent/full lead'],
    numericAsrToLiteralCaptionMap={'27':'스물일곱','14096':'만사천구십육','17016':'만칠천십육','2920':'이천구백이십','141':'백사십일'},
    overviewActualPcmSeconds=16.96, overviewPlannedTargetSeconds=[20,30], overviewPaddedOrSlowed=False,
    humanListening='pending', humanPronunciation='pending', finalMixedAsrApproved=False,
    finalTimingApproved=False, allFinalPixels=False, qaApproved=False, collected=False, privateUploaded=False,
    actualId=None, endingHeuristicUsedForApproval=False, newTtsJobs=0, newAsrJobs=0, newGpuJobs=0,
    newImagesOrGitMedia=0, duplicateCheck=dict(exitCode=dup.returncode, output=dup.stdout.strip()))
save(BASE / 'current-voice-selection-v7.json', selection)
mp = PROJECT / 'project.json'
m = read(mp)
m['status'] = 'current-unmixed-voice-reviewed-measured-timeline-pending'
m['currentVoiceSelection'] = rel(BASE / 'current-voice-selection-v7.json')
m['approvals']['currentUnmixedVoice'] = True
m['approvals']['finalMixedAsr'] = False
save(mp, m)
cp = read(BASE / 'latest-checkpoint.json')
cp.update(recordedAt=stamp, stage=m['status'], ownedJob=None, currentVoiceApproved=True,
    asrApproved=True, narrationApproved=True, approvalScope=selection['approvalScope'],
    currentVoiceSelection=rel(BASE / 'current-voice-selection-v7.json'),
    nextAction='Build measured normal-speed unique actual60:black explanation40 plan and literal KOEN captions. Preserve original30 and selected exact266.180125s PCM; final mixed/pair/pixels/QA/collection/private remain pending.')
save(BASE / 'latest-checkpoint.json', cp)
qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(8):
    raw = qp.read_text('utf-8-sig'); q = json.loads(raw)
    item = next(x for x in q['items'] if x['slug'] == 'presenting-game-scores')
    item.update(stage=cp['stage'], currentExecution=None, currentVoiceSelection=cp['currentVoiceSelection'],
                nextAction=cp['nextAction'])
    q['updatedAt'] = stamp; q['lastProgressAt'] = stamp
    if qp.read_text('utf-8-sig') == raw:
        save(qp, q); break
else:
    raise RuntimeError('Concurrent queue change; preserve foreign work.')
print(json.dumps(dict(scenes=19, paragraphs=39, pcmSeconds=total_samples/24000,
    currentUnmixedVoiceApproved=True, finalMixedAsrApproved=False, humanListening='pending')))

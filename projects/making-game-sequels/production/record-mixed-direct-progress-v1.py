"""Keep partial direct mixed-text review distinct from complete approval."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, time

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
W = BASE / 'final-v1'
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-making-game-sequels'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
stamp = datetime.now(timezone.utc).isoformat()


def write(p, data):
    temporary = p.with_name(p.name + f'.{os.getpid()}.writing')
    for attempt in range(120):
        try:
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            os.replace(temporary, p)
            return
        except OSError:
            if attempt == 119:
                raise
            time.sleep(.25)


progress_path = W / 'mixed-asr-direct-progress.json'
progress = read(progress_path)
assert not progress['technicallyApproved']
notes = {
    'scene-06': 'All six expected paragraphs and actual whole text/word anchors directly read. The chunk edge invents 다음 영상에서 만나요 at49.0–49.98s and repeats earlier words with timestamps jumping back to40s. Independent complete06p4–6 context remains pending; this is not declared an actual greeting/repetition or approved away.',
    'scene-13': 'All seven paragraphs and whole word anchors directly compared: same-game far/near actions, separate clips, no sequel-feature or optimal-strategy inference, and writing exercise. 안의/안에 transcription ambiguity is retained. No omitted meaning or arbitrary greeting observed in this window.',
    'scene-07': 'All four expected paragraphs and whole words directly read. At29.98s the chunk invents 같은 시각 세계였습니다 with zero-duration endings and repeats p3 with timestamps jumping back to20s. Independent retained-core context remains pending; no actual repetition/greeting or pronunciation approval is inferred.',
    'scene-08': 'All four expected paragraphs and actual whole text directly compared: ReadyUp path versus enemies, overhead preview, visible resource counter, sell prompt versus selling, and relation to future choices. 의/에 recognizer spelling ambiguity is retained; no omitted meaning or added rule observed.',
    'scene-09': 'All four paragraphs and whole mixed text directly compared: what/when choices happen, developer-play selection context, effects not inferred from later combat, and proposed verification. 사이에/사이의 transcription ambiguity retained; no missing meaning or arbitrary greeting observed.',
    'scene-10': 'All four paragraphs and whole text directly compared: first/second-wave aiming, visible overlapping defence/direct attack, no specific-card causality and retained/new decisions. 의/에 particle transcription remains human-pronunciation pending; no repeated sentence or missing ending observed.',
    'scene-11': 'All four paragraphs and whole text directly compared: returning/first-time players, hypothetical branching task, actual research distinguished, uncertainty and no success/sales guarantee. No omission/repetition/arbitrary greeting observed.',
    'scene-12': 'All six paragraphs and whole mixed text directly read, including both preparation/combat guides and all conclusion promises. At the recognizer chunk edge, 그 두 분은 and earlier conclusion words repeat; independent complete conclusion context remains pending, and this is not declared an actual PCM repeat.',
    '01-overview-clarity': 'All three complete overview paragraphs and independent current mixed text directly compared: central question, actual ordered actions and viewer outcome. Orcs transliteration preserved as pronunciation pending; no omitted meaning or arbitrary greeting observed.'
}
for label, note in notes.items():
    source = W / 'mixed-asr-v1' / (label + '.json')
    result = read(source)
    assert result['expectedWasRecognizerPrompt'] is False
    record = dict(label=label, source=rel(source), resultSha256=sha(source),
                  windowSha256=result['windowSha256'], allExpectedParagraphsAndActualWholeTextDirectlyRead=True,
                  note=note, humanListening='pending', humanPronunciation='pending')
    previous = next((row for row in progress['reviewedWindows'] if row['label'] == label), None)
    if previous:
        assert previous['resultSha256'] == record['resultSha256']
        progress['reviewedWindows'].remove(previous)
    progress['reviewedWindows'].append(record)
progress.update(reviewedAt=stamp, reviewedWindowCount=len(progress['reviewedWindows']),
                all26WindowsDirectlyCompared=False, technicallyApproved=False,
                unresolvedMixedRecognizerObservations=['scene04 Knight 나이드/나이트',
                    'scene06 chunk-edge greeting and backward/repeated timestamps',
                    'scene07 chunk-edge text and backward/repeated timestamps',
                    'scene12 chunk-edge conclusion word repetition'])
write(progress_path, progress)
git = read(PROOF / 'mixed-asr-handoff-git-verification.json')
assert git['normalPush'] and git['remoteMatches'] and git['pushExitCode'] == 0
qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
queue = read(qp)
item = next(row for row in queue['items'] if row['slug'] == 'making-game-sequels')
item['mixedAsrHandoffGit'] = dict(progressCommit=git['progressCommit'], latestVerification=git,
    completedVideoDelivery=False, newImages=0, mediaInGit=False)
item['currentMixedAsrDirectProgress'] = dict(path=rel(progress_path), reviewedWindows=progress['reviewedWindowCount'],
    requiredWindows=26, technicallyApproved=False, independentContextReviewPending=True,
    recognizerUncertaintyPreserved=True)
item['preparedReviewPairProducer'].update(executed=False, exactPresentationPacketClockRequired=True)
queue['updatedAt'] = stamp
write(qp, queue)
for path in [BASE / 'latest-checkpoint.json', PROOF / 'latest-checkpoint.json']:
    checkpoint = read(path)
    for key in ['mixedAsrHandoffGit', 'currentMixedAsrDirectProgress', 'preparedReviewPairProducer']:
        checkpoint[key] = item[key]
    checkpoint['updatedAt'] = stamp
    write(path, checkpoint)
print(json.dumps(dict(reviewed=progress['reviewedWindowCount'], required=26, approved=False,
                     actualHandoffCommit=git['progressCommit']), ensure_ascii=False))

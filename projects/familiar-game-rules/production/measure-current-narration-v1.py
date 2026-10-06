"""Measure the closed current synthesis. Measurement never grants audio approval."""
from pathlib import Path
from datetime import datetime, timezone
import array, hashlib, json, os, time, wave

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = lambda: datetime.now(timezone.utc).isoformat()


def write(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for n in range(40):
        try:
            os.replace(tmp, p)
            return
        except OSError:
            if n == 39:
                raise
            time.sleep(.15)


def measure(p):
    with wave.open(str(p), 'rb') as w:
        rate, channels, width, count = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
        assert rate == 24000 and channels == 1 and width == 2, 'Unexpected current PCM format'
        pcm = array.array('h', w.readframes(count))
    assert count > 0 and max(abs(v) for v in pcm) > 0
    return dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p), sampleRate=rate,
                channels=channels, sampleWidthBytes=width, sampleCount=count, seconds=count/rate,
                peakInt16=max(abs(v) for v in pcm))


dest = BASE / 'current-narration-measurement-v1.json'
assert not dest.exists(), 'Read existing measured evidence; do not repeat completed work'
execution = read(PROOF / 'narration-execution-v1.json')
assert execution.get('exitCode') == 0 and execution['status'] == 'synthesis-finished-awaiting-current-ASR'
review = read(PROOF / 'script-and-opening-direct-review-v1.json')
assert review['wholeScriptDirectReviewApproved'] and review['openingPromiseDirectReviewApproved']
for row in review['files']:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']
manifest = read(BASE.parent / 'project.json')
script = read(ROOT / manifest['paths']['script'])
chapters = read(ROOT / manifest['paths']['chapterPlan'])
out = ROOT / manifest['tts']['outputDir']
rows = []
for scene in script['scenes']:
    row = measure(out / 'chunks' / (scene['id'] + '-scene.wav'))
    row.update(scene=scene['id'], paragraphCount=len(scene['lines']),
               role=next(x['role'] for x in chapters['chapters'] if x['id'] == scene['id']))
    rows.append(row)
assert len(rows) == 11 and sum(x['paragraphCount'] for x in rows) == 46
assembled = measure(ROOT / manifest['paths']['narration'])
speech = sum(x['seconds'] for x in rows)
assert assembled['sampleCount'] == sum(x['sampleCount'] for x in rows) + round(.72 * 24000) * 10
white = sum(x['seconds'] for x in rows if x['role'] == 'explanation')
actual_speech = speech - white
bank = read(PROOF / 'source-action-bank-v2.json')
evidence = dict(schemaVersion=1, slug=manifest['slug'], measuredAt=now(), synthesisExecution=execution,
                scriptSha256=sha(ROOT / manifest['paths']['script']), measurements=rows,
                assembled=assembled, totalSpeechSeconds=speech, explanationSpeechSeconds=white,
                actualChapterSpeechSeconds=actual_speech, overviewSeconds=rows[0]['seconds'],
                minimumActualSecondsAt60_40=white*1.5, reviewedSourceSeconds=bank['candidateSeconds'],
                minimumSourceShortfallSeconds=max(0, white*1.5-bank['candidateSeconds']),
                sourceCapacityIsFinalTiming=False, finalTimingApproved=False, asrApproved=False,
                narrationApproved=False, humanWholeListening='pending', pronunciation='pending',
                subtitleTiming='TTS paragraph estimates only; align current ASR/PCM before final cues',
                preservation='Keep all measured PCM and useful explanation; add distinct related official actions and narration rather than cutting explanation to fit source capacity.')
write(dest, evidence)
qpath = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
q = read(qpath)
item = next(i for i in q['items'] if i['slug'] == manifest['slug'])
item.update(stage='current11-measured-awaiting-whole-ASR-and-source-expansion', updatedAt=now(),
            narrationMeasurement={k:v for k,v in evidence.items() if k not in ['synthesisExecution','measurements','assembled']},
            nextAction='Review all11 whole current PCM ASR then complete independent contexts; inspect more distinct official actions for measured60:40. Final pixels/render/collection/private pending.')
item['narrationMeasurement']['path'] = dest.relative_to(ROOT).as_posix()
item['checkpoints']['narration'] = False
write(qpath, q)
for p in [BASE/'latest-checkpoint.json', PROOF/'latest-checkpoint.json']:
    d = read(p)
    for k in ['stage','updatedAt','narrationMeasurement','nextAction']:
        d[k] = item[k]
    write(p,d)
print(json.dumps({k:evidence[k] for k in ['totalSpeechSeconds','overviewSeconds','explanationSpeechSeconds','minimumActualSecondsAt60_40','minimumSourceShortfallSeconds']}, ensure_ascii=False))

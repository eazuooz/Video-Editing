"""Give three isolated Korean words readable holds; preserve text, scene timing and both language tracks."""
from pathlib import Path
from datetime import datetime, timezone
import json, shutil, hashlib

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / 'projects/hierarchical-game-outlines/production/final-v1'
BASELINE = WORK / 'caption-temporal-baseline-v3'
assert not BASELINE.exists(), 'Inspect existing temporal revision.'
BASELINE.mkdir()
for name in ['caption-alignment.json', 'caption-layout-qa.json', 'captions.ko.srt', 'captions.en.srt', 'captions.ko.ass', 'final-source-cut-review.json']:
    shutil.copyfile(WORK / name, BASELINE / name)
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
data = read(WORK / 'caption-alignment.json')
cues = data['entries']
before_text = [(c['ko'], c['en']) for c in cues]
changes = []
for cue_number in [148, 226, 256]:
    i = cue_number - 1
    prev, cue, following = cues[i - 1:i + 2]
    old = {k: cue[k] for k in ['start', 'end', 'ko', 'en']}
    assert prev['scene'] == cue['scene'] == following['scene']
    assert .25 < cue['end'] - cue['start'] < .5
    extra = .65 - (cue['end'] - cue['start'])
    cue['start'] -= extra / 2
    cue['end'] += extra / 2
    prev['end'] = min(prev['end'], cue['start'] - .016)
    following['start'] = max(following['start'], cue['end'] + .016)
    assert prev['end'] - prev['start'] > .7 and following['end'] - following['start'] > .7
    changes.append({'cue': cue_number, 'before': old, 'after': {k: cue[k] for k in old},
                    'borrowingPerSideSeconds': extra / 2, 'affectedCues': [i, i + 1, i + 2]})
assert before_text == [(c['ko'], c['en']) for c in cues]
assert all(c['end'] > c['start'] for c in cues)
assert all(cues[i]['end'] <= cues[i + 1]['start'] for i in range(len(cues) - 1))
def stamp(t):
    n = round(t * 1000)
    return f'{n // 3600000:02}:{n // 60000 % 60:02}:{n // 1000 % 60:02},{n % 1000:03}'
for lang in ['ko', 'en']:
    paragraphs = []
    for i, c in enumerate(cues, 1):
        text = c[lang]
        if lang == 'en' and len(text) > 80:
            words = text.split()
            split = min(range(1, len(words)), key=lambda j: abs(len(' '.join(words[:j])) - len(' '.join(words[j:]))))
            text = ' '.join(words[:split]) + '\n' + ' '.join(words[split:])
        paragraphs.append(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{text}')
    (WORK / f'captions.{lang}.srt').write_text('\n\n'.join(paragraphs) + '\n', encoding='utf-8')
(WORK / 'caption-alignment.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
proof = {'createdAt': datetime.now(timezone.utc).isoformat(), 'changes': changes,
         'allKoreanAndEnglishTextIdentical': True, 'sharedBilingualTiming': True,
         'sceneStartsAudioAndCutsUnchanged': True, 'sourceSelectionSha256': hashlib.sha256((WORK / 'cut-selection.json').read_bytes()).hexdigest(),
         'fixedCaptionCenter': [960, 970], 'changedPixelReview': 'pending', 'finalCaptionReview': 'pending'}
(WORK / 'caption-temporal-v3.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'changedCues': [148, 226, 256], 'newHoldSeconds': .65, 'textPreserved': True}))

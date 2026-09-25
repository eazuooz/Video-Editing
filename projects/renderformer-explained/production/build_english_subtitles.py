"""Preserve every Korean cue's timing; validate the authored English translation."""
from pathlib import Path
import csv
import hashlib
import json
import textwrap

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / 'projects/renderformer-explained'
BASE = PROJECT / 'production/body-review'


def stamp(seconds):
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def main():
    timing = json.loads((BASE / 'timing.json').read_text(encoding='utf-8'))
    source = PROJECT / 'script/captions.en.tsv'
    with source.open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    translations = {(int(r['page']), int(r['cue'])): r['text'] for r in rows}
    if len(rows) != len(translations):
        raise ValueError('Duplicate translation key')
    expected = {(s['sourcePage'], i) for s in timing['scenes'] for i in range(len(s['cues']))}
    if translations.keys() != expected:
        raise ValueError(f'Missing: {expected-translations.keys()}; extra: {translations.keys()-expected}')
    cues = []
    for scene in timing['scenes']:
        for i, cue in enumerate(scene['cues']):
            text = translations[scene['sourcePage'], i].strip()
            if not text or '\ufffd' in text:
                raise ValueError(f'Invalid translation: {scene["sourcePage"]}:{i}')
            # Long technical sentences stay in at most two lines; no timing changes.
            width = max(48, (len(text) + 1)//2)
            lines = textwrap.wrap(text, width=width, break_long_words=False)
            while len(lines) > 2:
                width += 1
                lines = textwrap.wrap(text, width=width, break_long_words=False)
            global_cue = timing['captions'][len(cues)]
            cues.append({**global_cue, 'en': '\n'.join(lines)})
    previous = 0
    for cue in cues:
        if not 0 <= previous <= cue['start'] < cue['end'] <= timing['duration']:
            raise ValueError(f'Invalid timing: {cue}')
        previous = cue['end']
    srt = '\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["en"]}' for i,c in enumerate(cues))+'\n'
    (BASE / 'renderformer.en.srt').write_text(srt, encoding='utf-8')
    ko = (BASE / 'renderformer.ko.srt').read_text(encoding='utf-8')
    assert [l for l in ko.splitlines() if ' --> ' in l] == [l for l in srt.splitlines() if ' --> ' in l]
    report = {'cues': len(cues), 'pages': len(timing['scenes']), 'sameTimecodesAsKorean': True,
              'source': str(source.relative_to(ROOT)), 'sourceSHA256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'maxLines': 2, 'bodyDuration': timing['duration'], 'outroCue': False}
    (BASE / 'subtitle-validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()

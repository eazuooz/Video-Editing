"""Repartition translated words over fixed Korean cue times, without retiming.

The default writes a candidate, not the active captions of a running render.
Use --apply only after rendering has completed; the original is backed up.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from functools import lru_cache
from pathlib import Path

from build_translated_srt import wrapped_lines

ROOT = Path(__file__).resolve().parents[1]


def partition_timed(text: str, width: int, durations: list[float]) -> list[str]:
    words = text.split()
    if not durations or any(d <= 0 for d in durations):
        raise ValueError("Positive cue durations are required")
    average = len(text) / sum(durations)

    @lru_cache(None)
    def solve(start: int, cue: int):
        if cue == len(durations):
            return (0., 0., ()) if start == len(words) else (float('inf'), float('inf'), ())
        best = (float('inf'), float('inf'), ())
        remaining = len(durations) - cue
        for end in range(start + 1, len(words) - remaining + 2):
            chunk = ' '.join(words[start:end])
            if len(wrapped_lines(chunk, width)) > 2:
                break
            peak, cost, rest = solve(end, cue + 1)
            cps = len(chunk) / durations[cue]
            balance = (cps - average)**2 * durations[cue]
            # Prefer punctuation on ties while minimizing the worst reading rate.
            if chunk.endswith(('.', '?', '!', ',', ';', ':')):
                balance -= 4
            candidate = (max(cps, peak), balance + cost, (chunk, *rest))
            if candidate[:2] < best[:2]:
                best = candidate
        return best

    peak, _, chunks = solve(0, 0)
    if peak == float('inf'):
        raise ValueError('Translation cannot fit the fixed cue count/width')
    return list(chunks)


def parse_time(value: str) -> float:
    h, m, s, ms = map(int, re.split('[:,]', value))
    return h * 3600 + m * 60 + s + ms / 1000


def parse_srt(path: Path):
    result = []
    for i, block in enumerate(re.split(r'\n\s*\n', path.read_text(encoding='utf-8').strip()), 1):
        number, times, *lines = block.splitlines()
        if int(number) != i:
            raise ValueError('Non-sequential SRT')
        start, end = map(parse_time, times.split(' --> '))
        result.append(dict(number=i, times=times, start=start, end=end, text=' '.join(lines)))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    project = ROOT / 'projects' / args.project
    m = json.loads((project / 'project.json').read_text(encoding='utf-8'))
    output = ROOT / m['tts']['outputDir']
    stem = m['tts']['filenameStem']
    timing = json.loads((output / f'{stem}.timing.json').read_text(encoding='utf-8'))
    translated = json.loads((project / 'script/narration.en.json').read_text(encoding='utf-8'))
    paragraphs = [line for scene in translated['scenes'] for line in scene['lines']]
    ko = parse_srt(ROOT / m['paths']['captionsKo'])
    en_path = ROOT / m['paths']['captionsEn']
    previous = parse_srt(en_path)
    if len(paragraphs) != len(timing['entries']) or [c['times'] for c in ko] != [c['times'] for c in previous]:
        raise ValueError('Translation/timing mismatch')
    cursor = 0
    chunks = []
    for entry, text in zip(timing['entries'], paragraphs):
        cues = []
        while cursor < len(ko) and ko[cursor]['end'] <= entry['end'] + .002:
            cue = ko[cursor]
            if cue['start'] < entry.get('voice_start', entry['start']) - .002:
                raise ValueError('Cue crosses paragraph boundary')
            cues.append(cue)
            cursor += 1
        chunks.extend(partition_timed(text, 46, [c['end'] - c['start'] for c in cues]))
    if cursor != len(ko) or re.sub(r'\s+', '', ' '.join(chunks)) != re.sub(r'\s+', '', ' '.join(paragraphs)):
        raise ValueError('Lost translated words/cues')
    destination = en_path if args.apply else output / f'{stem}.en.balanced-candidate.srt'
    if args.apply:
        backup = output / f'{stem}.en.before-duration-balance.srt'
        if not backup.exists():
            shutil.copy2(en_path, backup)
    destination.write_text('\n\n'.join(f"{c['number']}\n{c['times']}\n" + '\n'.join(wrapped_lines(s, 46)) for c, s in zip(ko, chunks)) + '\n', encoding='utf-8')
    old_peak = max(len(c['text']) / (c['end'] - c['start']) for c in previous)
    new_peak = max(len(s) / (c['end'] - c['start']) for c, s in zip(ko, chunks))
    report = dict(cueCount=len(ko),timecodesUnchanged=True,allTranslatedWordsPreserved=True,oldMaxCps=old_peak,newMaxCps=new_peak,applied=args.apply,destination=str(destination.relative_to(ROOT)))
    (output / f'{stem}.translation-balance.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

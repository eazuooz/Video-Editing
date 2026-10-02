"""Inspect current speech/source fit without approving or changing the edit.

Run during synthesis or after ASR. Missing/current-hash mismatches stay pending.
This never pads, retimes, synthesizes, renders, or substitutes game footage.
"""
from pathlib import Path
import difflib
import hashlib
import json
import math
import re

import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'projects/picking-sides'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
manifest = read(BASE / 'project.json')
script = read(ROOT / manifest['paths']['script'])
bank = read(BASE / 'planning/action-map.json')
voice = ROOT / manifest['tts']['outputDir']
chapters = {c['scene']: c for c in bank['chapters']}


def normalize(text):
    return re.sub(r'[^a-z0-9가-힣]', '', text.lower())


def paragraph_times(lines, asr, duration):
    expected = normalize(''.join(lines))
    recognized = ''
    times = []
    for word in asr['words']:
        start, end = word['timestamp']
        if start is None or end is None:
            return None, 'unresolved-word-timestamp'
        chars = normalize(word['text'])
        for j, char in enumerate(chars):
            recognized += char
            times.append((start + (end-start)*j/len(chars),
                          start + (end-start)*(j+1)/len(chars)))
    match = difflib.SequenceMatcher(None, expected, recognized, autojunk=False)
    if match.ratio() < .94:
        return None, 'content-difference-requires-direct-review'
    mapping = {block.a+j: block.b+j for block in match.get_matching_blocks()
               for j in range(block.size)}

    def stamp(index, edge):
        nearest = min(mapping, key=lambda k: abs(k-index))
        target = max(0, min(len(times)-1, mapping[nearest]+index-nearest))
        return min(duration, max(0, times[target][edge]))

    rows, offset = [], 0
    for number, line in enumerate(lines, 1):
        length = len(normalize(line))
        rows.append({'paragraph': number, 'start': stamp(offset, 0),
                     'end': stamp(offset+length-1, 1)})
        offset += length
    return rows, None


rows = []
for scene in script['scenes']:
    sid = scene['id']
    wav = voice / 'chunks' / f'{sid}-scene.wav'
    row = {'scene': sid, 'classification': 'actual' if sid in chapters else 'explanation',
           'status': 'pending-wave', 'approved': False}
    rows.append(row)
    if not wav.exists():
        continue
    info = sf.info(wav)
    digest = hashlib.sha256(wav.read_bytes()).hexdigest()
    row.update(audioSha256=digest, voiceSeconds=info.frames/info.samplerate,
               minimumFrames=math.ceil(info.frames/info.samplerate*60-1e-7)+43,
               status='pending-current-hash-asr')
    cache = voice / 'asr' / f'{sid}.json'
    if not cache.exists():
        continue
    asr = read(cache)
    if asr['audio_sha256'] != digest:
        continue
    paragraphs, error = paragraph_times(scene['lines'], asr, row['voiceSeconds'])
    row.update(status=error or 'provisional-word-timing-only', paragraphs=paragraphs)
    if sid not in chapters or not paragraphs:
        continue
    chapter = chapters[sid]
    row['sourceGroups'] = []
    groups = chapter.get('paragraphGroups', [])
    for i, group in enumerate(groups):
        start = 0 if i == 0 else paragraphs[min(group['lines'])-1]['start']
        end = (paragraphs[min(groups[i+1]['lines'])-1]['start'] if i+1 < len(groups)
               else row['minimumFrames']/60)
        available = sum(c['end']-c['start'] for c in chapter['cuts']
                        if c['sourceId'] == group['sourceId'])
        row['sourceGroups'].append({**group, 'speechStart': start, 'speechEnd': end,
            'minimumSeconds': end-start, 'bankSeconds': available,
            'bankMinusSpeechSeconds': available-(end-start)})

explanation = [s for s in rows if s['classification'] == 'explanation']
actual = [s for s in rows if s['classification'] == 'actual']
P = sum(s.get('minimumFrames', 0) for s in explanation)
A = sum(s.get('minimumFrames', 0) for s in actual)
report = {'kind': 'provisional-measurement-not-editorial-approval',
          'completeWaves': all('voiceSeconds' in s for s in rows),
          'allCurrentAsr': all(s['status'] == 'provisional-word-timing-only' for s in rows),
          'explanationMinimumFrames': P,
          'actualTargetFramesIfExplanationsComplete': round(P*1.5),
          'availableActualBankSeconds': sum(c['availableSeconds'] for c in bank['chapters']),
          'currentlyMeasuredActualMinimumFrames': A,
          'explanationNotCut': True, 'renderAllowed': False, 'scenes': rows}
dest = BASE / 'production/existing-game-replan/provisional-speech-source-fit.json'
dest.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k != 'scenes'}, ensure_ascii=False))
for row in rows:
    if row.get('sourceGroups'):
        print(json.dumps({'scene':row['scene'], 'sourceGroups':row['sourceGroups']}, ensure_ascii=False))

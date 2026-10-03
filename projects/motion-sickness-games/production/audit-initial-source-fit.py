"""Research-only fit audit. Never installs final timing or approves pending speech."""
from pathlib import Path
import json, hashlib, re, difflib, datetime
import soundfile as sf
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'projects/motion-sickness-games'
VOICE = ROOT / 'shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v1'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
norm = lambda t: re.sub('[^a-z0-9가-힣]', '', t.lower())
script = read(BASE / 'production/repair1/baseline/script/narration.ko.json')
bank = read(BASE / 'planning/action-map.json')
results = []
durations = {}
for scene in script['scenes']:
    sid = scene['id']
    wav = VOICE / 'chunks' / f'{sid}-scene.wav'
    duration = sf.info(wav).duration
    durations[sid] = duration
    if int(sid) % 2 == 0:
        continue
    asr = read(VOICE / 'asr' / f'{sid}.json')
    assert asr['audio_sha256'] == sha(wav)
    expected = norm(''.join(scene['lines']))
    recognized, timestamps = '', []
    for word in asr['words']:
        start, end = word['timestamp']
        start = float(start if start is not None else (timestamps[-1][1] if timestamps else 0))
        end = min(duration, float(end if end is not None else duration))
        end = max(start, end)
        chars = norm(word['text'])
        for j, char in enumerate(chars):
            recognized += char
            timestamps.append((start + (end-start)*j/len(chars), start + (end-start)*(j+1)/len(chars)))
    match = difflib.SequenceMatcher(None, expected, recognized, autojunk=False)
    assert match.ratio() > .94
    mapping = {b.a+j: b.b+j for b in match.get_matching_blocks() for j in range(b.size)}
    def mapped(i):
        if i in mapping:
            return mapping[i]
        k = min(mapping, key=lambda k: abs(k-i))
        return max(0, min(len(timestamps)-1, mapping[k]+i-k))
    char_pos, boundaries = 0, []
    for line in scene['lines']:
        boundaries.append(timestamps[mapped(char_pos)][0])
        char_pos += len(norm(line))
    chapter = next(c for c in bank['chapters'] if c['scene'] == sid)
    groups = {}
    for cut in chapter['cuts']:
        group = tuple(cut['paragraphs'])
        groups.setdefault(group, []).append(cut)
    rows = []
    for group, cuts in groups.items():
        start = 0 if min(group) == 1 else boundaries[min(group)-1]
        end = duration if max(group) == len(scene['lines']) else boundaries[max(group)]
        available = sum(c['out']-c['in'] for c in cuts)
        rows.append({'paragraphs': list(group), 'initialVoiceStart': start, 'initialVoiceEnd': end,
                     'initialVoiceSeconds': end-start, 'bankSeconds': available,
                     'provisionalDeficitSeconds': max(0, end-start-available),
                     'sourceIntervals': [{'sourceId': c['sourceId'], 'in': c['in'], 'out': c['out']} for c in cuts]})
    results.append({'scene': sid, 'initialWavSha256': sha(wav), 'initialVoiceSeconds': duration,
                    'paragraphStartSeconds': boundaries, 'groups': rows,
                    'overlappingParagraphGroupsRequireSpecificAllocation': any(set(a) & set(b) for n, a in enumerate(groups) for b in list(groups)[n+1:])})
explanation = sum(d for sid, d in durations.items() if int(sid) % 2 == 0)
actual = sum(d for sid, d in durations.items() if int(sid) % 2)
result = {'recordedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'scope': 'Initial v1 audio research only. Seven repairs are pending. Not final timing, allocation, ratio, or source approval.',
          'sourcePlanSha256': sha(BASE / 'planning/action-map.json'),
          'initialActualSpeechSeconds': actual, 'initialExplanationSpeechSeconds': explanation,
          'initialRatioPlanningOnlyActualTarget': 1.5*explanation,
          'bankTotalSeconds': bank['provisionalActualBankSeconds'] if 'provisionalActualBankSeconds' in bank else sum(c['provisionalSourceBankSeconds'] for c in bank['chapters']),
          'finalTimingApproved': False, 'lockedInputsModified': False, 'scenes': results}
dest = BASE / 'production/source-fit-followup/initial-audit.json'
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'report': dest.relative_to(ROOT).as_posix(),
                  'initialVoiceOnlyTarget': result['initialRatioPlanningOnlyActualTarget'],
                  'deficitGroups': [{'scene': s['scene'], 'paragraphs': g['paragraphs'], 'seconds': round(g['provisionalDeficitSeconds'], 3)} for s in results for g in s['groups'] if g['provisionalDeficitSeconds'] > 0],
                  'finalApproval': False}, ensure_ascii=False))

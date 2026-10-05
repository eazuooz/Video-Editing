"""Correct only the overhead caption onset; retain v4 trial inputs and all PCM."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
WORK = BASE / 'measured-edit-v4'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
assert not (WORK / 'caption-tracks-v5.json').exists()
track = read(WORK / 'caption-tracks-v4.json')
old = copy.deepcopy(track)
plan = read(WORK / 'plan.json')
cut = next(c for s in plan['scenes'] for c in s['segments'] if c['id'] == '12-p1-action-48-19530-19742')
assert cut['startFrame'] == 32177
cue = next(c for c in track['koRows'] if c['index'] == 280)
assert cue['ko'] == '머리 위 공간의 미리보기를'
before = cue['startSeconds']
cue['startSeconds'] = cut['startFrame'] / 60
assert abs((cue['startSeconds'] - before) * 60 - 4) < 1e-6
assert cue['endSeconds'] > cue['startSeconds']
assert track['enRows'] == old['enRows']
assert all(a == b for a, b in zip(track['koRows'], old['koRows']) if a['index'] != 280)
record = dict(schemaVersion=1, reviewedAt=datetime.now(timezone.utc).isoformat(),
    previousTracks=dict(path=rel(WORK/'caption-tracks-v4.json'), sha256=sha(WORK/'caption-tracks-v4.json')),
    plan=dict(path=rel(WORK/'plan.json'), sha256=sha(WORK/'plan.json')),
    cue=280, literal=cue['ko'], previousStartSeconds=before,
    correctedStartSeconds=cue['startSeconds'], correctedStartFrame=32177,
    shiftFrames=4, reason='Overhead preview words begin just before the shot; start the fixed caption on the first overhead frame, preserving the spoken PCM and every other cue.',
    audioChanged=False, planChanged=False, allOriginalCharactersPreserved=True,
    englishByteIdentical=True, whiteCaptionRowsUnchanged=True,
    targetedPixelsReviewed=False, allFinalPixelsApproved=False, humanPronunciation='pending')
track['createdAt'] = record['reviewedAt']
track['status'] = 'one-overhead-onset-correction-target-pixels-pending'
track['overheadOnsetCorrection'] = record
(WORK/'caption-tracks-v5.json').write_text(json.dumps(track, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def ts(t):
    n = round(t*1000)
    return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
text = '\n\n'.join(f'{r["index"]}\n{ts(r["startSeconds"])} --> {ts(r["endSeconds"])}\n'+'\n'.join(r['lines']) for r in track['koRows'])+'\n'
(WORK/'captions.ko.candidate.v5.srt').write_text(text, encoding='utf-8')
(WORK/'captions.en.candidate.v5.srt').write_bytes((WORK/'captions.en.candidate.v4.srt').read_bytes())
ass = (WORK/'captions.ko.candidate.v4.ass').read_text(encoding='utf-8')
old_time, new_time = '0:08:56.22', '0:08:56.28'
lines = ass.splitlines(); changed = []
for i, line in enumerate(lines):
    if line.startswith('Dialogue: ') and line.split(',')[1:3] == [old_time, '0:08:58.04']:
        lines[i] = line.replace(','+old_time+',', ','+new_time+',', 1); changed.append(i+1)
assert len(changed) == 3, changed
(WORK/'captions.ko.candidate.v5.ass').write_text('\n'.join(lines)+'\n', encoding='utf-8')
record['changedAssLines'] = changed
record['assFirstCaptionFrame'] = 32177
record['updatedTracksSha256'] = sha(WORK/'caption-tracks-v5.json')
(WORK/'overhead-caption-boundary-v5.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(dict(changedCue=280, shiftFrames=4, allOtherCuesUnchanged=True, whiteUnchanged=True, targetPixelsApproved=False)))

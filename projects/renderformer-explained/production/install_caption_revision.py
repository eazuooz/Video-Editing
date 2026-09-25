"""Validate a newly composed display-only revision, then preserve and replace the old master."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'projects/renderformer-explained/production/body-review'

def run(*args):
    return subprocess.run(args, check=True, capture_output=True, encoding='utf-8').stdout

def audio_hash(path):
    return run('ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0', '-c', 'copy', '-f', 'hash', '-hash', 'sha256', '-').strip()

new = BASE / 'renderformer-captioned-paper-notation-v2.mp4'
current = BASE / 'renderformer-captioned-review.mp4'
backup = BASE / 'renderformer-captioned-before-paper-notation.mp4'
assert new.is_file() and not backup.exists(), 'Revision already installed or not rendered'
composition_path = BASE / 'caption-composition.json'
composition = json.loads(composition_path.read_text(encoding='utf-8'))
assert composition['fullDecodePassed'] and composition_path.stat().st_mtime >= new.stat().st_mtime
timing = json.loads((BASE / 'timing.json').read_text(encoding='utf-8'))
old = json.loads((BASE / 'timing.before-paper-notation.json').read_text(encoding='utf-8'))
assert [(c['start'], c['end']) for c in timing['captions']] == [(c['start'], c['end']) for c in old['captions']]
layout = json.loads((BASE / 'caption-overlays/layout.json').read_text(encoding='utf-8'))['layout']
assert len(layout) == 533 and all(len(c['lines']) <= 2 and c['width'] <= 1700 for c in layout)
assert [' '.join(c['lines']) for c in layout] == [c['ko'] for c in timing['captions']]
ko = (BASE / 'renderformer.ko.srt').read_text(encoding='utf-8')
en = (BASE / 'renderformer.en.srt').read_text(encoding='utf-8')
assert re.findall(r'^.* --> .*$', ko, re.M) == re.findall(r'^.* --> .*$', en, re.M)
assert not any(t in ko for t in ['스위글루', '젤루', '렐루', '피드포워드', 'FFN가', 'FFN를', 'FFN는'])
probe = json.loads(run('ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(new)))
video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
assert (video['width'], video['height'], video['r_frame_rate'], int(video['nb_frames'])) == (1920, 1080, '60/1', 158925)
assert abs(float(probe['format']['duration']) - 2648.75) < .02
digest = audio_hash(new)
assert digest == audio_hash(current) == audio_hash(BASE / 'renderformer-clean-review.mp4')
qa = BASE / 'paper-notation-qa'
qa.mkdir(exist_ok=True)
for page, index in [(28, 1), (73, 1), (75, 1), (75, 2), (75, 3), (82, 1)]:
    scene = timing['scenes'][page-1]
    cue = scene['cues'][index]
    at = scene['firstFrame']/60 + (cue['start'] + cue['end'])/2
    run('ffmpeg', '-v', 'error', '-y', '-ss', str(at), '-i', str(new), '-frames:v', '1', str(qa / f'page-{page:02}-cue-{index}.png'))
current.rename(backup)
new.rename(current)
composition['output'] = current.name
composition['captionNotationRevision'] = timing['captionNotationRevision']
composition_path.write_text(json.dumps(composition, indent=2)+'\n', encoding='utf-8')
media_path = BASE / 'media-validation.json'
media = json.loads(media_path.read_text(encoding='utf-8'))
for item in media['reports']:
    if item['variant'] == 'captioned':
        item['bytes'] = current.stat().st_size
        item['audioHash'] = digest
media['captionNotationRevision'] = timing['captionNotationRevision']
media['captionRevisionQA'] = 'paper-notation-qa/ (earlier video-qa/ captures are the pre-notation revision)'
media_path.write_text(json.dumps(media, indent=2)+'\n', encoding='utf-8')
report = {'revision': timing['captionNotationRevision'], 'cues': 533, 'changedCues': 136,
          'timestampsUnchanged': True, 'audioHash': digest, 'audioIdenticalToPreviousAndClean': True,
          'fullDecodePassed': True, 'captionLayoutPassed': True, 'frames': 158925, 'duration': 2648.75,
          'current': str(current), 'previousPreserved': str(backup)}
(BASE / 'caption-notation-validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps(report), flush=True)

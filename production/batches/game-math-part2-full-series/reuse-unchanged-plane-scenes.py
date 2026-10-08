"""Retain renders whose complete scene data and all render inputs are unchanged.

This narrowly bridges a whole-lesson hash after spoken sentence clarification.
Changed scenes keep their old fingerprints and must render again.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, shutil
import psutil
from production_control import require_current_authorization

ROOT = Path(__file__).resolve().parents[3]
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--baseline', required=True)
args = ap.parse_args()
slug = 'game-math-planes-barycentric'
require_current_authorization(slug, 'unchanged scene cache verification')

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

for p in psutil.process_iter(['cmdline']):
    command = ' '.join(p.info['cmdline'] or [])
    if 'incremental-render.py' in command and slug in command:
        raise SystemExit('Finish the current incremental render before updating its receipts.')

baseline = (ROOT / args.baseline).resolve()
assert baseline.is_relative_to(ROOT / 'shared/output' / slug / 'spoken-clarity')
current = Path(__file__).parent / 'lessons' / (slug + '.json')
old, new = read(baseline / current.name), read(current)
old_scenes = {s['id']: s for s in old.pop('scenes')}
new_scenes = {s['id']: s for s in new.pop('scenes')}
assert old == new and old_scenes.keys() == new_scenes.keys(), 'Global lesson inputs changed'
work = ROOT / 'shared/output' / slug
receipt_path = work / 'render-receipts.json'
receipts = read(receipt_path)
manifest = read(ROOT / 'projects' / slug / 'project.json')
source = ROOT / manifest['paths']['sharedManimLesson']
unchanged, changed = [], []
for sid, scene in new_scenes.items():
    if scene['kind'] != 'explanation':
        continue
    if old_scenes[sid] != scene:
        changed.append(sid)
        continue
    r = receipts[sid]
    assert r['dataSha256'] == sha(baseline / current.name)
    assert r['lessonSha256'] == sha(source)
    assert r['helperSha256'] == sha(source.parent / 'lesson.py')
    assert r['stubSha256'] == sha(ROOT / f'manim/projects/{slug}/scene.py')
    assert r['voiceSha256'] == sha(ROOT / manifest['tts']['outputDir'] / 'chunks' / (sid + '-scene.wav'))
    assert all(sha(ROOT / p) == value for p, value in r.get('dependencySha256', {}).items())
    assert (work / f'manim/videos/scene/1080p60/Scene{sid}.mp4').exists()
    unchanged.append(sid)
shutil.copy2(receipt_path, baseline / 'render-receipts-before-unchanged-cache-verification.json')
for sid in unchanged:
    receipts[sid]['dataSha256'] = sha(current)
    receipts[sid]['unchangedSceneVerification'] = dict(
        baseline=args.baseline, sceneDataSha256=hashlib.sha256(json.dumps(new_scenes[sid], sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
        verifiedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
receipt_path.write_text(json.dumps(receipts, indent=2) + '\n', encoding='utf-8')
proof = dict(status='unchanged-complete-scene-data-and-render-inputs-verified',
             unchanged=unchanged, changedRequireRender=changed, baseline=args.baseline,
             beforeLessonSha256=sha(baseline / current.name), afterLessonSha256=sha(current))
(ROOT / 'projects' / slug / 'production/unchanged-scene-cache-review.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
print(json.dumps(proof))

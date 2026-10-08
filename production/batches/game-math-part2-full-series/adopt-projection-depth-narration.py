"""Adopt unchanged full-chapter takes with exact script, voice and cache proof.

This is a CPU file operation, not new synthesis or listening approval.
Scene04's historical take is only a preserved replacement baseline.
"""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import sys
import numpy as np
import soundfile as sf
from production_control import require_current_authorization

ROOT = Path(__file__).resolve().parents[3]
BATCH = Path(__file__).parent
SLUG = 'game-math-projection-depth'
require_current_authorization(SLUG, 'verified unchanged narration adoption')
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
write = lambda p, v: p.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
baseline = ROOT / 'shared/output/game-math-camera-projection/before-conceptual-episode-refinement'
lesson = read(BATCH / f'lessons/{SLUG}.json')
manifest = read(ROOT / f'projects/{SLUG}/project.json')
old_manifest = read(baseline / 'project.json')
old_script = {s['id']: s for s in read(baseline / 'narration.ko.json')['scenes']}
current_script = {s['id']: s for s in read(ROOT / manifest['paths']['script'])['scenes']}
voice_keys = ['model', 'reference', 'referenceText', 'language', 'renderMode',
              'tailRatioThreshold', 'tailDecayMsThreshold', 'edgeFadeSeconds']
assert all(manifest['tts'].get(k) == old_manifest['tts'].get(k) for k in voice_keys)
out = ROOT / manifest['tts']['outputDir']
assert out.resolve().is_relative_to((ROOT / 'shared/output/narration' / SLUG).resolve())
(out / 'chunks').mkdir(parents=True, exist_ok=True)
(out / 'asr').mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / 'qwen3-tts'))
import render_narration as renderer
renderer.np = np
renderer.sf = sf
renderer.configure_project(SLUG)
records = []
for sid, prepared in lesson['preparedNarration'].items():
    old_sid = prepared['scene']
    source = ROOT / prepared['baselineWave']
    assert source.resolve().parent == baseline.resolve()
    assert sha(source) == prepared['wavSha256']
    target = out / 'chunks' / f'{sid}-scene.wav'
    replacement = prepared['requiresNewWave']
    if not replacement:
        assert current_script[sid]['lines'] == old_script[old_sid]['lines']
        assert not renderer.needs_render(source), f'Unchanged scene{sid} needs an ending repair'
    if target.exists():
        if replacement and sha(target) != prepared['wavSha256']:
            repair = read(ROOT / f'shared/output/{SLUG}/line-repair-{sid}/provenance.json')
            assert repair['sha256'] == sha(target), 'Preserve and inspect an unexplained replacement'
        else:
            assert sha(target) == prepared['wavSha256'], 'Do not overwrite a different current take'
    else:
        shutil.copy2(source, target)
    raw_path = baseline / f'{old_sid}.asr.json'
    raw = read(raw_path)
    assert raw['audio_sha256'] == sha(source)
    cache_path = None
    if not replacement:
        cache_path = out / 'asr' / f'{sid}.json'
        renamed = {**raw, 'scene': sid}
        if cache_path.exists():
            assert read(cache_path) == renamed
        else:
            write(cache_path, renamed)
    samples, sr = sf.read(source, dtype='float32')
    records.append(dict(scene=sid, sourceScene=old_sid,
                        baselineWave=source.relative_to(ROOT).as_posix(), baselineWaveSha256=sha(source),
                        targetWave=target.relative_to(ROOT).as_posix(), currentWaveSha256=sha(target),
                        baselineRawAsr=raw_path.relative_to(ROOT).as_posix(), baselineRawAsrSha256=sha(raw_path),
                        adoptedRawAsr=cache_path.relative_to(ROOT).as_posix() if cache_path else None,
                        exactScriptLinesUnchanged=not replacement, replacementRequired=replacement,
                        seconds=len(samples)/sr, rawCacheTransformation='Scene identifier only; recognized text and every word timestamp unchanged' if cache_path else None))
proof = dict(status='eight-unchanged-takes-adopted-with-text-voice-and-hash-proof',
             recordedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
             voiceSettingsCompared=voice_keys, records=records, humanListening='pending',
             currentMeaningNumberReview='pending-direct-full-raw-comparison',
             newSynthesisScenes=['01', '04'])
destination = ROOT / f'projects/{SLUG}/production/narration-adoption.json'
destination.parent.mkdir(parents=True, exist_ok=True)
write(destination, proof)
review = read(BATCH / 'preflight/projection-depth-baseline-raw-review.json')
assert review['status'] == 'eight-preserved-takes-full-current-script-and-raw-review-passed'
mapped_rows = []
for row in review['scenes']:
    sid = row['scene']
    raw_file = out / 'asr' / f'{sid}.json'
    raw = read(raw_file)
    assert row['wavSha256'] == sha(out / 'chunks' / f'{sid}-scene.wav') == raw['audio_sha256']
    assert row['expected'] == ' '.join(current_script[sid]['lines']) and row['recognized'] == raw['text']
    mapped_rows.append({**row, 'rawAsrSha256': sha(raw_file),
                        'adoptedEvidence': 'Recognized text and timestamps unchanged; scene ID remapped with baseline proof.'})
current_review = destination.with_name('narration-review-in-progress.json')
if not current_review.exists():
    write(current_review, dict(status='partial-direct-script-and-raw-ASR-review',
          humanListening='pending', reviewedAt=review['recordedAtUtc'], scenes=mapped_rows,
          pendingScenes=['01', '04'], baselineReview=(BATCH / 'preflight/projection-depth-baseline-raw-review.json').relative_to(ROOT).as_posix()))
tail_proof = ROOT / review['scene09IndependentTailReadback']['path']
assert sha(tail_proof) == review['scene09IndependentTailReadback']['sha256']
tail = read(tail_proof)
tail.update(scene='09', preparedSourceScene='23', preservedBaselineProof=tail_proof.relative_to(ROOT).as_posix())
write(destination.with_name('scene09-tail-readback.json'), tail)
print(json.dumps(dict(slug=SLUG, unchangedTakes=8, replacementBaselinePreserved='04', newSynthesis=['01','04'])))

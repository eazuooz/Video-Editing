"""Verify current-ASR PCM windows and preserve the existing sample-placement proof."""
import os
os.environ['OMP_NUM_THREADS'] = '2'
os.environ['MKL_NUM_THREADS'] = '2'
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT = Path(__file__).resolve().parents[3]
P = ROOT / 'projects/game-lighting-history-04/production'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h = hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024), b''): h.update(b)
 return h.hexdigest()
execution = read(P / 'part3-final-mixed-asr-execution-v147.json')
request = read(P / 'part3-final-mixed-asr-request-v147.json')
assert execution['status'] == 'complete' and execution['exitCode'] == 0
assert len(execution['results']) == len(request['windows']) == 23
additionalExecution = read(P / 'part3-artifact-context-execution-v152.json')
assert additionalExecution['status'] == 'complete' and additionalExecution['exitCode'] == 0
additionalRequest = read(P / 'part3-artifact-context-request-v152.json')
assert len(additionalExecution['results']) == len(additionalRequest['windows']) == 5
planPath = P / 'part3-final-input-plan-v145.json'; plan = read(planPath)
settingsPath = P / 'part3-final-mix-settings-v146.json'; settings = read(settingsPath)
placementPath = P / 'part3-final-pcm-preservation-v146.json'; placement = read(placementPath)
assert sha(placementPath) == settings['pcmProofSha256']
assert placement['planSha256'] == sha(planPath) == settings['planSha256'] == execution['planSha256']
assert placement['allOriginalChapterSamplesPartitionedOnce'] and placement['allSelectedPcmValuesExact'] and placement['roundTripExact']
assert sha(ROOT / placement['path']) == placement['sha256'] == settings['voiceSha256']
mix = ROOT / settings['wav']; assert sha(mix) == settings['wavSha256'] == execution['mixSha256']
target = P / 'part3-current-mix-pcm-corroboration-v147.json'
assert not target.exists(), 'Preserve prior verification'
import numpy as np, soundfile as sf
checks = []
with sf.SoundFile(mix) as f:
 assert f.samplerate == 48000 and f.channels == 2 and f.frames == plan['finalFrames'] * 800
 for row in execution['results'] + additionalExecution['results']:
  resultPath = ROOT / row['path']; assert sha(resultPath) == row['sha256']
  d = read(resultPath); w = d['window']
  assert d['mixSha256'] == settings['wavSha256'] and d['planSha256'] == sha(planPath)
  wave = resultPath.with_suffix('.wav'); assert sha(wave) == d['windowSha256']
  f.seek(w['fromFrame'] * 800)
  expected = f.read((w['toFrame'] - w['fromFrame']) * 800, dtype='float32', always_2d=True).mean(axis=1)
  actual, rate = sf.read(wave, dtype='float32')
  assert rate == 48000 and len(actual) == d['sourceSamples'] == len(expected)
  assert np.array_equal(actual, expected), row['label']
  checks.append({'label': row['label'], 'windowSha256': d['windowSha256'], 'resultSha256': row['sha256'],
    'fromFrame': w['fromFrame'], 'toFrame': w['toFrame'], 'samples': len(actual), 'allMonoMeanSamplesExact': True})
assert sha(mix) == settings['wavSha256']
proof = {'verifiedAt': datetime.now(timezone.utc).isoformat(), 'planSha256': sha(planPath),
 'currentMixSha256': settings['wavSha256'], 'settingsSha256': sha(settingsPath),
 'preservedOriginalPcmProof': {'path': placementPath.relative_to(ROOT).as_posix(), 'sha256': sha(placementPath)},
 'allOriginalChapterSamplesPartitionedOnce': True, 'allSelectedPcmValuesExact': True,
 'all23RecognitionWindowsCurrentMixExact': True, 'windows': checks,
 'allAdditionalArtifactContextsCurrentMixExact': True,
 'additionalWindowCount': len(additionalExecution['results']),
 'recognitionArtifactsAreNotAutomaticallyAccepted': True, 'finalMixedAsrApproved': False,
 'humanWholeListening': 'pending', 'humanPronunciation': 'pending', 'newMedia': 0}
target.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps({'currentWindowsExact': len(checks), 'newMedia': 0, 'approved': False}))

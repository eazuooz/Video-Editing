"""Place approved current scene PCM at measured starts without resynthesis or shortening."""
from pathlib import Path
import hashlib, json
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'projects/hierarchical-game-outlines'
WORK = BASE / 'production/final-v1'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
plan = read(WORK / 'plan.json')
voice = read(BASE / 'production/voice-approval-v2.json')
assert voice['allCurrentScenesTechnicallyReviewed'] and voice['unchangedPcmVerified']
assert plan['finalSourceTimingApproved'] and plan['actualFootageMeasuredAndApproved']
output = WORK / 'narration-timed-body.wav'
proof_path = WORK / 'narration-timed-body-proof.json'
assert not output.exists() and not proof_path.exists(), 'Inspect existing timed PCM; do not overwrite.'
pieces, rows, position = [], [], 0
for scene in plan['scenes']:
    path = ROOT / scene['voice']
    assert sha(path) == scene['audioSha256']
    pcm, rate = sf.read(path, dtype='int16')
    assert rate == 24000 and pcm.ndim == 1
    assert scene['startFrame'] - plan['introFrames'] == position // 400
    target = scene['frames'] * 400
    assert target >= len(pcm)
    placed = np.concatenate([pcm, np.zeros(target - len(pcm), dtype=np.int16)])
    assert np.array_equal(pcm, placed[:len(pcm)])
    pieces.append(placed)
    rows.append({'scene': scene['id'], 'source': scene['voice'], 'sourceSha256': sha(path),
                 'sourceSamples': len(pcm), 'bodyFromSample': position, 'placedSamples': target,
                 'editorialTailSilenceSamples': target - len(pcm), 'allSourcePcmIdentical': True,
                 'observationPurpose': scene.get('observationPurpose', 'Retained explanation read/pause'),
                 'explanationNotShortened': scene['classification'] != 'explanation' or
                                           target >= scene['voiceFrames'] * 400 + 43 * 400})
    position += target
body = np.concatenate(pieces)
assert len(body) == plan['bodyFrames'] * 400
sf.write(output, body, 24000, subtype='PCM_16')
decoded, rate = sf.read(output, dtype='int16')
assert rate == 24000 and np.array_equal(body, decoded)
proof = {'bodySeconds': len(body) / rate, 'bodyFrames': plan['bodyFrames'], 'sampleRate': rate,
         'all12ScenePcmIdentical': True, 'unchangedParagraphs': 54, 'sourceSpeechNotPaddedToRepairAnError': True,
         'tailPolicy': 'Approved chapter gaps and reviewed normal-speed continuing-action observation; no source looping or slowdown.',
         'scenes': rows, 'file': output.relative_to(ROOT).as_posix(), 'sha256': sha(output),
         'humanListening': 'pending', 'finalMixApproved': False}
proof_path.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
plan['timedBodyNarration'] = proof['file']
plan['timedBodyNarrationSha256'] = proof['sha256']
(WORK / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'seconds': proof['bodySeconds'], 'all12ScenePcmIdentical': True, 'sha256': proof['sha256']}))

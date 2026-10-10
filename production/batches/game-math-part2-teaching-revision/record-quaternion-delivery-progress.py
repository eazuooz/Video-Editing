"""Reconcile observed browser playback and collected files without implying publication QA."""
from pathlib import Path
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf8'))
def write(p, data): p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
proof_path = ROOT/'shared/output/game-math-part2-teaching-revision/studio-quaternion/current-final-native-playback.json'
proof = read(proof_path)
slugs = ['game-math-quaternion-calculations-v2', 'game-math-quaternion-foundations-v2']
observations = []
for slug, snapshot in zip(slugs, proof['snapshots']):
    p = ROOT/'projects'/slug
    review = read(p/'production/current-pixel-review.json')
    assert slug in snapshot['src'] and review['sha256'][:16] in snapshot['src']
    assert snapshot['ended'] and snapshot['paused'] and snapshot['playbackRate'] == 1
    assert snapshot['currentTime'] == snapshot['duration']
    for ending in ['captioned.mp4', 'clean.mp4', 'ko.srt', 'en.srt']:
        assert (ROOT/'output'/slug/f'{slug}.{ending}').stat().st_size > 0
    receipt = read(p/'publishing/youtube-upload.json')
    assert receipt['video']['sha256'] == review['sha256']
    review['currentWholeNativePlayback'] = {**snapshot, 'observedAt': proof['observedAt'], 'proof': str(proof_path.relative_to(ROOT)).replace('\\','/'), 'humanListeningApproved': False}
    review['localDeliveryCollected'] = True
    review['actualUploadId'] = receipt['videoId']
    review['platformComplete'] = False
    write(p/'production/current-pixel-review.json', review)
    observations.append({'slug': slug, 'sha256': review['sha256'], **snapshot, 'actualUploadId': receipt['videoId'], 'platformComplete': False})
history = read(B/'quaternion-native-review-history.json')
history['currentFinalWholePlaybackObservations'] = observations
history['nextRequiredPixelReview'] = 'Uploaded YouTube player with CC off; the current final local file and all selectively changed scenes have been directly reviewed.'
history['platformMutation'] = True
write(B/'quaternion-native-review-history.json', history)
queue = read(B/'queue.json')
item = queue['items'][0]
item['revision']['localOutputsCollected'] = True
item['revision']['videoIds'] = [read(ROOT/'projects'/s/'publishing/youtube-upload.json')['videoId'] for s in reversed(slugs)]
item['revision']['wholeNativePlaybackComplete'] = True
item['revision']['privateUploadComplete'] = False
queue['execution']['stage'] = 'Both quaternion deliveries collected and current whole1x playback ended; two actual private drafts uploading; platform QA/settings pending'
queue['studioEvidence']['platformMutations'] = True
queue['updatedAt'] = datetime.now(timezone.utc).isoformat()
write(B/'queue.json', queue)
print(json.dumps({'localCollected': slugs, 'wholeNativePlaybackEnded': True, 'actualDraftIds': item['revision']['videoIds'], 'privateUploadComplete': False}, ensure_ascii=False))

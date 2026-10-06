"""Seal the user's pause after the current lecture's verified private delivery."""
from pathlib import Path
import datetime
import json

batch = Path(__file__).resolve().parent
root = batch.parents[2]
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
write = lambda p, v: p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
queue_path = batch / 'queue.json'
queue = read(queue_path)
control = queue['executionControl']
assert control['mode'] == 'finish-current-video-then-pause'
assert control['nextVideoMayStart'] is False
slug = control['currentVideo']
item = next(x for x in queue['items'] if x['slug'] == slug)
receipt = read(root / f'projects/{slug}/publishing/youtube-upload.json')
assert item['renderComplete'] and item['privateUploadComplete']
assert item['fullPublishingSettingsComplete']
assert receipt['uploadTransferComplete'] and receipt['fullSettingsVerified']
assert receipt['metadata']['privacyStatus'] == 'private'
assert receipt['status'] == 'private-upload-saved-and-settings-verified'
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
remaining = [x['slug'] for x in queue['items'] if x['order'] > item['order']]
control.update(mode='paused', pausedAtUtc=now, completedVideo=slug,
               completedPrivateUrl=receipt['url'], preservedRemainingLectures=remaining,
               resumeRequiresLaterUserInstruction=True,
               finalProductionGpuJobsRunning=False,
               resourceHoldPreserved='shared/output/GPU_TTS_HOLD.json',
               checkpoint='Current lecture render, QA, collection and private settings finished. Next lectures remain paused; preserve prepared scripts, voice clips and lookdev. No automatic production resume.')
queue['checkpointAt'] = now
if queue.get('latestRequest', {}).get('evidence') != control['instruction']:
    queue.setdefault('requestHistory', []).append(queue['latestRequest'])
queue['latestRequest'] = {
    'at': control['userRequestedAt'], 'evidence': control['instruction'],
    'scope': 'Finish only the current lecture, then pause all remaining PART2 production to prioritize paper experiments. Preserve prepared work; resume only on a later explicit user instruction.',
}
write(queue_path, queue)
write(batch / 'research/production-pause-request.json', control)
print(json.dumps({'mode': 'paused', 'completedVideo': slug,
                  'privateUrl': receipt['url'], 'remainingPreserved': len(remaining)}))

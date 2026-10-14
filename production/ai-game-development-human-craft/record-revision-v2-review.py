"""Reconcile only the current v2 evidence; retain v1 and human review boundaries."""
from pathlib import Path
import datetime, hashlib, json
from revision_paths import workroot

ROOT = Path(__file__).resolve().parents[2]
SLUG = 'ai-game-development-human-craft'
P = ROOT / 'projects' / SLUG
O = workroot(ROOT)
BASE = O.relative_to(ROOT).as_posix()

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p, x): p.write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
m = read(P / 'project.json')
assert m['revision']['id'] == 'v2'
control_path = ROOT / 'shared/publishing/video-production-control.json'
control = read(control_path)
assert control['selectedVideo'] == SLUG
integrity = read(O / 'encoded-integrity.json')
motion = read(O / 'encoded-motion-review/review.json')
captions = read(O / 'caption-pixel-qa/report.json')
ratio = read(O / 'screen-role-measurement.json')
audio = read(O / 'audio/level-continuity.json')
asr = read(O / 'audio/final-asr/complete-readback.json')
narration = read(O / 'narration-assembly.json')
joins = read(O / 'speech-joins.json')
files = read(O / 'four-file-verification.json')
assert captions['status'] == files['status'] == ratio['status'] == 'pass'
assert audio['processingAttenuationStatus'] == 'pass'
assert all(x['fullVideoDecode'] == x['fullAudioDecode'] == x['pts'] == 'pass' for x in integrity['outputs'])
assert motion['status'] == 'pass-agent-scoped-visual-review'
assert motion['movieSha256'] == integrity['outputs'][1]['sha256']
assert asr['fullTextReview'].startswith('pass') and narration['fullTextReview'].startswith('pass')
assert joins.get('reviewStatus', '').startswith('reviewed'), 'Review current pause/word flags before delivery'
delivery = read(O / 'drive-final-v2-delivery.json')
mobile = read(ROOT / delivery['qualityEvidence'])
assert mobile['status'] == 'pass-agent-mobile-review-copy'
assert delivery['sourceMasterSha256'] == mobile['sourceSha256'] == motion['movieSha256']
assert delivery['localSha256'] == mobile['localSha256'] == sha(ROOT / delivery['localPath'])
assert delivery['sizeBytes'] == mobile['sizeBytes'] < 100 * 1024 * 1024
assert mobile['fullVideoAudioDecode'] == mobile['pts'] == 'pass'
assert mobile['frames'] * 2 == integrity['outputs'][1]['frames']
assert delivery['fileId'] and delivery['accessStatus'] == 'verified-owner-only'
assert delivery['remoteSha256'] == delivery['localSha256'], 'Verify the actual uploaded bytes'

ledger = read(P / 'production/review-ledger.json')
def check(id, **fields):
    row = next((x for x in ledger['checks'] if x['id'] == id), None)
    if row is None:
        row = {'id': id}; ledger['checks'].append(row)
    elif row.get('revision') != 'v2':
        ledger.setdefault('priorRevisionChecks', []).append(dict(row))
        row.clear(); row['id'] = id
    row.update(revision='v2', reviewedAt=now, **fields)

check('whole-video-delivery', status='pass-local-four-files; full-mobile-review-delivered',
      scope='Complete current clean/captioned/KO/EN and private mobile review copy. Human listening/review pending; publication uses a separately approved master.',
      files=files['files'], drive=delivery)
check('standalone-narration-v1', status='pass-current-script-and-readback',
      scope='Source/adaptation framing removed from active spoken text, captions and scene text; required credits and internal provenance retained. Third-party biography is not asserted as our own.',
      evidence=[f'{BASE}/narration-assembly.json', f'{BASE}/audio/final-asr/complete-readback.json'])
check('full-narration-production', status='complete-human-listening-pending',
      sourceSha256=audio['sourceSha256'], evidence=f'{BASE}/narration-assembly.json',
      scope='Current complete readback reviewed, identical retained PCM evidence reused only by hash; no ASR result is a human listening pass.')
check('natural-narration-joins-v1', status=joins['reviewStatus'], evidence=f'{BASE}/speech-joins.json', humanListening='pending')
check('first-word-listening-followup', status='revised-complete-readback; human-listening-pending',
      scope='Opening and scene03 complete contexts regenerated and compared with current text; v1 first-word concern superseded by current evidence.',
      evidence=[f'{BASE}/narration-assembly.json', f'{BASE}/audio/final-asr/complete-readback.json'])
check('full-composite-visual-qa', status=motion['status'], evidence=f'{BASE}/encoded-motion-review/review.json',
      movieSha256=motion['movieSha256'], frames=motion['frames'], scope=motion['method'], humanFullPlayback='pending')
check('final-caption-pixels', status='pass', evidence=f'{BASE}/caption-pixel-qa/report.json', movieSha256=motion['movieSha256'])
check('v2-caption-alignment-preflight', status='pass-current343cues; current-final-encoded-pixels-pass',
      evidence=[f'{BASE}/caption-data-compatibility.json', f'{BASE}/caption-pixel-qa/report.json'],
      scope='Current bilingual cue timing and unchanged clean visual data verified; final caption pixels subsequently passed all343 cues.')
check('final-encoded-integrity', status='pass', evidence=f'{BASE}/encoded-integrity.json', outputs=integrity['outputs'], captions=integrity['captions'])
check('narration-level-continuity', status='pass-measured-processing; source-prosody-listening-pending',
      evidence=f'{BASE}/audio/level-continuity.json', sourceSha256=audio['sourceSha256'],
      stemSha256=audio['stemSha256'], finalSha256=audio['finalSha256'], humanListening='pending')
check('actual-footage-60-v2', status='pass-measured-current-output', evidence=f'{BASE}/screen-role-measurement.json',
      actualShare=ratio['actualShare'], actualFrames=ratio['actualFrames'], bodyFrames=ratio['bodyFrames'],
      scope='Unique native-speed independent development/craft/history/game cuts; self-authored Unity remains explanation.')

checkpoint = read(P / 'production/checkpoint.json')
plan = read(P / 'planning/production-plan.json')
next_action = 'User reviews complete v2 Drive video and listens to the revised narration. Preserve v1 and1080p60 masters. No YouTube upload or next video before user instruction.'
for obj, key in [(ledger, 'finalDriveReview'), (checkpoint, 'finalReviewDelivery'), (plan, 'finalReviewDelivery'), (control, 'finalReviewDelivery')]:
    prior = obj.get(key)
    if prior and prior.get('fileId') and prior.get('fileId') != delivery['fileId']:
        history = obj.setdefault(key+'History', [])
        if not any(x.get('fileId') == prior['fileId'] for x in history): history.append(prior)
    obj[key] = delivery
checkpoint.update(updatedAt=now, stage='drive-review-delivered-awaiting-user', activeJobs=[],
                  pending=['Human complete-v2 review and listening before YouTube'], nextAction=next_action,
                  finalGitReceipt=f'{BASE}/git-final-delivery/committed.json')
prior_recovery = checkpoint.get('narrationRecovery')
if prior_recovery and prior_recovery.get('sourceSha256') != narration['sourceSha256']:
    checkpoint.setdefault('priorNarrationRecovery', []).append(prior_recovery)
checkpoint['narrationRecovery'] = {
    'current': 'v2 complete;23 revised scene takes and5 byte-identical retained takes; full raw and encoded readback reviewed',
    'sourceSha256': narration['sourceSha256'], 'researchPaused': False, 'activeLease': None,
    'humanListening': 'pending', 'evidence': f'{BASE}/narration-assembly.json'}
checkpoint['driveDestinationReadback'].update(finalFileId=delivery['fileId'], observedAt=now)
checkpoint['gitDelivery'] = {'status': 'consult-final-operation-receipt', 'receipt': checkpoint['finalGitReceipt'],
                            'rule': 'Only actual commit and remote SHA confirm delivery; no future self-SHA is embedded.'}
for item in ['v2 standalone narration and complete current readbacks reviewed', 'v2 four outputs and current encoded QA complete', 'v2 private Drive upload and complete remote byte verification complete; v1 retained']:
    if item not in checkpoint['completed']: checkpoint['completed'].append(item)
plan.update(status=checkpoint['stage'], nextAction=next_action)
plan['approvals']['finalDriveUserReview'].update(status='pending-user-review', fileId=delivery['fileId'], version='v2', sha256=delivery['localSha256'])
m.update(status=checkpoint['stage'], publishReady=False)
m['delivery']['driveReview'] = delivery
m['revision']['status'] = 'delivered-awaiting-user-review'
ledger.update(updatedAt=now, activeRevision='v2')
control['updatedAt'] = now
# Canonical output now contains v2. Keep old review records pointing at the
# preserved v1 master instead of silently pointing them at the replacement.
old_sha = 'ab8915aa1b62655335e60f69c897787b9ac55e1857666276da9f2ebf611d4efc'
archives = sorted((P/'production/delivery-history').glob(f'*/{SLUG}.captioned.mp4'), reverse=True)
old_master = next((p for p in archives if sha(p) == old_sha), None)
assert old_master is not None, 'Preserved v1 master must remain available'
def repair_historical_pointer(obj):
    if isinstance(obj, dict):
        if obj.get('sourceMasterSha256') == old_sha and 'sourceMasterPath' in obj:
            obj.setdefault('sourceMasterPathAtOriginalDelivery', obj['sourceMasterPath'])
            obj['sourceMasterPath'] = old_master.relative_to(ROOT).as_posix()
        for value in obj.values(): repair_historical_pointer(value)
    elif isinstance(obj, list):
        for value in obj: repair_historical_pointer(value)
for obj in [m, ledger, checkpoint, plan, control]: repair_historical_pointer(obj)
for path, obj in [(P/'project.json',m),(P/'production/review-ledger.json',ledger),(P/'production/checkpoint.json',checkpoint),(P/'planning/production-plan.json',plan),(control_path,control)]: write(path,obj)
print(json.dumps({'stage': checkpoint['stage'], 'driveUrl': delivery['url'], 'publishReady': False}))

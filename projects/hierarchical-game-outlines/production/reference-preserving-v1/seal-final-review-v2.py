"""Record the completed direct V2 review and verify its existing artifacts; no render."""
from pathlib import Path
import datetime, hashlib, json
from PIL import Image

P = Path(__file__).resolve().parent
ROOT = P.parents[3]
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

out = P / 'final-direct-review-v2.json'
assert not out.exists(), 'Completed review already recorded'
pixel = read(P / 'final-pixel-plan-v2.json')
technical = read(P / 'final-repair-execution-v2.json')
assert technical['exitCode'] == 0
assert len(pixel['samples']) == 288 and len(pixel['boards']) == 65
for row in pixel['samples'] + pixel['boards']:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']
inherited = [row for row in pixel['samples'] if row['inherited']]
assert len(inherited) == 30
for row in inherited:
    current = Image.open(ROOT / row['path']).convert('RGB').tobytes()
    prior = Image.open(ROOT / row['priorPath']).convert('RGB').tobytes()
    assert current == prior
    assert hashlib.sha256(current).hexdigest() == row['rgbSha256']
pair = [row for row in technical['completed'] if row['stage'] == 'current-technical']
assert len(pair) == 2
for row in pair:
    assert sha(ROOT / row['path']) == row['sha256']
    assert row['decodeExit'] == 0 and row['frames'] == 17140 and row['ptsStep'] == 1500
assert pair[0]['aacPacketSha256'] == pair[1]['aacPacketSha256']
review = {
    'at': now, 'captionedSha256': pixel['captionedSha256'],
    'technicalEvidence': 'final-repair-execution-v2.json',
    'technicalEvidenceSha256': sha(P / 'final-repair-execution-v2.json'),
    'pixelPlan': 'final-pixel-plan-v2.json', 'pixelPlanSha256': sha(P / 'final-pixel-plan-v2.json'),
    'plannedSamplesReviewed': 288, 'newDirectSamplesReviewed': 258,
    'newDirectBoardsReviewed': 65, 'directBoardRange': 'changed-board-001.jpg through changed-board-065.jpg',
    'exactRgbPriorSamplesInherited': 30, 'sampleAndBoardHashesVerified': True,
    'priorReview': 'final-direct-review-v1-held.json',
    'all48CuesAnd21CutsSampled': True,
    'findings': [
        'All 65 changed boards were directly read. Caption first/middle/last and cut-adjacent frames, explanation movements, menu UI, fixed bottom captions and retained member/branding samples are clear within this sampled scope.',
        'At f540 the first gameplay caption is now present; f541/f542 remain continuous. f2688/f2700 are correctly blank between cues and f2708 begins the next cue.',
        'Sound parent/children annotations end at the reviewed f6118/f6119 boundary and are absent when the recording returns to Options. No incorrect Sound label persists over the later menu.',
        'Collapse/expand, same-level move and reparent are visibly differentiated. Word outline is explicitly illustrative/version-dependent; notes-for-self versus document-for-readers and the small-list conclusion remain connected.',
        'Only independent menu/combat recordings are in the cut list. No Sakurai lesson, narrated Direct or stage-demonstration media is used.'
    ],
    'normalPlayback': {
        'priorWhole': read(P / 'final-direct-review-v1-held.json')['normalPlayback'],
        'currentChangedRanges': [
            {'tab': 146, 'startUTC': '2026-10-13T06:22:37.356Z', 'startSeconds': 8.75211, 'endUTC': '2026-10-13T06:22:38.141Z', 'endSeconds': 9.496156, 'rate': 1, 'muted': True, 'boundedEnd': True},
            {'tab': 146, 'startUTC': '2026-10-13T06:23:08.281Z', 'startSeconds': 99.501409, 'endUTC': '2026-10-13T06:23:22.079Z', 'endSeconds': 113.257513, 'rate': 1, 'muted': True, 'boundedEnd': True}
        ],
        'scope': 'Prior full silent normal-speed playback plus current changed-range endpoints; not human listening or a claim to see every intermediate frame.'
    },
    'approvedForPrivateUpload': True, 'allIntermediateFramesReviewed': False,
    'humanFullListening': False, 'exactPronunciationApproved': False, 'publicRightsApproved': False,
    'remaining': ['Human listening/pronunciation, particularly scene06 Word and scene07 wording', 'Menu recording uploader reuse permission and public rights', 'External media backup and previously pending original Nimbus/member sources']
}
write(out, review)
ledger_path = P.parents[1] / 'production/review-ledger.json'
ledger = read(ledger_path)
ledger['updatedAt'] = now
for entry in ledger['entries']:
    if entry.get('check') == 'modern-equivalent-and-source-aligned-script':
        entry['status'] = 'superseded-by-current-records'
        entry['appliesToCurrentReferenceRevision'] = False
for label, filename in [('current-mixed-audio', 'mix-direct-review-v1.json'), ('current-final-pixels-and-technical', out.name)]:
    ledger['entries'].append({'check': label, 'status': 'pass-for-private-editorial-review', 'scopeVersion': 'reference-preserving-v1', 'appliesToCurrentReferenceRevision': True, 'evidence': (P / filename).relative_to(ROOT).as_posix(), 'sha256': sha(P / filename), 'humanFullListening': False, 'publicRightsApproved': False})
ledger['fullProductionComplete'] = True
ledger['privateUploadComplete'] = False
ledger['currentPolicy'] = 'one-video-autonomous-through-private-upload-v1'
write(ledger_path, ledger)
checkpoint = read(P / 'latest-checkpoint.json')
checkpoint.update(updatedAt=now, stage='reviewed-ready-collect-and-private-upload', next='Promote reviewed local manifest, collect four files once, upload current captioned file once privately and save/reopen available settings.', finalReview=out.name, finalDelivery=False)
write(P / 'latest-checkpoint.json', checkpoint)
print(json.dumps({'approvedForPrivateUpload': True, 'plannedSamples': 288, 'newDirectSamples': 258, 'newDirectBoards': 65, 'exactPrior': 30, 'pairHashesVerified': True}))

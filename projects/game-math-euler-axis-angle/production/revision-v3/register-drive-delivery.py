"""Record observed Drive delivery only, preserving old uploads and other work."""
from pathlib import Path
import json, datetime, sys, subprocess

R = Path(__file__).resolve().parents[4]
P = R / 'projects/game-math-euler-axis-angle'
O = P / 'production/local/revision-v3'

def read(p):
    return json.loads(p.read_text(encoding='utf8'))

def save(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

incoming = read(R / sys.argv[1])
control = read(R / 'shared/publishing/video-production-control.json')
assert control['selectedVideo'] == P.name
delivery = read(P / 'production/delivery-output.json')
captioned = next(f for f in delivery['files'] if f['name'].endswith('.captioned.mp4'))
assert incoming['localSha256'] == captioned['sha256']
assert incoming['remoteBytes'] == captioned['bytes']
assert incoming['access']['visibility'] == 'restricted'
assert incoming['humanReview']['status'] == 'pending'
assert incoming['youtube']['uploaded'] is False
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
old = read(P / 'publishing/drive-review.json')
if old['fileId'] != incoming['fileId']:
    incoming['previousVersions'] = [old]
else:
    incoming['previousVersions'] = old.get('previousVersions', [])
incoming.update(recordedAt=now, preservedEarlierVersions=True)
save(P / 'publishing/drive-review.json', incoming)
ready = incoming['playback']['status'] == 'verified'
stage = 'awaiting-human-drive-final-review' if ready else 'drive-upload-complete-playback-processing'
project = read(P / 'project.json')
project.update(status=stage, publishReady=False)
project['publishing']['driveReview'] = 'projects/' + P.name + '/publishing/drive-review.json'
project['publishing']['driveFileId'] = incoming['fileId']
project['publishing']['driveUrl'] = incoming['url']
project['publishing']['youtubeReplacementAuthorized'] = False
project['finalRender']['openItems'] = ['완성본 Drive 사용자 검수 및 전체 청취·발음 확인 대기', '기존 비공개 YouTube 업로드 유지']
save(P / 'project.json', project)
checkpoint = read(P / 'production/checkpoint.json')
pair = read(O / 'pair-source.json')
checkpoint.update(updatedAt=now, stage=stage, runningJob=None,
    nextAction='Wait for user review of the exact complete Drive version; no YouTube or next video.',
    lastCompletedCommit='bc3d55aea5dc98fb568e2be3ce13f4aeaee7e9fb')
checkpoint['currentMaster'].update(outputs=pair['outputs'], status='complete; current integrity and changed visual checks recorded')
checkpoint['annotationSourceReview'] = '25 source-timed guide windows; current final captions and moving native/mobile output reviewed;14-turn clears before jump'
checkpoint['preparedActualScenes'] = ['02','05','08','11','14','17','20','23']
checkpoint['delivery'] = dict(newFinalVideoExists=True, fourOutputs='production/delivery-output.json', driveUploaded=True,
    driveReceipt='publishing/drive-review.json', fileId=incoming['fileId'], url=incoming['url'],
    masterSha256=incoming['localSha256'], playback=incoming['playback']['status'], humanReview='pending', youtubeBaselinePreserved=True)
save(P / 'production/checkpoint.json', checkpoint)
qa = read(P / 'production/qa.json')
qa.update(drive='publishing/drive-review.json', status='internal-technical-and-visual-checks-complete-human-listening-pending')
save(P / 'production/qa.json', qa)
ledger = read(P / 'production/review-ledger.json')
ledger.update(updatedAt=now, currentOutput=qa, currentDriveReview=incoming, humanWholeListening='pending')
save(P / 'production/review-ledger.json', ledger)
plan = read(P / 'planning/production-plan.json')
plan.update(updatedAt=now, status=stage)
plan['selectedRevision']['stage'] = stage
plan['currentProduction']['driveReview'] = 'publishing/drive-review.json'
save(P / 'planning/production-plan.json', plan)
# Read shared documents immediately before writing to preserve unrelated changes.
work = read(R / 'shared/publishing/video-worklist.json')
row = next(v for v in work['rows'] if v['slug'] == P.name)
row.update(productionComplete=True, productionStatus='닌텐도3게임·추가BGM제거 수정본 완료',
    reviewStatus='화면·자막·음성 기술검수 완료 / 전체 청취·발음 검수 대기',
    humanApproval='현재 v3 Drive 완성본 사용자 검수 대기',
    platformStatus='새 v3 Drive 업로드 완료 · 이전 Drive와 비공개 YouTube 유지',
    executionStatus='사용자 최종 검수 대기' if ready else 'Drive 재생 처리 대기',
    localMasterAvailable=True, latestRulesPassed=None)
row['driveReview'] = dict(receipt='publishing/drive-review.json', **{k: incoming[k] for k in
    ['fileId','url','driveRevisionId','localSha256','remoteSha256','remoteBytes','access','playback','humanReview']}, readyForHumanReview=ready)
work['updatedAt'] = now
save(R / 'shared/publishing/video-worklist.json', work)
control = read(R / 'shared/publishing/video-production-control.json')
assert control['selectedVideo'] == P.name
control['selectedDelivery'].update(stage=stage, gpuStatus='All selected finite jobs completed; owned GPU leases released',
    driveReview='projects/' + P.name + '/publishing/drive-review.json', driveId=incoming['fileId'],
    driveRevisionId=incoming['driveRevisionId'], masterSha256=incoming['localSha256'],
    userReview='pending exact v3 complete version', youtubeUploadAuthorized=False, completedAt=now)
control['updatedAt'] = now
save(R / 'shared/publishing/video-production-control.json', control)
subprocess.run([str(R/'qwen3-tts/.venv/Scripts/python.exe'), 'scripts/render-video-worklist.py'], cwd=R, check=True)
print(stage)

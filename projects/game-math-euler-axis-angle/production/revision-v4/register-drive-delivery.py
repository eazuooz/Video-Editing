"""Record observed Drive delivery only, preserving old uploads and other work."""
from pathlib import Path
import json, datetime, sys, subprocess

R = Path(__file__).resolve().parents[4]
P = R / 'projects/game-math-euler-axis-angle'
O = P / 'production/local/revision-v4-clarity'

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
    incoming['previousVersions'] = [old] + incoming.get('previousVersions',[])
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
project['publishing']['driveRevisionId'] = incoming['driveRevisionId']
project['publishing']['driveMasterSha256'] = incoming['localSha256']
project['publishing']['currentRevision'] = 'standard-game-audio-v4'
project['revision']['nextRevision'] = dict(id='standard-game-audio-v4',stage=stage)
project['publishing']['youtubeReplacementAuthorized'] = False
project['finalRender']['openItems'] = ['완성본 Drive 사용자 검수 및 전체 청취·발음 확인 대기', '기존 비공개 YouTube 업로드 유지']
if incoming['playback'].get('highDefinitionProcessing') == 'pending':
    project['finalRender']['openItems'].insert(0, 'Drive1080p 미리보기 변환 대기; 업로드 원본은1920×1080/60fps')
save(P / 'project.json', project)
checkpoint = read(P / 'production/checkpoint.json')
pair = read(O / 'pair-source.json')
checkpoint.update(updatedAt=now, stage=stage, runningJob=None,
    nextAction='Wait for user review of the exact complete Drive version; no YouTube or next video.',
    lastCompletedCommit='5ec3f95cf4b217e0afcd26093388ff78c8b72ceb')
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
row.update(productionComplete=True, productionStatus='게임 원음 일반 기준 복원·추가 BGM만 제거',
    reviewStatus='화면·자막·음성 기술검수 완료 / 전체 청취·발음 검수 대기',
    humanApproval='현재 v4 Drive 완성본 사용자 검수 대기',
    platformStatus='새 v4 Drive 업로드 완료 · 이전 Drive와 비공개 YouTube 유지',
    executionStatus='사용자 최종 검수 대기' if ready else 'Drive 재생 처리 대기',
    localMasterAvailable=True, latestRulesPassed=None)
row['driveReview'] = dict(receipt='publishing/drive-review.json', **{k: incoming[k] for k in
    ['fileId','url','driveRevisionId','localSha256','remoteSha256','remoteBytes','access','playback','humanReview']}, readyForHumanReview=ready)
row['notes']='게임 원음은 일반 제작 기준으로 복원. 따로 추가한 BGM만 제거. 젤다 한 설명 대사의 음성 우선 덕킹. 기존 설명·자막·내레이션 PCM·닌텐도3종·관찰 표시 유지. 원래 무음인 마리오 카트 자료에 소리를 생성하지 않음.'
work['updatedAt'] = now
save(R / 'shared/publishing/video-worklist.json', work)
control = read(R / 'shared/publishing/video-production-control.json')
assert control['selectedVideo'] == P.name
control['selectedDelivery'].update(revision='standard-game-audio-v4', stage=stage, gpuStatus='All selected finite jobs completed; owned GPU leases released',
    driveReview='projects/' + P.name + '/publishing/drive-review.json', driveId=incoming['fileId'],
    driveRevisionId=incoming['driveRevisionId'], masterSha256=incoming['localSha256'],
    userReview='pending exact v4 complete version', youtubeUploadAuthorized=False, completedAt=now)
control['updatedAt'] = now
save(R / 'shared/publishing/video-production-control.json', control)
subprocess.run([str(R/'qwen3-tts/.venv/Scripts/python.exe'), 'scripts/render-video-worklist.py'], cwd=R, check=True)
print(stage)

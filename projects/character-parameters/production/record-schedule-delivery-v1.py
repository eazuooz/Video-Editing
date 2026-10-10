"""Seal observed Studio scheduling after the actual production push; no media or UI work."""
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
BASE = 'projects/character-parameters'
PUB = BASE + '/publishing'
BATCH = 'production/batches/sakurai-planning-game-design'
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def write(p, v): (ROOT/p).write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
def digest(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
now = datetime.now(timezone.utc).isoformat()
git = read(PUB+'/private-delivery-git-verification-v1.json')
assert git['pushed'] and git['exactLocalRemoteMatch'] and git['allRemoteBlobsVerified'] and git['externalIndexUnchanged']
before = read(PUB+'/ui-proof-v1/future-schedules-before.json')
after = read(PUB+'/ui-proof-v1/future-schedules-after.json')
def row_id(r): return r['url'].split('/')[2]
before_ids = {row_id(r): r for r in before['rows']}
after_ids = {row_id(r): r for r in after['rows']}
assert len(before_ids) == 23 and len(after_ids) == 24
assert set(after_ids)-set(before_ids) == {'nic5Sp6dylQ'}
assert all(after_ids[k]['title'] == v['title'] and after_ids[k]['cells'][1:3] == v['cells'][1:3] for k,v in before_ids.items())
assert not any('2026. 10. 30.' in r['cells'][2] for r in before['rows'])
assert after_ids['nic5Sp6dylQ']['cells'][1] == '예약됨' and '2026. 10. 30.' in after_ids['nic5Sp6dylQ']['cells'][2]
ax_path = PUB+'/ui-proof-v1/schedule-reopened.ax.txt'
ax = (ROOT/ax_path).read_text(encoding='utf-8')
assert all(s in ax for s in ['nic5Sp6dylQ','2026. 10. 30.','오전 9:00','GMT+0900','모든 변경사항이 저장되었습니다.'])
image = PUB+'/schedule-reopened-proof-v1.png'
review = dict(schemaVersion=1, slug='character-parameters', actualVideoId='nic5Sp6dylQ', category='game-design', date='2026-10-30', time='09:00', timezone='Asia/Seoul', timezoneOffset='+09:00', publishAt='2026-10-30T00:00:00Z', saved=True, savedReopened=True, status='actual-saved-reopened', premiere=False, verifiedAt=after['observedAt'], evidence=ax_path, evidenceSha256=digest(ax_path), screenshot=image, screenshotSha256=digest(image), preAssignmentInventory=PUB+'/ui-proof-v1/future-schedules-before.json', currentEmptyMatchingSlotVerified=True, original23FutureSchedulesPreserved=True, futureListReaccessed=True, previousHistorical24LedgerEntriesPreserved=True, humanListeningAndRightsRemainIncomplete=True, productionGitCommit=git['commit'])
write(PUB+'/schedule-direct-review-v1.json',review)
ledger_path = 'shared/publishing/daily-alternating-schedule.json'
ledger = read(ledger_path)
assert len(ledger['actualSchedules']) == 24 and not any(x['slug']=='character-parameters' for x in ledger['actualSchedules'])
entry = {k:review[k] for k in ['slug','actualVideoId','category','date','time','timezoneOffset','publishAt','verifiedAt','evidence','evidenceSha256','status']}
entry['videoId']=entry.pop('actualVideoId'); entry['title']='능력치는 어떻게 캐릭터의 개성을 만들까?'; entry['categoryOrder']=11
ledger['actualSchedules'].append(entry); ledger['actualSchedules'].sort(key=lambda x:x['date'])
ledger['pendingTargets']=[x for x in ledger['pendingTargets'] if x['slug']!='character-parameters']; ledger['updatedAt']=now
assert len(ledger['actualSchedules'])==25 and len(ledger['pendingTargets'])==6
write(ledger_path,ledger)
registry_path='shared/git-essential-images.json'; registry=read(registry_path)
assert not any(x['path']==image for x in registry['entries'])
registry['entries'].append(dict(path=image, project='character-parameters', purpose='minimal-publishing-proof', reason='Actual saved and reopened Oct30 09KST schedule with the video title visible.', reviewedAt=now, sha256=digest(image)))
write(registry_path,registry)
ignore=ROOT/'.gitignore'; txt=ignore.read_text(encoding='utf-8-sig')
assert '!'+image not in txt.splitlines()
ignore.write_text(txt.rstrip()+'\n!'+image+'\n',encoding='utf-8',newline='\n')
receipt_path=PUB+'/youtube-upload-v1.json'; receipt=read(receipt_path)
assert receipt['actualVideoId']=='nic5Sp6dylQ' and receipt['fullSettingsVerified'] and receipt['uploadedCcOffPixelsVerified']
receipt.update(status='reviewed-complete-production-git-delivered-and-scheduled-awaiting-evidence-git', privacy='scheduled-publication-private-until-date', scheduled=True, scheduleVerified=True, schedule=review, targetIsPlatformReservation=True, productionGitDelivered=True, productionGitCommit=git['commit'], productionGitVerification=PUB+'/private-delivery-git-verification-v1.json', publishingGitDelivered=False, updatedAt=now)
write(receipt_path,receipt)
project_path=BASE+'/project.json'; project=read(project_path)
project['status']='reviewed-scheduled-awaiting-evidence-git'
project['publishing'].update(scheduleVerified=True, scheduled=True, targetIsPlanOnly=False, actualDate='2026-10-30', actualTime='09:00', scheduleReview=PUB+'/schedule-direct-review-v1.json', productionGitCommit=git['commit'])
write(project_path,project)
checkpoint_path=BASE+'/production/latest-checkpoint.json'; checkpoint=read(checkpoint_path)
checkpoint.update(stage='reviewed-scheduled-awaiting-evidence-git', scheduled=True, scheduleVerified=True, productionGitDelivered=True, productionGitCommit=git['commit'], scheduleReview=PUB+'/schedule-direct-review-v1.json', recordedAt=now, nextAction='Selective scheduling/evidence Git delivery, then limited-color-world full source/content/current Studio duplicate review.')
write(checkpoint_path,checkpoint)
queue_path=BATCH+'/queue.json'; queue=read(queue_path); item=next(x for x in queue['items'] if x['slug']=='character-parameters')
item.update(status='complete', stage='production-git-delivered-and-scheduled-awaiting-evidence-git', scheduled=True, scheduleVerified=True, schedule=review, productionGitCommit=git['commit'], productionGitVerification=PUB+'/private-delivery-git-verification-v1.json', nextAction='Selective scheduling/evidence Git delivery, then next queued limited-color-world.', updatedAt=now)
item['checkpoints'].update(git=True,scheduled=True)
queue.update(nextSlug='limited-color-world',lastProgressAt=now,updatedAt=now)
follow_path='projects/picking-sides/publishing/postpublication-20261010/youtube-pinned-comment-v1.json'; follow=read(follow_path)
assert follow['posted'] and follow['pinned']
follow.update(gitDelivery=True, productionGitCommit=git['commit'], productionGitVerification=PUB+'/private-delivery-git-verification-v1.json'); write(follow_path,follow)
pick=next(x for x in queue['items'] if x['slug']=='picking-sides')
pick['postPublicationFollowup'].update(gitDelivery=True,productionGitCommit=git['commit'])
write(queue_path,queue)
readme=ROOT/BASE/'README.md'; text=readme.read_text(encoding='utf-8-sig')
text=text.replace('선택Git·실제 공개예약은 아직 미완료이며10/30 오전09시 Asia/Seoul은 목표일이다.', '제작 기록482개 최종blob를 실제 production commit `'+git['commit']+'`로 일반push했고 local/remote와 외부index 보존을 확인했다. 현재Studio의23개 미래예약·10/30빈슬롯을 읽은 뒤2026-10-30 오전09:00 Asia/Seoul/GMT+0900 공개예약을 실제 저장·재열람했고, 목록 재접속에서24개 미래예약과 기존23날짜 보존을 확인했다. 예약/evidence 선택Git은 이어서 전달한다.')
readme.write_text(text,encoding='utf-8',newline='\n')
prefix='2026-10-10 current actual delivery: character-parameters nic5Sp6dylQ completed389.95s/23397frames1080p60, all1266samples/211boards,201KO/95EN,49mixed-ASR contexts and four-file collection. All available private settings, SD/HD, copyright/ad checks and uploaded1080p60 CC-off game/black2.5D pixels were saved/reopened. Production '+git['commit']+' was normally pushed with482finalblobs/localremote/externalindex preserved. Actual Oct30 09:00 Asia/Seoul schedule was saved/reopened and the24future rows include the new video while the preceding23dates remain unchanged. Historical ledger25entries/design11lecture14 includes already-published picking-sides; remaining6targets are plans. Picking-sides actual public coaching comment UgynTM-MA24mW_yhUx14AaABAg was posted/pinned once and reopened. Human listening/pronunciation/finalrights/Nimbus/handles/backup/dubbing/optionalCC and character publication comment remain pending. Scheduling/evidence Git is next, then limited-color-world full content/current Studio duplicate preflight. All earlier checkpoints below are preserved history.\n\n'
write(PUB+'/schedule-batch-readme-prefix-v1.json',{'prefix':prefix,'recordedAt':now})
batch_readme=ROOT/BATCH/'README.md'; old=batch_readme.read_text(encoding='utf-8-sig'); batch_readme.write_text(prefix+old,encoding='utf-8',newline='\n')
print(json.dumps({'scheduled':True,'actualId':'nic5Sp6dylQ','historicalLedger':25,'actualFutureRows':24,'pendingTargets':6,'productionCommit':git['commit'],'newEssentialImage':image}))

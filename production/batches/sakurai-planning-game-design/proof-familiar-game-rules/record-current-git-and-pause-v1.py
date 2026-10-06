"""Record an actual successful primary push and the user's requested pause."""
from pathlib import Path
import sys, subprocess, json
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'projects/familiar-game-rules/production'))
from final_cpu_common import read,write,now,PROOF,BASE
BATCH=PROOF.parent
verification=read(PROOF/'final-private-delivery-git-verification.json')
assert verification['pushExitCode']==0 and verification['remoteMatches']
commit=verification['productionCommit']
assert verification['localSha']==verification['remoteSha']==commit
assert verification['foreignIndexEntriesUnchanged'] and not verification['mediaCommitted']
assert verification['newRasterCommitted']==5 and verification['newQaSourceImages']==0
actual_config=Path('C:/Users/eazuo/.codex/automations/24/automation.toml').read_text(encoding='utf-8')
assert 'status = "PAUSED"' in actual_config
stamp=now()
stop=dict(slug='familiar-game-rules',userEvidence='논문 실험 먼저 진행해야 해서 이것까지만 완료되면 일단 정지해줘~',
    policy='Current video delivered; keep automation24 PAUSED. No next queued production, thumbnail retry or GPU work until the user resumes.',
    status='paused-after-current-delivery',completedAt=stamp,nextQueuedStarted=False,
    productionCommit=commit,normalPushVerified=True)
delivery=dict(productionCommit=commit,parent=verification['parent'],pushExitCode=0,
    normalPush=True,forcePush=False,remoteSha=commit,remoteMatches=True,
    verifiedAt=verification['verifiedAt'],evidence='production/batches/sakurai-planning-game-design/proof-familiar-game-rules/final-private-delivery-git-verification.json',
    foreignIndexEntriesUnchanged=True,essentialImages=5,newQaSourceImages=0,mediaCommitted=False,
    availableSettingsVerified=True,fullSettingsVerified=False,thumbnailPending=True,humanReviewsPending=True)
qpath=BATCH/'queue.json';q=read(qpath);i=next(v for v in q['items'] if v['slug']=='familiar-game-rules')
i.update(stage='private-delivery-git-verified-paused',status='uploaded-private-awaiting-user-review',
    updatedAt=stamp,gitDelivery=delivery,stopAfterCurrent=stop,
    nextAction='Paused at user request. Preserve the completed files/private ID; only user resume may authorize thumbnail follow-up or the next queued item.',
    reviewServersStopped='projects/familiar-game-rules/production/final-v1/current-review-servers-stopped-v1.json')
i['checkpoints']['gitDelivery']=True
i['execution'].update(alive=False,status='completed-and-paused',cpuProductionJobs=0,gpuSynthesisJobs=0,uploads=0,
                       activeTasks=[],nextTask='User resume required')
q.update(status='paused-after-current-delivery',updatedAt=stamp,lastProgressAt=stamp,stopAfterCurrent=stop)
q['progress']['productionGitDelivered']=13
q['automation'].update(status='PAUSED',observedAt=stamp,intervalMinutes=30,intervalHours=0.5,
    checkpointPromptVerified='Actual automation24 remains PAUSED; current private production and ordinary Git push complete; ten queued items not started.')
write(qpath,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    c=read(p);c.update({k:i[k] for k in ['stage','status','updatedAt','gitDelivery','stopAfterCurrent','nextAction','execution','reviewServersStopped']});write(p,c)
for p in [ROOT/'projects/familiar-game-rules/project.json',ROOT/'projects/familiar-game-rules/publishing/youtube-upload.json']:
    j=read(p);j.update(gitDelivery=delivery,stopAfterCurrent=stop);write(p,j)
record='\n\n실제 제작 전달 '+commit+'을 origin/main에 일반 푸시하고 local/remote SHA 일치를 확인했다. 명시618경로·최종blob/외부index항목동일·필수이미지5/새QA이미지0/미디어0이며13편 제작Git·비공개전달/12전체게시설정/1썸네일후속·10queued 정지다. 자동화24는PAUSED, 현재검수서버2개는정확명령줄과생성시각을 대조 후 종료했고 논문실험/GPU보류/외부작업을 보존했다. 증거 커밋의 미래 자체SHA는 기록하지 않는다.\n'
for rel in ['projects/familiar-game-rules/README.md','production/batches/sakurai-planning-game-design/README.md','docs/VIDEO_ADDITIVE_REVISION.md']:
    p=ROOT/rel;text=p.read_text(encoding='utf-8-sig');assert commit not in text;p.write_text(text.rstrip()+record,encoding='utf-8')
write(PROOF/'actual-pause-after-current-v1.json',dict(recordedAt=stamp,stopAfterCurrent=stop,
    actualAutomationStatus='PAUSED',actualConfig='C:/Users/eazuo/.codex/automations/24/automation.toml',
    nextQueuedStarted=False,remainingQueued=10,currentOwnedProductionJobs=0,currentOwnedGpuJobs=0,uploads=0,
    productionGitDelivered=13,privateSaved=13,fullSettingsDelivered=12,thumbnailFollowups=1,
    serversStoppedEvidence=i['reviewServersStopped'],foreignPaperGpuJobsPreserved=True))
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/build-rebuild-manifests.cjs','familiar-game-rules'],cwd=ROOT,check=True)
selected=['projects/familiar-game-rules/project.json','projects/familiar-game-rules/rebuild.json',
    'projects/familiar-game-rules/README.md','projects/familiar-game-rules/publishing/youtube-upload.json',
    'projects/familiar-game-rules/production/latest-checkpoint.json','projects/rebuild-index.json',
    'production/batches/sakurai-planning-game-design/queue.json','production/batches/sakurai-planning-game-design/README.md',
    'docs/VIDEO_ADDITIVE_REVISION.md',
    *[(PROOF/name).relative_to(ROOT).as_posix() for name in [
        'latest-checkpoint.json','record-current-git-and-pause-v1.py','actual-pause-after-current-v1.json',
        'final-private-delivery-git-verification.json','final-private-evidence-paths.json','final-private-evidence-prechecks.json']]]
write(PROOF/'final-private-evidence-paths.json',sorted(selected))
print(json.dumps(dict(primaryCommit=commit,automation24='PAUSED',queuedNotStarted=10,evidencePaths=len(selected))))

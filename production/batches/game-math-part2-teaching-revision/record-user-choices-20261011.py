"""Record the exact two user replies after the verified polygon deletion.

No frozen TTS source, existing media, unrelated schedule or staged index edits.
"""
from pathlib import Path
import datetime, hashlib, json

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).parent
Q = B / 'cross-game-review-20261011/quaternion-four-game-v3'
E = ROOT / 'shared/publishing/polygons-four-game-schedule-20261011'
read = lambda p: json.loads(p.read_text(encoding='utf8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
master = ROOT / 'projects/game-math-quaternion-cross-game-additions-v3'
frozen = {str(p.relative_to(ROOT)): sha(p) for p in [master/'project.json', master/'script/narration.ko.json', master/'script/narration.en.json']}
links = ['https://www.youtube.com/watch?v=uWKEJ92486U', 'http://multiverse.spiderlinggames.co.uk/']
approval = dict(recordedAt=now, userAnswer='필수 링크 2개만 추가하고 사용', sourceId='besiege-uWKEJ92486U', sourceSha256='81bb3d5d1e15cf6d60e0e8dd44d986bcd7a4c4898cb64590e6cfee698e5b86c5', requiredDescriptionLinks=links, scope='Only the two mandatory Besiege links in both localized episode descriptions; preserve the channel footer and omit other public source credits.', sourceConditionExceptionAuthorized=True, externalUploadHold=False, sourceAndGameIPHumanReview='pending', descriptionPlatformVerification='pending')
write(Q/'besiege-description-exception-approval.json', approval)
approval_path = str((Q/'besiege-description-exception-approval.json').relative_to(ROOT)).replace('\\','/')

def release(value):
    if isinstance(value, dict):
        if value.get('game') == 'Besiege':
            value.update(descriptionExceptionAuthorized=True, externalUploadHold=False, descriptionExceptionApproval=approval_path)
        if value.get('id') in ['QF30','QC30'] and 'externalUploadHold' in value:
            value.update(externalUploadHold=False, descriptionExceptionApproval=approval_path)
        for v in value.values(): release(v)
    elif isinstance(value, list):
        for v in value: release(v)

for path in [Q/'additions.json', Q/'candidate-comparison.json']:
    value=read(path); release(value); write(path,value)
for episode in ['foundations','calculations']:
    p=ROOT/f'projects/game-math-quaternion-{episode}-v3'
    for rel in ['production/lesson.json','sources/candidate-comparison.json']:
        value=read(p/rel); release(value); write(p/rel,value)
    coverage=read(p/'planning/game-example-coverage.json')
    for game in coverage['games']:
        if game['gameId']=='besiege':
            game.update(sourceConditionChoicePending=False, requiredDescriptionLinks=links, descriptionExceptionApproval=approval_path)
    write(p/'planning/game-example-coverage.json',coverage)
    m=read(p/'project.json')
    m['publishing'].update(pendingBesiegeDescriptionException=False, besiegeDescriptionExceptionApproval=approval_path)
    m['approvals'].update(rights='Besiege mandatory-link exception explicitly authorized; platform link verification and other source/game-IP human review remain pending.', voice='Fourteen additions synthesized; current-hash CPU ASR and math readback checked. Original eighty scenes and PCM retained; human whole listening pending.')
    m['finalRender']['openItems']=[x for x in m['finalRender']['openItems'] if not x.startswith('Resolve Besiege')]
    write(p/'project.json',m)
    outline=p/'planning/outline.md'
    outline.write_text(outline.read_text(encoding='utf8').replace('비시지는 필수 출처 링크 선택이 미완료이므로 외부 업로드를 보류합니다.','비시지는 사용자가 승인한 필수 링크 두 개를 한영 설명란에 넣습니다. 저장·재열기 확인과 최종 영상 검수는 별도로 진행합니다.'),encoding='utf8')

proof=E/'L7SXFwn4i2k-deleted-watch.txt'
assert '업로더가 삭제한 동영상입니다.' in proof.read_text(encoding='utf8')
deletion=dict(videoId='L7SXFwn4i2k', title='게임수학 Part 2 · 기하 기본 요소 ③ 삼각형의 중심과 다각형', userAnswer='기존 L7SXFwn4i2k 영구 삭제 확인', action='YouTube Studio permanent deletion', status='permanently-deleted-with-action-time-user-confirmation', verifiedAt=now, replacementVideoIds=['YgcN8vs0gNo','pfagaQK-xfI'], replacementDates=['2026-11-02T09:00:00+09:00','2026-11-04T09:00:00+09:00'], evidence=str(proof.relative_to(ROOT)).replace('\\','/'), screenshot=str((E/'L7SXFwn4i2k-deleted-watch.png').relative_to(ROOT)).replace('\\','/'), evidenceSha256=sha(proof), platformMessage='업로더가 삭제한 동영상입니다.', historicalProductionPreserved=True)
write(E/'L7SXFwn4i2k-permanent-deletion.json',deletion)
dp=str((E/'L7SXFwn4i2k-permanent-deletion.json').relative_to(ROOT)).replace('\\','/')
q=read(B/'queue.json')
item=next(i for i in q['items'] if i['slug']=='game-math-polygons-triangulation')
item['status']='four-game-two-episode-revisions-reviewed-scheduled-and-Git-delivered; baseline-permanently-deleted-with-user-confirmation'
item['baseline'].update(actualStudioStatus='영구 삭제 완료; 업로더 삭제 메시지 확인', currentScheduleEvidence=dp, permanentlyDeleted=True, deletion=deletion)
item['revision']['baselineDeletionComplete']=True
q['execution'].update(mode='active',stage='quaternion-four-game-current-timing-final-render',besiegeSourceExceptionApproval=approval_path)
write(B/'queue.json',q)
progress=B/'cross-game-review-20261011/polygons-v4-current-progress.json'
v=read(progress);v.update(baselineStatus='permanently deleted with current user confirmation',baselineDeletion=deletion);write(progress,v)
receipt=ROOT/'projects/game-math-polygons-triangulation/publishing/youtube-upload.json'
v=read(receipt);v.update(currentVisibility='permanently-deleted',scheduledAt=None,permanentDeletion=deletion,historicalUploadReceiptPreserved=True);write(receipt,v)
ledger_path=ROOT/'shared/publishing/daily-alternating-schedule.json';ledger=read(ledger_path)
def historical_update(value):
    if isinstance(value,dict):
        if value.get('videoId')=='L7SXFwn4i2k':
            value.update(currentStatus=deletion['status'],deletedAt=now,deletionEvidence=dp)
        for child in value.values(): historical_update(child)
    elif isinstance(value,list):
        for child in value: historical_update(child)
historical_update(ledger);ledger['updatedAt']=now;write(ledger_path,ledger)
assert all(sha(ROOT/p)==digest for p,digest in frozen.items()),'Frozen TTS inputs must stay exact'
write(Q/'user-choices-recorded.json',dict(recordedAt=now,besiegeApproval=approval_path,polygonDeletion=dp,frozenTtsInputsStillExact=frozen,unrelatedSchedulesAndMediaPreserved=True))
print('Recorded exact user choices; polygon deletion verified; Besiege links required; final publishing pending.')

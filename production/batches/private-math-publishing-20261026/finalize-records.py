"""Record observed publishing results without changing any platform state."""
from pathlib import Path
import json, datetime, hashlib, html
R=Path('D:/Github/VideoEditing'); B=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text('utf-8-sig'))
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
c=read(B/'checkpoint.json'); now=datetime.datetime.now(datetime.timezone.utc).isoformat()
assert len(c['entries'])==18
for e in c['entries']:
    assert e['scheduleVerified'] and e['monetization']=='enabled-reopened-verified',e['id']
    assert all(e['metadataReopened'][k] for k in ['koTitle','koDescription','enTitle','enDescription','thumbnail','hd','playlist']),e['id']
    e['status']='scheduled-duplicate-deletion-confirmation-pending'
    e['url']='https://youtu.be/'+e['videoId']
    e['koSrtUploaded']=e.get('koSrtUploaded',bool(e.get('settings',{}).get('koSubtitles')))
    e['pinnedCommentStatus']='prepared-pending-video-publication'
    p=B/'packages'/e['id']/'publishing'; p.mkdir(exist_ok=True)
    (p/'pinned-comment.ko.txt').write_text(e['title']+' 강의에서 직접 계산해 보고 싶은 부분이나 궁금한 점을 댓글로 남겨 주세요.\n\n프로그래밍 1:1 코칭\nhttps://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328\n',encoding='utf8')
    e['packageHashes']={lang:hashlib.sha256(Path(e[key]).read_bytes()).hexdigest() for lang,key in [('ko','descriptionKO'),('en','descriptionEN')]}
c['updatedAt']=now;c['uploadsCompleted']=18;c['uploadsQueued']=0;c['scheduled']=18;c['status']='scheduled-duplicate-deletion-confirmation-pending'
c['scheduleDecision']='Studio DATE report2026-09-27–2026-10-24: Wednesday2371.75 and Thursday2499.25 mean daily channel views, four observations each. Schedule18 at09:00 Asia/Seoul from2026-11-04 to2026-12-31. Existing2026-10-28 reservation preserved. Each date/time/GMT+0900 reopened; all18 also found in final Studio content inventory.'
c['limitations']=['Analytics measure channel daily views, not causal weekday performance or per-video audience retention.','Whole human viewing/listening not inferred from this upload authorization.','Channel-default automatic dubs are unreviewed; KO narration and manual KO/EN subtitles are the verified language deliverables.','Pinned comments remain local until publication.']
c['deletionConfirmation']={'required':True,'confirmed':False,'scopeCount':21,'publicCount':1,'privateCount':20,'reason':'Computer/browser use policy requires action-time confirmation for irreversible deletion. Existing YouTube IDs and per-video comments/metrics cannot be restored by uploading the master again.','state':'all old uploads preserved'}
write(B/'checkpoint.json',c)
intro='# 게임수학 YouTube 업로드·예약 결과\n\n18편 업로드·예약 저장 완료. **2026년11월4일–12월31일, 매주 수·목09:00(한국시간)**.\n\n최근28일 Studio 일별 조회수 평균은 수요일2371.75회, 목요일2499.25회로 가장 낮았다. 요일별4일씩 비교했으며 채널 전체 조회수 기준이다. 이 수치가 새 영상의 성과를 보장하지 않는다. 기존10월28일 예약은 보존했다.\n\n1080p60 captioned 마스터, 한·영 수동 자막, 한·영 제목·설명, 썸네일, Part2 재생목록,00:00 코칭 카드, 마지막10초 엔딩3요소, 수익 사용 설정을 저장했다. 각 영상의 실제 예약 날짜·시간과 고화질 처리를 확인했다. 광고 수익 설정과 플랫폼 자동 심사는 별개로 기록한다.\n\n'
table='| 순서 | 강의 · 새 YouTube 링크 | 예약 공개(KST) | 상태 |\n|---|---|---|---|\n'
for e in c['entries']: table+=f"|{e['id']}|[{e['title']}]({e['url']})|{e['schedule'][:10]} 09:00|예약 저장·재열람 확인|\n"
tail='\n전체 시청·청취를 사람이 완료했다고 기록하지 않는다. 자동 더빙은 별도 미검수이며, 수동 한·영 자막과 한국어 원음 설정을 기준으로 한다. 고정 댓글은 공개 전까지 원문만 준비한다.\n\n## 기존 중복본21편 — 삭제 확인 대기\n\n아래 정확한 영상만 삭제 대상이다. **공개1편·비공개20편 모두 아직 보존 중**이다. 삭제 시 기존 링크, 댓글과 영상별 기록을 원상복구할 수 없다. 다른 강의·쇼츠·예약은 대상이 아니다.\n\n| 기존 ID | 강의 | 기존 길이 | 공개 상태 | 새 버전 |\n|---|---|---|---|---|\n'
for d in c['deletions']:
    e=next(e for e in c['entries'] if e['id']==d['replacedByEpisode'])
    tail+=f"|[{d['videoId']}](https://youtu.be/{d['videoId']})|{d['title']}|{d['oldDuration']}|{d['visibility']}|[{e['id']}]({e['url']})|\n"
tail+='\n삭제는 새 업로드의 설정·예약·Git 기록을 마친 뒤, 영구 삭제 직전 한 번의 명시 확인을 받아 진행한다.\n'
(B/'PROGRESS.md').write_text(intro+table+tail,encoding='utf8')
wpath=R/'shared/publishing/video-worklist.json'; w=read(wpath)
w['privateMathPolish']['publishingRevision']={'batch':B.name,'updatedAt':now,'status':c['status'],'uploaded':18,'scheduled':18,'oldUploadsDeleted':0,'deletionConfirmationPending':21,'progress':str((B/'PROGRESS.md').relative_to(R)).replace('\\','/'),'entries':[dict(id=e['id'],title=e['title'],videoId=e['videoId'],url=e['url'],scheduledAt=e['schedule'],masterSha256=e['sha256'],status=e['status']) for e in c['entries']]}
write(wpath,w)
block='<!-- MATH-PUBLISHING-20261026-START -->\n'+intro+table+'\n기존 중복21편은 영구 삭제 확인 대기. [상세 결과·삭제 대상 목록](../production/batches/private-math-publishing-20261026/PROGRESS.md). 아래 제작·검수 기록은 당시의 이력이며 이번 사용자 지시로 위18편 게시가 승인됐다. 전체 인간 시청을 새로 확인한 것은 아니다.\n<!-- MATH-PUBLISHING-20261026-END -->\n\n'
for name in ['GAME_MATH_PRIVATE_POLISH.md','VIDEO_WORKLIST.md']:
    p=R/'docs'/name;t=p.read_text('utf8');a='<!-- MATH-PUBLISHING-20261026-START -->';z='<!-- MATH-PUBLISHING-20261026-END -->'
    if a in t:t=t.split(a,1)[0]+block+t.split(z,1)[1].lstrip('\n')
    else:t=block+t
    p.write_text(t,encoding='utf8')
print('Recorded18 schedules;21 old uploads retained; worklist updated.')

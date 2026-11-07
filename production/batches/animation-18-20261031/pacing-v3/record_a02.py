from pathlib import Path
import json,datetime,importlib.util,sys,contextlib
R=Path('D:/Github/VideoEditing');H=R/'production/batches/animation-18-20261031/pacing-v3'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
pub=R/'projects/animation-exaggeration/publishing/pacing-v3';ck=R/'projects/animation-exaggeration/production/pacing-v3/checkpoint.json'
now=datetime.datetime.now(datetime.timezone.utc).isoformat();j=read(pub/'upload.json');master=j['master']
j={k:j[k] for k in ['revision','newVideoId','master','userAuthorization','humanReviewOfNewHash','oldVideoId','preserveSchedule','url','thumbnail']}
j.update(state='replacement-scheduled-old-private',youtubeId='VW4Bj-qmIZg',verifiedAt=now,scheduledAt='2026-11-08T08:00:00+09:00',oldVideoAction='schedule-cancelled-and-private',permanentDeletion=False,adSuitabilityBackendVerified=True,adRatingSubmittedBy='user',copyrightCheck='complete-no-issues',adSuitabilityCheck='complete-no-issues',hdProcessing='complete',subtitles={'ko':'uploaded','en-US':'published'},localizedMetadata={'ko':'saved','en-US':'published'},playlist='게임 애니메이션 | 움직임과 타격감의 비밀',endScreen={'state':'saved-reopened','start':'6:30:26','end':'6:40:26','elements':['subscribe','animation-playlist','canonical-coaching-link'],'memberTitleAndIdentitiesClear':True},infoCard={'state':'saved-reopened','start':'00:00','url':'https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328'},pinnedComment='prepared-pending-publication',proofDirectory=pub.relative_to(R).as_posix()+'/proof')
save(pub/'upload.json',j)
(pub/'pinned-comment.ko.txt').write_text('동작을 기본 속도로 먼저 관찰한 뒤, 느리게 보며 어디가 크게 움직이는지 비교해 보세요.\n\n프로그래밍 코칭 안내\nhttps://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328\n','utf-8')
c=read(ck);c['platform']=j;save(ck,c)
save(H/'checkpoint.json',dict(stage='a02-replacement-complete-other17-planning',completed=['A02'],remaining=[f'A{i:02d}' for i in range(1,19) if i!=2],platformAuthorizedEpisodes=['A02'],updatedAt=now,platformReceipt=(pub/'upload.json').relative_to(R).as_posix()))
f=R/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py';s=importlib.util.spec_from_file_location('scoped',f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
W='shared/publishing/video-worklist.json';D='docs/VIDEO_WORKLIST.md';C='shared/publishing/video-production-control.json';F='docs/VIDEO_WORKFLOW.md'
fields=dict(productionStatus='기본 속도 약3회 관찰 후 느린 분석 · 6분40초',reviewStatus='1080p60·전체 디코딩·44개 변경 화면 표본 검토 완료; 실제 전체 청취 미확인',platformStatus='수정본 11월8일08시 KST 예약 · 구본 비공개',videoId='VW4Bj-qmIZg',url=j['url'],executionStatus='A02 교체 완료 · 나머지17편 페이싱 수정',updatedAt=now,deliveryLedger=ck.relative_to(R).as_posix(),captionedMasterSha256=master['sha256'])
control=read(R/C)['animationPacingRevision20261107'];control.update(a02PlatformReceipt=(pub/'upload.json').relative_to(R).as_posix(),a02ReplacementComplete=True)
marker='<!-- ANIMATION-PACING-20261107 -->';addition=(R/F).read_text('utf-8').split(marker)[1]
def overlay(name,raw,spec):
 if name==C:return m.patch(raw,['animationPacingRevision20261107'],control)
 if name==W:
  index=next(i for i,x in enumerate(m.load(raw)['rows']) if x['id']=='A02')
  for k,v in fields.items():raw=m.patch(raw,['rows',index,k],v)
  return raw
 if name==F:
  text=raw.decode('utf-8-sig');text=text.split(marker)[0].rstrip()+'\n\n'+marker+addition
  return text.encode('utf-8')
 if name==D:
  text=raw.decode('utf-8-sig');lines=text.splitlines(keepends=True)
  for i,line in enumerate(lines):
   if line.startswith('| A02 | '):
    end=line.rfind('|');before=line.rfind('|',0,end);lines[i]=line[:before+1]+' 페이싱 수정본 · 11/8 08시 예약 완료 / 구본 비공개 |\n'
  return ''.join(lines).encode('utf-8')
 raise ValueError(name)
m.SHARED={W,D,C,F};m.overlay=overlay
for name in m.SHARED:(R/name).write_bytes(overlay(name,(R/name).read_bytes(),{}))
paths=[p.relative_to(R).as_posix() for folder in (H,pub,ck.parent) for p in folder.iterdir() if p.is_file() and p.suffix in ('.py','.json','.cjs','.txt')]
paths+=['output/animation-series-review/pacing-v3/index.html']
def validate(spec):
 assert spec['ownedPaths']==sorted(paths)
 assert all((R/name).is_file() for name in paths)
 return sorted(paths)+sorted(m.SHARED)
m.validate=validate;L=H.parent/'local/pacing-v3';spec=L/'a02-commit-spec.json';save(spec,dict(ownedPaths=sorted(paths)))
sys.argv=[str(f),'--spec',str(spec),'--execute','--push','--message','Replace A02 with paced motion review and preserve scheduled release']
with (L/'a02-commit-result.json').open('w',encoding='utf-8') as out,contextlib.redirect_stdout(out):m.main()
r=read(L/'a02-commit-result.json');print({k:r[k] for k in ['status','commit','remoteSha','foreignIndexPreserved']})

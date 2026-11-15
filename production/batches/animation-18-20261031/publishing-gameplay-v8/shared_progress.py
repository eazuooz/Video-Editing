"""Publish only exact per-episode fields, image entries and a marked worklist block."""
from pathlib import Path,PurePosixPath
import importlib.util,json,datetime,hashlib,shutil,sys
ROOT=Path('D:/Github/VideoEditing');HERE=Path(__file__).parent
PREFIX=HERE.relative_to(ROOT).as_posix()+'/'
KEY='animationGameplayPublishing20261115'
C='shared/publishing/video-production-control.json';W='shared/publishing/video-worklist.json';D='docs/VIDEO_WORKLIST.md';I='shared/git-essential-images.json';G='.gitignore'
BEGIN='<!-- ANIMATION-GAMEPLAY-V8-PUBLISHING-20261115 -->';END='<!-- ANIMATION-GAMEPLAY-V8-PUBLISHING-20261115-END -->'
SPEC=HERE/'local/shared-commit-spec.json'
module=importlib.util.spec_from_file_location('publishing_scope',ROOT/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py');scoped=importlib.util.module_from_spec(module);module.loader.exec_module(scoped)
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def overlay(name,raw,data):
 if name==C:return scoped.patch(raw,[KEY],data['control'])
 if name==W:
  for row in data['rows']:
   n=[i for i,x in enumerate(scoped.load(raw)['rows']) if x['id']==row['id']];assert len(n)==1
   for key,value in row['changes'].items():raw=scoped.patch(raw,['rows',n[0],key],value)
  return raw
 if name==D:
  a,z=raw.find(BEGIN.encode()),raw.find(END.encode());assert (a<0)==(z<0)
  nl='\r\n' if b'\r\n' in raw else '\n';block=data['markdown'].replace('\n',nl).encode()
  return raw[:a]+block+raw[z+len(END):] if a>=0 else raw+(nl*2).encode()+block+nl.encode()
 if name==I:
  for entry in data['essentialImages']:raw=scoped.upsert(raw,'entries','path',entry)
  return raw
 if name==G:
  nl=b'\r\n' if b'\r\n' in raw else b'\n';lines=raw.decode('utf-8-sig').splitlines()
  for entry in data['essentialImages']:
   path=entry['path']
   if '!/'+path not in lines and '!'+path not in lines:raw+=(b'' if raw.endswith(b'\n') else nl)+('!/'+path).encode()+nl
  return raw
 raise AssertionError(name)
def validate(data):
 assert data['scope']==KEY and {x['id'] for x in data['rows']}=={f'A{i:02}' for i in range(3,19)}
 for name in data['ownedPaths']:
  p=PurePosixPath(name);assert name.startswith(PREFIX) and '..' not in p.parts and 'local' not in p.parts and '__pycache__' not in p.parts and (p.suffix in {'.json','.py','.md','.txt','.jpg'} or p.name=='.gitignore')
 for entry in data['essentialImages']:assert sha(ROOT/entry['path'])==entry['sha256']
 return sorted(data['ownedPaths'])+sorted(scoped.SHARED)
def prepare():
 manifests=load(HERE/'upload-manifest.json');ledger=load(HERE/'platform-ledger.json');now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();rows=[];images=[];done=[]
 table=[BEGIN,'','## 애니메이션 A03–A18 업로드·예약','','사용자: gameplay-v8 통합 검수 승인. 검수한 captioned FHD60 원본 파일과 해시 동일. 기존 예약 마지막 2026-12-31을 보존하고 2027-01-01부터 매일08:00 Asia/Seoul 배정. 광고 평가도 이번16편은 사용자 명시 위임.','','| 편 | 주제 | 예약 예정(KST) | 실제 상태 | Studio |','|---|---|---|---|---|']
 for m in manifests:
  ep=m['id'];fact=ledger['videos'][ep];scheduled=fact.get('status')=='scheduled-confirmed'
  if scheduled:done.append(ep)
  state='예약 확정' if scheduled else '업로드 완료 · 자막/광고 평가 저장 · 엔딩/카드/예약 진행 대기' if fact.get('adSuitability') else '업로드·제목·썸네일·설명 저장 · 한영 자막/광고 평가/엔딩/카드/예약 대기'
  image=HERE/'thumbnails'/f'{ep}.jpg';image.parent.mkdir(exist_ok=True);shutil.copy2(Path(m['thumbnail']),image);assert sha(image)==m['thumbnailSha256']
  images.append(dict(path=image.relative_to(ROOT).as_posix(),purpose='delivery-thumbnail',reason='Requested YouTube publishing thumbnail; original calico branding,1280x720, headline spelling and320px mobile contact sheet inspected. Native source and generation prompts retained separately.',sha256=sha(image),reviewedAt=now,project=Path(m['master']).name.removesuffix('.captioned.mp4')))
  upload=dict(revision='gameplay-v8',status=fact['status'],videoId=fact['videoId'],url='https://youtu.be/'+fact['videoId'],master=m['master'],captionedMasterSha256=m['masterSha256'],thumbnail=image.relative_to(ROOT).as_posix(),thumbnailSha256=m['thumbnailSha256'],humanApproved=True,plannedSchedule=m['scheduledFor'],actualSchedule=m['scheduledFor'] if scheduled else None,timezone='Asia/Seoul',subtitlesKo=fact.get('subtitlesKo','pending'),subtitlesEn=fact.get('subtitlesEn','pending'),englishMetadata=fact.get('englishMetadata','pending'),adSuitability=fact.get('adSuitability','pending'),endScreen=fact.get('endScreen','pending'),card=fact.get('card','pending'),evidence=(HERE/'platform-ledger.json').relative_to(ROOT).as_posix())
  changes=dict(reviewStatus='gameplay-v8 사용자 검수 승인',humanApproval='현재 통합 검수본 전체 승인 및 동일파일 YouTube 업로드·08시 예약 명시 요청',uploadStarted=True,platformStatus=state,videoId=fact['videoId'],url=upload['url'],executionStatus=fact['status'],captionedMasterSha256=m['masterSha256'],deliveryLedger=upload['evidence'],reviewUrl='http://127.0.0.1:9302/'+ep+'/',updatedAt=now,youtubeUpload=upload)
  rows.append(dict(id=ep,changes=changes));table.append(f'| {ep} | {m["titleKo"].split("|")[0].strip()} | {m["scheduledFor"][:10]} 08:00 | {state} | [열기](https://studio.youtube.com/video/{fact["videoId"]}/edit) |')
  save(HERE/ep/'youtube-upload.json',upload)
 table+=['',f'확정 {len(done)}/16편. 자동 검사/수익 상태와 사용자 검수 승인은 별도 기록. 자동 더빙은 검수하지 않았으며 한영 수동 SRT와 영어 제목·설명만 직접 게시.','',END]
 markdown='\n'.join(table);(HERE/'schedule-review.md').write_text(markdown+'\n',encoding='utf-8')
 control=dict(id=KEY,scope=[m['id'] for m in manifests],humanReviewed=True,youtubeAuthorized=True,schedulingAuthorized=True,driveAuthorized=False,deletionAuthorized=False,advertiserAssessmentAuthorized=True,userEvidence='검수했어~ 좋아. A03~A18 전부 이 버전으로 유튜브에 업로드 / 오전8시 / 전부 너가 제출해줘',status='scheduled-complete' if len(done)==16 else 'upload-complete-scheduling-partial',uploaded=[m['id'] for m in manifests],scheduled=done,pending=[m['id'] for m in manifests if m['id'] not in done],ledger=str((HERE/'platform-ledger.json').relative_to(ROOT)),updatedAt=now)
 owned=sorted(p.relative_to(ROOT).as_posix() for p in HERE.rglob('*') if p.is_file() and 'local' not in p.relative_to(HERE).parts and '__pycache__' not in p.parts and (p.suffix in {'.json','.py','.md','.txt','.jpg'} or p.name=='.gitignore'))
 save(SPEC,dict(scope=KEY,control=control,rows=rows,markdown=markdown,essentialImages=images,ownedPaths=owned));print(json.dumps({'prepared':len(rows),'scheduled':len(done),'pending':control['pending'],'spec':str(SPEC)}))
if __name__=='__main__':
 if sys.argv[1:]==['--prepare']:prepare()
 else:
  scoped.SHARED={C,W,D,I,G};scoped.overlay=overlay;scoped.validate=validate;scoped.main()

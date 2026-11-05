"""Record just the two requested private versions; leave other worktree staging intact."""
from pathlib import Path
import json,sys,hashlib
from datetime import datetime,timezone
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];A=R/'projects/animation-assigning'
sys.path.insert(0,str(P/'production'))
from commit_reviews import C,W,D,engine,overlay as shared_overlay
E='shared/git-essential-images.json';I='.gitignore'
engine.SHARED={W,D,C,E,I}
thumb=P/'publishing/studio-newsroom-v3/thumbnail.jpg'
def rel(p):return p.relative_to(R).as_posix()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def overlay(name,raw,spec):
 if name==E:
  x=spec['essential']
  entries=engine.load(raw)['entries'];match=next((e for e in entries if e['path']==x['path']),None)
  if match is not None:assert match==x;return raw
  return engine.patch(raw,['entries','append'],x)
 if name==I:
  line=('!'+rel(thumb)).encode();nl=b'\r\n' if b'\r\n' in raw else b'\n'
  if line in raw.splitlines():return raw
  return raw.rstrip(b'\r\n')+nl+line+nl
 return shared_overlay(name,raw,spec)
engine.overlay=overlay
def validate(spec):
 assert set(spec['table'])=={x['id'] for x in spec['rows']}=={'A01','S-UE6'}
 for f in spec['ownedPaths']:
  assert (R/f).is_file() and '/local/' not in f and f.startswith(('projects/unreal-engine-6-verse-gameplay/','projects/animation-assigning/'))
 return sorted(set(spec['ownedPaths'])|engine.SHARED)
engine.validate=validate
def prepare():
 j=read(H/'checkpoint.json');a=read(A/'publishing/studio-unreal-kit-v2/upload.json');news=read(P/'publishing/studio-newsroom-v3/upload.json')
 assert j['masterSha256']==news['masterSha256'] and a['masterSha256']==read(A/'production/unreal-kit-v2/checkpoint.json')['captionedMasterSha256']
 rows=[dict(row) for row in read(R/W)['rows'] if row['id'] in ('A01','S-UE6')];table={}
 for row in rows:
  rec=a if row['id']=='A01' else news;id=rec['youtubeId'];priv=bool(rec.get('finalPrivateSave'))
  row.update(uploadStarted=True,videoId=id,url=rec['watchUrl'],platformStatus='YouTube 비공개 저장 완료' if priv else 'YouTube 업로드 완료 · 사용자 광고 평가 후 비공개 저장 대기',executionStatus='수동 KO/EN 자막 · 영문 메타데이터 · 카드·엔딩 설정 완료',updatedAt=datetime.now(timezone.utc).isoformat(),captionedMasterSha256=rec['masterSha256'])
  if row['id']=='S-UE6':
   row.update(title=read(P/'project.json')['title'],productionComplete=True,productionStatus='발표 보도와 액터·폰 추가 편집 · 4분 9초 · 1080p60',deliveryLedger=rel(H/'checkpoint.json'),humanApproval='사용자가 액터·폰을 추가한 새 버전 직접 업로드 요청 · 전체 청취 여부 미확인')
  receipt=rel((A/'publishing/studio-unreal-kit-v2' if row['id']=='A01' else P/'publishing/studio-newsroom-v3')/'upload.json')
  if receipt not in row['evidence']:row['evidence'].append(receipt)
  current=next(line for line in (R/D).read_text('utf-8-sig').splitlines() if line.startswith('| '+row['id']+' | '))
  msg=('비공개' if priv else '업로드 · 광고 평가 대기')
  if row['id']=='A01':table['A01']=current[:current.rfind(' | ',0,len(current)-2)]+' | [YouTube '+msg+']('+rec['watchUrl']+') |'
  else:table['S-UE6']='| S-UE6 | [언리얼 6에서 블루프린트가 사라진다?](http://127.0.0.1:9247/news/) | ☑ 액터·폰 추가 · 4분 9초 | ☐ 사용자 전체 시청·청취 | [YouTube '+msg+']('+rec['watchUrl']+') |'
 grants={
 'unreal-newsroom-v4-private-upload':{'project':P.name,'revision':'newsroom-v4','scope':'Revise Actor/Pawn scope and upload the one new master privately; scheduling belongs to the user. Delete only an identified prior version.','renderAuthorized':True,'newTtsAuthorized':True,'youtubeAuthorized':True,'scheduleAuthorized':False},
 'animation-assigning-unreal-kit-private-upload':{'project':A.name,'revision':'unreal-kit-v2','scope':'User explicitly requested private upload of the latest A01, no schedule.','youtubeAuthorized':True,'scheduleAuthorized':False}}
 owned={rel(f) for f in H.iterdir() if f.is_file() and f.suffix in ('.py','.json','.txt')}
 for folder in [P/'publishing/studio-newsroom-v3',A/'publishing/studio-unreal-kit-v2']:
  owned.update(rel(f) for f in folder.iterdir() if f.is_file() and f.suffix in ('.jpg','.txt','.json'))
 owned.update([rel(P/'project.json'),rel(P/'production/delivery-output.json'),rel(P/'rebuild.json'),rel(A/'project.json'),rel(P/'production/serve_reviews.cjs')])
 spec={'rows':rows,'table':table,'grants':grants,'ownedPaths':sorted(owned),'essential':{'path':rel(thumb),'purpose':'delivery-thumbnail','reason':'Original channel-calico newsroom artwork showing the interrupted Blueprint wire; legible Korean question.','sha256':hashlib.sha256(thumb.read_bytes()).hexdigest(),'reviewedAt':'2026-11-05','project':P.name}}
 save(P/'production/local/newsroom-v4/studio-scope.json',spec)
if __name__=='__main__':
 if '--prepare' in sys.argv:prepare()
 else:engine.main()

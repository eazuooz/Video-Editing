"""Use the repo's isolated index writer for just the news master and A01 private upload kit."""
from pathlib import Path
import importlib.util,sys,json,hashlib
from datetime import datetime,timezone
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];A=R/'projects/animation-assigning'
sys.path.insert(0,str(P/'production'))
from commit_reviews import engine,overlay as base_overlay,C,W,D
E='shared/git-essential-images.json';I='.gitignore';thumb='projects/animation-assigning/publishing/studio-grid-v1/thumbnail.jpg'
engine.SHARED={W,D,C,E,I}
def overlay(name,raw,spec):
 if name==I:
  line=b'!'+thumb.encode()
  if line in raw.splitlines():return raw
  nl=b'\r\n' if b'\r\n' in raw else b'\n';return raw.rstrip(b'\r\n')+nl+line+nl
 if name==E:
  entry=spec['essential'];items=engine.load(raw)['entries']
  if not any(x['path']==thumb for x in items):return engine.patch(raw,['entries','append'],entry)
  assert next(x for x in items if x['path']==thumb)==entry;return raw
 return base_overlay(name,raw,spec)
def allowed(spec):
 assert {r['id'] for r in spec['rows']}=={'A01','S-UE6'} and set(spec['table'])=={'A01','S-UE6'}
 for name in spec['ownedPaths']:
  assert (R/name).is_file() and 'production/local/' not in name and '__pycache__' not in name
  assert name.startswith(('projects/unreal-engine-6-verse-gameplay/','projects/animation-assigning/publishing/studio-grid-v1/')) or name=='projects/animation-assigning/project.json'
 return sorted(set(spec['ownedPaths'])|engine.SHARED)
engine.overlay=overlay;engine.validate=allowed
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def rel(p):return p.relative_to(R).as_posix()
def prepare():
 ledger=read(P/'production/checkpoint.json');assert ledger['revision']=='newsroom-v3'
 u=[dict(r) for r in read(R/W)['rows'] if r['id'] in ('A01','S-UE6')]
 stamp=datetime.now(timezone.utc).isoformat()
 for row in u:
  row['updatedAt']=stamp
  if row['id']=='A01':
   row.update(platformStatus='YouTube 비공개 업로드 준비 · 브라우저 주소 확인 실패로 미전송',humanApproval='사용자가 해당 A01 최종본 업로드를 명시적으로 요청 · 실제 전체 시청 확인 없음',executionStatus='업로드 파일·KO/EN 설명·썸네일 준비 · Studio 연결 대기',reviewStatus='기존 검수본 해시 확인 · 업로드 요청 접수')
   add=rel(A/'publishing/studio-grid-v1/upload.json')
  else:
   duration=round(ledger['durationSeconds']);row.update(productionStatus=f'실제 에픽 발표·작업 화면 중심 재편집 · {duration//60}분 {duration%60}초 · 1080p60',reviewStatus='뉴스 편집본 제공 · 사용자 시청·청취 대기',captionedMasterSha256=ledger['masterSha256'])
   add=rel(H/'final-cut-ledger.json')
  if add not in row['evidence']:row['evidence'].append(add)
 table={}
 for line in (R/D).read_text(encoding='utf-8-sig').splitlines():
  if line.startswith('| A01 | '):table['A01']=line[:line.rfind(' | ',0,len(line)-2)]+' | 비공개 업로드 요청 · 파일·설명·썸네일 준비 · Studio 연결 대기 |'
  if line.startswith('| S-UE6 | '):
   duration=round(ledger['durationSeconds']);table['S-UE6']=f'| S-UE6 | [블루프린트가 사라지면 언리얼을 왜 쓸까?](http://127.0.0.1:9244/news/) | ☑ 실제 발표·시연 중심 1080p60 · {duration//60}분 {duration%60}초 | ☐ 사용자 시청·청취 | 미업로드 |'
 owned={rel(f) for folder in (H,A/'publishing/studio-grid-v1') for f in folder.iterdir() if f.is_file()}
 for name in ('project.json','production/edition.py','production/timeline.py','production/mix.py','production/finish.py','production/serve_reviews.cjs','production/checkpoint.json','production/authorization.json','production/delivery-output.json','publishing/sources.txt'):
  owned.add(rel(P/name))
 for name in ('rebuild.json',):
  f=P/name
  if f.exists():owned.add(rel(f))
 owned.add(rel(A/'project.json'))
 ctrl=read(R/C)['scopedProductionAuthorizations'];key1=P.name;key2='animation-assigning-private-upload'
 entry={'path':thumb,'purpose':'delivery-thumbnail','reason':'A01 channel-calico motion director, Korean headline with mobile visual inspection, prepared for the requested YouTube upload.','sha256':hashlib.sha256((R/thumb).read_bytes()).hexdigest(),'reviewedAt':'2026-11-05','project':A.name}
 spec={'rows':u,'table':table,'grants':{k:ctrl[k] for k in (key1,key2)},'essential':entry,'ownedPaths':sorted(owned)}
 d=P/'production/local/newsroom-v3/git-scope.json';d.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':
 if '--prepare' in sys.argv:prepare()
 else:engine.main()

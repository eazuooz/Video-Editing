"""Register the selected A03 delivery and A02 upload request while preserving other staging."""
from pathlib import Path
import json,sys,hashlib
from datetime import datetime,timezone
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1]
sys.path.insert(0,str(R/'projects/unreal-engine-6-verse-gameplay/production'))
from commit_reviews import engine,overlay as upstream,C,W,D
E='shared/git-essential-images.json';I='.gitignore';engine.SHARED={C,W,D,E,I}
thumb='projects/animation-exaggeration/publishing/studio-v4/thumbnail.jpg'
def overlay(name,raw,spec):
 if name==I:
  line=('!'+thumb).encode()
  if line in raw.splitlines():return raw
  nl=b'\r\n' if b'\r\n' in raw else b'\n';return raw.rstrip(b'\r\n')+nl+line+nl
 if name==E:
  entry=spec['essential'];items=engine.load(raw)['entries']
  if not any(v['path']==thumb for v in items):return engine.patch(raw,['entries','append'],entry)
  assert next(v for v in items if v['path']==thumb)==entry;return raw
 return upstream(name,raw,spec)
engine.overlay=overlay
def validate(spec):
 assert set(spec['table'])=={r['id'] for r in spec['rows']}=={'A02','A03'}
 assert set(spec['grants'])=={P.name,'animation-exaggeration-private-upload'}
 for name in spec['ownedPaths']:
  assert '/local/' not in name and '__pycache__' not in name and (R/name).is_file()
  assert name.startswith(('projects/'+P.name+'/','projects/animation-exaggeration/publishing/studio-v4/','unity/VideoEditing/Assets/VideoScenes/'+P.name)) or name in ('projects/animation-exaggeration/project.json','projects/unreal-engine-6-verse-gameplay/production/serve_reviews.cjs')
 return sorted(set(spec['ownedPaths'])|engine.SHARED)
engine.validate=validate
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
rel=lambda p:p.relative_to(R).as_posix()
def prepare():
 report=read(H/'checkpoint.json');assert report['status']=='local-delivery-user-review-pending'
 length=round(report['durationSeconds']);span=f'{length//60}분 {length%60}초'
 rows=[dict(x) for x in read(R/W)['rows'] if x['id'] in ('A02','A03')]
 stamp=datetime.now(timezone.utc).isoformat()
 for row in rows:
  row['updatedAt']=stamp
  if row['id']=='A03':
   row.update(productionComplete=True,productionStatus='완성 · 실제 게임 60% / 설명 40% · Unity 여섯 씬 · '+span,executionStatus='로컬 검수본 전달',reviewStarted=True,reviewStatus='1080p60 기술 검사 · 사용자 시청·청취 대기',humanApproval='A03 제작 명시 승인 · 현재 버전 사람 검수 대기',platformStatus='로컬 검수 · YouTube 미업로드',localMasterAvailable=True,captionedMasterSha256=report['captionedMasterSha256'],deliveryLedger=rel(H/'checkpoint.json'))
   add=rel(H/'edit-plan-final.json')
  else:
   row.update(executionStatus='최신본 YouTube 비공개 저장 및 HD 처리 완료 · KO/EN 자막·영어 메타데이터 반영',humanApproval='사용자가 A02 비공개 업로드를 명시적으로 요청 · 전체 시청 여부 미확인',platformStatus='YouTube 비공개',uploadStarted=True,videoId='BDmb5VwES5M',url='https://youtu.be/BDmb5VwES5M')
   add='projects/animation-exaggeration/publishing/studio-v4/upload.json'
  if add not in row['evidence']:row['evidence'].append(add)
 table={}
 for line in (R/D).read_text('utf-8-sig').splitlines():
  for ident in ['A02','A03']:
   if line.startswith('| '+ident+' | '):
    action=('[YouTube 비공개 · 쿨라·리리](https://youtu.be/BDmb5VwES5M) · HD·한영 자막' if ident=='A02' else f'[1080p60 · {span} · 전체 검수본](http://127.0.0.1:9245/a03/) · 사용자 시청 대기')
    table[ident]=line[:line.rfind(' | ',0,len(line)-2)]+' | '+action+' |'
 owned=set()
 for folder in (P,R/'projects/animation-exaggeration/publishing/studio-v4'):
  for f in folder.rglob('*'):
   if not f.is_file() or {'local','__pycache__'}&set(f.relative_to(folder).parts):continue
   if f.suffix in ('.json','.md','.py','.txt','.jpg') or f.name=='.gitignore':owned.add(rel(f))
 folder=R/'unity/VideoEditing/Assets/VideoScenes'/P.name
 for f in folder.rglob('*'):
  if f.is_file() and f.suffix in ('.cs','.mat','.unity','.meta'):owned.add(rel(f))
 owned.update([rel(folder)+'.meta','projects/unreal-engine-6-verse-gameplay/production/serve_reviews.cjs','projects/animation-exaggeration/project.json'])
 control=read(R/C)['scopedProductionAuthorizations']
 spec={'rows':rows,'table':table,'grants':{name:control[name] for name in (P.name,'animation-exaggeration-private-upload')},'ownedPaths':sorted(owned),'essential':{'path':thumb,'purpose':'delivery-thumbnail','reason':'A02 final channel-cat illustration contrasting the attack anticipation with the fully extended pose; Korean type checked at thumbnail size.','sha256':hashlib.sha256((R/thumb).read_bytes()).hexdigest(),'reviewedAt':'2026-11-05','project':'animation-exaggeration'}}
 dest=P/'production/local/grid-v1/git-scope.json';dest.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(len(owned),'owned files')
if __name__=='__main__':
 if '--prepare' in sys.argv:prepare()
 else:engine.main()

"""Selective Web/full-film checkpoints; preserves foreign staging and shared edits."""
from pathlib import Path,PurePosixPath
import contextlib,datetime,hashlib,importlib.util,io,json,subprocess,sys
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[3];home=root/'projects/ai-3d-lofi-gaming-room/production'
s=importlib.util.spec_from_file_location('garden_scope',home/'scoped-garden-commit.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
m=g.m;base=g.base;SPEC=home/'web-final-v6-commit-spec.json';PREFIXES=base.PREFIXES;KEY=base.KEY
def validate(spec):
 assert spec['scope']=='ai3d-web-final-and-film-20261117'
 names=spec['ownedPaths'];images={v['path'] for v in spec['essentialImages']};assert len(images)==9 and images<=set(names)
 for name in names:
  p=PurePosixPath(name);assert name.startswith(PREFIXES) and not p.is_absolute() and '..' not in p.parts
  assert '/local/' not in name and '/Library/' not in name
  assert p.suffix.lower() not in {'.mp4','.mp3','.wav','.ogg','.zip','.7z','.exe','.dll','.log','.fbx','.glb','.gltf','.bin'}
  assert p.suffix.lower()!='.png' or name in images
  assert (root/name).is_file() and (root/name).resolve().is_relative_to(root.resolve())
 for v in spec['essentialImages']:assert hashlib.file_digest((root/v['path']).open('rb'),'sha256').hexdigest()==v['sha256']
 build=json.loads((home/'local/web-final-v6/web-build.json').read_text());assert build['result']=='Succeeded' and build['errors']==0
 return sorted(names)+sorted(m.SHARED)
def prepare():
 now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();full=home/'full-video-delivery.json';done=full.exists() and json.loads(full.read_text('utf-8')).get('stage')=='local-final-review-ready'
 status='web-and-full-video-local-review-ready' if done else 'web-ready-full-video-rendering'
 record=m.load((root/base.C).read_bytes())[KEY]
 record.update(status=status,productionComplete=done,webBuildDeferred=False,webModuleInstalled=True,webGameBuilt=True,gameReviewUrl='http://127.0.0.1:9324/',fullVideoDelivery='projects/ai-3d-lofi-gaming-room/production/full-video-delivery.json' if done else None,fullVideoReviewUrl='http://127.0.0.1:9325/' if done else None,humanReview=False,youtubeAuthorized=False,publicWebDeploymentAuthorized=False,updatedAtKst=now)
 old=json.loads((home/'garden-v5-delivery.json').read_text('utf-8'));images=[{'path':v['path'],'purpose':'required-scene-asset','reason':'Original model PBR texture or own map artwork referenced by the final Unity room.','sha256':v['sha256'],'reviewedAt':now,'project':'ai-3d-lofi-gaming-room'} for v in old['textureInputs']]
 raw=subprocess.check_output(['git','-c','core.longpaths=true','ls-files','-m','-o','--exclude-standard','-z','--',*PREFIXES],cwd=root).decode().split('\0')
 excluded=('/local/','__pycache__','/GeneratedAtmosphereV3/','/GeneratedHearthV4/','/GeneratedGardenV5/')
 names={n for n in raw if n and not any(v in n for v in excluded)};names.add(SPEC.relative_to(root).as_posix())
 for v in images:names|={v['path'],v['path']+'.meta'}
 production='웹 빌드·차분한 앉기 완료; 전체 제작 영상·한영 자막·위키 검수본' if done else '웹 빌드·차분한 앉기·메모/타이머 복원 QA 완료; 전체 영상 렌더링 중'
 section=f'''<!-- AI3D-LOFI-GAMING-ROOM-20261116 -->
## AI 3D LOFI 게이밍룸 제작

| 영상 | 제작 | 검수 | 게시 |
|---|---|---|---|
| AI로 만드는 3D LOFI 게이밍룸 | {production} | [게임](http://127.0.0.1:9324/){' · [전체 검수](http://127.0.0.1:9325/)' if done else ''} · 사용자 전체 검수 대기 | 미업로드·공개 웹 배포 없음 |

기존 v1–v5 파일을 보존했다. v6 앉기는 기존 인체 클립을 약 2.22초로 재생하고 의자 정렬·골반 접촉·앉은 자세 연결을 완화했다. WebGL 빌드 성공 후 실제 브라우저에서 독서, 한글 메모, 단축키 분리, 새로고침 저장 복원, 음량과 타이머를 확인했다. [AI 게임 제작 위키](https://app.notion.com/p/41b0b1ffa61e81f1a484f6c3e4b0555b). 모바일 실제 기기 및 사용자 전체 시청 검수는 대기다.
<!-- AI3D-LOFI-GAMING-ROOM-20261116-END -->'''
 spec={'scope':'ai3d-web-final-and-film-20261117','scopeRecord':record,'worklistSet':{'productionComplete':done,'productionStatus':production,'reviewStatus':'로컬 사용자 전체 검수 대기','executionStatus':status,'sampleReviewUrl':'http://127.0.0.1:9324/','notes':'웹 모듈 설치 후 WebGL 성공. 전체 영상과 상세 Notion 글까지 현재 선택 범위. YouTube/공개 웹 배포 별도.','updatedAt':now},'essentialImages':images,'markdownSection':section,'ownedPaths':sorted(names)}
 SPEC.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n','utf-8')
 for name in spec['ownedPaths']:
  p=root/name
  if p.suffix.lower()=='.png':continue
  raw=p.read_bytes()
  try:text=raw.decode('utf-8-sig')
  except UnicodeDecodeError:continue
  clean=('\n'.join(line.rstrip() for line in text.splitlines()).rstrip()+'\n').encode()
  if raw!=clean:p.write_bytes(clean)
 print(json.dumps({'paths':len(names),'status':status}))
m.overlay=base.overlay;m.validate=validate
if __name__=='__main__':
 if '--prepare' in sys.argv:prepare()
 else:
  if '--spec' not in sys.argv:sys.argv[1:1]=['--spec',str(SPEC)]
  if '--execute' in sys.argv:g.warm_objects(json.loads(SPEC.read_text('utf-8')))
  out=io.StringIO()
  with contextlib.redirect_stdout(out):m.main()
  result=json.loads(out.getvalue());summary={k:v for k,v in result.items() if k!='paths'};summary['pathsCount']=len(result.get('paths',[]));print(json.dumps(summary,ensure_ascii=True))

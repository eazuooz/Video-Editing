"""Selective Web/full-film checkpoints; preserves foreign staging and shared edits."""
from pathlib import Path,PurePosixPath
import contextlib,datetime,hashlib,importlib.util,io,json,subprocess,sys
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[3];home=root/'projects/ai-3d-lofi-gaming-room/production'
s=importlib.util.spec_from_file_location('garden_scope',home/'scoped-garden-commit.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
m=g.m;base=g.base;SPEC=home/'tutorial-v3-commit-spec.json';PREFIXES=base.PREFIXES;KEY=base.KEY
def validate(spec):
 assert spec['scope']=='ai3d-tutorial-v3-and-film-20261117'
 names=spec['ownedPaths'];images={v['path'] for v in spec['essentialImages']};assert len(images)==9 and images<=set(names)
 for name in names:
  p=PurePosixPath(name);assert name.startswith(PREFIXES) and not p.is_absolute() and '..' not in p.parts
  assert '/local/' not in name and '/Library/' not in name
  assert p.suffix.lower() not in {'.mp4','.mp3','.wav','.ogg','.zip','.7z','.exe','.dll','.log','.fbx','.glb','.gltf','.bin'}
  assert p.suffix.lower()!='.png' or name in images
  assert (root/name).is_file() and (root/name).resolve().is_relative_to(root.resolve())
 for v in spec['essentialImages']:assert hashlib.file_digest((root/v['path']).open('rb'),'sha256').hexdigest()==v['sha256']
 build=json.loads((home/'local/living-room-v9/web-build.json').read_text());assert build['result']=='Succeeded' and build['errors']==0
 return sorted(names)+sorted(m.SHARED)
def prepare():
 now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();full=home/'full-video-delivery.json';delivery=json.loads(full.read_text('utf-8')) if full.exists() else {};done=delivery.get('stage')=='local-final-review-ready' and '/full-video-v3/' in delivery.get('outputs',[{},{}])[1].get('path','').replace(chr(92),'/')
 status='tutorial-v3-and-full-film-local-review-ready' if done else 'tutorial-v3-browser-corrections-and-voice-in-progress'
 record=m.load((root/base.C).read_bytes())[KEY]
 record.update(latestUserRequest='2026-11-17 natural cat, fitted reading contacts and AI-tools recreation tutorial',publicWikiArticlesAuthorized=True,existing2dDescriptionEditAuthorized='e7hxBpIetq4',status=status,productionComplete=done,webBuildDeferred=False,webModuleInstalled=True,webGameBuilt=True,gameReviewUrl='http://127.0.0.1:9324/',fullVideoDelivery='projects/ai-3d-lofi-gaming-room/production/full-video-delivery.json' if done else None,fullVideoReviewUrl='http://127.0.0.1:9329/' if done else None,humanReview=False,youtubeAuthorized=False,publicWebDeploymentAuthorized=False,updatedAtKst=now)
 old=json.loads((home/'garden-v5-delivery.json').read_text('utf-8'));images=[{'path':v['path'],'purpose':'required-scene-asset','reason':'Original model PBR texture or own map artwork referenced by the final Unity room.','sha256':v['sha256'],'reviewedAt':now,'project':'ai-3d-lofi-gaming-room'} for v in old['textureInputs']]
 raw=subprocess.check_output(['git','-c','core.longpaths=true','ls-files','-m','-o','--exclude-standard','-z','--',*PREFIXES],cwd=root).decode().split('\0')
 excluded=('/local/','__pycache__','/GeneratedAtmosphereV3/','/GeneratedHearthV4/','/GeneratedGardenV5/','/GeneratedWebFinalV6/','/Assets/Settings/UniversalRenderPipelineGlobalSettings.asset','/ProjectSettings/ProjectAuditorSettings.asset','/ProjectSettings/ProjectSettings.asset')
 names={n for n in raw if n and not any(v in n for v in excluded)};names.add(SPEC.relative_to(root).as_posix())
 for v in images:names|={v['path'],v['path']+'.meta'}
 production='AI 도구별 입력·요청문·설정·결과 튜토리얼, 고양이·독서 접촉 보완 완료' if done else '고양이 재질·독서 접촉 보완, AI 도구 따라 만들기 대본·화면·음성 제작 중'
 section=f'''<!-- AI3D-LOFI-GAMING-ROOM-20261116 -->
## AI 3D LOFI 게이밍룸 제작

| 영상 | 제작 | 검수 | 게시 |
|---|---|---|---|
| AI로 만드는 3D LOFI 게이밍룸 | {production} | [게임](http://127.0.0.1:9324/){' · [전체 검수](http://127.0.0.1:9329/)' if done else ''} · 사용자 전체 검수 대기 | 미업로드·공개 웹 배포 없음 |

기존 v8 게임과 full-video-v2 영상을 보존했다. v9는 삼색 무늬·매끈한 꼬리와 독서 시 책·손목·팔꿈치 접촉을 보완했다. full-video-v3는 이미지 입력 → Tripo 생성·정리 → Codex 요청과 Unity 구현 → 웹 확인 순서의 따라 만들기 튜토리얼이다. 개발 수정 이력 대신 요청문·설정·결과·전달 파일을 보여 준다. [상세 위키](https://www.yamyamcoding.com/41b0b1ff-a61e-8171-8cf1-fa0b0af02ece)에 재현 요청문과 검증 기준을 연결한다. 다른 영상·플랫폼은 변경하지 않으며 사용자 전체 검수는 대기다.
<!-- AI3D-LOFI-GAMING-ROOM-20261116-END -->'''
 spec={'scope':'ai3d-tutorial-v3-and-film-20261117','scopeRecord':record,'worklistSet':{'productionComplete':done,'productionStatus':production,'reviewStatus':'로컬 사용자 전체 검수 대기','executionStatus':status,'sampleReviewUrl':'http://127.0.0.1:9324/','notes':'v9 게임의 고양이·독서 접촉과 full-video-v3 AI 도구 활용 튜토리얼, 기존 3D 위키 보완. v8/v2 보존. 새 YouTube 업로드·공개 웹 배포 별도.','updatedAt':now},'essentialImages':images,'markdownSection':section,'ownedPaths':sorted(names)}
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

"""Selective Web/full-film checkpoints; preserves foreign staging and shared edits."""
from pathlib import Path,PurePosixPath
import contextlib,datetime,hashlib,importlib.util,io,json,subprocess,sys
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[3];home=root/'projects/ai-3d-lofi-gaming-room/production'
s=importlib.util.spec_from_file_location('garden_scope',home/'scoped-garden-commit.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
m=g.m;base=g.base;SPEC=home/'rattan-tutorial-v5-commit-spec.json';PREFIXES=base.PREFIXES;KEY=base.KEY
def validate(spec):
 assert spec['scope']=='ai3d-rattan-v11-tutorial-v5-20261118'
 names=spec['ownedPaths'];images={v['path'] for v in spec['essentialImages']};assert len(images) in (14,18) and images<=set(names)
 for name in names:
  p=PurePosixPath(name);assert name.startswith(PREFIXES) and not p.is_absolute() and '..' not in p.parts
  assert '/local/' not in name and '/Library/' not in name
  assert p.suffix.lower() not in {'.mp4','.mp3','.wav','.ogg','.zip','.7z','.exe','.dll','.log','.fbx','.glb','.gltf','.bin','.wasm','.pdb','.sym'}
  assert p.suffix.lower()!='.png' or name in images
  assert (root/name).is_file() and (root/name).resolve().is_relative_to(root.resolve())
 for v in spec['essentialImages']:assert hashlib.file_digest((root/v['path']).open('rb'),'sha256').hexdigest()==v['sha256']
 build=json.loads((home/'local/living-room-v10/web-build.json').read_text());assert build['result']=='Succeeded' and build['errors']==0
 return sorted(names)+sorted(m.SHARED)
def prepare():
 now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();full=home/'full-video-delivery.json';delivery=json.loads(full.read_text('utf-8')) if full.exists() else {};done=delivery.get('stage')=='local-final-review-ready' and '/full-video-v5/' in delivery.get('outputs',[{},{}])[1].get('path','').replace(chr(92),'/')
 status='rattan-v11-tutorial-v5-local-review-ready' if done else json.loads((home/'checkpoint.json').read_text('utf-8'))['status']
 record=m.load((root/base.C).read_bytes())[KEY]
 record.update(latestUserRequest='2026-11-18 light wood/woven sofa, matching low coffee table for feet, real Tripo calico breathing/tail, same-voice AI-tools recreation tutorial',publicWikiArticlesAuthorized=True,existing2dDescriptionEditAuthorized='e7hxBpIetq4',status=status,productionComplete=done,webBuildDeferred=False,webModuleInstalled=True,webGameBuilt=True,gameReviewUrl='http://127.0.0.1:9324/',fullVideoDelivery='projects/ai-3d-lofi-gaming-room/production/full-video-delivery.json' if done else None,fullVideoReviewUrl='http://127.0.0.1:9329/' if done else None,humanReview=False,youtubeAuthorized=False,publicWebDeploymentAuthorized=False,updatedAtKst=now)
 target_report=home/'local/living-room-v11/web-build.json';target_build=json.loads(target_report.read_text('utf-8')) if target_report.exists() else {};target_built=target_build.get('result')=='Succeeded' and target_build.get('errors')==0
 record.update(targetGameRevision='living-room-v11',targetVideoRevision='full-video-v5',targetGameBuilt=target_built,latestPlayableGameRevision='living-room-v11' if target_built else 'living-room-v10',furnitureDownloadPending=json.loads((home/'rattan-v11-scope.json').read_text('utf-8'))['userDownloadPending'],latestUserEvidence=['밝은 목재·짜임 소파와 탁자로 변경, 탁자에 발을 올리고 독서','실제 Tripo 삼색고양이에 천천히 숨 쉬기와 꼬리 움직임','게임·화면 공유 끝났어. GPU 진행'])
 old=json.loads((home/'garden-v5-delivery.json').read_text('utf-8'));images=[{'path':v['path'],'purpose':'required-scene-asset','reason':'Original model PBR texture or own map artwork referenced by the final Unity room.','sha256':v['sha256'],'reviewedAt':now,'project':'ai-3d-lofi-gaming-room'} for v in old['textureInputs']]
 for relative in ['ThirdParty/VintageSofaV10/BaseColor.png', 'ThirdParty/VintageSofaV10/Normal.png', 'ThirdParty/VintageSofaV10/MetallicSmoothness.png', 'TripoSleepingCatV10/BaseColor.png', 'TripoSleepingCatV10/Normal.png']:
  p=root/'unity/LofiGamingRoomWeb/Assets/LofiRoom'/relative
  images.append({'path':p.relative_to(root).as_posix(),'purpose':'required-scene-asset','reason':'Actually referenced v10 URP texture; source and license recorded beside the file.','sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),'reviewedAt':now,'project':'ai-3d-lofi-gaming-room'})
 raw=subprocess.check_output(['git','-c','core.longpaths=true','ls-files','-m','-o','--exclude-standard','-z','--',*PREFIXES],cwd=root).decode().split('\0')
 excluded=('/local/','__pycache__','/GeneratedAtmosphereV3/','/GeneratedHearthV4/','/GeneratedGardenV5/','/GeneratedWebFinalV6/','/Data/','/Assets/Settings/UniversalRenderPipelineGlobalSettings.asset','/ProjectSettings/ProjectAuditorSettings.asset','/ProjectSettings/ProjectSettings.asset','/ProjectSettings/URPProjectSettings.asset','/production/finish-sofa-v4-cpu.py')
 names={n for n in raw if n and not any(v in n for v in excluded) and PurePosixPath(n).suffix.lower() not in {'.mp4','.mp3','.wav','.ogg','.zip','.7z','.exe','.dll','.log','.fbx','.glb','.gltf','.bin','.jpg','.png','.webp'}};names.add(SPEC.relative_to(root).as_posix())
 for v in images:names|={v['path'],v['path']+'.meta'}
 production='라탄 가구·삼색고양이 수면 동작과 AI 도구 따라 만들기 영상 완료' if done else '라탄 소파·탁자 Tripo 생성 완료·파일 수신 대기, 고양이 동작과 31문단 음성·249개 한영 자막 준비 완료'
 section=f'''<!-- AI3D-LOFI-GAMING-ROOM-20261116 -->
## AI 3D LOFI 게이밍룸 제작

| 영상 | 제작 | 검수 | 게시 |
|---|---|---|---|
| AI로 만드는 3D LOFI 게이밍룸 | {production} | [게임](http://127.0.0.1:9324/){' · [전체 검수](http://127.0.0.1:9329/)' if done else ''} · 사용자 전체 검수 대기 | 미업로드·공개 웹 배포 없음 |

기존 v10 게임과 full-video-v2 영상을 보존했다. 현재 [12초 고양이 시연](http://127.0.0.1:9330/)은 실제 Tripo 삼색고양이의 국소 호흡·꼬리 움직임을 보여 준다. v11의 밝은 목재·짜임 소파와 낮은 탁자는 Tripo 생성·리토포가 끝났으며 Chrome의 ZIP 차단으로 사용자 다운로드를 기다린다. v5 튜토리얼은 이미지 입력 → Tripo 생성·정리 → Codex 요청과 Unity 구현 → 웹 확인 순서이며 31문단 음성과 전체 음성·믹스 ASR, 249개 한영 자막 준비를 마쳤다. 새 가구 실제 접촉 검수·웹 빌드·전체 영상 렌더는 아직 완료되지 않았다. [상세 위키](https://www.yamyamcoding.com/41b0b1ff-a61e-8171-8cf1-fa0b0af02ece)에 재현 요청문과 검증 기준을 연결한다. 다른 영상·플랫폼은 변경하지 않으며 사용자 전체 검수는 대기다.
<!-- AI3D-LOFI-GAMING-ROOM-20261116-END -->'''
 spec={'scope':'ai3d-rattan-v11-tutorial-v5-20261118','scopeRecord':record,'worklistSet':{'productionComplete':done,'productionStatus':production,'reviewStatus':'고양이 12초 시연 제공; 새 전체 게임·영상 검수본 준비 중','executionStatus':status,'sampleReviewUrl':'http://127.0.0.1:9324/','notes':'v11 라탄 가구 Tripo 생성 완료·사용자 ZIP 다운로드 대기. 고양이 실제 동작과 v5 31문단 음성·자막 QA 완료. v10 게임/v2 영상 보존. 새 가구 접촉·빌드·전체 렌더/위키 미완성. 새 YouTube·공개 배포 별도.','updatedAt':now},'essentialImages':images,'markdownSection':section,'ownedPaths':sorted(names)}
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

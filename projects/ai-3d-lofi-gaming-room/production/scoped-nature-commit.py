"""Isolated nature-v2 commit, with batched content-addressed object preparation."""
from pathlib import Path,PurePosixPath
import contextlib,datetime,hashlib,importlib.util,io,json,subprocess,sys

sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[3];home=root/'projects/ai-3d-lofi-gaming-room/production'
loader=importlib.util.spec_from_file_location('sample_scope',home/'scoped-sample-commit.py')
base=importlib.util.module_from_spec(loader);loader.loader.exec_module(base);m=base.m
SPEC=home/'nature-v2-commit-spec.json';KEY=base.KEY;PREFIXES=base.PREFIXES

def validate(spec):
    assert spec['scope']=='ai3d-nature-v2-PC-review-20261116'
    paths=spec['ownedPaths'];assert len(paths)==len(set(paths))
    images={e['path'] for e in spec['essentialImages']};assert len(images)==9 and images<=set(paths)
    for name in paths:
        p=PurePosixPath(name);assert not p.is_absolute() and '..' not in p.parts
        assert name.startswith(PREFIXES) and '/local/' not in name and '/Library/' not in name
        assert p.suffix.lower() not in {'.mp4','.mp3','.wav','.zip','.7z','.exe','.dll','.log'}
        assert p.suffix.lower()!='.png' or name in images
        assert (root/name).is_file() and (root/name).resolve().is_relative_to(root.resolve())
    for e in spec['essentialImages']:assert hashlib.file_digest((root/e['path']).open('rb'),'sha256').hexdigest()==e['sha256'] and e['path']+'.meta' in paths
    d=json.loads((home/'nature-v2-delivery.json').read_text(encoding='utf-8'))
    assert not d['humanReview'] and not d['youtubeUploaded'] and d['videoFrames']==2880 and d['nativeBuild']['errors']==0
    return sorted(paths)+sorted(m.SHARED)

def prepare():
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
    d=json.loads((home/'nature-v2-delivery.json').read_text(encoding='utf-8'))
    record=m.load((root/base.C).read_bytes())[KEY]
    record.update(status='nature-v2-pc-review-ready',scope='One original 3D LOFI room and production video. Current unit: PC hair, nature, model-detail and material revision. Final WebGL build explicitly deferred again.',latestUserEvidence=['머리카락·풀잎·모델링 디테일·텍스처 품질 개선','웹빌드는 나중에 최종으로하자 일단 피시 기준으로 테스트해보고 가자~'],sampleDelivery='projects/ai-3d-lofi-gaming-room/production/nature-v2-delivery.json',sampleReviewUrl='http://127.0.0.1:9320/',webBuildDeferred=True,webModuleInstalled=False,updatedAtKst=now)
    images=[{'path':t['path'],'purpose':'required-scene-asset','reason':'Actually referenced texture for the reviewed PC nature scene: original 4K model color/data material input or original generated forest-map wall artwork.','sha256':t['sha256'],'reviewedAt':now,'project':'ai-3d-lofi-gaming-room'} for t in d['textureInputs']]
    paths=subprocess.check_output(['git','-c','core.longpaths=true','ls-files','-m','-o','--exclude-standard','-z','--',*PREFIXES],cwd=root).decode().split('\0')
    selected={p for p in paths if p and '/local/' not in p and '__pycache__' not in p}
    selected|={SPEC.relative_to(root).as_posix()}
    for e in images:selected|={e['path'],e['path']+'.meta'}
    section='''<!-- AI3D-LOFI-GAMING-ROOM-20261116 -->
## AI 3D LOFI 게이밍룸 제작

| 영상 | 제작 | 검수 | 게시 |
|---|---|---|---|
| [AI로 만드는 3D LOFI 게이밍룸](../projects/ai-3d-lofi-gaming-room/planning/outline.md) | PC v2: 머리카락 흔들림·311개 잎·가구 마감·4K/PBR 재질 · Windows 실행 파일·48초 FHD60 완료 | [새 검수·전후 비교](http://127.0.0.1:9320/) · v1 사용자 호평 · v2 검수 대기 | 미업로드·예약 없음 |

기존 시안과 걷기·대기 모션을 보존하고 자연/재질 디테일을 보완했다. 캐릭터·헤드폰 색상은 실제 4K 원본이며 굴곡·거칠기·금속성 지도는 원본 해상도로 연결했다. 식물·소품은 직접 작성한 3D 형상, 벽 지도는 자체 이미지 생성이다. [파일·QA 기록](../projects/ai-3d-lofi-gaming-room/production/nature-v2-delivery.json) · [재질·이미지 프롬프트](../projects/ai-3d-lofi-gaming-room/production/nature-v2-art-record.json). 사용자 요청으로 웹 모듈 설치·빌드는 다시 보류했다. 앉기·독서·전체 제작 영상은 남아 있다.
<!-- AI3D-LOFI-GAMING-ROOM-20261116-END -->'''
    spec={'scope':'ai3d-nature-v2-PC-review-20261116','scopeRecord':record,'worklistSet':{'productionComplete':False,'productionStatus':'PC v2: 머리카락·311개 잎·가구 디테일·4K/PBR 보완 · 48초 FHD60·Windows 실행 파일 완료','reviewStatus':'v1 사용자 호평; nature v2 PC 검수 대기; 전체 영상 미완성','executionStatus':'nature-v2-pc-review-ready','sampleReviewUrl':'http://127.0.0.1:9320/','notes':'웹빌드는 사용자가 다시 최종 단계로 보류. PC v2 실행·시각 QA 완료. 앉기·독서와 전체 제작 영상은 남음.','updatedAt':now},'essentialImages':images,'markdownSection':section,'ownedPaths':sorted(selected)}
    SPEC.write_bytes((json.dumps(spec,ensure_ascii=False,indent=2)+'\n').encode())
    # Unity-generated YAML is normalized only inside this owned unit.
    for name in spec['ownedPaths']:
        p=root/name
        if p.suffix.lower() in {'.png','.fbx'}:continue
        raw=p.read_bytes()
        try:text=raw.decode('utf-8-sig')
        except UnicodeDecodeError:continue
        clean=('\n'.join(line.rstrip() for line in text.splitlines()).rstrip()+'\n').encode()
        if raw!=clean:p.write_bytes(clean)
    print(json.dumps({'preparedPaths':len(selected),'essentialImages':len(images)}))

def warm_objects(spec):
    """Same Git clean filters as --path; no index changes, no cached ref reads."""
    original=m.git;paths=spec['ownedPaths'];raw={p:(root/p).read_bytes() for p in paths}
    identities=original('hash-object','-w','--stdin-paths',data=('\n'.join(paths)+'\n').encode()).decode().splitlines();assert len(identities)==len(paths)
    ids=dict(zip(paths,identities));blobs={}
    payload=original('cat-file','--batch',data=('\n'.join(dict.fromkeys(identities))+'\n').encode());offset=0
    while offset<len(payload):
        end=payload.index(b'\n',offset);identity,kind,size=payload[offset:end].split();assert kind==b'blob';size=int(size);start=end+1;blobs[identity.decode()]=payload[start:start+size];assert payload[start+size:start+size+1]==b'\n';offset=start+size+1
    # Check filter equivalence on text and raster samples before using the cache.
    for name in [next(p for p in paths if p.endswith('.cs')),next(p for p in paths if p.endswith('.png'))]:assert original('hash-object','--path='+name,'--stdin',data=raw[name]).strip().decode()==ids[name]
    def cached(*args,env=None,data=None,optional=False):
        if args[:2]==('hash-object','-w') and len(args)==4 and args[2].startswith('--path='):
            name=args[2][7:]
            if name in raw and data==raw[name]:return (ids[name]+'\n').encode()
        if args[:2]==('cat-file','blob') and args[2] in blobs:return blobs[args[2]]
        return original(*args,env=env,data=data,optional=optional)
    m.git=cached

m.overlay=base.overlay;m.validate=validate
if __name__=='__main__':
    if '--prepare' in sys.argv:prepare()
    else:
        if '--spec' not in sys.argv:sys.argv[1:1]=['--spec',str(SPEC)]
        if '--execute' in sys.argv:warm_objects(json.loads(SPEC.read_text(encoding='utf-8')))
        output=io.StringIO()
        with contextlib.redirect_stdout(output):m.main()
        result=json.loads(output.getvalue());summary={k:v for k,v in result.items() if k!='paths'};summary['pathsCount']=len(result.get('paths',[]));print(json.dumps(summary,ensure_ascii=True))

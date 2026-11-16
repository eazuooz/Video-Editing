"""Isolated hearth-v4 commit, using batched content-addressed object preparation; preserves foreign staging."""
from pathlib import Path,PurePosixPath
import contextlib,datetime,hashlib,importlib.util,io,json,subprocess,sys

sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[3];home=root/'projects/ai-3d-lofi-gaming-room/production'
loader=importlib.util.spec_from_file_location('sample_scope',home/'scoped-sample-commit.py')
base=importlib.util.module_from_spec(loader);loader.loader.exec_module(base);m=base.m
SPEC=home/'hearth-v4-commit-spec.json';KEY=base.KEY;PREFIXES=base.PREFIXES

def validate(spec):
    assert spec['scope']=='ai3d-hearth-v4-PC-review-20261116'
    paths=spec['ownedPaths'];assert len(paths)==len(set(paths))
    images={e['path'] for e in spec['essentialImages']};assert len(images)==9 and images<=set(paths)
    for name in paths:
        p=PurePosixPath(name);assert not p.is_absolute() and '..' not in p.parts
        assert name.startswith(PREFIXES) and '/local/' not in name and '/Library/' not in name
        assert p.suffix.lower() not in {'.mp4','.mp3','.wav','.zip','.7z','.exe','.dll','.log'}
        assert p.suffix.lower()!='.png' or name in images
        assert (root/name).is_file() and (root/name).resolve().is_relative_to(root.resolve())
    for e in spec['essentialImages']:assert hashlib.file_digest((root/e['path']).open('rb'),'sha256').hexdigest()==e['sha256'] and e['path']+'.meta' in paths
    d=json.loads((home/'hearth-v4-delivery.json').read_text(encoding='utf-8'))
    assert not d['humanReview'] and not d['youtubeUploaded'] and d['videoFrames']==4320 and d['nativeBuild']['errors']==0
    return sorted(paths)+sorted(m.SHARED)

def prepare():
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
    d=json.loads((home/'hearth-v4-delivery.json').read_text(encoding='utf-8'))
    record=m.load((root/base.C).read_bytes())[KEY]
    record.update(status='hearth-v4-pc-review-ready',scope='One original 3D LOFI room and production video. Current unit: PC v4 real chair entry/exit, computer/reading interactions, compact iMac desk, two-tier shelves, fireplace particles/crackle and a synchronized record player. Web build remains deferred.',latestUserEvidence=['걷기·앉기·컴퓨터·독서·일어나기 연결, 양옆 2단 책장과 벽난로 불꽃·장작 소리','최종 선택은 아이맥 한 대와 작은 책상; 노트북 제안 대체','창문 아래 작은 탁상과 로파이 레코드 플레이어'],sampleDelivery='projects/ai-3d-lofi-gaming-room/production/hearth-v4-delivery.json',sampleReviewUrl='http://127.0.0.1:9322/',webBuildDeferred=True,webModuleInstalled=False,updatedAtKst=now)
    images=[{'path':t['path'],'purpose':'required-scene-asset','reason':'Actually referenced texture for the reviewed PC nature scene: original 4K model color/data material input or original generated forest-map wall artwork.','sha256':t['sha256'],'reviewedAt':now,'project':'ai-3d-lofi-gaming-room'} for t in d['textureInputs']]
    paths=subprocess.check_output(['git','-c','core.longpaths=true','ls-files','-m','-o','--exclude-standard','-z','--',*PREFIXES],cwd=root).decode().split('\0')
    selected={p for p in paths if p and '/local/' not in p and '__pycache__' not in p and '/GeneratedAtmosphereV3/' not in p}
    selected|={SPEC.relative_to(root).as_posix()}
    for e in images:selected|={e['path'],e['path']+'.meta'}
    section='''<!-- AI3D-LOFI-GAMING-ROOM-20261116 -->
## AI 3D LOFI 게이밍룸 제작

| 영상 | 제작 | 검수 | 게시 |
|---|---|---|---|
| [AI로 만드는 3D LOFI 게이밍룸](../projects/ai-3d-lofi-gaming-room/planning/outline.md) | PC v4: 실제 앉기·일어나기·아이맥·독서, 양옆 2단 책장·벽난로·레코드 플레이어 · 72초 FHD60·Windows 완료 | [새 상호작용·소리 검수](http://127.0.0.1:9322/) · v4 사용자 검수 대기 | 미업로드·예약 없음 |

기존 걷기·대기·4K 재질·머리카락·잎과 창가 빛을 유지했다. KayKit의 실제 앉기·일어나기와 보유 EmacEArt 독서 모션을 사용하고 의자·손·발을 맞췄다. 듀얼 모니터·본체는 작은 아이맥 책상으로 교체했다. 가운데 벽난로에 불꽃·불티·연기와 CC0 장작 소리를, 창가 작은 탁상에 음악과 동기화되는 레코드 플레이어를 추가했다. 음악·장작 음량은 개별 조절한다. [파일·QA 기록](../projects/ai-3d-lofi-gaming-room/production/hearth-v4-delivery.json) · [에셋·라이선스](../projects/ai-3d-lofi-gaming-room/production/hearth-v4-asset-record.json). v1–v3 검수 파일은 보존했다. 웹 설치·빌드는 사용자 지시로 계속 보류하고 전체 제작 영상은 남아 있다.
<!-- AI3D-LOFI-GAMING-ROOM-20261116-END -->'''
    spec={'scope':'ai3d-hearth-v4-PC-review-20261116','scopeRecord':record,'worklistSet':{'productionComplete':False,'productionStatus':'PC v4: 앉기·아이맥·독서·일어나기, 벽난로 불꽃/소리, 레코드 플레이어 · 72초 FHD60·Windows 완료','reviewStatus':'v1 사용자 호평; PC v4 사용자 검수 대기; 전체 영상 미완성','executionStatus':'hearth-v4-pc-review-ready','sampleReviewUrl':'http://127.0.0.1:9322/','notes':'웹빌드 최종 보류 유지. PC v4 상호작용·장작/음악 연결과 렌더·셰이더 QA 완료. 전체 제작 영상 미완성.','updatedAt':now},'essentialImages':images,'markdownSection':section,'ownedPaths':sorted(selected)}
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

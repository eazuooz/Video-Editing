"""Isolated garden-v5 commit, using batched content-addressed object preparation; preserves foreign staging."""
from pathlib import Path,PurePosixPath
import contextlib,datetime,hashlib,importlib.util,io,json,subprocess,sys

sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[3];home=root/'projects/ai-3d-lofi-gaming-room/production'
loader=importlib.util.spec_from_file_location('sample_scope',home/'scoped-sample-commit.py')
base=importlib.util.module_from_spec(loader);loader.loader.exec_module(base);m=base.m
SPEC=home/'garden-v5-commit-spec.json';KEY=base.KEY;PREFIXES=base.PREFIXES

def validate(spec):
    assert spec['scope']=='ai3d-garden-v5-PC-review-20261117'
    paths=spec['ownedPaths'];assert len(paths)==len(set(paths))
    images={e['path'] for e in spec['essentialImages']};assert len(images)==9 and images<=set(paths)
    for name in paths:
        p=PurePosixPath(name);assert not p.is_absolute() and '..' not in p.parts
        assert name.startswith(PREFIXES) and '/local/' not in name and '/Library/' not in name
        assert p.suffix.lower() not in {'.mp4','.mp3','.wav','.zip','.7z','.exe','.dll','.log'}
        assert p.suffix.lower()!='.png' or name in images
        assert (root/name).is_file() and (root/name).resolve().is_relative_to(root.resolve())
    for e in spec['essentialImages']:assert hashlib.file_digest((root/e['path']).open('rb'),'sha256').hexdigest()==e['sha256'] and e['path']+'.meta' in paths
    d=json.loads((home/'garden-v5-delivery.json').read_text(encoding='utf-8'))
    assert not d['humanReview'] and not d['youtubeUploaded'] and d['videoFrames']==2880 and d['nativeBuild']['errors']==0
    return sorted(paths)+sorted(m.SHARED)

def prepare():
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
    d=json.loads((home/'garden-v5-delivery.json').read_text(encoding='utf-8'))
    record=m.load((root/base.C).read_bytes())[KEY]
    record.update(status='garden-v5-pc-review-ready',scope='One original 3D LOFI room and production video. Current unit: PC v5 reduced chair occlusion, lower display, forest/moon panorama, stronger constrained wind and locally autosaved notes. Web build remains deferred.',latestUserEvidence=['의자 가림 축소·모니터 낮추기','창밖 숲과 달·잎과 머리 흔들림 확대','메모 UI와 로컬 컴퓨터 자동저장 추가'],sampleDelivery='projects/ai-3d-lofi-gaming-room/production/garden-v5-delivery.json',sampleReviewUrl='http://127.0.0.1:9323/',webBuildDeferred=True,webModuleInstalled=False,updatedAtKst=now)
    images=[{'path':t['path'],'purpose':'required-scene-asset','reason':'Actually referenced texture for the reviewed PC nature scene: original 4K model color/data material input or original generated forest-map wall artwork.','sha256':t['sha256'],'reviewedAt':now,'project':'ai-3d-lofi-gaming-room'} for t in d['textureInputs']]
    paths=subprocess.check_output(['git','-c','core.longpaths=true','ls-files','-m','-o','--exclude-standard','-z','--',*PREFIXES],cwd=root).decode().split('\0')
    selected={p for p in paths if p and '/local/' not in p and '__pycache__' not in p and '/GeneratedAtmosphereV3/' not in p and '/GeneratedHearthV4/' not in p}
    selected|={SPEC.relative_to(root).as_posix()}
    for e in images:selected|={e['path'],e['path']+'.meta'}
    section='''<!-- AI3D-LOFI-GAMING-ROOM-20261116 -->
## AI 3D LOFI 게이밍룸 제작

| 영상 | 제작 | 검수 | 게시 |
|---|---|---|---|
| [AI로 만드는 3D LOFI 게이밍룸](../projects/ai-3d-lofi-gaming-room/planning/outline.md) | PC v5: 낮은 등받이·모니터, 창밖 숲·달, 바람 강화와 로컬 자동저장 메모 · 48초 FHD60·Windows 완료 | [수정 PC 검수](http://127.0.0.1:9323/) · v5 사용자 검수 대기 | 미업로드·예약 없음 |

실제 앉기·독서·일어나기와 벽난로·레코드 소리는 유지했다. 등받이는 높이 78→37cm·폭 48→39cm로 줄이고 모니터는 13cm 낮췄다. 자체 숲·달 파노라마와 약 3배 잎 바람, 더 큰 제한형 머리 움직임을 반영했다. 메모는 UTF-8 파일로 자동 저장되며 백업/복구와 실제 PC 재실행을 검수했다. [파일·QA](../projects/ai-3d-lofi-gaming-room/production/garden-v5-delivery.json). 기존 v1–v4 검수 파일을 보존했고 웹 설치·빌드와 전체 제작 영상은 남아 있다.
<!-- AI3D-LOFI-GAMING-ROOM-20261116-END -->'''
    spec={'scope':'ai3d-garden-v5-PC-review-20261117','scopeRecord':record,'worklistSet':{'productionComplete':False,'productionStatus':'PC v5: 낮은 등받이·모니터, 숲·달·바람 강화, 로컬 자동저장 메모 · 48초 FHD60·Windows 완료','reviewStatus':'v4 피드백 반영; PC v5 사용자 검수 대기; 전체 영상 미완성','executionStatus':'garden-v5-pc-review-ready','sampleReviewUrl':'http://127.0.0.1:9323/','notes':'웹빌드 최종 보류 유지. PC v5 가림·창밖·바람과 자동저장/복구·실제 재실행 QA 완료. 전체 제작 영상 미완성.','updatedAt':now},'essentialImages':images,'markdownSection':section,'ownedPaths':sorted(selected)}
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
    for suffix in ('.cs','.png'):
        name=next((p for p in paths if p.endswith(suffix)),None)
        if name:assert original('hash-object','--path='+name,'--stdin',data=raw[name]).strip().decode()==ids[name]
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

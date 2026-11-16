"""Use the existing isolated-index committer with this sample's exact scope."""
from pathlib import Path, PurePosixPath
import datetime, hashlib, importlib.util, json, subprocess, sys

sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[3]
home=root/'projects/ai-3d-lofi-gaming-room/production'
source=root/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py'
loader=importlib.util.spec_from_file_location('isolated_commit',source)
m=importlib.util.module_from_spec(loader);loader.loader.exec_module(m)
C='shared/publishing/video-production-control.json';W='shared/publishing/video-worklist.json';D='docs/VIDEO_WORKLIST.md';I='shared/git-essential-images.json'
KEY='ai3dLofiGamingRoom20261116';SLUG='ai-3d-lofi-gaming-room'
BEGIN='<!-- AI3D-LOFI-GAMING-ROOM-20261116 -->';END='<!-- AI3D-LOFI-GAMING-ROOM-20261116-END -->'
PREFIXES=('projects/'+SLUG+'/','unity/LofiGamingRoomWeb/')
SPEC=home/'sample-commit-spec.json'

def overlay(name,raw,spec):
    if name in {C,W}:
        raw=m.patch(raw,[KEY],spec['scopeRecord'])
        if name==W:
            rows=m.load(raw)['rows'];positions=[i for i,r in enumerate(rows) if r['id']=='S-AI3D'];assert len(positions)==1
            for field,value in spec['worklistSet'].items():raw=m.patch(raw,['rows',positions[0],field],value)
        return raw
    if name==I:
        for entry in spec['essentialImages']:raw=m.upsert(raw,'entries','path',entry)
        return raw
    if name==D:
        text=raw.decode('utf-8-sig');assert text.count(BEGIN)==text.count(END)==1
        newline='\r\n' if '\r\n' in text else '\n'
        start=text.index(BEGIN);end=text.index(END)+len(END)
        text=text[:start]+spec['markdownSection'].replace('\n',newline)+text[end:]
        return (b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+text.encode('utf-8')
    raise AssertionError(name)

def validate(spec):
    assert spec['scope']=='ai3d-unity-first-sample-20261116'
    paths=spec['ownedPaths'];assert len(paths)==len(set(paths))
    required={x['path'] for x in spec['essentialImages']}
    assert len(required)==2 and required<=set(paths)
    for path in paths:
        p=PurePosixPath(path);assert not p.is_absolute() and '..' not in p.parts
        assert path.startswith(PREFIXES) and '/local/' not in path and '/Library/' not in path
        assert p.suffix.lower() not in {'.mp3','.wav','.mp4','.zip','.7z','.exe','.dll','.log'}
        assert p.suffix.lower()!='.png' or path in required
        assert (root/path).is_file() and (root/path).resolve().is_relative_to(root.resolve())
    for entry in spec['essentialImages']:assert hashlib.file_digest((root/entry['path']).open('rb'),'sha256').hexdigest()==entry['sha256']
    delivery=m.load((home/'unity-sample-delivery.json').read_bytes())
    assert delivery['humanReview'] is False and not delivery['youtubeUploaded'] and not delivery['webGameBuilt']
    assert delivery['integrity']['videoFrames']==2160 and delivery['nativeBuild']['errors']==0
    return sorted(paths)+sorted(m.SHARED)

def prepare():
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
    record=m.load((root/C).read_bytes())[KEY]
    record.update(status='unity-first-sample-ready',scope='One original 3D LOFI gaming room and production video. Current delivery is first native Unity sample; WebGL build explicitly deferred by user. No YouTube upload or public web deployment.',tripoAccountStatus='paid Studio login verified; hero and headphones generated/imported; 175 credits used',latestUserEvidence=['트리포 한달 결제하고 로그인해뒀어','웹 빌드는 나중에, Unity 샘플부터 진행'],sampleDelivery='projects/ai-3d-lofi-gaming-room/production/unity-sample-delivery.json',sampleReviewUrl='http://127.0.0.1:9319/',webBuildDeferred=True,updatedAtKst=now)
    images=[]
    for path in (root/'unity/LofiGamingRoomWeb/Assets/LofiRoom/Models').rglob('*.png'):
        if path.name not in {'tripo_node_78e9fd4b-b711-4bdf-93c3-1d7a766d3e04_BaseColor.png','headphones-native_basecolor.png'} or '/hero-idle/' in path.as_posix():continue
        images.append({'path':path.relative_to(root).as_posix(),'purpose':'required-scene-asset','reason':'Actual imported Tripo model BaseColor atlas referenced by the Unity LOFI review scene; visually checked in the native model close-up.','sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest(),'reviewedAt':now,'project':SLUG})
    paths=subprocess.check_output(['git','ls-files','-c','-o','--exclude-standard','-z','--',*PREFIXES],cwd=root).decode().split('\0')
    paths=sorted({p for p in paths if p and '/local/' not in p and '__pycache__' not in p}|{SPEC.relative_to(root).as_posix()})
    section='''<!-- AI3D-LOFI-GAMING-ROOM-20261116 -->
## AI 3D LOFI 게이밍룸 제작

| 영상 | 제작 | 검수 | 게시 |
|---|---|---|---|
| [AI로 만드는 3D LOFI 게이밍룸](../projects/ai-3d-lofi-gaming-room/planning/outline.md) | Tripo 캐릭터·헤드폰 + 기본 걷기·대기 · Unity 첫 샘플/Windows 실행 파일 완성 · 전체 제작 영상은 진행 중 | [36초 FHD60 샘플 보기](http://127.0.0.1:9319/) · 사용자 검수 대기 | 미업로드·예약 없음 |

Spirit City의 편안한 방 경험을 참고해 자체 3D 게이밍룸을 만든다. 공식 Unity CLI·MCP로 실제 임포트·씬·실행·캡처·빌드를 수행했다. Studio 175크레딧 사용. 사용자 요청으로 WebGL 설치·빌드는 뒤로 미뤘다. 방 세부 장식·앉기·독서와 전체 영상은 남아 있다. [샘플·검사 기록](../projects/ai-3d-lofi-gaming-room/production/unity-sample-delivery.json) · [도구/MCP 실행표](../projects/ai-3d-lofi-gaming-room/planning/mcp-tools.md). 기존 프로젝트와 외부 작업은 보존했다.
<!-- AI3D-LOFI-GAMING-ROOM-20261116-END -->'''
    spec={'scope':'ai3d-unity-first-sample-20261116','scopeRecord':record,'worklistSet':{'productionComplete':False,'productionStatus':'Tripo 캐릭터·헤드폰 · Unity 첫 샘플/Windows 빌드/36초 FHD60 완료 · 전체 영상 제작 중','reviewStatus':'첫 Unity 샘플 사용자 검수 대기; 전체 영상 미완성','executionStatus':'unity-first-sample-ready','notes':'공식 Unity CLI/MCP 실제 실행. WebGL은 사용자 요청으로 보류. 앉기·독서·방 상세와 전체 제작 영상은 남음.','sampleAvailable':True,'sampleReviewUrl':'http://127.0.0.1:9319/','updatedAt':now},'essentialImages':images,'markdownSection':section,'ownedPaths':paths}
    SPEC.write_bytes((json.dumps(spec,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'preparedPaths':len(paths),'essentialImages':len(images)},ensure_ascii=True))

m.SHARED={C,W,D,I};m.overlay=overlay;m.validate=validate
if __name__=='__main__':
    if '--prepare' in sys.argv:prepare()
    else:
        if '--spec' not in sys.argv:sys.argv[1:1]=['--spec',str(SPEC)]
        m.main()

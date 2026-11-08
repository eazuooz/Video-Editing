"""Selective latest-game delivery commit; preserve foreign working/index bytes."""
from pathlib import Path, PurePosixPath
import importlib.util, sys, re, hashlib, struct
sys.dont_write_bytecode = True
H = Path(__file__).resolve().parent
R = H.parents[3]
sp = importlib.util.spec_from_file_location('scope',R/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py')
m = importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
P='projects/ai-2d-game-assets/project.json'
L='projects/ai-2d-game-assets/production/review-ledger.json'
C='shared/publishing/video-production-control.json'
W='shared/publishing/video-worklist.json'
D='docs/VIDEO_WORKLIST.md'
I='shared/git-essential-images.json';G='.gitignore'
THUMB='projects/ai-2d-game-assets/publishing/room-v3-upload-20261108/thumbnail-v1.png'
PREFIXES=('projects/ai-2d-game-assets/production/room-v4-video/','projects/ai-2d-game-assets/publishing/room-v3-upload-20261108/')

def overlay(name,raw,s):
    if name in {P,L}:
        for ch in s['projectChanges' if name==P else 'ledgerChanges']:
            assert ch['path'][0] in ({'status','video','delivery','currentRevision','paths','editing'} if name==P else {'stage','master','previousMasters','currentRevision','technicalQa','sampledVisualQa','narrationLevelContinuity','platform','reviewUrl'})
            raw=m.patch(raw,ch['path'],ch['value'])
        return raw
    if name==C:
        for key,value in s['controls'].items():
            assert key in {'ai2dUpload20261108','ai2dLatestGameVideo20261108'}
            raw=m.patch(raw,[key],value)
        return raw
    if name==W:
        rows=m.load(raw)['rows'];ids=[i for i,r in enumerate(rows) if r['id']=='S-AI2D'];assert len(ids)==1
        for key,value in s['worklistSet'].items():
            assert key in {'productionComplete','productionStatus','reviewStatus','humanApproval','platformStatus','executionStatus','updatedAt','reviewUrl','notes','evidence','latestRevision','supersededPrivateDraft'}
            raw=m.patch(raw,['rows',ids[0],key],value)
        return raw
    if name==D:
        text=raw.decode('utf-8-sig');rows=re.findall(r'^\| S-AI2D \| .*?$',text,re.M);assert len(rows)==1
        cols=rows[0].rstrip('\r').split('|');assert len(cols)==7
        cols[3]=' 1080p60·20분55초 v6게임 반영 ';cols[4]=' room-v4-video 사용자 검수 대기 ';cols[5]=' 새판 미업로드 · 이전 비공개 초안 보존 · 웹 v6 공개 '
        text=text.replace(rows[0],'|'.join(cols)+ ('\r' if rows[0].endswith('\r') else ''))
        return (b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+text.encode('utf-8')
    if name==I:
        return m.upsert(raw,'entries','path',s['essentialImage'])
    if name==G:
        newline=b'\r\n' if b'\r\n' in raw else b'\n';exception='!/'+THUMB
        if exception not in raw.decode('utf-8-sig').splitlines():raw+=(b'' if raw.endswith(b'\n') else newline)+exception.encode()+newline
        return raw
    raise AssertionError(name)

def validate(s):
    assert s['scope']=='ai2d-latest-game-v6-local-review-20261108'
    delivery=m.load((H/'delivery.json').read_bytes())
    assert delivery['userReview'] is False and delivery['youtubeUploaded'] is False
    master=delivery['files'][0]
    assert master['sha256']=='97003cf1db875a25aa862f1cf0acdf68fe21d8667b094b268af0be4b12ed848f'
    assert hashlib.file_digest(Path(master['path']).open('rb'),'sha256').hexdigest()==master['sha256']
    c=s['controls']['ai2dLatestGameVideo20261108'];assert c['sameVersionUserReview'] is False and not c['youtubeAuthorizedNow']
    assert s['controls']['ai2dUpload20261108']['status']=='superseded-private-draft-rebuild-required'
    pixels=(R/THUMB).read_bytes();assert pixels[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',pixels[16:24])==(1280,720)
    assert hashlib.sha256(pixels).hexdigest()==s['essentialImage']['sha256'] and len(pixels)<2*1024*1024
    paths=s['ownedPaths'];assert len(paths)==len(set(paths)) and THUMB in paths
    for name in paths:
        p=PurePosixPath(name);assert not p.is_absolute() and '..' not in p.parts
        assert any(name.startswith(prefix) for prefix in PREFIXES) and '/local/' not in name
        assert name==THUMB or p.suffix in {'.json','.md','.py','.cjs','.txt'}
        assert (R/name).is_file()
    return sorted(paths)+sorted(m.SHARED)

m.SHARED={P,L,C,W,D,I,G};m.overlay=overlay;m.validate=validate
if __name__=='__main__':
    if '--spec' not in sys.argv:sys.argv[1:1]=['--spec',str(H/'delivery-commit-spec.json')]
    m.main()

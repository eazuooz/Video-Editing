"""Selective revision metadata commits; preserve all unrelated staging."""
import importlib.util,sys
from pathlib import PurePosixPath
from common import *
C='shared/publishing/video-production-control.json';W='shared/publishing/video-worklist.json';D='docs/VIDEO_WORKLIST.md'
BEGIN='<!-- ANIMATION-GAMEPLAY-V8-20261115 -->';END='<!-- ANIMATION-GAMEPLAY-V8-20261115-END -->'
SPEC=WORK/'commit-spec.json';PREFIX=HERE.relative_to(ROOT).as_posix()+'/'
spec=importlib.util.spec_from_file_location('scoped_v8',ROOT/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py')
scoped=importlib.util.module_from_spec(spec);spec.loader.exec_module(scoped)
def overlay(name,raw,data):
    if name==C:return scoped.patch(raw,[KEY],data['control'])
    if name==W:
        for row in data['rows']:
            indices=[i for i,x in enumerate(scoped.load(raw)['rows']) if x['id']==row['id']];assert len(indices)==1
            raw=scoped.patch(raw,['rows',indices[0],'gameplayRevision'],row['revision'])
        return raw
    if name==D:
        a,z=raw.find(BEGIN.encode()),raw.find(END.encode());assert (a<0)==(z<0)
        nl='\r\n' if b'\r\n' in raw else '\n';block=data['markdown'].replace('\n',nl).encode()
        return raw[:a]+block+raw[z+len(END):] if a>=0 else raw+(nl*2).encode()+block+nl.encode()
    raise AssertionError(name)
def validate(data):
    assert data['scope']==KEY and data['control']['scope']==SCOPE and data['control']['preserved']==['A06']
    assert not any(data['control'][x] for x in ['youtubeAuthorized','driveAuthorized','schedulingAuthorized','deletionAuthorized'])
    for name in data['ownedPaths']:
        p=PurePosixPath(name);assert name.startswith(PREFIX) and '..' not in p.parts and (p.suffix in {'.py','.json','.html','.cjs','.txt','.md'} or p.name=='.gitignore') and 'local' not in p.parts
    return sorted(data['ownedPaths'])+sorted(scoped.SHARED)
def prepare():
    plan=read(HERE/'plan.json');now=stamp();done=[];rows=[]
    table=[BEGIN,'','## 애니메이션 실제 게임 분석 수정','','[통합 검수표](http://127.0.0.1:9302/)','','A06 원본 그대로 보존.나머지15편만 실제 게임/원리 도식/화면 대응 대본으로 수정.기존 개론·마지막 정리·완성본 보존.플랫폼 변경 없음.','','| 편 | 주제 | 제작 상태 | 사용자 검수 |','|---|---|---|---|']
    for ep in [f'A{i:02}' for i in range(3,19)]:
        original=next(e for e in plan['episodes'] if e['id']==ep);receipt=OUTPUT/ep/'delivery.json'
        ready=receipt.is_file() and not read(receipt).get('visualReviewPending',True)
        if ready:done.append(ep)
        status='A06 그대로 보존' if ep=='A06' else '로컬 수정본 검수 가능' if ready else '실제 영상·원리 도식·대본 대응 제작 중'
        revision=dict(revision='gameplay-v8',status=status,updatedAt=now,preservedExactly=ep=='A06',humanReviewed=False,platformChanged=False,
                      reviewUrl='http://127.0.0.1:9302/'+ep+'/' if ready else None)
        if ready:revision.update(delivery=str(receipt),captionedMasterSha256=next(f['sha256'] for f in read(receipt)['files'] if f['kind']=='captioned.mp4'))
        rows.append(dict(id=ep,revision=revision));table.append(f'| {ep} | {original["title"].split("|")[0]} | {status} | {"기존 상태 유지" if ep=="A06" else "대기"} |')
    table+=['',END];markdown='\n'.join(table)
    control=dict(id='animation-gameplay-v8',requestedAt=plan['requestedAt'],userEvidence=plan['userEvidence'],scope=SCOPE,preserved=['A06'],excludedUploaded=['A01','A02'],
        status='local-final-review-ready' if len(done)==16 else 'gameplay-diagram-and-narration-revision',renderAuthorized=True,ttsAuthorized=True,
        youtubeAuthorized=False,driveAuthorized=False,schedulingAuthorized=False,deletionAuthorized=False,humanReviewed=False,platformChanged=False,
        resources=plan['resources'],completed=done,plan=str(HERE.relative_to(ROOT)/'plan.json'),checkpoint=str(HERE.relative_to(ROOT)/'checkpoint.json'),updatedAt=now)
    save(HERE/'checkpoint.json',dict(stage=control['status'],scope=SCOPE,preserved=['A06'],completed=done,remaining=[e for e in SCOPE if e not in done],updatedAt=now,humanReviewed=False,platformChanged=False))
    (HERE/'review-table.md').write_text(markdown+'\n',encoding='utf-8')
    save(SPEC,dict(scope=KEY,control=control,rows=rows,markdown=markdown,ownedPaths=sorted(p.relative_to(ROOT).as_posix() for p in HERE.iterdir() if p.is_file() and (p.suffix in {'.py','.json','.html','.cjs','.txt','.md'} or p.name=='.gitignore'))))
    print(SPEC)
if __name__=='__main__':
    if sys.argv[1:]==['--prepare']:prepare()
    else:scoped.SHARED={C,W,D};scoped.overlay=overlay;scoped.validate=validate;scoped.main()

"""Register the revised A01 and the verified A02 Studio receipt without touching other staged work."""
from pathlib import Path
import json,sys
from datetime import datetime,timezone
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/unreal-kit-v2'
sys.path.insert(0,str(R/'projects/unreal-engine-6-verse-gameplay/production'))
from commit_reviews import engine,overlay,C,W,D
engine.SHARED={C,W,D};engine.overlay=overlay
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
rel=lambda p:p.relative_to(R).as_posix()
NATIVE='GameAnimationSample/Content/YamyamA01/assigning_v2/'
A02='projects/animation-exaggeration/publishing/studio-v4/'
SERVER='projects/unreal-engine-6-verse-gameplay/production/serve_reviews.cjs'
def validate(spec):
    assert set(spec['table'])=={x['id'] for x in spec['rows']}=={'A01','A02'}
    assert set(spec['grants'])=={'animation-assigning-unreal-kit-v2'}
    for name in spec['ownedPaths']:
        assert (R/name).is_file() and '/local/' not in name and '__pycache__' not in name
        assert name.startswith(('projects/'+P.name+'/',NATIVE,A02)) or name==SERVER
        assert not name.startswith(NATIVE+'Animations/')
    return sorted(set(spec['ownedPaths'])|engine.SHARED)
engine.validate=validate
def prepare():
    result=read(H/'checkpoint.json')
    assert result['status']=='local-delivery-user-review-pending'
    length=round(result['durationSeconds']);span=f'{length//60}분 {length%60}초'
    stamp=datetime.now(timezone.utc).isoformat();rows=[dict(x) for x in read(R/W)['rows'] if x['id'] in ('A01','A02')]
    for row in rows:
        if row['id']=='A01':
            row.update(updatedAt=stamp,productionComplete=True,productionStatus='언리얼 애니메이션 샘플 시연 다섯 장면 · '+span,executionStatus='언리얼 수정본 로컬 검수 대기',reviewStarted=True,reviewStatus='최신본 기술 검사 완료 · 사용자 시청·청취 대기',humanApproval='A01 언리얼 시연 및 해설 보강 명시 승인 · 새 버전 사람 검수 대기',platformStatus='최신본 로컬 검수',localMasterAvailable=True,captionedMasterSha256=result['captionedMasterSha256'],deliveryLedger=rel(H/'checkpoint.json'))
            for name in [rel(H/'checkpoint.json'),rel(H/'edit-plan-final.json')]:
                if name not in row['evidence']:row['evidence'].append(name)
        else:
            row.update(updatedAt=stamp,platformStatus='YouTube 비공개 · 광고 적합성 및 저작권 검사 완료',executionStatus='비공개 저장 확인 · 한영 자막 및 광고 적합성 검사 완료')
    table={}
    for line in (R/D).read_text('utf-8-sig').splitlines():
        if line.startswith('| A01 | ') or line.startswith('| A02 | '):
            ident=line.split('|')[1].strip()
            status=f'[언리얼 시연 수정본 · {span}](http://127.0.0.1:9246/kit/) · 사용자 검수 대기' if ident=='A01' else '[YouTube 비공개 · 쿨라·리리](https://youtu.be/BDmb5VwES5M) · 광고 및 저작권 검사 완료'
            table[ident]=line[:line.rfind(' | ',0,len(line)-2)]+' | '+status+' |'
    owned={rel(f) for f in H.iterdir() if f.is_file() and f.suffix in ('.py','.json','.txt')}
    owned.update(rel(f) for f in (R/NATIVE).rglob('*') if f.is_file() and 'Animations' not in f.relative_to(R/NATIVE).parts and (f.suffix in ('.umap','.uasset') or f.name=='.gitignore'))
    owned.update([SERVER,rel(P/'project.json'),rel(P/'production/delivery-output.json'),A02+'upload.json',A02+'description.ko.txt',A02+'description.en.txt'])
    for name in ['rebuild.json','production/rebuild-manifest.json']:
        if (P/name).is_file():owned.add(rel(P/name))
    grant='animation-assigning-unreal-kit-v2';control=read(R/C)['scopedProductionAuthorizations']
    spec={'rows':rows,'table':table,'grants':{grant:control[grant]},'ownedPaths':sorted(owned)}
    (L/'git-scope.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':
    if '--prepare' in sys.argv:prepare()
    else:engine.main()

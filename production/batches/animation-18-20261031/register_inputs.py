"""Record the approved finite set's prepared inputs, without marking any unbuilt master reviewed."""
from datetime import datetime,timezone
from pathlib import Path
import json,sys
B=Path(__file__).resolve().parent;R=B.parents[2]
sys.path.insert(0,str(B))
from register_local import engine,read,save,rel
E={f'A{n:02}' for n in range(7,19)}
def validate(spec):
    ids={x['id'] for x in spec['rows']};assert ids and ids<=E and ids==set(spec['table'])
    current=read(R/'shared/publishing/video-worklist.json')['rows']
    slugs={x['slug'] for x in current if x['id'] in ids}
    for s in spec['ownedPaths']:
        ok=s.startswith(rel(B)+'/') or any(s.startswith('projects/'+slug+'/') for slug in slugs)
        native=any(s.startswith(f'GameAnimationSample/Content/YamyamAnimationSeries/{ep}/') for ep in ids)
        assert (ok or native) and '/local/' not in s and (R/s).is_file() and (R/s).suffix in ('.json','.txt','.py','.cjs','.umap','.uasset')
    return sorted(set(spec['ownedPaths'])|engine.SHARED)
engine.validate=validate
def prepare():
    current=read(R/'shared/publishing/video-worklist.json')['rows']
    checkpoint=read(B/'checkpoint.json');batch=read(B/'batch.json')
    assert E<=set(batch['episodeIds']) and batch['productionAuthorized'] and not batch['youtubeAuthorized']
    doc=(R/engine.D).read_text('utf-8-sig').splitlines();rows=[];table={};owned=set()
    summary={}
    for x in current:
        ep=x['id']
        if ep not in E:continue
        p=R/'projects'/x['slug'];h=p/'production/series-v1';l=p/'production/local/series-v1'
        if (h/'checkpoint.json').is_file():continue
        assert read(h/'production-binding.json')['episode']==ep and (h/'make_poses.py').is_file()
        selection=read(h/'source-selection.json');assert selection['examples'] and selection['referenceRole']=='research only'
        stages=(l/'native-build-receipt.json').is_file()
        if ep=='A09':stages=all((l/(k+'.mp4')).is_file() for k in read(h/'visual-plan.json')['rigs'])
        stage=('Manim 원본 시연 4개 렌더 완료' if ep=='A09' else '언리얼 비교 씬 빌드 완료') if stages else '시연 동작 작성 완료'
        status='한·영 대본과 실제 게임 장면 배치 완료 · '+stage
        evidence=list(x.get('evidence',[]))
        if rel(h/'production-binding.json') not in evidence:evidence.append(rel(h/'production-binding.json'))
        rows.append(dict(id=ep,productionStatus=status,executionStatus='통합 검수본 제작 중',reviewStatus='완성본 제작 중 · 사용자 검수 전',productionComplete=False,evidence=evidence))
        line=next(s for s in doc if s.startswith('| '+ep+' | '))
        table[ep]=line[:line.rfind(' | ',0,len(line)-2)]+f' | {status} |'
        owned.update(rel(f) for f in h.iterdir() if f.is_file() and f.suffix in ('.py','.json','.txt'))
        owned.add(rel(p/'project.json'))
        native=R/'GameAnimationSample/Content/YamyamAnimationSeries'/ep
        owned.update(rel(f) for f in native.rglob('*') if f.is_file() and f.suffix in ('.umap','.uasset'))
        summary[ep]=dict(script=rel(h/'production-binding.json'),editableStudies=rel(h/'make_poses.py'),preparedStage=stages)
    checkpoint['preparedLocalInputs']=summary
    checkpoint['reviewCollectionWithFileFolders']='http://127.0.0.1:9252/'
    checkpoint['currentWork']=['완성된 A01–A06은 통합 검수 목록에 있음','A07–A18 대본·한영 자막 문안·실제 장면과 시연 입력 준비. 각 완성본은 음성·편집·검사 후에만 등록.']
    checkpoint['costlyJobSummary']={'assembledReviewEpisodes':checkpoint['completedLocalDeliveries'],'queue':'A07–A18: serialized voice and native or mathematical studies; assemble, technical review and collect four local files.','humanReview':'pending on the exact locally collected masters'}
    checkpoint['updatedAt']=datetime.now(timezone.utc).isoformat();save(B/'checkpoint.json',checkpoint)
    owned.update(rel(f) for f in (B/'native').glob('*.py'))
    owned.update(rel(B/name) for name in ('checkpoint.json','footage-catalog.json','register_inputs.py','bind_reviewed_script.py','assemble_episode.py','render_voice.py','readback.py','register_local.py','finish_queue.py','review-collection.cjs') if (B/name).is_file())
    dest=R/'projects/animation-attack-poses/production/local/series-v1/inputs-commit-spec.json'
    save(dest,dict(rows=rows,table=table,ownedPaths=sorted(owned)))
if __name__=='__main__':
    if '--prepare' in sys.argv:prepare()
    else:engine.main()

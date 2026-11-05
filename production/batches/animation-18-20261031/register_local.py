"""Register one completed animation master and update just its worklist row."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent;R=B.parents[2];sys.path.insert(0,str(R/'projects/unreal-engine-6-verse-gameplay/production'))
from commit_reviews import engine,overlay,W,D
engine.SHARED={W,D};engine.overlay=overlay
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(R).as_posix()
def validate(spec):
 ep=spec['episode'];assert {x['id'] for x in spec['rows']}==set(spec['table'])=={ep}
 episode=next(row for row in read(R/W)['rows'] if row['id']==ep);slug=episode['slug']
 for name in spec['ownedPaths']:
  assert (R/name).is_file() and '/local/' not in name and '__pycache__' not in name
  assert name.startswith(('projects/'+slug+'/',rel(B)+'/',f'GameAnimationSample/Content/YamyamAnimationSeries/{ep}/'))
 return sorted(set(spec['ownedPaths'])|engine.SHARED)
engine.validate=validate
def prepare(ep):
 rows=read(R/W)['rows'];row=dict(next(z for z in rows if z['id']==ep));slug=row['slug'];p=R/'projects'/slug;h=p/'production/series-v1';local=p/'production/local/series-v1'
 ledger=read(h/'checkpoint.json');assert ledger['episode']==ep
 seconds=round(ledger['durationSeconds']);span=f'{seconds//60}분 {seconds%60}초';pct=round(ledger['gameplayShare']*100)
 row.update(productionComplete=True,executionStatus='로컬 제작 완료 · 통합 검수 대기',productionStatus=f'1080p60 · {span} · 실제 영상 {pct}% / 설명 {100-pct}%',reviewStarted=True,reviewStatus='기술 검수 완료 · 사용자 통합 검수 대기',humanApproval='애니메이션 재생목록의 남은 편 일괄 제작 요청 · 현재 버전 실제 사용자 시청 대기',localMasterAvailable=True,captionedMasterSha256=ledger['captionedMasterSha256'],deliveryLedger=rel(h/'checkpoint.json'),platformStatus='로컬 검수 · YouTube 미업로드',updatedAt=datetime.now(timezone.utc).isoformat())
 if rel(h/'checkpoint.json') not in row['evidence']:row['evidence'].append(rel(h/'checkpoint.json'))
 doc=(R/D).read_text('utf-8-sig').splitlines();line=next(x for x in doc if x.startswith('| '+ep+' | '))
 line=line[:line.rfind(' | ',0,len(line)-2)]+f' | [전체 검수본 · {span}](http://127.0.0.1:9248/{ep}/captioned.mp4) · 사용자 통합 검수 대기 |'
 # Reflect only completed four-output masters, including the prior three.
 completed=['A01','A02','A03']
 for x in rows:
  if x['id'] not in [f'A{i:02}' for i in range(4,19)]:continue
  ledgerfile=R/'projects'/x['slug']/'production/series-v1/checkpoint.json'
  if ledgerfile.is_file():completed.append(x['id'])
 batchState=read(B/'checkpoint.json');batchState.update(completedLocalDeliveries=completed,completedLocalReviews=[],currentEpisode=ep,currentWork=['완성본 '+', '.join(completed)+' · 나머지 편 순차 제작'],nextAction='사용자가 선택한 A04–A18의 통합 검수본 제작. 공개·예약·다른 편 업로드는 별도.',reviewCollection='http://127.0.0.1:9248/',updatedAt=datetime.now(timezone.utc).isoformat())
 batchState['batchContinuationUserEvidence']={'message':'나머지 작업 애니메이션 재생목록 전부 해줘 검수 모아서 한번에 할게','scope':'A04–A18 to verified local outputs. Separate private uploads apply only where explicitly requested.'};save(B/'checkpoint.json',batchState)
 if len(completed)==18:
  batchState.update(status='local-batch-delivered-user-review-pending',currentWork=['18편 전체 로컬 통합 검수 가능'],reviewCollection='http://127.0.0.1:9274/',offlineReviewIndex='output/animation-series-review/index.html',nextAction='사용자 통합 검수.')
  save(B/'checkpoint.json',batchState)
 owned={rel(f) for f in h.iterdir() if f.is_file() and f.suffix in ('.py','.txt','.json')}
 owned.update(rel(f) for f in (p/'project.json',p/'rebuild.json',p/'production/delivery-output.json',B/'checkpoint.json',B/'review-collection.cjs',B/'prepare_selected_episode.py',B/'assemble_episode.py',B/'render_voice.py',B/'readback.py',B/'register_local.py') if f.is_file())
 owned.update(rel(f) for f in (B/'native').glob('*.py'))
 owned.update(rel(B/name) for name in ('bind_reviewed_script.py','finish_queue.py','footage-catalog.json','translate_drafts.py','gpu_slot.py','screen_share.py','series_voice.py') if (B/name).is_file())
 native=R/'GameAnimationSample/Content/YamyamAnimationSeries'/ep
 owned.update(rel(f) for f in native.rglob('*') if f.is_file() and f.suffix in ('.umap','.uasset'))
 dest=local/'commit-spec.json';save(dest,{'episode':ep,'rows':[row],'table':{ep:line},'ownedPaths':sorted(owned)})
if __name__=='__main__':
 if '--prepare' in sys.argv:prepare(sys.argv[sys.argv.index('--prepare')+1])
 else:engine.main()

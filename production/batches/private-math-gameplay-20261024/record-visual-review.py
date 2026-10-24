"""Call only after actual frame/mobile inspection and observed playback receipts."""
from pathlib import Path
import json,sys,datetime
B=Path(__file__).resolve().parent;R=B.parents[2]
def rd(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
proofpath=B/sys.argv[1];proof=rd(proofpath)['results'];entries={e['id']:e for e in rd(B/'edit-list-audit.json')['entries']}
for eid in sys.argv[2:]:
 e=entries[eid];h=R/'projects'/e['slug']/'production/gameplay-v3';o=rd(h/'outputs.json');cap=next(x for x in o['outputs'] if x['path'].endswith('.captioned.mp4'));v=proof[eid]
 assert cap['sha256']==v['sha256'] and v['error'] is None and v['rate']==1
 assert (h/'technical-qa.json').exists()
 retained=o.get('retainedByteIdentical',False)
 frames=f'shared/output/private-math-gameplay-20261024/retention-review/{eid}-sheet0.jpg' if retained else f'shared/output/private-math-gameplay-20261024/final-review/{eid}-sheet0.jpg'
 if eid=='M08':frames='shared/output/private-math-gameplay-20261024/final-caption-review/m08-sheet0.jpg'
 assert (R/frames).exists()
 report=dict(status='visual-pass',checkedAt=datetime.datetime.now().astimezone().isoformat(),episode=eid,captionedSha256=cap['sha256'],frameEvidence=frames,playbackEvidence=str(proofpath.relative_to(R)),playback=v,checks=['Concept-matched visible target and action/result','Guides on inspected targets; no claimed hidden-engine measurements','Game/model labels and fixed final captions clear','Native-speed intervals and original joins replayed','375px readability inspected'],retainedByteIdentical=retained,actualWholeListening=False,humanReview='pending',scope='Changed visuals and joins only; original narration and lesson remain unchanged.')
 save(h/'visual-review.json',report)
 index=R/'output'/f'{e["slug"]}-gameplay-v3/index.html';text=index.read_text('utf8');text=text.replace('<b>내부 검수 중</b>','<b>변경 화면·연결 검수 완료 · 사용자 검수 대기</b><p>전체 최종 청취는 별도입니다.</p>');index.write_text(text,encoding='utf8')
 print(eid,'visual review recorded',flush=True)

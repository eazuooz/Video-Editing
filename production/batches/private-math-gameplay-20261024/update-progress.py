"""Publish only evidence-backed local status, never infer human approval."""
from pathlib import Path
import json,datetime,html,hashlib
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
def rd(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=datetime.datetime.now().astimezone().isoformat();c=rd(B/'checkpoint.json');ready=0;encoded=0;retained=0
for e in c['entries']:
 h=R/'projects'/e['slug']/'production/gameplay-v3';plan=B/f"{e['id'].lower()}-gameplay-plan.json"
 e['humanReview']='pending'
 e['newReviewReady']=False
 if (h/'outputs.json').exists():
  o=rd(h/'outputs.json')
  if o.get('planSha256') and o['planSha256']!=hashlib.sha256(plan.read_bytes()).hexdigest():
   e['status']='최신 장면 수정 반영 중';continue
  isret=o.get('retainedByteIdentical',False);retained+=int(isret);encoded+=int(not isret);e['newOutput']=str(Path('output')/(e['slug']+'-gameplay-v3')).replace('\\','/');e['newRender']=not isret;e['status']='기존 파일 재검수 중' if isret else '전체 렌더 완료 · 화면/연결 검수 중';e['technicalQa']=(h/'technical-qa.json').exists()
  if (h/'visual-review.json').exists():
   v=rd(h/'visual-review.json');cap=next(x for x in o['outputs'] if x['path'].endswith('.captioned.mp4'))
   if v.get('captionedSha256')==cap['sha256'] and v.get('status')=='visual-pass':
    e['status']='시각 검수 완료 · 사용자 검수 대기';e['actualFinalReview']='changed-visuals-and-playback-only';e['wholeListening']=False;e['newReviewReady']=True;ready+=1
 elif (h/'patches.json').exists():e['status']='게임 구간 합성 완료 · 구간 검수 중'
 elif plan.exists():e['status']='실제 장면/표식 위치 확인 · 구간 제작 중'
 else:e['status']='기존 장면 재검수 중 · 보존 여부 확인'
evidence='시각 검수 완료는 실제 변경 화면·연결과 파일 검사를 뜻합니다. 전체 최종 청취와 사용자 승인은 별도이며, 검수 전 영상은 완료로 세지 않습니다.'
complete=ready==len(c['entries'])
c.update(updatedAt=now,ready=ready,encoded=encoded,retained=retained,status='local-review-ready' if complete else 'gameplay-only-revision-active',current='human-local-review' if complete else 'gameplay-only-revision',nextAction='User reviews local complete videos; whole listening is not inferred. No upload or next production authorized.' if complete else 'Finish patched segments, inspect actual frames and joins, then encode remaining scoped lectures.');save(B/'checkpoint.json',c)
wpath=R/'shared/publishing/video-worklist.json';w=rd(wpath);w['privateMathPolish']['gameplayTimingRevision'].update(status=f'시각 검수 {ready}/18 · 수정 렌더 {encoded}/15 · 기존 보존 {retained}/3',readyCount=ready,renderedCount=encoded,retainedCount=retained,entries=[{k:e.get(k) for k in ['id','slug','title','status','newOutput','newReviewReady','wholeListening']} for e in c['entries']]);save(wpath,w)
rows=[];hrows=[]
for e in c['entries']:
 link=f"[수정본](../{e['newOutput']}/index.html)" if e.get('newOutput') else '제작 중'
 rows.append(f"| {e['id']} | {e['title']} | {e['status']} | {link} | 미승인 |")
 url='../../'+e['newOutput']+'/index.html' if e.get('newOutput') else None
 hrows.append('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in [e['id'],e['title'],e['status']])+('<td><a href="'+url+'">수정본 보기</a></td>' if url else '<td>제작 중</td>')+'<td>미승인</td></tr>')
report=f'# 게임수학 실제 게임 장면 재검수\n\n갱신: {now}\n\n**시각 검수 완료 {ready}/18 · 수정 렌더 완료 {encoded}/15 · 적합한 기존 영상 보존 {retained}/3.** 설명·수식·애니메이션·음성·전체 길이를 보존하고 게임 장면·기즈모·연결을 수정합니다.\n\n{evidence}\n\n| 번호 | 강의 | 진행 상태 | 검수 링크 | 사용자 검수 |\n|---|---|---|---|---|\n'+'\n'.join(rows)+'\n'
(B/'review-table.md').write_text(report,encoding='utf8')
doc=R/'docs/GAME_MATH_PRIVATE_POLISH.md';text=doc.read_text('utf-8-sig');start='<!-- GAMEPLAY-20261024-START -->';end='<!-- GAMEPLAY-20261024-END -->';text=text.split(start)[0]+start+'\n'+report+'\n'+end+text.split(end,1)[1];doc.write_text(text,encoding='utf8')
O=R/'output/private-math-gameplay-20261024';O.mkdir(exist_ok=True)
(O/'index.html').write_text(f'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>게임수학 게임 장면 수정 검수표</title><style>body{{background:#101412;color:#f5f5ef;font:17px/1.6 system-ui;margin:28px}}h1{{color:#ffd773}}table{{border-collapse:collapse;width:100%}}td,th{{padding:12px;text-align:left;border-bottom:1px solid #455047}}a{{color:#80d3a2}}.scroll{{overflow:auto}}</style><h1>게임수학 게임 장면 수정 검수표</h1><p>시각 검수 <b>{ready} / 18</b> · 수정 렌더 {encoded} / 15 · 기존 보존 {retained} / 3</p><p>기존 설명·음성·순서·길이 보존. 게임 장면, 표식, 연결만 수정합니다.</p><p>{evidence}</p><p>갱신: {now}</p><div class="scroll"><table><tr><th>번호</th><th>강의</th><th>상태</th><th>영상</th><th>사용자 검수</th></tr>'+''.join(hrows)+'</table></div></html>',encoding='utf8')
print(f'Visual {ready}/18; encoded {encoded}/15; retained {retained}/3')

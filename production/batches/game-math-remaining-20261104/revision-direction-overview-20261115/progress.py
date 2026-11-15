"""A local, explicit review table. Never infer YouTube state from local renders."""
import json,os,sys,html,subprocess
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];HUB=ROOT/'output/game-math-direction-overview-20261115'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def block(path,start,end,value):
 s=path.read_text(encoding='utf8');text=start+'\n'+value.rstrip()+'\n'+end
 if start in s:s=s[:s.index(start)]+text+s[s.index(end)+len(end):]
 else:s=s.rstrip()+'\n\n'+text+'\n'
 path.write_text(s,encoding='utf8')
def junction(path,target):
 target=Path(target).resolve();assert target.is_dir()
 assert path.absolute().is_relative_to(HUB.absolute())
 if path.exists():assert path.resolve()==target;return
 command="New-Item -ItemType Junction -Path '"+str(path).replace("'","''")+"' -Target '"+str(target).replace("'","''")+"' | Out-Null"
 subprocess.run(['powershell','-NoProfile','-Command',command],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
def main():
 HUB.mkdir(exist_ok=True);plan=read(HERE/'plan.json');state=[];ht=[];md=[]
 visual=read(HERE/'visual-review.json') if (HERE/'visual-review.json').exists() else dict(episodes=[])
 inspected={r['id'] for r in visual['episodes'] if r.get('passed')}
 for row in plan['episodes']:
  eid=row['id'];receipt=HERE/'deliveries'/f'{eid}.json';delivery=read(receipt) if receipt.exists() else None
  publishable=bool(delivery) and (eid not in ('M25','M26','M28','M33') or delivery.get('correctionsComplete'))
  status='내부 검수 완료 · 사용자 검수 대기' if eid in inspected else '렌더·재생 검사 완료 · 화면 검수 중' if delivery else '수정 렌더 대기 / 진행 중'
  if delivery and not publishable:status='렌더·재생 검사 완료 · 방향·수학 기호 표기 보정 중'
  record=dict(id=eid,title=row['title'],status=status,technicalQa=bool(delivery),visualQa=eid in inspected,humanReviewed=False,overviewAt=row['start'],recapAt=row['recapStart'])
  link='—'
  if publishable:
   dest=Path(delivery['files']['clean']['path']).parent;junction(HUB/eid,dest)
   link=f'<a href="{eid}/index.html">영상 검수</a>';record.update(files=delivery['files'],reviewPage=str(HUB/eid/'index.html'))
   buttons=''.join(f'<button data-time="{t}">{label}</button>' for label,t in [('개론',row['start']),('핵심 정리',row['recapStart'])])
   summaries=''.join('<li>'+html.escape(p['title'])+'<br><span>'+html.escape(p['meaning'])+'</span></li>' for p in row['recap'])
   (dest/'index.html').write_text(f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{eid} · {html.escape(row['title'])}</title><style>body{{background:#090b0b;color:#f4f2eb;font:18px/1.6 system-ui;max-width:1280px;margin:auto;padding:24px}}h1{{color:#e9ce83}}video{{width:100%;background:black}}a{{color:#73c7c2}}button{{background:#172522;color:#f4f2eb;border:1px solid #73c7c2;padding:10px 20px;margin:12px 12px 12px 0;font:inherit;cursor:pointer}}span{{color:#b0b7b2}}li{{margin-bottom:14px}}</style><a href="../index.html">전체 검수표</a><h1>{eid} · {html.escape(row['title'])}</h1><p>{status} · 1080p 60fps · {int(row['frames']/60)//60}분 {int(row['frames']/60)%60}초</p><video controls preload="metadata" src="{row['slug']}.captioned.mp4"></video><div>{buttons}</div><p><a href="{row['slug']}.clean.mp4">Clean MP4</a> · <a href="{row['slug']}.ko.srt">한국어 자막</a> · <a href="{row['slug']}.en.srt">영어 자막</a></p><h2>이번 편 핵심</h2><ol>{summaries}</ol><p>실제 이미지의 시점·앞쪽과 설명 방향을 구분해 확인해주세요. 기존 음성·속도·한영 자막을 유지했습니다.</p><script>const v=document.querySelector('video');for(const b of document.querySelectorAll('button'))b.onclick=()=>{{v.currentTime=Number(b.dataset.time);v.play()}};</script></html>''',encoding='utf8')
  state.append(record);ht.append(f'<tr><td>{eid}</td><td>{html.escape(row["title"])}</td><td>{status}</td><td>{link}</td></tr>')
  md.append(f'| {eid} | {row["title"]} | {status} | '+(f'[로컬 검수]({(HUB/eid/"index.html").as_posix()})' if publishable else '—')+' |')
 ready=sum(s['visualQa'] for s in state);encoded=sum(s['technicalQa'] for s in state)
 (HUB/'index.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>게임수학 M21–M33 · 방향·개론·정리 검수</title><style>body{background:#090b0b;color:#f4f2eb;font:17px/1.65 system-ui;max-width:1180px;margin:auto;padding:24px}h1{color:#e9ce83}a{color:#73c7c2}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #3b4540;padding:14px;text-align:left}p{max-width:1000px}.wrap{overflow-x:auto}</style><h1>게임수학 M21–M33 · 수정 검수표</h1><p>실제 이미지의 측면·위쪽 시점과 진행 방향을 맞추고, 몸의 방향과 속도·힘을 구분했습니다. 각 편은 실제 사례에서 개론·학습 순서로 이어지고, 끝에는 배운 핵심을 정리합니다.</p>'''+f'<p>13편 중 렌더·재생 검사 {encoded}편 / 내부 화면 검수 {ready}편 · 사용자 검수 전</p><div class="wrap"><table><thead><tr><th>번호</th><th>강의</th><th>상태</th><th>보기</th></tr></thead><tbody>'+''.join(ht)+'</tbody></table></div><p>기존 음성·설명 순서·길이·한영 자막 유지 · FHD 60fps</p></html>',encoding='utf8')
 payload=dict(scope=plan['scope'],status='all-thirteen-local-user-review-pending' if ready==13 else 'finite-local-render-and-internal-QA',encodedCount=encoded,localReadyCount=ready,rows=state,reviewHub=str(HUB/'index.html'),humanReviewed=False,platformChanged=False,updatedAt=datetime.now(timezone.utc).isoformat())
 save(HERE/'progress.json',payload);save(HERE/'checkpoint.json',payload)
 path=ROOT/'shared/publishing/video-worklist.json';j=read(path);j['mathDirectionOverview20261115']=payload
 for r in j['rows']:
  own=next((s for s in state if s['id']==r['id']),None)
  if own:r['directionOverview20261115']=own
 save(path,j)
 path=ROOT/'shared/publishing/video-production-control.json';j=read(path);own=j['explicitMathRemainingBatch20261104']['directionOverviewRevision20261115'];own.update(status=payload['status'],encodedCount=encoded,localReadyCount=ready,renderAuthorized=ready<13,costlyJobsClosed=ready==13,reviewHub=payload['reviewHub'],humanReviewed=False,checkedAt=payload['updatedAt']);save(path,j)
 block(ROOT/'docs/VIDEO_WORKLIST.md','<!-- MATH-DIRECTION-OVERVIEW-20261115 -->','<!-- MATH-DIRECTION-OVERVIEW-20261115-END -->','### M21–M33 방향·개론·정리 수정 검수\n\n'+f'렌더·재생 검사 {encoded}/13 · 내부 화면 검수 {ready}/13 · 사용자 검수 전.\n\n| 번호 | 강의 | 상태 | 링크 |\n|---|---|---|---|\n'+'\n'.join(md))
 print(encoded,'encoded;',ready,'visually inspected;',HUB/'index.html')
if __name__=='__main__':main()

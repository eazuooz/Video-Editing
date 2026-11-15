import html,json
from pathlib import Path
from datetime import datetime,timezone
from subject_revision import *
START='<!-- MATH-GAME-SUBJECTS-20261115 -->';END='<!-- MATH-GAME-SUBJECTS-20261115-END -->'
def update():
 rows=[];titles={x['id']:x['title'] for x in read(HERE.parent/'batch.json')['items']}
 for eid,e in EPISODES.items():
  p=work(e);ep=read(p/'encoded.json') if (p/'encoded.json').exists() else {};qa=read(p/'qa.json') if (p/'qa.json').exists() else {};worker=read(p/'worker.json') if (p/'worker.json').exists() else {}
  ready=qa.get('status')=='pass'
  files=ep.get('files',{})
  pending=read(HERE/'pending-corrections.json').get('episodes',{}) if (HERE/'pending-corrections.json').exists() else {}
  correction=pending.get(eid,{})
  if correction and correction.get('status')!='resolved':ready=False
  rendering={'rendering-clean':'Clean 렌더 중','rendering-captioned':'자막본 렌더 중','rendering-clean-and-captioned':'Clean·자막본 동시 렌더 중'}.get(worker.get('status'))
  state='기존 구·표면 설명 검수 완료 · 변경 없이 유지' if eid=='M21' and ready else '내부 검수 완료 · 사용자 검수 대기' if ready else rendering if rendering else '인코딩 완료 · 실제 화면 검수 중' if ep else '화면 보정 완료 · 렌더 대기' if correction and correction.get('status')!='resolved' else '실제 게임 이미지 합성·화면 검수 중'
  rows.append(dict(id=eid,title=titles.get(eid,e['slug']),slug=e['slug'],status=state,files=files,ready=ready,humanReviewed=False))
 hub=ROOT/'output/game-math-game-subjects-20261115';hub.mkdir(exist_ok=True)
 body=[]
 for row in rows:
  path=row['files'].get('captioned',{}).get('path')
  link='제작 중'
  if path and Path(path).exists():
   folder=Path(path).parent
   parts=[]
   if (folder/'index.html').exists():parts.append(f'<a href="{(folder/"index.html").as_uri()}">재생·구간 이동</a>')
   parts.extend(f'<a href="{Path(row["files"][k]["path"]).as_uri()}">{label}</a>' for k,label in [('captioned','자막 영상'),('clean','Clean'),('ko','KO SRT'),('en','EN SRT')] if Path(row['files'][k]['path']).exists())
   link='<br>'.join(parts)
  body.append(f'<tr><td>{row["id"]}</td><td>{html.escape(row["title"])}</td><td>{html.escape(row["status"])}</td><td>{link}</td></tr>')
 text='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>게임수학 실제 게임 이미지 연결 수정</title><style>body{max-width:1240px;margin:auto;padding:26px;background:#080808;color:white;font:18px/1.65 system-ui}h1{color:#e8cf83}a{color:#73c7c2}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #444;text-align:left;padding:12px}</style><h1>M21–M33 실제 게임 이미지 연결 수정</h1><p>이전 대본·음성·수식 전개와 게임 녹화를 보존하고, 게임의 캐릭터·물체를 설명 그림에 연결합니다. 기술 검사와 실제 사용자 시청은 별도로 기록합니다.</p><table><tr><th>편</th><th>강의</th><th>현재 상태</th><th>검수</th></tr>'''+''.join(body)+'</table><p><a href="../game-math-teaching-sync-20261115/index.html">보존한 이전 전체 검수본</a></p></html>'
 (hub/'index.html').write_text(text,encoding='utf8');save(HERE/'progress.json',dict(rows=rows,readyCount=sum(r['ready'] for r in rows),humanReviewed=False,checkedAt=datetime.now(timezone.utc).isoformat()))
 checkpoint=read(HERE/'checkpoint.json');checkpoint.update(status='local-user-review-pending' if all(r['ready'] for r in rows) else 'serialized-render-and-actual-picture-QA',completedFinalMasters=[r['id'] for r in rows if r['ready']],encoded=[r['id'] for r in rows if r['files']],next='Finish guarded remaining renders, inspect actual encoded game-subject correspondence, then local user review. No platform mutations.')
 save(HERE/'checkpoint.json',checkpoint)
 plan=read(HERE/'plan.json');plan['status']=checkpoint['status'];save(HERE/'plan.json',plan)
 ledger=ROOT/'shared/publishing/video-worklist.json';data=read(ledger);data['mathGameSubjects20261115']=dict(scope=list(EPISODES),reviewHub=str(hub/'index.html'),readyCount=sum(r['ready'] for r in rows),humanReviewed=False)
 for item in data.get('rows',[]):
  if item['id'] in EPISODES:
   r=next(r for r in rows if r['id']==item['id']);item['gameSubjects20261115']={k:v for k,v in r.items() if k not in ('title','slug')}
 save(ledger,data)
 p=ROOT/'docs/VIDEO_WORKLIST.md';s=p.read_text(encoding='utf-8-sig');block=START+'\n\n### 게임수학 실제 게임 이미지 연결 수정\n\n[현재 검수표](../output/game-math-game-subjects-20261115/index.html) · 대본·음성·길이 보존 · 플랫폼 변경 없음\n\n| 편 | 제목 | 상태 |\n|---|---|---|\n'+''.join(f'| {r["id"]} | {r["title"]} | {r["status"]} |\n' for r in rows)+'\n'+END
 if START in s:s=s[:s.index(START)]+block+s[s.index(END)+len(END):]
 else:s=s.rstrip()+'\n\n'+block+'\n'
 p.write_text(s,encoding='utf8')
 return rows
if __name__=='__main__':update()

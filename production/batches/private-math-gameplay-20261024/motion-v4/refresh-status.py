"""Current revision ledger, derived from hash-matched outputs and explicit review."""
from pathlib import Path
import json,hashlib,html,re
from datetime import datetime
R=Path(__file__).resolve().parents[4];V=Path(__file__).resolve().parent;B=V.parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replace_block(path,start,end,body):
 s=path.read_text('utf-8-sig');a=s.index(start);z=s.index(end,a)+len(end)
 path.write_text(s[:a]+start+'\n\n'+body+'\n'+end+s[z:],encoding='utf8')
wpath=R/'shared/publishing/video-worklist.json';w=read(wpath);g=w['privateMathPolish']['gameplayTimingRevision'];cp=read(V/'checkpoint.json');now=datetime.now().astimezone().isoformat();entries=[]
for old in g['entries']:
 ep='m03' if old['id']=='M03-original' else old['id'].lower();pp=V/(ep+'-plan.json');row={k:old[k] for k in ('id','slug','title')};row.update(newReviewReady=False,wholeListening=False,humanReview='pending',freezePaddingSeconds=0,rendered=False)
 row['status']='원본 동작 확인 중';row['nativeSeconds']=None;row['examples']=0
 if pp.exists():
  p=read(pp);row['nativeSeconds']=round(sum(x['duration'] for x in p['patches']),3);row['examples']=len(p['patches']);row['status']='게임 구간 준비 · 렌더 대기'
  row['plan']=pp.relative_to(R).as_posix();H=R/'projects'/p['slug']/'production'/p['revision'];op=H/'outputs.json';tp=H/'technical-qa.json';vp=H/'visual-review.json';np=H/'native-frame-evidence.json';mp=H/'motion-continuity.json'
  if op.exists():
   out=read(op)
   if out.get('planSha256')==sha(pp) and all((R/x['path']).exists() for x in out['outputs']):
    row.update(rendered=True,newOutput='output/'+p['slug']+'-'+p['revision'],status='렌더 완료 · 기술 검사 대기')
    master=next(x for x in out['outputs'] if x['path'].endswith('.captioned.mp4'));row['masterSha256']=master['sha256']
    if tp.exists() and {x['path']:x['sha256'] for x in read(tp)['checks']}=={x['path']:x['sha256'] for x in out['outputs']}:
     row['status']='기술 검사 통과 · 변경 화면 검수 중';row['technicalQa']=tp.relative_to(R).as_posix()
     if np.exists() and read(np)['masterSha256']==master['sha256'] and read(np).get('allSourceIntervalsPresentAtSampledTimes'):
      row['nativeFrameQa']=np.relative_to(R).as_posix()
     if mp.exists() and read(mp)['masterSha256']==master['sha256'] and read(mp).get('addedFreezeFlags')==[]:
      row['motionContinuityQa']=mp.relative_to(R).as_posix()
     if vp.exists() and read(vp)['masterSha256']==master['sha256'] and read(vp)['planSha256']==sha(pp) and row.get('nativeFrameQa') and row.get('motionContinuityQa'):
      row.update(newReviewReady=True,status='변경 화면 확인 · 사용자 검수 대기',visualQa=vp.relative_to(R).as_posix())
    row['outputs']=out['outputs'];row['seconds']=out['seconds']
  if p.get('blockers'):row.update(newReviewReady=False,status='일부 구간 근거 보완 필요',blockers=p['blockers'])
 if row.get('rendered'):
  # Keep local review links bound to this exact current plan/master. Chapter
  # jumps help the user inspect each actual action without guessing its time.
  placed=read(H/'patches.json')['patches'];jumps=[]
  for q,a in zip(p['patches'],placed):
   seconds=a['start'];stamp=f'{int(seconds)//60:02d}:{int(seconds)%60:02d}'
   jumps.append(f'<li><button type="button" data-time="{seconds:.3f}">{stamp} · {html.escape(q["title"])}</button> <small>{q["duration"]:g}초 · {html.escape(p["sources"][q["source"]]["game"])}</small></li>')
  missing=''
  if p.get('blockers'):
   missing='<p class="pending">보완 중: 사각형이 잘린 뒤 회전하는 Shapez 2 구간은 충분한 길이의 적합한 원본을 아직 확보하지 못했습니다. 해당 부분은 기존 설명 모형을 보존했으며, 실제 게임 예시 완료로 표시하지 않습니다.</p>'
  page=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{html.escape(row['title'])} · 검수</title><style>body{{background:#101412;color:#f5f5ef;font:18px/1.7 system-ui;max-width:1200px;margin:30px auto;padding:20px}}h1{{color:#ffd773}}video{{width:100%}}a,button{{color:#a5e2bd}}button{{font:inherit;border:0;background:transparent;text-align:left;cursor:pointer;padding:6px 0;text-decoration:underline}}small{{color:#c1c8c2}}.pending{{border-left:4px solid #ffd773;padding-left:14px}}li{{margin:8px 0}}</style><h1>{html.escape(row['title'])}</h1><p>{row['status']} · 1920×1080 / 60fps</p><p>기존 설명·음성·순서·전체 길이 보존. 실제 게임은 원래 속도로 재생하며, 정지 화면으로 길이를 늘리지 않았습니다.</p>{missing}<video id="review-video" controls preload="metadata" src="{p['slug']}.captioned.mp4"></video><p><a href="{p['slug']}.captioned.mp4">자막 영상</a> · <a href="{p['slug']}.clean.mp4">무자막 영상</a> · <a href="{p['slug']}.ko.srt">한국어 자막</a> · <a href="{p['slug']}.en.srt">영어 자막</a></p><h2>게임 장면 바로 보기</h2><p><small>시작 시점으로 이동해 실제 동작과 설명의 연결을 확인할 수 있습니다.</small></p><ol>{''.join(jumps)}</ol><p><small>내부 확인 범위: 전체 파일 디코딩, 원본 음성 보존, 자막, 변경 구간의 시작·동작·결과·설명 복귀 프레임과 모바일 화면, 원본과의 프레임 대조. 전체 연속 청취 및 사용자 최종 검수는 별도입니다.</small></p><p><a href="../private-math-gameplay-20261024/index.html">18편 진행표</a></p><script>const v=document.getElementById('review-video');for(const b of document.querySelectorAll('[data-time]'))b.addEventListener('click',()=>{{v.currentTime=Number(b.dataset.time);v.play().catch(()=>{{}});v.scrollIntoView({{behavior:'smooth',block:'center'}});}});</script></html>'''
  (R/row['newOutput']/'index.html').write_text(page,encoding='utf8')
 entries.append(row)
ready=sum(x['newReviewReady'] for x in entries);rendered=sum(x['rendered'] for x in entries);all_ready=ready==len(entries)
all_resolved=rendered==len(entries) and all(x['newReviewReady'] or (x.get('blockers') and x.get('technicalQa')) for x in entries)
status='local-human-review-pending' if all_ready else 'local-review-with-source-blocker' if all_resolved else 'native-motion-render-and-review'
cp.update(updatedAt=now,status=status,ready=ready,rendered=rendered,current=[x['id'] for x in entries if not x['newReviewReady']],entries=entries)
save(V/'checkpoint.json',cp)
g.update(status=cp['status'],readyCount=ready,ready=ready,renderedCount=rendered,retainedCount=0,fileDeliveries=rendered,entries=entries,revision='gameplay-motion-v4',checkpoint=(V/'checkpoint.json').relative_to(R).as_posix(),updatedAt=now)
save(wpath,w)
oldcp=read(B/'checkpoint.json');oldcp.update(updatedAt=now,status=cp['status'],ready=ready,encoded=rendered,fileDeliveries=rendered,retained=0,current=cp['current'],entries=entries,nextAction='Local user review. Resolve explicitly listed source blocker before marking that episode ready. No upload, heartbeat or automatic next batch.' if all_resolved else 'Finish hash-matched current revision QA, then local user review; no upload or automatic next batch.',explanationPreserved=True,newTts=False,platformChanges=False)
oldcp.pop('next',None)
oldcp.update(revision='gameplay-motion-v4',gameplayPresenceAuditScope='Historical presence audit; use current entries and hash-matched QA for this revision.')
save(B/'checkpoint.json',oldcp)
cpath=R/'shared/publishing/video-production-control.json';control=read(cpath);scope=control['scopedBatchAuthorizations'][B.name];scope['latestRevision'].update(status=cp['status'],rendered=rendered,reviewReady=ready,checkpoint=g['checkpoint']);scope.pop('completedAt',None);save(cpath,control)
summary=f'갱신: {now}\n\n**이번 수정본 렌더 {rendered}/18 · 변경 화면 확인 {ready}/18 · 사용자 검수 승인 0/18.**\n\n설명·음성·순서·전체 길이는 보존합니다. 게임은 원래 속도로 재생하고 정지 화면·반복·슬로모션으로 길이를 채우지 않습니다. 표의 시간은 실제 게임 재생만 합산한 값입니다. 장면의 시작·동작·결과와 설명으로 돌아오는 최종 프레임, 모바일 화면 및 전체 파일 디코딩을 확인합니다. 전체 연속 시청·청취와 사용자 승인은 별도입니다.\n\n[현재 검수 페이지](../output/private-math-gameplay-20261024/index.html) · [이전본 문제 조사표](../output/private-math-gameplay-20261024/audit.html)\n\n| 번호 | 강의 | 실제 재생 / 삽입 | 이번 상태 | 검수본 |\n|---|---|---:|---|---|\n'
for e in entries:
 link=f"[보기](../{e['newOutput']}/index.html)" if e.get('newOutput') else '준비 중';tim='확인 중' if e['nativeSeconds'] is None else f"{e['nativeSeconds']:g}초 / {e['examples']}구간"
 summary+=f"| {e['id']} | {e['title']} | {tim} | {e['status']} | {link} |\n"
summary+='\n이전 버전의18/18 완료 표시는 이번 움직임·개념 대응 검수의 완료를 뜻하지 않습니다. 아래의 이전 제작 기록은 이력이며 현재 상태는 위 표를 따릅니다.\n'
replace_block(R/'docs/GAME_MATH_PRIVATE_POLISH.md','<!-- GAMEPLAY-20261024-START -->','<!-- GAMEPLAY-20261024-END -->',summary)
replace_block(R/'docs/VIDEO_WORKLIST.md','<!-- GAMEPLAY-PRESENCE-AUDIT-20261024-START -->','<!-- GAMEPLAY-PRESENCE-AUDIT-20261024-END -->',summary)
rows=[]
for e in entries:
 links='준비 중'
 if e.get('newOutput'):
  prefix='../'+Path(e['newOutput']).name;links=f'<a href="{prefix}/index.html">영상·자막</a> · <a href="{prefix}/{e["slug"]}.captioned.mp4">전체 영상</a>'
 t='—' if e['nativeSeconds'] is None else f'{e["nativeSeconds"]:g}초 · {e["examples"]}구간'
 rows.append(f'<tr><td>{e["id"]}</td><td>{html.escape(e["title"])}</td><td>{t}</td><td>{e["status"]}</td><td>{links}</td></tr>')
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>게임수학 — 움직이는 실제 게임 검수</title><style>body{background:#101412;color:#f5f5f0;font:17px/1.65 sans-serif;max-width:1400px;margin:40px auto;padding:0 20px}h1{color:#ffe08a}a{color:#9ddbb7}table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid #465048;padding:14px 10px;text-align:left}small{color:#c3c8c3}.scroll{overflow:auto}</style>'''
page+=f'<h1>게임수학 실제 게임 장면 수정</h1><p>렌더 {rendered}/18 · 변경 화면 확인 {ready}/18 · 사용자 검수 대기</p><p>설명과 음성은 그대로, 게임은 원래 속도로 재생합니다. 정지 화면으로 늘린 시간은0초입니다. 각 게임 장면의 시작·동작·결과와 설명 복귀 화면을 확인합니다.</p><p><small>검사는 변경 구간의 최종 프레임·모바일 화면과 전체 파일 디코딩입니다. 전체 연속 시청·청취 또는 사용자 승인으로 표시하지 않습니다. 짧은 동작은 길이를 늘리지 않고 그 자체의 완결 여부를 확인합니다.</small></p><div class="scroll"><table><thead><tr><th>번호</th><th>강의</th><th>실제 재생</th><th>상태</th><th>보기</th></tr></thead><tbody>'+''.join(rows)+f'</tbody></table></div><p><a href="audit.html">이전본 전수조사 기록</a></p><small>갱신 {now}</small></html>'
(R/'output/private-math-gameplay-20261024/index.html').write_text(page,encoding='utf8')
save(V/'delivery-manifest.json',dict(updatedAt=now,revision='gameplay-motion-v4',rendered=rendered,changedFramesChecked=ready,humanApproved=0,entries=entries))
print('rendered',rendered,'changed-frames-checked',ready,flush=True)

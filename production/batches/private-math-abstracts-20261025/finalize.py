"""Publish only inspected local results into the existing review ledger."""
from render import *
import html,re
E=html.escape
CSS='body{font:17px/1.65 system-ui;background:#101512;color:#f2f5f2;max-width:1400px;margin:32px auto;padding:0 20px}h1,h2{color:#ffdf73}a{color:#8cdbbc}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:12px;border-bottom:1px solid #405147}.scroll{overflow:auto}video{width:100%;max-height:78vh;background:#000}.status{border-left:4px solid #ffdf73;padding:16px;background:#18201b}code{overflow-wrap:anywhere}'
def page(title,body):return '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>'+E(title)+'</title><style>'+CSS+'</style>'+body+'</html>'
def project_page(p,r,qa):
 D=R/p['output'];slug=p['slug'];master=next(x for x in r['outputs'] if '.captioned.' in x['path']);games=[];seen=set()
 for s in p['segments']:
  if s['source'] in seen:continue
  seen.add(s['source']);link='<a href="'+E(s['sourceUrl'],quote=True)+'">원본 링크</a>' if s.get('sourceUrl') else '출처·이용 근거는 기존 소스 기록 참조'
  games.append('<li>'+E(s['game'])+' — '+link+'<br><small>'+E(s['rightsEvidence'])+'</small></li>')
 links=' · '.join('<a href="'+slug+'.'+ext+'">'+label+'</a>' for ext,label in [('captioned.mp4','전체 자막 영상'),('clean.mp4','클린 영상'),('ko.srt','한국어 자막'),('en.srt','영어 자막')])
 body=f'<h1>{E(p["title"])}</h1><p class="status">실제 게임 Abstract 적용 · 1080p60 · 로컬 사용자 검수 대기</p><p>{E(p["headline"])}. 기존 도입 설명에 실제 게임 장면과 의미 표식을 결합했습니다. 영상 길이·음성·한영 자막·본문 설명은 유지했습니다.</p><video controls preload="metadata" src="{slug}.captioned.mp4"></video><p>{links}</p><p>브랜딩 뒤 2.00–{p["abstractEnd"]:.2f}초가 이번 변경 구간입니다. 정지 화면 반복이나 재생 속도 조정은 없습니다.</p><p>검사: 디코딩·보존 구간 검증, 1080p60·프레임 수, 음성 스트림 및 한영 자막 동일성, 변경 후 본문 영상 스트림 동일성, 변경 장면·연결부·모바일 프레임을 확인했습니다. 실제 전체 연속 청취와 사용자 검수 승인은 아직 대기입니다. 기존 발음 확인 항목은 <a href="../{Path(p["oldOutput"]).name}/index.html">이전 검수 기록</a>을 유지합니다.</p><h2>출처와 검수 기록</h2><ul>'+''.join(games)+f'</ul><p>본문의 기존 출처·권리 기록은 <a href="../{Path(p["oldOutput"]).name}/index.html">이전 검수본 기록</a>에 연결합니다. 실제 게임 화면은 관찰 예시이며, 기즈모·표식은 이해를 돕는 편집 표시입니다.</p><p>검수 파일 SHA256<br><code>{master["sha256"]}</code></p><p><a href="../private-math-abstracts-20261025/index.html">전체18편 검수표</a></p>'
 (D/'index.html').write_text(page(p['title'],body),encoding='utf8')
def main():
 cp=read(B/'checkpoint.json');w=read(R/'shared/publishing/video-worklist.json');now=datetime.datetime.now().astimezone().isoformat()
 reviewed=set(sys.argv[1:]);assert reviewed <= {e['id'] for e in cp['entries']}
 for e in cp['entries']:
  if e['id']=='M14':
   assert sha(R/e['output']/f'{e["slug"]}.captioned.mp4')==e['masterSha256'];continue
  pp=R/e['plan'];p=read(pp);W=Path(p['work']);rpath=W/'render-receipt.json';qpath=W/'qa.json'
  if e['id'] in reviewed:
   r=read(rpath);qa=read(qpath);assert qa['status'] in ['technical-pass-visual-review-pending','internal-qa-pass-human-review-pending']
   qa.update(status='internal-qa-pass-human-review-pending',visualReview=dict(by='assistant',method='Source chronological contact frames plus final changed segments and joins; full-resolution opening and375px mobile frame.',at=now,wholePlayback=False,wholeListening=False),humanReview='pending')
   evidence=R/'projects'/p['slug']/'production/actual-abstract-v6'
   prior=W/'qa-initial.json'
   if prior.exists():
    save(evidence/'qa-initial.json',read(prior))
   qa['bodyPreservation']='Original imagery, narration, subtitles and order retained; only the opening through the next safe keyframe is re-encoded. Remaining body VCL payload is byte-identical.'
   save(qpath,qa);save(evidence/'qa.json',qa)
   p['status']='local-human-review-pending';save(pp,p);save(R/'projects'/p['slug']/'production/actual-abstract-v6/plan.json',p)
   e.update(status='local-human-review-pending',masterSha256=next(x['sha256'] for x in r['outputs'] if '.captioned.' in x['path']),abstractSeconds=p['abstractEnd']-2,qa=(Path('projects')/p['slug']/'production/actual-abstract-v6/qa.json').as_posix(),humanReview='pending')
   project_page(p,r,qa)
  elif e['status']!='local-human-review-pending':e['status']='technical-pass-visual-review-pending' if qpath.exists() else 'encoded-qa-pending' if rpath.exists() else p['status']
 ready=sum(e['status'] in ['local-human-review-pending','retained-complete'] for e in cp['entries']);cp.update(ready=ready,status='local-human-review-pending' if ready==18 else 'render-and-qa',updatedAt=now);save(B/'checkpoint.json',cp)
 w['privateMathPolish']['abstractRevision']=dict(status=cp['status'],checkpoint=(B/'checkpoint.json').relative_to(R).as_posix(),ready=ready,total=18,entries=cp['entries'],reviewPage='output/private-math-abstracts-20261025/index.html')
 # Keep previous timings and output evidence, add the selected latest version.
 for e in cp['entries']:
  if e['status'] not in ['local-human-review-pending','retained-complete']:continue
  old=next(x for x in w['privateMathPolish']['gameplayTimingRevision']['entries'] if x['id']==e['id'])
  if e['id']!='M14':
   old.setdefault('preAbstractOutput',old['newOutput']);old.setdefault('preAbstractMasterSha256',old['masterSha256']);old.update(newOutput=e['output'],masterSha256=e['masterSha256'],abstractRevision=e['plan'],abstractSeconds=e['abstractSeconds'],humanReview='pending')
 save(R/'shared/publishing/video-worklist.json',w)
 cpath=R/'shared/publishing/video-production-control.json';c=read(cpath);c['scopedBatchAuthorizations'][B.name].update(status='local-human-review-pending' if ready==18 else 'active',ready=ready,total=18);save(cpath,c)
 body=f'<h1>게임수학18편 · 실제 게임 Abstract 검수표</h1><p class="status">도입부 적용·내부 검사 완료 {ready}/18 · 사용자 검수 승인0/18</p><p>{E(now)} 갱신. M14의 완성된 도입부는 유지하고, 나머지17편은 기존 핵심 질문·개요 음성에 실제 게임을 결합합니다. 본문 설명·음성·순서·길이를 유지합니다. 업로드는 하지 않았습니다.</p><div class="scroll"><table><tr><th>번호</th><th>강의</th><th>도입부</th><th>상태</th><th>검수</th></tr>'
 md=f'갱신: {now}\n\n**실제 게임 Abstract 적용·내부 검사 {ready}/18 · 사용자 승인0/18.**\n\nM14는 완성본을 유지하고 다른17편은 기존 개요 음성과 실제 게임 장면을 통합합니다. 본문 설명·음성·순서·길이는 보존합니다. 전체 연속 청취·사용자 승인은 별도입니다.\n\n[최신18편 검수표](../output/private-math-abstracts-20261025/index.html)\n\n| 번호 | 강의 | 실제 게임 도입 | 이번 상태 | 검수본 |\n|---|---|---:|---|---|\n'
 for e in cp['entries']:
  done=e['status'] in ['local-human-review-pending','retained-complete'];dur=18.15 if e['id']=='M14' else e.get('abstractSeconds',read(R/e['plan'])['abstractEnd']-2);status='도입부 적용 · 사용자 검수 대기' if done else {'sources-reviewed':'장면 확인 · 렌더 대기','rendering':'렌더 중','encoded-qa-pending':'렌더 완료 · 기술 검사 중','technical-pass-visual-review-pending':'기술 검사 완료 · 화면 확인 중'}.get(e['status'],e['status'])
  folder=Path(e['output']).name;link=f'<a href="../{folder}/index.html">검수 폴더</a> · <a href="../{folder}/{e["slug"]}.captioned.mp4">전체 영상</a>' if done else '준비 중'
  body+=f'<tr><td>{e["id"]}</td><td>{E(e["title"])}</td><td>{dur:.2f}초</td><td>{status}</td><td>{link}</td></tr>'
  md+=f'| {e["id"]} | {e["title"]} | {dur:.2f}초 | {status} | '+(f'[보기](../{e["output"]}/index.html)' if done else '준비 중')+' |\n'
 body+='</table></div><p>18편 모두 음성과 기존 본문 설명을 유지합니다. M14의 기존 청취 확인 항목도 보존합니다. 표식은 편집 안내이며 게임 내부 수치를 측정한 결과가 아닙니다.</p>'
 O=R/'output/private-math-abstracts-20261025';O.mkdir(exist_ok=True);(O/'index.html').write_text(page('게임수학 Abstract 검수표',body),encoding='utf8')
 for path,start,end in [('docs/GAME_MATH_PRIVATE_POLISH.md','<!-- GAMEPLAY-20261024-START -->','<!-- GAMEPLAY-20261024-END -->'),('docs/VIDEO_WORKLIST.md','<!-- GAMEPLAY-PRESENCE-AUDIT-20261024-START -->','<!-- GAMEPLAY-PRESENCE-AUDIT-20261024-END -->')]:
  f=R/path;s=f.read_text('utf8');assert start in s and end in s;f.write_text(s.split(start,1)[0]+start+'\n\n'+md+'\n'+end+s.split(end,1)[1],encoding='utf8')
 for path in ['output/private-game-math-polish/index.html','output/private-math-gameplay-20261024/index.html']:
  f=R/path;s=f.read_text('utf8');s=re.sub(r'<!-- ABSTRACT-V6-START -->.*?<!-- ABSTRACT-V6-END -->','',s,flags=re.S);notice=f'<!-- ABSTRACT-V6-START --><aside style="padding:20px;background:#173728;color:#fff;font:20px/1.5 system-ui">최신 실제 게임 도입부 검수 {ready}/18 · <a style="color:#ffdf73" href="../private-math-abstracts-20261025/index.html">최신 검수표 열기</a> · 아래는 보존된 이전 기록입니다.</aside><!-- ABSTRACT-V6-END -->';idx=s.find('</style>')+8;f.write_text(s[:idx]+notice+s[idx:],encoding='utf8')
 print('Review-ready',ready,'/18',flush=True)
if __name__=='__main__':main()

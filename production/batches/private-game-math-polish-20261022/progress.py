"""Evidence-based local dashboard; render completion is not human approval."""
import datetime,html,subprocess
from polish_common import *
now=datetime.datetime.now(datetime.timezone.utc).isoformat();q=read(B/'queue.json');w=read(R/'shared/publishing/video-worklist.json');rows={r['id']:r for r in w['rows']}
table=[]
blockers=read(B/'source-blockers.json') if (B/'source-blockers.json').exists() else {}
for entry in q['entries']:
 e=Episode(entry['id']);audio=e.H/'restoration.json';clips=e.H/'explanation-restoration.json';game=e.H/'gameplay-restoration.json';qa=e.H/'technical-qa.json';visual=e.H/'visual-review.json'
 n=len(read(clips)['scenes']) if clips.exists() else 0;ng=len(read(game)['scenes']) if game.exists() else 0
 total=sum(s['classification']=='explanation' for s in e.T['scenes']);actual=len(e.T['scenes'])-total
 # This positive status requires manual, version-bound visual review evidence.
 ready=False;technical_current=False;visual_record=read(visual) if visual.exists() else {}
 if qa.exists() and (e.H/'outputs.json').exists():
  technical_outputs={x.get('sha256') for x in read(qa).get('outputs',[]) if x.get('fullDecode') is True}
  encoded_outputs=[x['sha256'] for x in read(e.H/'outputs.json')['outputs'] if x['path'].endswith('.mp4')]
  technical_current=len(encoded_outputs)==2 and all(d in technical_outputs for d in encoded_outputs)
 if qa.exists() and visual.exists() and (e.D/f'{e.slug}.captioned.mp4').exists():
  v=read(visual);digest=sha(e.D/f'{e.slug}.captioned.mp4')
  technical=next((x for x in read(qa).get('outputs',[]) if x.get('kind')=='captioned'),{})
  ready=v.get('status')=='passed' and v.get('captionedSha256')==digest and technical.get('sha256')==digest and technical.get('fullDecode') is True
 status='검수대기' if ready else (f'설명 {n}/{total} · 게임 {ng}/{actual} 복원' if n or ng else ('기존 음성 복구 · 화면 복원 대기' if audio.exists() else '원본 복구 대기'))
 if not ready and technical_current:
  technical_caption=next(x['sha256'] for x in read(qa)['outputs'] if x['kind']=='captioned')
  status='기술 검사 완료 · 최종 화면 검수 중'
  if visual_record.get('status')=='needs-repair' and visual_record.get('captionedSha256')==technical_caption:status='기술 검사 완료 · 화면 오류 수정 중'
 issue=blockers.get(e.id)
 if issue and not ready:status+=' · '+issue['shortStatus']
 entry.update(status='ready-for-human-review' if ready else 'production-in-progress',audioRecovered=audio.exists(),explanationsRestored=n,explanationCount=total,gameplayRestored=ng,actualSceneCount=actual,technicalQaComplete=technical_current,humanReview='pending')
 if issue:entry['sourceBlocker']=issue
 else:entry.pop('sourceBlocker',None)
 row=rows[e.id]['privatePolish'];row.update(status=status,sourceMaster=rel(audio) if audio.exists() else row['sourceMaster'],renderComplete=(e.H/'outputs.json').exists(),technicalQaComplete=technical_current,humanReview='수정본 검수 전')
 link=f'<a href="../{e.slug}-private-polish/index.html">검수 영상</a>' if ready else '제작 중'
 table.append(f'<tr><td>{e.id}</td><td>{html.escape(entry["title"])}</td><td>{status}</td><td>{link}</td></tr>')
q['updatedAt']=now;save(B/'queue.json',q);w['updatedAt']=now;w['privateMathPolish']['updatedAt']=now
p=w['privateMathPolish'];p['reviewSequence']={'policy':'user-authorized-sixteen-local-review-batch','userEvidence':q['authorization']['userEvidence'],'scope':q['authorization']['ids'],'automaticNextVideo':True,'advanceBeyondList':False,'stopAt':'all sixteen ready for local human review','humanReviewStillRequired':True,'publicationAuthorized':False}
save(R/'shared/publishing/video-worklist.json',w);subprocess.run(['python',str(R/'scripts/render-video-worklist.py')],cwd=R,check=True,capture_output=True)
out=R/'output/private-game-math-polish';out.mkdir(parents=True,exist_ok=True)
(out/'index.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>비공개 게임수학 보강 진행표</title><style>body{max-width:1100px;margin:30px auto;padding:0 18px;background:#121915;color:#f6f8f6;font:17px/1.6 system-ui}h1{color:#ffdf73}table{width:100%;border-collapse:collapse}td,th{padding:12px;border-bottom:1px solid #405147;text-align:left}a{color:#8cdbbc}</style><h1>게임수학 기존 강의 보강</h1><p>M04 검수 완료. 아래 16편은 기존 대본·음성·순서를 유지하여 보강합니다. 내부 검사가 끝난 편부터 검수 링크가 표시됩니다. 업로드·공개는 진행하지 않습니다.</p><table><thead><tr><th>번호</th><th>강의</th><th>상태</th><th>검수</th></tr></thead><tbody>'''+''.join(table)+f'</tbody></table><p>갱신: {now}</p></html>',encoding='utf8')
print('Audio recovered',sum(e['audioRecovered'] for e in q['entries']),'of',len(q['entries']),'Ready',sum(e['status']=='ready-for-human-review' for e in q['entries']),flush=True)

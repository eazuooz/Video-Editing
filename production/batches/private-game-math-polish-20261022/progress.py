"""Evidence-based local dashboard; render completion is not human approval."""
import datetime,html,subprocess
from polish_common import *
now=datetime.datetime.now(datetime.timezone.utc).isoformat();q=read(B/'queue.json');w=read(R/'shared/publishing/video-worklist.json');rows={r['id']:r for r in w['rows']}
table=[]
blockers=read(B/'source-blockers.json') if (B/'source-blockers.json').exists() else {}
finish_job=read(B/'approved-portal-finish-job.json') if (B/'approved-portal-finish-job.json').exists() else {}
finish_alive=False
if os.name=='nt' and finish_job.get('status')=='running':
 import ctypes
 kernel=ctypes.WinDLL('kernel32',use_last_error=True)
 kernel.OpenProcess.restype=ctypes.c_void_p
 kernel.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_ulong)]
 kernel.CloseHandle.argtypes=[ctypes.c_void_p]
 handle=kernel.OpenProcess(0x1000,False,finish_job['pid'])
 if handle:
  exit_code=ctypes.c_ulong()
  finish_alive=bool(kernel.GetExitCodeProcess(handle,ctypes.byref(exit_code))) and exit_code.value==259
  kernel.CloseHandle(handle)
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
 if not ready and not technical_current:
  guide_preflight=e.H/'observed-guide-preflight.json'
  if guide_preflight.exists() and read(guide_preflight).get('status')=='passed-still-preflight':status+=' · 표식 사전 점검 완료'
  partial_guides=e.H/'available-guides-review.json'
  if partial_guides.exists() and read(partial_guides).get('status')=='partial-guides-inspected-full-episode-pending':
   status+=' · 일부 게임 표식 점검'
 polish_name=({'M08':'conversions-legibility','M09':'geometry-legibility','M10':'geometry-legibility','M11':'planes-legibility','M12':'planes-legibility','M17':'projection-legibility'}).get(e.id,'interpolation-legibility')
 source_polish=e.H/(polish_name+'-render.json')
 if source_polish.exists():
  source_record=read(source_polish);polished=len(source_record.get('scenes',{}))
  source_review=e.H/(polish_name+'-review.json')
  source_review_status=read(source_review).get('status','pending') if source_review.exists() else 'pending'
  detail={'renderedScenes':polished,'sceneCount':total,'renderManifest':rel(source_polish),'sourceVisualReview':source_review_status,'isFullMaster':False}
  entry['explanationPolish']=detail;rows[e.id]['privatePolish']['explanationPolish']=detail
  if not ready:
   status+=f' · 설명 보강 {polished}/{total}'
   if source_review_status=='passed-source-visual-review':status+=' · 설명 화면 검수 완료'
 issue=blockers.get(e.id)
 if issue and not ready:status+=' · '+issue['shortStatus']
 if not ready and finish_alive and e.id in finish_job.get('ids',[]):
  if finish_job.get('episode')==e.id:
   stage={'prepare-observed-composition.py':'표식 합성 준비 중','register-reviewed-geometry-inputs.py':'설명 장면 연결 중','assemble.py':'전체1080p60 렌더링 중','technical-qa.py':'전체 파일 기술 검사 중','review-final-pixels.py':'최종 화면 검수 이미지 추출 중'}.get(finish_job.get('stage'),'마무리 작업 중')
   status=stage+' · 원본 해상도 예외 승인 장면만 적용'
  elif e.id not in finish_job.get('results',{}):
   status='모든 장면 복원·사전 점검 완료 · 순차 렌더 대기'
 entry.update(status='ready-for-human-review' if ready else 'production-in-progress',audioRecovered=audio.exists(),explanationsRestored=n,explanationCount=total,gameplayRestored=ng,actualSceneCount=actual,technicalQaComplete=technical_current,humanReview='pending')
 if issue:entry['sourceBlocker']=issue
 else:entry.pop('sourceBlocker',None)
 row=rows[e.id]['privatePolish'];row.update(status=status,selected=True,sourceMaster=rel(audio) if audio.exists() else row['sourceMaster'],renderComplete=(e.H/'outputs.json').exists(),technicalQaComplete=technical_current,humanReview='수정본 검수 전',contentReviewed=ready,annotationsComplete=ready,animationPolishComplete=ready or (source_polish.exists() and source_review_status=='passed-source-visual-review'))
 if ready:
  row['localReview']={'status':'ready-for-human-local-review','directory':rel(e.D),'index':rel(e.D/'index.html'),'captionedVideo':rel(e.D/f'{e.slug}.captioned.mp4'),'captionedMasterSha256':digest,'technicalQa':rel(qa),'pixelReview':rel(visual),'humanFinalReview':'pending','youtubeUploadAuthorized':False}
 else:
  row['localReview']={'status':'not-ready','reason':issue['shortStatus'] if issue else status,'humanFinalReview':'pending','youtubeUploadAuthorized':False}
 link=f'<a href="../{e.slug}-private-polish/index.html">검수 영상</a>' if ready else '제작 중'
 table.append(f'<tr><td>{e.id}</td><td>{html.escape(entry["title"])}</td><td>{status}</td><td>{link}</td></tr>')
q['updatedAt']=now;save(B/'queue.json',q);w['updatedAt']=now;w['privateMathPolish']['updatedAt']=now
p=w['privateMathPolish'];p['reviewSequence']={'policy':'user-authorized-sixteen-local-review-batch','userEvidence':q['authorization']['userEvidence'],'scope':q['authorization']['ids'],'automaticNextVideo':True,'advanceBeyondList':False,'stopAt':'all sixteen ready for local human review','humanReviewStillRequired':True,'publicationAuthorized':False}
save(R/'shared/publishing/video-worklist.json',w);subprocess.run(['python',str(R/'scripts/render-video-worklist.py')],cwd=R,check=True,capture_output=True)
out=R/'output/private-game-math-polish';out.mkdir(parents=True,exist_ok=True)
(out/'index.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>비공개 게임수학 보강 진행표</title><style>body{max-width:1100px;margin:30px auto;padding:0 18px;background:#121915;color:#f6f8f6;font:17px/1.6 system-ui}h1{color:#ffdf73}table{width:100%;border-collapse:collapse}td,th{padding:12px;border-bottom:1px solid #405147;text-align:left}a{color:#8cdbbc}</style><h1>게임수학 기존 강의 보강</h1><p>M04 검수 완료. 아래 16편은 기존 대본·음성·순서를 유지하여 보강합니다. 내부 검사가 끝난 편부터 검수 링크가 표시됩니다. 업로드·공개는 진행하지 않습니다.</p><table><thead><tr><th>번호</th><th>강의</th><th>상태</th><th>검수</th></tr></thead><tbody>'''+''.join(table)+f'</tbody></table><p>갱신: {now}</p></html>',encoding='utf8')
print('Audio recovered',sum(e['audioRecovered'] for e in q['entries']),'of',len(q['entries']),'Ready',sum(e['status']=='ready-for-human-review' for e in q['entries']),flush=True)

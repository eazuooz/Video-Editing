"""Publish only verified local D25–D30 delivery state; never touches platforms."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,uuid

R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
SLUGS=['limited-color-world','computer-controlled-players','in-game-cutscenes','start-with-climax','kind-to-beginners','respect-player-time']
IDS=['D25','D26','D27','D28','D29','D30'];BATCH='design-finish-six-20261026'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def save(p,d):
 tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
def cell(v):return str(v).replace('|',' / ').replace('\n',' ')

control_path=R/'shared/publishing/video-production-control.json';control_before=sha(control_path);control=read(control_path)
auth=control['finiteBatchAuthorizations'][BATCH]
assert auth['localProductionAuthorized'] and auth['slugs']==SLUGS
now=datetime.now(timezone.utc).isoformat();verified=[]
for episode,slug in zip(IDS,SLUGS):
 project=R/'projects'/slug;rev=project/'production/batch-v1'
 q=read(rev/'review-status.json')
 assert q['status']=='local-review-ready' and q['fourOutputsVerified'] is True,(slug,'review incomplete')
 manifest=read(project/'project.json');delivery=R/manifest['delivery']['localStorageRoot']/manifest['delivery']['directory']
 assert delivery.resolve().is_relative_to(Path('C:/Users/1/.codex/video-production')/BATCH/slug)
 paths={};hashes={}
 for kind in ['captioned.mp4','clean.mp4','ko.srt','en.srt']:
  p=delivery/(slug+'.'+kind);assert p.is_file() and p.stat().st_size>0
  paths[kind]=p.relative_to(R).as_posix();hashes[kind]=sha(p)
 assert (delivery/'index.html').is_file()
 review=read(rev/'final-comparison-review.json');assert review['fullTextDirectlyCompared'] is True
 plan=read(rev/'edit-plan.json');edit=R/plan['outputDir'];technical=read(edit/'structural-verification.json')
 assert technical['status']=='pass'
 for language in ['ko','en']:assert hashes[language+'.srt']==sha(edit/f'captions.{language}.srt')
 for kind,key in [('captioned.mp4','captioned'),('clean.mp4','clean')]:
  output=technical['outputs'][key];assert output['sha256']==hashes[kind]
  assert output['video']['width']==1920 and output['video']['height']==1080 and output['video']['avg_frame_rate']=='60/1'
  assert output['audioPacketsSha256']==review['encodedAudioPacketsSha256']
 assert 0.599<=technical['ratio']['gameplayShare']<=0.601
 verified.append({'id':episode,'slug':slug,'q':q,'manifest':manifest,'paths':paths,'hashes':hashes,'index':(delivery/'index.html').relative_to(R).as_posix(),'seconds':technical['outputs']['captioned']['durationSeconds']})

# Only after all six current output hashes and audio evidence pass, update state.
assert sha(control_path)==control_before,'Concurrent control update; rerun against latest state'
work_path=R/'shared/publishing/video-worklist.json';work=read(work_path)
checkpoint=read(B/'checkpoint.json')
for v in verified:
 slug=v['slug'];row=next(x for x in work['rows'] if x['id']==v['id'])
 assert not row.get('videoId') and not row.get('url'), 'Preserve any unexpected platform state'
 row.update(productionComplete=True,productionStatus='1080p60 완성본·한영 자막 완료',reviewStatus='로컬 완성본 사용자 검수 대기',humanApproval='pending',executionStatus='D25–D30 일괄 제작 완료 · 사용자 검수 대기',localMasterAvailable=True,activeRevision='batch-v1',selectedBatch=BATCH)
 row['internalQaStatus']='complete; actual human viewing/listening pending'
 row['localReview']={'status':'ready-for-human-local-review','index':v['index'],'captionedVideo':v['paths']['captioned.mp4'],'cleanVideo':v['paths']['clean.mp4'],'captionsKo':v['paths']['ko.srt'],'captionsEn':v['paths']['en.srt'],'captionedSha256':v['hashes']['captioned.mp4'],'durationSeconds':v['seconds'],'actualUserViewed':False,'humanWholeListening':'pending','updatedAt':now}
 evidence=f'projects/{slug}/production/batch-v1/review-status.json'
 row.setdefault('evidence',[])
 if evidence not in row['evidence']:row['evidence'].append(evidence)
 row['notes']='전체 영상·한영 자막 로컬 검수 대기. 기술/대본 대조/화면 검사는 내부 근거이며 실제 사용자 시청·청취 승인과 구분. YouTube 업로드·예약 미실행.'
 m=v['manifest'];m['status']='local-review-ready';m['updatedAt']=now
 m['localFinalReview']={'index':v['index'],'files':v['paths'],'sha256':v['hashes'],'durationSeconds':v['seconds'],'actualUserViewed':False,'humanWholeListening':'pending','internalQa':'complete','reviewRecord':evidence}
 if 'publishReady' in m:m['publishReady']=False
 if 'finalRender' in m:m['finalRender'].update(status='complete-local-review-ready',openItems=['Actual user whole-video viewing/listening and any resulting corrections.'])
 save(R/'projects'/slug/'project.json',m)
 e=next(x for x in checkpoint['episodes'] if x['slug']==slug)
 e.update(stage='완성본·4파일 내부 검수 완료 · 사용자 검수 대기',productionComplete=True,humanReview='pending',humanListening='pending',durationSeconds=v['seconds'],captionedSha256=v['hashes']['captioned.mp4'],localReviewIndex=v['index'])
 control['scopedProductionAuthorizations'][slug]['status']='local-review-ready-user-pending'

checkpoint.update(status='six-local-reviews-ready',updatedAt=now,completed=6,total=6,youtubeMutation=False,driveMutation=False)
control['finiteBatchAuthorizations'][BATCH].update(status='local-review-ready-user-pending',completed=6,total=6)
save(work_path,work);save(control_path,control);save(B/'checkpoint.json',checkpoint)

# Render only the six owned worklist rows; preserve unrelated sections byte for byte.
doc=R/'docs/VIDEO_WORKLIST.md'
with doc.open('r',encoding='utf-8-sig',newline='') as f:lines=f.read().splitlines(keepends=True)
rows={r['id']:r for r in work['rows'] if r['id'] in IDS}
for i,line in enumerate(lines):
 for episode,r in rows.items():
  nl='\r\n' if line.endswith('\r\n') else '\n'
  if line.startswith('| '+episode+' |'):
   lines[i]=f"| {episode} | {cell(r['title'])} | ☑ {cell(r['productionStatus'])} | ☐ {cell(r['reviewStatus'])} | {cell(r['platformStatus'])} |"+nl
  elif '| 게임디자인 | '+episode+' ' in line:
   order=line.split('|')[1].strip();lines[i]=f"| {order} | 게임디자인 | {episode} {cell(r['title'])} | {cell(r['executionStatus'])} | ☐ {cell(r['reviewStatus'])} |"+nl
  elif line.startswith('| '+episode+' '):
   lines[i]=f"| {episode} {cell(r['title'])} | {cell(r['notes'])} |"+nl
with doc.open('w',encoding='utf-8',newline='') as f:f.write(''.join(lines))
subprocess.run([os.fspath(R/'qwen3-tts/.venv/Scripts/python.exe'),str(B/'build_review.py')],cwd=R,check=True)
print(json.dumps({'status':'six-local-reviews-ready','completed':6,'humanReview':'pending','platformMutations':False,'masterHashes':{v['id']:v['hashes']['captioned.mp4'] for v in verified}},ensure_ascii=False))

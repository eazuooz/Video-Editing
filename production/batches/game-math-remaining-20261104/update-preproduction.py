"""Refresh the exact authorized batch from current persisted media evidence."""
from pathlib import Path
from datetime import datetime,timezone
import json,re,subprocess,psutil,time
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def latest(base,pattern):
 ps=list(base.glob(pattern));return max(ps,key=lambda p:int(re.search(r'-v(\d+)',p.name)[1])) if ps else None
def state(p):
 if not p or not p.is_file():return {}
 for attempt in range(8):
  try:return read(p)
  except (PermissionError,json.JSONDecodeError):
   if attempt==7:raise
   time.sleep(.15)
def live(s):
 try:return abs(psutil.Process(s['pid']).create_time()-s['createTime'])<.1
 except (KeyError,psutil.NoSuchProcess):return False
at=datetime.now(timezone.utc).isoformat();batch=read(B/'batch.json');work=read(R/'shared/publishing/video-worklist.json');rows={x['id']:x for x in work['rows']}
active=[];voices={};previews={};evidence={}
finisher=state(B/'local/finish-module-candidates.json')
remaining=state(B/'local/remaining-speech-worker.json')
repairfiles=sorted((B/'local').glob('finish-m*-audio-v*.json'))
repairs=[(f,state(f)) for f in repairfiles]
for item in batch['items']:
 P=R/'projects'/item['slug'];plan=read(P/'planning/production-plan.json');bindings=read(P/'planning/scene-bindings.json')
 audio=latest(P/'production/local','audio-v*');preview=latest(P/'production/unity-staging','local-preflight-v*');render=latest(P/'production/local','render-v*')
 voice=state(audio/'finite-worker.json' if audio else None);words=state(audio/'finite-word-review.json' if audio else None);pv=state(preview/'progress.json' if preview else None)
 capture=state(render/'progress.json' if render else None);composite=state(render/'composite/worker.json' if render else None)
 qa=state(render/'final-qa/report.json' if render else None);content=state(render/'content-review.json' if render else None)
 n=len(bindings['scenes']);stage=f'{n}문단 한영 대본·설명 장면 작성'
 if pv:
  count=len(pv.get('completed',[]));stage+=f' · 최신 실행 샘플 {count}개'
  if pv['status']=='images-ready-for-internal-visual-QA':stage+=' 생성·화면 검수 중'
  elif pv['status']=='failed-or-blocked':stage+=' · 실행 오류 확인 중'
  else:stage+=' · GPU 순차 검사 중'
 elif preview and (preview/'queue.json').is_file():
  stage+=f' · 추가 Unity 장면 {len(read(preview/"queue.json")["jobs"])}개 검사 대기'
 if voice:
  label={'synthesizing':'음성 생성 중','voice-generated-review-pending':'음성 생성 완료','failed-or-blocked':'음성 작업 오류 확인 중'}.get(voice['status'],'음성 순차 대기')
  stage+=' · '+label+' ('+audio.name+')';voices[item['id']]=voice
  chunks=[p for p in (audio/'chunks').glob('*.wav') if p.stat().st_size>44]
  if voice['status']!='voice-generated-review-pending':stage+=f' · 문단 음성 파일 {len(chunks)}/{n}'
  retake=state(audio/'retake-plan.json')
  if retake:
   changed=retake.get('retakeScenes',[])
   if changed:stage+=f' (기존 음성 {n-len(changed)}개 유지 · {len(changed)}개 재녹음)'
 if words.get('status')=='word-evidence-ready-content-review-pending':stage+=' · 발화 시각 확보'
 measured=state(P/('production/local/'+audio.name.replace('audio-','edit-')+'/word-aligned-timeline.json')) if audio else {}
 if measured.get('flags'):stage+=f' · 대사·자막 재확인 {len(measured["flags"])}건'
 if capture:
  stage=f'음성·자막 연결 · 본편 설명 씬 {len(capture.get("completed",[]))}개 렌더'
  if capture['status']=='body-captures-complete-compositing-and-QA-pending':stage='설명 씬 렌더 완료 · 본편 합성/검수 중'
 if composite.get('status')=='encoded' or qa:stage='1080p60 영상 2개·한영 자막 2개 생성 · 내부 검수 중'
 ready=bool(content.get('localFinalReviewReady'))
 if ready:stage='1080p60 네 파일 · 내부 검수 완료 · 사용자 검수 대기'
 elif item['id']=='M21' and content.get('annotationRevision')=='sphere-v5' and state(render/'final-qa/browser-playback.json'):
  stage='1080p60 수정본 · 재질 구·광선·카메라·영문 기호 반영 · 전체 디코딩·브라우저 재생 검사 완료'
 elif content.get('status')=='four-files-available-integrated-listening-pending':stage='1080p60 네 파일 · 전체 디코딩·79문단 ASR·544프레임 검사 완료 · 연속 재생/청취 전'
 detail=finisher.get('results',{}).get(item['id'],{})
 for rp,worker in repairs:
  if item['id'] in worker.get('selected',[]) and audio and rp.stem.endswith(audio.name):
   detail=worker.get('results',{}).get(item['id'],{})
 if detail.get('status')=='production-attention-required' and not ready:stage+=' · 현재 제작 오류 점검 필요'
 outputs={}
 if qa:
  for k,v in qa.get('files',{}).items():
   if isinstance(v,dict) and v.get('path'):outputs[k]=v['path']
  dest=Path(qa['files']['captioned']['path']).parent
  outputs.update(index=str(dest/'index.html'),ko=str(dest/(item['slug']+'.ko.srt')),en=str(dest/(item['slug']+'.en.srt')))
 four=all(Path(outputs.get(k,'__missing__')).is_file() for k in ['clean','captioned','ko','en'])
 item.update(status='local-review-ready' if ready else ('media-generated-internal-review-pending' if four else 'active-production'),localReviewReady=ready,outputCandidatesAvailable=four,outputs=outputs)
 row=rows[item['id']];row.update(productionStatus=stage,productionComplete=ready,reviewStatus='사용자 최종 검수 대기' if ready else ('연속 재생·청취 검수 남음' if four else '완성 영상 대기 · 내부 검수 중'),notes='2026-11-04 승인된 M21–M33 로컬 제작 범위. '+stage+'. 업로드·예약 미승인.')
 item['evidence']={k:str(P/v) for k,v in [('sourceAudit','planning/source-audit.json'),('footageAudit','planning/footage-audit.json'),('sceneBindings','planning/scene-bindings.json'),('bilingualMap','planning/bilingual-caption-map.json')]}
 if render and qa:item['evidence'].update(technicalQa=str(render/'final-qa/report.json'),contentReview=str(render/'content-review.json') if content else None)
 if item['id']=='M21' and content.get('annotationRevision')=='sphere-v5' and (P/'production/sphere-v5/review-evidence.json').is_file():
  item['evidence'].update(sphereEvidence=str(P/'production/sphere-v5/review-evidence.json'),sceneCatalog=str(P/'production/sphere-v5/scene-catalog.json'))
  row.update(localMasterAvailable=four)
 cp=P/'production/checkpoint.json';d=state(cp);d.update(updatedAt=at,stage=stage,batch='production/batches/game-math-remaining-20261104/batch.json',localReviewReady=ready,humanReview=item.get('humanReviewed',False),outputsReady=four,outputCandidates=outputs,evidence=item['evidence'],boundSourceParagraphs=n,voiceWorker=voice,wordReviewWorker=words)
 d['nextAction']='Finish actual speech, source-matched runtime/annotation checks, full edit and internal audiovisual/mobile review. Existing outputs remain candidates until the stated review is complete.'
 running=[]
 for path,s in [(audio/'finite-worker.json' if audio else None,voice),(audio/'finite-word-review.json' if audio else None,words),(preview/'progress.json' if preview else None,pv),(render/'progress.json' if render else None,capture),(render/'composite/worker.json' if render else None,composite)]:
  if live(s) and s['status'] in {'synthesizing','running-preflight','capturing','transcribing-word-timestamps','compositing'}:
   record=dict(episode=item['id'],status=s['status'],pid=s['pid'],evidence=path.relative_to(R).as_posix());active.append(record);running.append(record)
 d['runningCostlyJobs']=running;save(cp,d);evidence[item['id']]=dict(stage=stage,localReviewReady=ready,outputsReady=four,evidence=item['evidence'])
 if pv:previews[item['slug']]=dict(pv,progressPath=(preview/'progress.json').relative_to(R).as_posix())
batch['updatedAt']=at;save(B/'batch.json',batch);save(R/'shared/publishing/video-worklist.json',work)
c=read(B/'checkpoint.json');c.update(updatedAt=at,status='active-production',currentWorkingEpisodes=sorted({x['episode'] for x in active}),currentWork=[k+': '+v['stage'] for k,v in evidence.items()],localReviewReady=[x['id'] for x in batch['items'] if x['localReviewReady']],outputCandidatesAvailable=[x['id'] for x in batch['items'] if x['outputCandidatesAvailable']],episodeVoiceWorkers=voices,modulePreflights=previews,runningCostlyJobs=active,resourceGate=dict(status='active-owned-work' if active else 'waiting-or-idle',jobs=active),nextAction='Finish exact M21–M33 local productions. Latest revisions and evidence above supersede historical snapshots. No platform mutation.',lastProductionCommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip())
c.update(currentEpisode=active[0]['episode'] if active else None,finiteProductionJobs=[{'file':file,'status':s.get('status'),'alive':live(s),'current':s.get('current'),'step':s.get('step'),'results':s.get('results',{})} for file,s in [('local/finish-module-candidates.json',finisher),('local/remaining-speech-worker.json',remaining)]+[(f.relative_to(B).as_posix(),s) for f,s in repairs]])
save(B/'checkpoint.json',c)
subprocess.run(['python','-X','utf8',str(B/'progress.py')],cwd=R,check=True)

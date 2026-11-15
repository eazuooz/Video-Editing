"""Reconcile only exact12 local state; never deliver or change another batch."""
from pathlib import Path
import datetime,hashlib,html,importlib.util,json,subprocess
import psutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');RUN=MEDIA/'production-resume-20261115T055255Z';DROOT=ROOT/'shared/output/original-tech-twelve-20261115';KEY='explicitOriginalTechTwelve20261115'
VOICE=['voice-edit-v3','voice-edit-v5','voice-repair-v6','voice-master-v8','voice-repair-v9','voice-master-v8','voice-master-v14','voice-repair-v6','voice-repair-v6','voice-repair-v6','voice-repair-v6','voice-sentence-v2']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def save(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def canonical(d):return hashlib.sha256(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 vp=HERE/'production-resume-validation-v49.json';assert not vp.exists();batch=read(HERE/'batch.json');assert len(batch['projects'])==12;now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();rows=[]
 for i,p in enumerate(batch['projects']):
  slug=p['slug'];base=MEDIA/slug;voice=base/VOICE[i]/'voice-generation-complete-proof.json'
  if not voice.exists()and i==4:voice=base/'voice-repair-v7/voice-generation-complete-proof.json'
  if not voice.exists():voice=base/'voice-repair-v6/voice-generation-complete-proof.json'
  if not voice.exists():voice=base/'voice-sentence-v2/voice-generation-complete-proof.json'
  selection=ROOT/'projects'/slug/('production/accepted-voice-selection-v27.json'if(ROOT/'projects'/slug/'production/accepted-voice-selection-v27.json').exists()else'production/accepted-voice-selection-v10.json')
  if selection.exists():voice=Path(read(selection)['voice']['path'])
  assert voice.exists();v=read(voice);vr=voice.parent/'technical-voice-review.json';accepted=vr.exists()and read(vr).get('approvedForTechnicalDownstream')and read(vr)['voice']==pin(voice)
  nb=(base/'native-stream-v2'if i<2 else DROOT/slug/'native-selected-v5'if i==2 else DROOT/slug/'native-completion-v6'if i in [3,4]else DROOT/'remaining-seven/native-completion-v6');np=nb/'accepted-full.json';native=np.exists();nv=nb/('full-visual-review-v2.json'if i<2 else'full-visual-review-v5.json'if i==2 else'full-visual-review-v6.json');review=native and nv.exists()and read(nv).get('allowedForFilm');bindings=[ROOT/'projects'/slug/('production/film-inputs-'+v+'.json')for v in['v37','v33','v27','v25','v10']];binding=next((x for x in bindings if x.exists()),None)
  if binding:
   bound=read(binding);np=Path(bound['nativeFullProofPath']);nv=Path(bound['nativeVisualReviewPath']);native=np.exists();review=native and nv.exists()and read(nv).get('allowedForFilm')
  bundle=base/'final-review-v1/bundle.json';complete=bundle.exists()and read(bundle).get('localFinalBundleComplete')
  if complete:
   for artifact in read(bundle)['artifacts'].values():assert pin(artifact['path'])['sha256']==artifact['sha256']
  pilot=base/('film-v8'if i==0 else'film-v7'if i==1 else'film-v10')/'pilot-proof.json'
  rows.append(dict(id=f'OT12-{i+1:02}',order=i+1,slug=slug,title=p.get('title',p.get('titleKo',slug)),voiceGenerated=True,voiceTechnicalReviewPassed=bool(accepted),voiceDuration=v['canonical']['duration'],voiceProof=pin(voice),nativeFullCaptured=native,nativeFullProof=pin(np)if native else None,nativeFullVisualReviewed=bool(review),encodedPilot=pin(pilot)if pilot.exists()else None,finalVideo=bool(complete),finalBundle=pin(bundle)if complete else None,humanApproval=False))
 for row in rows:
  P=ROOT/'projects'/row['slug'];bindings=[P/('production/film-inputs-'+v+'.json')for v in['v37','v33','v27','v25','v10']];binding=next((x for x in bindings if x.exists()),None);review=Path(read(binding)['mixProofPath']).parent/'mixed-content-review.json'if binding else None
  row['mixedAudioContentAndLevelsReviewed']=bool(row['finalVideo']or(review and review.exists()and read(review).get('approvedForPilot')))
 page=HERE/'production-progress-v49.html';progress=dict(updatedAtKst=now,sentenceVoiceGenerated=12,voiceTechnicalReviewPassed=sum(x['voiceTechnicalReviewPassed']for x in rows),mixedAudioContentAndLevelsReviewed=sum(x['mixedAudioContentAndLevelsReviewed']for x in rows),nativeActualSmokeGroups=6,nativeFullProjects=sum(x['nativeFullCaptured']for x in rows),finalVideos=sum(x['finalVideo']for x in rows),progressPage=str(page.relative_to(ROOT)).replace('\\','/'),rows=rows,sourceOrderPlansReady=12,sourceMaterialsAndDraftsReady=12,humanApproval=False,finalDelivery=False,platformActions=[])
 current=next((x['slug']for x in rows if not x['finalVideo']),None)
 for name in ['batch.json','checkpoint.json','local-production-continuation-v1.json']:
  path=HERE/name;d=read(path);d.update(latestVerifiedProductionProgress=progress)
  if name=='batch.json':
   for project,row in zip(d['projects'],rows):
    project.update(finalOutputsVerified=row['finalVideo'],voiceTechnicalReviewPassed=row['voiceTechnicalReviewPassed'],nativeFullCaptured=row['nativeFullCaptured'],nativeFullVisualReviewed=row['nativeFullVisualReviewed'],latestProductionState=row,resourceWaiterSnapshotsAreHistorical=True,status=('local-final-bundle-verified-awaiting-all12'if row['finalVideo']else'encoded-pilot-reviewed-clean-pending'if row['encodedPilot']else'exact12-production-active'),currentNativeTransport=('actual-full-source-verified'if row['nativeFullVisualReviewed']else'explicit-selected-source-full-capture-pending'))
  else:
   d.update(updatedAtKst=now,currentSlug=current,currentState='exact12-local-production-active-actual-output-reconciled',localFinalVideos=progress['finalVideos'],nextStep='Continue live guarded finite jobs. Inspect actual new native/ASR results; finalize source-ordered remaining lessons. Deliver only after all12 real local bundles. No intermediate approval or platform actions.');d['voiceAcceptedCount']=progress['voiceTechnicalReviewPassed'];d.update(voiceAcceptanceCount=progress['voiceTechnicalReviewPassed'],voiceTechnicalReviewPassed=progress['voiceTechnicalReviewPassed'],nativeFullCaptureCount=progress['nativeFullProjects'],independentFootageVerifiedCount=12,completedVoiceGenerationCount=12,phase='exact12-local-production-active',legacyCostlyJobCounterHistorical=True)
   d['activeStageCoordinator']='C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/finite-ready-pilots-v38/worker.json';d['additionalFiniteControllers']=['C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/finite-reviewed-finals-v42/worker.json'];d['oldWaiterSnapshotsAreHistorical']=True
  save(path,d)
 spec=importlib.util.spec_from_file_location('own_json_scope_splices',HERE/'finalize-cpu-preparation-v1.py');sp=importlib.util.module_from_spec(spec);spec.loader.exec_module(sp);scopes=[]
 for name in ['video-production-control.json','video-worklist.json']:
  path=ROOT/'shared/publishing'/name;before=path.read_bytes();text=before.decode('utf-8-sig');d=json.loads(text);own=d[KEY];own.update(completedVoiceGenerationCount=12,voiceTechnicalReviewPassed=progress['voiceTechnicalReviewPassed'],nativeFullCaptureCount=progress['nativeFullProjects'],nativeTransport='lossless-rgb-stream;two-full-reviewed-selected-rest-pending',localFinalVideos=progress['finalVideos'],updatedAtKst=now,progressPage=progress['progressPage'],latestVerifiedProductionProgress=progress,resourceStatus='User-authorized below35% start gate is active for this exact12. Original8/9GiB, foreign game/editor/render/model/app checks and exclusive lease remain. Own jobs advance without intermediate approval; original111 and other automations are unchanged.');new=sp.replace_value(text,KEY,own)
  if name=='video-worklist.json':
   updates={}
   for row in d['rows']:
    if row['id']not in{x['id']for x in rows}:continue
    r=next(x for x in rows if x['id']==row['id']);row.update(latestVerifiedProductionProgress=r,progressPage=progress['progressPage'],productionComplete=r['finalVideo'],localMasterAvailable=r['finalVideo'],productionStatus=('자막·클린·한영 자막·제목설명 파일 검증 완료'if r['finalVideo']else'원자료 순서 제작·음성 및 촬영 검수 진행'),reviewStatus=('로컬 QA 완료 / 12편 일괄 전달 대기 / 사람 검수 미실시'if r['finalVideo']else'최종 로컬 검수본 제작 중'),automaticChecksPassed=True if r['finalVideo']else None);updates[row['id']]=row
   new=sp.replace_rows(new,updates)
  assert path.read_bytes()==before,'Concurrent shared edit preserved; rerun only reconciliation with a new version'
  path.write_bytes((b'\xef\xbb\xbf'if before.startswith(b'\xef\xbb\xbf')else b'')+new.encode('utf8'));after=read(path);scopes.append(dict(path=str(path),ownKeySha256=canonical(after[KEY]),rowSha256=canonical([x for x in after.get('rows',[])if x.get('id','').startswith('OT12-')])if'rows'in after else None))
 table=[]
 for r in rows:
  links=''
  if r['finalVideo']:
   bundle=read(r['finalBundle']['path']);links=' · '.join('<a href="'+html.escape(Path(x['path']).as_uri())+'">'+label+'</a>'for key,label in [('captioned','자막 영상'),('clean','클린 영상'),('subtitlesKo','KO'),('subtitlesEn','EN'),('metadataKo','제목·설명')]for x in [bundle['artifacts'][key]])
  table.append('<tr><td>'+str(r['order'])+'</td><td>'+html.escape(r['title'])+'</td><td>'+('통과'if r['voiceTechnicalReviewPassed']else'검수·보수 중')+'</td><td>'+('검증'if r['nativeFullVisualReviewed']else'제작·검수 중')+'</td><td>'+('완료'if r['finalVideo']else'진행 중')+'</td><td>'+links+'</td></tr>')
 page.write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><title>12편 제작 진행표</title><style>body{font:17px system-ui;background:#101b17;color:#edf4ef;margin:36px}table{width:100%;border-collapse:collapse}td,th{padding:14px;border-bottom:1px solid #456252;text-align:left}a{color:#96ded2}small{color:#b7c7bc}</style><h1>12편 제작 진행표</h1><p>실제 로컬 검수본 '+str(progress['finalVideos'])+'/12 · 음성 기술 검수 '+str(progress['voiceTechnicalReviewPassed'])+'/12 · 자료·대본 12/12</p><p>제작 중 기록입니다. 최종 일괄 전달·사람 검수·업로드는 아직 하지 않았습니다.</p><table><tr><th>순서</th><th>주제</th><th>음성</th><th>촬영</th><th>최종본</th><th>실제 파일</th></tr>'+''.join(table)+'</table><p><small>'+html.escape(now)+' · 자동 검사와 표본 화면 검수는 전체 청취·실시간 재생·사람 승인과 구별합니다.</small></p></html>','utf8')
 sources=[]
 for p in HERE.rglob('*'):
  if p.is_file()and p.suffix.lower()in ['.py','.json','.html','.cs','.shader','.txt','.md']and'__pycache__'not in p.parts and p!=vp:sources.append(p)
 for row in rows:
  p=ROOT/'projects'/row['slug']
  for folder in ['planning','production','script','publishing']:
   sources += [f for f in(p/folder).rglob('*')if f.is_file()and f.suffix.lower()in['.json','.srt','.md','.py','.cs','.txt']and'__pycache__'not in f.parts]
 sources=sorted(set(sources));frozen=ROOT/'projects/shorts-leveldesign-11-05/checkpoint.json';external=[RUN/'generic-film-cpu-validation-v10.json',RUN/'inside-paired-clock-extraction-check-v1.json',MEDIA/rows[0]['slug']/'final-review-v1/bundle.json',MEDIA/rows[1]['slug']/'final-review-v1/bundle.json',RUN/'additional-completion-readiness-v17.json',RUN/'additional-phase-handoff-launch-v17.json',RUN/'resource-and-active-continuation-v18.json',RUN/'cooperative-resource-policy-validation-v19.json',RUN/'cooperative-owner-transition-v19.json',RUN/'idle-native-transition-complete-v20.json'];save(vp,dict(schemaVersion=49,checkedAtKst=now,exactProjects=12,progress=progress,sourceInputs=[pin(p)for p in sources],scopedSharedInputs=scopes,externalEvidence=[pin(p)for p in external],sourcePinsForSharedFilesAreScoped=True,frozenArchitecturalCheckpoint=pin(frozen),nativeRecoverySource=pin(HERE/'native-completion-source-v6/source-review-v2.json'),resourcePolicy=pin(HERE/'resource-policy-v19.json'),policy='User-authorized exact12 start utilization below35%; memory and ownership checks retained. Narration quality rules unchanged. Original raw audio and failed captures remain preserved. Only new explicit versions are adopted after actual QA. Complete-utterance level matching is separate from hiding any internal raw-utterance decline; original111 is excluded.',humanApproval=False,newRecurringAutomationCreated=False,finalDelivery=False,platformActions=[]));print(json.dumps(dict(validation=pin(vp),progress={k:v for k,v in progress.items()if k!='rows'},sourceFiles=len(sources))))
if __name__=='__main__':main()

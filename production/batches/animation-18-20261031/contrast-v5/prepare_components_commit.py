from pathlib import Path
import json
import hashlib
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
H=Path(__file__).resolve().parent;R=H.parents[3]
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf8')
now=datetime.now(ZoneInfo('Asia/Seoul')).isoformat()
final_review='--final-review' in sys.argv[1:]
s=read(H/'integration-progress-commit-spec.json');c=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
c.update(updatedAt=now,latestCompletionRequest='응~ 17편 전부 마저 완성해서 통합 검수 링크 줘~ 한꺼번에 볼게',gpuBoundary=read(H/'gpu-authorization.json'))
ready={}
integration=H/'renderer/integration-caption-safe.json'
if not integration.exists():integration=H/'renderer/integration-manifest.json'
integrationSha=hashlib.sha256(integration.read_bytes()).hexdigest()
for ep in c['episodes']:
 p=Path('C:/Users/1/Videos/YamyamCoding/animation-contrast-v5-review')/ep/'delivery.json'
 if p.exists():
  d=read(p)
  plan=H/'local/explanation-assembly'/ep/'edl.json'
  if d.get('localFinalFilesReady')and plan.exists()and read(plan)['integrationManifestSHA256']==integrationSha:
   master=next(f for f in d['files']if f['kind']=='captioned.mp4')
   try:
    with Path(master['path']).open('rb')as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
    if actual==master['sha256']:ready[ep]=d
   except OSError:pass
progress=c['componentProgress'];progress.update(newFullMastersCompleted=len(ready),finalCombinedReviewReady=False,finalFullVideoRenderRunningAtStatusCheck=True,sourceSpecificNarrationChanges=88,preservedNarrationSentences=913,gpuSpeechReleaseEvidence='화면공유끝',explanationManifest=integration.relative_to(R).as_posix(),explanationManifestSha256=integrationSha,gamePlateEpisodesReady=17,gamePlateManifest='production/batches/animation-18-20261031/contrast-v5/game-plates-caption-safe.json',captionSafePatch={'explanationRows':63,'retimedCopies':59,'canonicalGameHeaderRows':9})
if final_review:
 manifest=read(H/'review-manifest.json')
 assert manifest['scope']==c['episodes'] and len(ready)==17
 for record in manifest['records']:
  assert record['files']==ready[record['id']]['files']
 c['status']='local-final-review-ready'
 c['currentStage']='awaiting-human-final-review'
 progress.update(finalCombinedReviewReady=True,finalFullVideoRenderRunningAtStatusCheck=False,
                 reviewManifest=(H/'review-manifest.json').relative_to(R).as_posix(),
                 combinedReviewUrl=manifest['url'],sampledVisualQaEpisodes=17,
                 encodedAudioReadbackPassages=sum(record['encodedAudioReadback']['checkedPassages'] for record in manifest['records']),
                 remaining=['Human review of the exact delivered masters', 'Publication-use conditions if a later upload is selected'])
cp=read(H/'checkpoint.json');cp.update(updatedAt=now,gpuBoundary=c['gpuBoundary'],componentProgress=progress)
if(H/'local/tts-coordinator-state.json').exists():cp['activeSpeechPass']=read(H/'local/tts-coordinator-state.json')
if final_review:
 for key in ('activeSpeechPass','activeCpuTts'):
  cp.pop(key,None)
 cp.update(stage='awaiting-human-final-review',status='local-final-review-ready',reviewUrl=manifest['url'],
           humanReviewed=False,activeTasks=[],next='Review the exact local masters at the combined review URL.')
save(H/'checkpoint.json',cp)
s['control']=c;work={r['id']:r for r in read(R/'shared/publishing/video-worklist.json')['rows']};s['worklist']=[]
for ep in c['episodes']:
 q=work[ep]['contrastRevision'];q.update(componentStatus=c['status'],finalMasterReady=ep in ready)
 if ep in ready:q.update(status='four-local-files-ready-integrated-review-pending',captionedMasterSha256=next(f['sha256']for f in ready[ep]['files']if f['kind']=='captioned.mp4'),humanReviewed=False,platformChanged=False)
 if final_review:
  q.update(status='local-final-review-ready', reviewUrl=manifest['url']+ep+'/',
           sampledVisualQa=True, humanViewed=False, humanListened=False)
 s['worklist'].append({'id':ep,'set':{'updatedAt':now,'contrastRevision':q}})
s['markdownStatus']=f'비교 시연17편 완료 · 최종본{len(ready)}/17 통합 중 · 사용자 검수 대기'
if final_review:s['markdownStatus']='최종본 완료 · 통합 페이지에서 사용자 검수 대기'
m=read(H/'renderer/owned-files.json');files=[v['path'] for v in m['files']]+[m['selfEntry']]
names=['align_baseline.py','baseline-sentence-timing.json','edit_core.py','prepare_narration.py','run_cpu_narration.py','prepare_reviewed_tts.py','run_reviewed_cpu_tts.py','render_shape_diagram.cjs','serve_review.cjs','gpu-authorization.json','scoped_components_commit.py','prepare_components_commit.py','checkpoint.json']
names+=['assemble_explanations.py','prepare_final_audio.py','asr_changed_passages.py','render_game_plates.py','build_final_extensions.py','finish_remaining_tts.py','finish_local_review_queue.py','finalize_episode.py']
names+=['finish_quality_retakes.py','build_review_manifest.py','mix_verified_game_audio.py','qa_final_episode_frames.py','asr_final_aac.py','sync_changed_audio.py','review_changed_readbacks.py','build_changed_clauses.py','test_mix_idempotence.py','game-plates-manifest.json','game-plates-caption-safe.json']
files += [(H/n).relative_to(R).as_posix() for n in names]
files += [(H/'footage'/n).relative_to(R).as_posix()for n in ['final-audio-adoption.json','source-summary.json','final-source-metadata-check.json','canonical-name-lune.json','audio-technical-windows.json','game-audio-mixer-qa.json','final-picture-adoption.json','final-game-visibility.json','final-source-dimensions.json']]
files += [(H/'renderer'/n).relative_to(R).as_posix()for n in ['caption_safe_stage_footer.py','caption_safe_own_copies.py','qa_caption_safe_footer.py','integration-caption-safe.json','caption-safe/handoff.json','caption-safe/parent-adoption.json']]
handoff=H/'renderer/caption-safe/handoff.json'
if handoff.exists():files+=[q['path']for q in read(handoff)['ownedSourceAndMetadata']]
files += [p.relative_to(R).as_posix() for p in (H/'narration').iterdir() if p.is_file() and p.suffix in ['.json','.md','.py']]
files += ['projects/'+r['slug']+'/production/contrast-v5/final.'+lang+'.json' for r in read(H/'baseline-review-manifest.json')['records'] if r['id'] in c['episodes'] for lang in ['ko','en']]
p=R/'projects/animation-always-keep-attack-collision-in-mind/production/contrast-v5/changed-files.json'
if p.exists():files+=[r['path']for r in read(p)['ownedSourceAndMetadata']]+[p.relative_to(R).as_posix()]
if final_review:
 final_sources=['build_review_manifest.py','measure_final_picture.py','review-manifest.json',
                'prepare_a11_canonical_term.py','prepare_clarity_retakes.py','prepare_last_clarity_pair.py',
                'test_map_audio_boundary.py','test_tail_continuity.py','renderer/a11_term_chip.py',
                'qa_preserved_baseline_team_b.py','watch_final_frames_team_b.py',
                'footage/game-coverage-team-a.json','footage/team-b/game-coverage.json']
 files.extend((H/name).relative_to(R).as_posix() for name in final_sources)
 for directory in ['visual-corrections','visual-qa','picture-metrics']:
  files.extend(p.relative_to(R).as_posix() for p in (H/directory).iterdir()
               if p.is_file() and p.suffix in {'.json','.py'})
 revisions=read(H/'narration/source-verified-revisions.json')
 for episode in revisions['episodes']:
  for change in episode['changes']:
   for item in change.get('evidenceFiles',[]):
    evidence=R/item['path']
    if evidence.is_relative_to(H/'footage') and 'local' not in evidence.relative_to(H).parts and evidence.is_file():
     files.append(evidence.relative_to(R).as_posix())
s['ownedPaths']=sorted(set(files));save(H/'components-commit-spec.json',s)
print('Owned source files',len(s['ownedPaths']))

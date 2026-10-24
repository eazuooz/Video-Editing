"""Record completed local deliveries, scoped QA evidence and honest review limits."""
from pathlib import Path
import json,datetime,hashlib
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat();batch=read(B/'batch.json');slugs=batch['authorization']['slugs']
playback=read(B/'browser-playback-check.json');assert playback['status']=='pass'
playbackBySlug={r['slug']:r for r in playback['reports']};assert set(playbackBySlug)==set(slugs)
U=R/'unity/VideoEditing/Assets/VideoScenes/distinctive-shorts-20261024'
for f in U.rglob('*'):
 if f.suffix in ['.cs','.shader','.unity','.mat','.meta','.asset']:
  try:s=f.read_text(encoding='utf8');f.write_text('\n'.join(x.rstrip() for x in s.splitlines())+'\n',encoding='utf8')
  except UnicodeError:pass
topics=['titanfall','superliminal','ghost','gears','portal'];deliveries=[]
notes=[
 'Two stacked variants, unchanged x/z, once-only height transfer synchronized to the 10m phrase; over-shoulder confirmation switches intact/ruined variants. New v2 master preserves earlier outputs.',
 'Player and observer views show equal projected size while distance and object scale rise together. Surface rays are explanatory guides; gameplay confirmation shows the enlarged wedge used to reach a high exit.',
 'Same initial leaves with wind OFF/ON; no-wind falls toward the pit, updraft lifts leaves. Historical non-burning bug is a reconstruction, not presented as a recorded modern bug.',
 'Static 20/50-degree worked comparison, then a decaying 30-degree offset and continuous velocity. First cat reaction moved after the motion settled to protect the right arm.',
 'Actual stencil/RenderTexture implementation, nested views and finite depth. Scene values belong to our reconstruction, not a measurement of Valve internals.'
]
for i,slug in enumerate(slugs):
 p=R/'projects'/slug;project=read(p/'project.json');L=p/project.get('currentFinalDirectory','production/local/final-reviewed');A=p/('production/local/audio-v2' if (p/'production/local/audio-v2/voice/narration.wav').exists() else 'production/local/audio-v1')
 d=read(p/'production/delivery.json');integrity=read(L/'integrity.json');assert integrity['status']=='pass'
 browser=playbackBySlug[slug];assert browser['ended'] and browser['masterSha256']==d['files']['captioned']['sha256']
 assert sha(L/'captioned.mp4')==d['files']['captioned']['sha256']
 for item in d['files'].values():assert Path(item['path']).is_file() and sha(Path(item['path']))==item['sha256']
 voice=next(A.glob('asr-voice-*.json'));mix=next(A.glob('asr-mix-*.json'));continuity=read(A/'audio-continuity.json')
 assert read(voice)['fullInput'] and read(mix)['fullInput'] and continuity['fullDecodedAudioChecked']
 assert not continuity.get('sustainedEncodedAttenuationCandidates',[])
 q=L/('qa-sequential-'+d['files']['captioned']['sha256'][:12]);assert (q/'index.json').exists()
 visual=read(p/'production/visual-review.json');assert visual['masterSha256']==d['files']['captioned']['sha256']
 assert visual['inspectedSheets'] and visual['fullResolutionFrames']
 project.update(status='complete-local-final-review-pending',masterVersion=d['masterVersion'],publishReady=False)
 project['authorization']['status']='local-delivery-complete-awaiting-human-review'
 project['paths'].update(timeline=f'projects/{slug}/production/rebuild-timeline.json',footageManifest=f'projects/{slug}/sources/selected-footage.json',delivery=f'projects/{slug}/production/delivery.json',captionsKo=Path(d['files']['ko']['path']).relative_to(R).as_posix(),captionsEn=Path(d['files']['en']['path']).relative_to(R).as_posix())
 save(p/'project.json',project)
 checks=[{'id':'source-facts-and-rights','status':'recorded','evidence':['planning/production-plan.json','sources/selected-footage.json'],'limits':'Recording CC BY is not ownership of all underlying game IP; original audio removed and all credits preserved in the description.'},
 {'id':'master-integrity','status':'pass','evidence':str((L/'integrity.json').relative_to(p))},
 {'id':'browser-complete-playback','status':'pass','evidence':'production/batches/distinctive-shorts-20261024/browser-playback-check.json','limits':'Sequential normal-speed muted technical playback at 375px viewport; not human viewing/listening. A prior five-way CPU playback attempt timed out; master files did not change for this test.'},
 {'id':'visual-review','status':'inspected-at-recorded-points','evidence':'production/visual-review.json','notes':notes[i],'limits':'Sequential sampled frames and source ranges; not a claim of human full playback.'},
 {'id':'speech-and-mix','status':'technical-continuity-pass; human-listening-pending','evidence':[str(x.relative_to(p)) for x in [voice,mix,A/'audio-continuity.json',A/'caption-alignment.json']],'limits':'Whole-file unprompted ASR and decoded audio analysis; remaining name/particle pronunciation and contextual level flags require human listening.'}]
 ledger=read(p/'production/review-ledger.json');ledger.update(checks=checks,updatedAt=now,humanFinalReview='pending',humanListening='pending');save(p/'production/review-ledger.json',ledger)
 cp=read(p/'production/checkpoint.json');cp.update(stage='complete-local-final-review-pending',updatedAt=now,nextAction='User reviews this exact captioned SHA256 and final pronunciation/mix. No platform mutation authorized by this batch.',humanFinalReview='pending',platformChangesPerformed=False,currentEvidence={'delivery':'production/delivery.json','review':'production/review-ledger.json','currentFinalDirectory':project.get('currentFinalDirectory','production/local/final-reviewed'),'captionedSha256':d['files']['captioned']['sha256'],'voiceVersion':A.name,'resourceMode':'CPU / Unity WARP; user editors and unrelated jobs preserved'});save(p/'production/checkpoint.json',cp)
 plan=read(p/'planning/production-plan.json');plan['research']['productionStatus']='Finished local review delivery; human final viewing/listening pending';plan['finalVisualEvidence']='production/visual-review.json';plan['finalDelivery']='production/delivery.json'
 plan['assetChoice']={'libraryConsulted':'shared/assets/unity-asset-library.json; imported catalog','choice':'KayKit Adventurers Knight.fbx and knight_texture.png, CC0' if i==0 else 'Self-authored '+['','pawn and measured camera stage','leaf/flame meshes and airflow simulation','articulated mannequin and quaternion/angle demonstration','portal room and stencil/recursive RenderTexture implementation'][i],'reason':'Recognizable teaching object and one-variable comparison; no unnecessary environment pack.','provenance':'unity/VideoEditing/Assets/ThirdParty/KayKitAdventurers/provenance.json' if i==0 else 'Batch Unity source and generated mesh assets authored for this lesson.'}
 sceneRoot=R/f'unity/VideoEditing/Assets/VideoScenes/distinctive-shorts-20261024/Scenes/{topics[i]}'
 plan['savedScenes']=[x.relative_to(R).as_posix() for x in sorted(sceneRoot.glob('*.unity'))];assert plan['savedScenes']
 plan['measuredActualGameShare']=d['actualGameShare'];plan['shortFormatReason']='One specific mechanism, source-grounded actual game opening, native reconstruction and meaningful comparison. Report actual share; no unrelated combat padding.'
 plan['exampleSelectionReason']='Human explicitly selected these five game-specific mechanisms. Preserve each named game; do not add unrelated Nintendo or cross-genre examples to satisfy a long-form example-count target.'
 save(p/'planning/production-plan.json',plan)
 src=read(p/'sources/selected-footage.json');src['licenseUrl']='https://creativecommons.org/licenses/by/4.0/';src['licenseVersionBasis']='Current YouTube official CC BY help links CC BY 4.0; individual recording metadata confirms CC BY reuse label, not a separately exposed historical license-version field.';src['officialLicenseHelp']='https://support.google.com/youtube/answer/2797468?hl=en';save(p/'sources/selected-footage.json',src)
 timing=read(p/'production/visual-timing.json');timing['sources']['gameplay']['originalOffsetSeconds']=src['originalOffsetSeconds']
 for dest in [p/'production/visual-timing.json',p/'production/local/visual-timing.json',A/'visual-timing.json']:save(dest,timing)
 dependencies=[R/'motion-canvas/src/projects/distinctive-shorts-20261024/composite.tsx',R/f'motion-canvas/src/projects/distinctive-shorts-20261024/{topics[i]}/scene.tsx',R/'unity/VideoEditing/Assets/VideoScenes/distinctive-shorts-20261024/DemoState.cs',R/'unity/VideoEditing/Assets/VideoScenes/distinctive-shorts-20261024/Editor/BatchCapture.cs']
 save(p/'production/rebuild-timeline.json',{'schemaVersion':1,'currentMasterVersion':d['masterVersion'],'fps':60,'frames':timing['frames'],'scenes':timing['sections'],'sources':timing['sources'],'sourceOffsetMeaning':'Section sourceStart/sourceEnd are seconds within the downloaded local segment; add originalOffsetSeconds only to locate it in the original public recording.','nativeCaptureMode':timing['captureMode'],'gameFramesDirectory':timing.get('gameFramesDirectory','game-frames'),'audioDirectory':A.relative_to(R).as_posix(),'delivery':'production/delivery.json','editableDependencies':[{'path':x.relative_to(R).as_posix(),'sha256':sha(x)} for x in dependencies],'savedUnityScenes':plan['savedScenes'],'approvedHumanReview':False})
 deliveries.append(d)
batch.update(stage='complete-local-final-review-pending',updatedAt=now,completedAt=now,humanFinalReview='pending',deliveryManifest='production/batches/distinctive-shorts-20261024/delivery-manifest.json');batch['authorization']['status']='local-delivery-complete-awaiting-human-review'
for row in batch['projects']:row['status']='complete-local-final-review-pending'
save(B/'batch.json',batch)
save(B/'delivery-manifest.json',{'authorization':batch['authorization']['id'],'completedAt':now,'reviewPage':str(R/'output/distinctive-shorts-20261024/index.html'),'deliveries':deliveries,'humanReview':'pending','youtube':'not-uploaded','drive':'not-requested','automaticNextOutsideBatch':False})
control=read(R/'shared/publishing/video-production-control.json');control['shortsBatchAuthorization'].update(status='local-delivery-complete-awaiting-human-review',completedAt=now,deliveryManifest='production/batches/distinctive-shorts-20261024/delivery-manifest.json');save(R/'shared/publishing/video-production-control.json',control)
work=read(R/'shared/publishing/shorts-worklist.json')
for row in work['rows']:
 if row.get('slug') in slugs:
  d=deliveries[slugs.index(row['slug'])];row.update(production='complete-local-final-review-pending',review='human-final-review-pending',updatedAt=now,delivery='projects/'+row['slug']+'/production/delivery.json',captionedSha256=d['files']['captioned']['sha256'])
work['updatedAt']=now;save(R/'shared/publishing/shorts-worklist.json',work)
print('Five deliveries recorded; human review pending; no platform changes.')

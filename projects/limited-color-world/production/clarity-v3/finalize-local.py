"""Collect only the fully verified new D25 version; preserve prior deliveries."""
from pathlib import Path
from datetime import datetime,timezone
import json,copy,subprocess
import audio_pipeline as a
H=Path(__file__).resolve().parent;P=H.parents[1];R=H.parents[3]

def main():
 a.require_authorized('finalize-new-d25-local-review')
 plan=a.read(H/'edit-plan.json');out=a.repo_path(plan['outputDir']);structure=a.read(out/'structural-verification.json');pixels=a.read(H/'visual-review.json');audio=a.read(H/'audio-review.json');comparison=a.read(H/'final-comparison-review.json');build=a.read(out/'audio-build.json')
 assert structure['status']=='pass' and structure['identicalContinuousAudio']
 outputs=structure['outputs'];capHash=outputs['captioned']['sha256']
 assert pixels['status']=='pass' and pixels['masterSha256']==capHash
 assert set(pixels['reviewedCutIds'])=={c['id'] for c in plan['cuts']}
 assert pixels['allCaptionCuesReviewed'] is True and pixels['native1080AndMobile375Reviewed'] is True
 assert audio['status']=='pass' and audio['encodedAudioPacketsSha256']==outputs['captioned']['audioPacketsSha256']
 assert comparison['fullTextDirectlyCompared'] is True and comparison['encodedAudioPacketsSha256']==outputs['captioned']['audioPacketsSha256']
 assert build['sourcePcmPreserved'] and build['levelTargetsMet'] and build['music']['configured']
 for rec in outputs.values():assert a.sha(a.repo_path(rec['path']))==rec['sha256']
 captions={lang:out/f'captions.{lang}.srt' for lang in ['ko','en']}
 for rec in build['outputs']:assert a.sha(a.repo_path(rec['path']))==rec['sha256']
 saved=[]
 for cut in plan['cuts']:
  if cut['kind']!='explanation' or cut['variant'] in {'proof-options','puyo-official-filters','mirror-still'}:continue
  movie=a.repo_path(cut['renderedSource']);receipt=a.read(movie.parent/'render-success.json');assert receipt['status']=='complete' and receipt['frames']==cut['frames']
  scene=receipt['scene'];scene=('unity/VideoEditing/'+scene) if scene.startswith('Assets/') else scene
  assert a.repo_path(scene).is_file();saved.append(a.artifact(a.repo_path(scene)))
 assert len(saved)==18
 manifestPath=P/'project.json';originalBytes=manifestPath.read_bytes();manifest=json.loads(originalBytes.decode('utf-8-sig'));now=datetime.now(timezone.utc).isoformat()
 backup=H/'baseline-manifest.json'
 if not backup.exists():backup.write_bytes(originalBytes)
 else:assert a.read(backup)['revision']=='unity-visual-v2'
 baseline=a.read(backup);preserved=[]
 for key,oldHash in baseline['localFinalReview']['sha256'].items():
  oldPath=a.repo_path(baseline['localFinalReview']['files'][key]);assert a.sha(oldPath)==oldHash;preserved.append({'path':a.relative(oldPath),'sha256':oldHash})
 oldDelivery=P/'production/delivery-output.json'
 if oldDelivery.exists() and not (H/'baseline-delivery-output.json').exists():(H/'baseline-delivery-output.json').write_bytes(oldDelivery.read_bytes())
 delivery='projects/limited-color-world/production/local/clarity-v3/delivery';directory=delivery+'/output/limited-color-world';index=directory+'/index.html'
 files={'videoBurnedCaptions':outputs['captioned']['path'],'videoClean':outputs['clean']['path'],'captionsKo':a.relative(captions['ko']),'captionsEn':a.relative(captions['en'])}
 hashes={'captioned.mp4':capHash,'clean.mp4':outputs['clean']['sha256'],'ko.srt':a.sha(captions['ko']),'en.srt':a.sha(captions['en'])}
 manifest.setdefault('revisionHistory',[]).append({'revision':baseline['revision'],'manifest':a.relative(backup),'localFinalReview':baseline['localFinalReview']})
 manifest.update(revision='clarity-v3',status='local-review-ready',updatedAt=now)
 manifest['currentRevision']={'id':'clarity-v3','status':'local-review-ready','productionComplete':True,'humanFinalReview':'pending','automaticNextVideo':False,'baseRevision':'unity-visual-v2','visualOnly':False}
 manifest['plan']=manifest['visualRevisionPlan']=a.relative(H/'production-plan.json')
 manifest['latestCheckpoint']=a.relative(H/'checkpoint.json')
 manifest['paths'].update(files)
 manifest['paths'].update(script=a.relative(H/'narration.ko.json'),scriptEnglish=a.relative(H/'narration.en.json'),scriptEn=a.relative(H/'narration.en.json'),scriptSpoken=a.relative(H/'narration.spoken-ko.json'),productionPlan=a.relative(H/'production-plan.json'),scenePlan=a.relative(H/'production-plan.json'),visualRevisionPlan=a.relative(H/'production-plan.json'),finalPlan=a.relative(H/'edit-plan.json'),checkpoint=a.relative(H/'checkpoint.json'),reviewStatus=a.relative(H/'review-status.json'),captionAlignment=a.relative(out/'caption-alignment.json'),deliveryIndex=index,outputDirectory=directory)
 manifest['delivery'].update(localStorageRoot=delivery,userReviewClaimed=False)
 manifest['audio']={'voice':'Own ElevenLabs Sample B; newly expanded approved scope','backgroundMusic':'Nimbus — Eveningland, original approved file; measured normal game-design mix','humanWholeListening':'pending','sourcePcmPreserved':True,'sameContinuousAacInBothMasters':True,'previousRevisionAudioAndMediaPreserved':True}
 manifest['approvals'].update(render=True,qa=True,collected=False,uploaded=False);manifest['publishReady']=False
 manifest['finalRender']={'status':'complete-local-review-ready','captionedSha256':capHash,'durationSeconds':plan['totalFrames']/60,'openItems':['새 설명과 음성을 포함한 전체 영상의 사용자 최종 검수 대기'],'previousRevisionPreserved':True,'newVoiceAndTimingIntentional':True}
 manifest['localFinalReview']={'index':index,'files':{key:directory+'/limited-color-world.'+key for key in hashes},'sha256':hashes,'durationSeconds':plan['totalFrames']/60,'actualUserViewed':False,'humanWholeListening':'pending','internalQa':'complete','reviewRecord':a.relative(H/'review-status.json')}
 if manifestPath.read_bytes()!=originalBytes:raise RuntimeError('Concurrent manifest update detected; re-read before finalizing')
 manifestPath.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
 subprocess.run(['node','scripts/collect-video-output.cjs','limited-color-world'],cwd=R,check=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 collection=a.read(oldDelivery);assert collection['directory']==directory and len(collection['files'])==4
 for file in collection['files']:assert a.sha(a.repo_path(directory+'/'+file['name']))==file['sha256']
 manifest=a.read(manifestPath);manifest['approvals']['collected']=True;manifestPath.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
 review={'schemaVersion':1,'slug':'limited-color-world','revision':'clarity-v3','status':'local-review-ready','stage':'local-final-review','fourOutputsVerified':True,'captionedSha256':capHash,'durationSeconds':plan['totalFrames']/60,'localFiles':files,'localOutputDirectory':directory,'localIndex':index,'technicalSummary':'Both complete FHD60 masters decoded; exact frame/PTS grid, identical current continuous AAC and four-file hashes verified.','visualSummary':pixels,'audioSummary':audio,'reviewFocus':['같은 Unity 장면의 컬러→흑백→밝기/경계 보완→색 복원 흐름','게임의 대상·행동·결과와 설명의 연결','새 Sample B 발음과 전체 음량·호흡'],'humanWholeReview':'pending','humanWholeListening':'pending','nativeReplacedCutCount':18,'savedScenePaths':[x['path'] for x in saved],'savedScenes':saved,'photoOnlyExplanationCuts':5,'measuredShare':plan['measuredShare'],'preservedPriorDelivery':preserved,'uploadAuthorized':False,'schedulingAuthorized':False,'evidence':{'structural':a.relative(out/'structural-verification.json'),'visual':a.relative(H/'visual-review.json'),'audio':a.relative(H/'audio-review.json'),'finalAsr':a.relative(H/'final-comparison-review.json'),'collection':a.relative(oldDelivery)},'updatedAt':now}
 exception={'scope':'17 previously generated private c032 materials only','evidence':'production/batches/design-25-30-review-actions-20261029/contrast-repair/representative-pixel-proof.json','finding':'Earlier hash-only snapshot differs after AssetDatabase save/refresh; current bytes were preserved, not speculatively restored. Their BaseColor values match the previous c030 same-mode final values. Internal flush causality was not directly traced. Earlier native movies, saved scene files, delivered masters and vendor inputs retained their verified hashes.'}
 review['generatedAssetPreservationException']=exception
 review['finalVisualCorrection']={'nativeCuts':['c025','c026','c027','c030','c032'],'annotationOnlyCut':'c028','audioAndCaptionTimingUnchanged':True,'receipt':'production/batches/design-25-30-review-actions-20261029/D25-contrast-repair-native-receipt.json'}
 a.save(H/'review-status.json',review)
 production=a.read(H/'production-plan.json');production.update(status='local-review-ready',updatedAt=now);production['delivery'].update(localOutputDirectory=directory,localIndex=index,captionedSha256=capHash,fourOutputsVerified=True);a.save(H/'production-plan.json',production)
 checkpoint=a.read(H/'checkpoint.json');checkpoint.pop('oldVersionsChanged',None);checkpoint.update(status='local-review-ready',stage='local-final-review',updatedAt=now,captionedSha256=capHash,reviewStatus=a.relative(H/'review-status.json'),localOutputDirectory=directory,nextAction='Actual user review of this complete new version; no upload or next video authorized.',humanFinalReview='pending',oldDeliveriesChanged=False,generatedAssetPreservationException=exception);checkpoint['pending']=['actual user whole-video review'];a.save(H/'checkpoint.json',checkpoint)
 # The collector snapshots project settings before the final collected flag.
 # Replace only that JSON value; preserve all other exported records and bytes.
 rebuildPath=P/'rebuild.json';rebuildText=rebuildPath.read_text('utf8');marker='"projectSettings": '
 assert rebuildText.count(marker)==1
 start=rebuildText.index(marker)+len(marker);_,length=json.JSONDecoder().raw_decode(rebuildText[start:]);end=start+length
 latest=a.read(manifestPath);replacement=json.dumps(latest,ensure_ascii=False,indent=2).replace('\n','\n  ')
 updated=rebuildText[:start]+replacement+rebuildText[end:]
 assert json.loads(updated)['projectSettings']==latest
 rebuildPath.write_text(updated,'utf8')
 assert a.read(rebuildPath)['projectSettings']==a.read(manifestPath)
 print(json.dumps({'status':'local-review-ready','index':index,'captionedSha256':capHash}))
if __name__=='__main__':main()

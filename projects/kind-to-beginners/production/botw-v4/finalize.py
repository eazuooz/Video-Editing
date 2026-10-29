"""Select the verified isolated revision for local review. No platform writes."""
from pathlib import Path
import datetime,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;P=HERE.parents[1];LOCAL=P/'production/local/botw-v4';SLUG=P.name
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def rel(p):return p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 plan=read(HERE/'edit-plan.json');proof=read(LOCAL/'edit/structural-verification.json');pixels=read(HERE/'pixel-review.json');audio=read(HERE/'audio-review.json');native=read(HERE/'native-review.json')
 assert proof['status']=='pass'and proof['identicalContinuousAudio']
 assert pixels['status']=='passed'and audio['status']=='passed'and native['status']=='passed'
 assert pixels['editPlanSha256']==sha(HERE/'edit-plan.json')
 assert audio['sourceVoiceSha256']==read(HERE/'voice-generation-record.json')['source']['sha256']
 assert audio['fullCurrentTextCompared']is True and audio['bgmPresentVerified']is True
 for x in native['savedScenePaths']:assert(ROOT/x).is_file(),x
 files={'videoBurnedCaptions':LOCAL/f'edit/{SLUG}-captioned.mp4','videoClean':LOCAL/f'edit/{SLUG}-clean.mp4','captionsKo':LOCAL/'edit/captions.ko.srt','captionsEn':LOCAL/'edit/captions.en.srt'}
 hashes={k:sha(v)for k,v in files.items()}
 assert hashes['videoBurnedCaptions']==proof['outputs']['captioned']['sha256']and hashes['videoClean']==proof['outputs']['clean']['sha256']
 assert pixels['captionedSha256']==native['captionedSha256']==hashes['videoBurnedCaptions'],'Pixel/native review must describe this exact final master'
 assert pixels['captionsAssSha256']==sha(LOCAL/'edit/captions.ko.ass')
 assert pixels['captionsKoSha256']==hashes['captionsKo']and pixels['captionsEnSha256']==hashes['captionsEn']
 assert native['nativeBindingSha256']==sha(HERE/'native-binding.json')
 assert native['savedScenePaths']==read(HERE/'native-binding.json')['savedScenePaths']
 pair=read(LOCAL/'edit/pair-build.json');aac=LOCAL/'edit/pair-audio.m4a'
 assert audio['finalAacSha256']==pair['signature']['aacSha256']==sha(aac)
 for kind in ['captioned','clean']:
  assert pair['outputs'][kind]['sha256']==proof['outputs'][kind]['sha256']
  assert pair['outputs'][kind]['audioPacketsSha256']==proof['outputs'][kind]['audioPacketsSha256']
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();manifest=read(P/'project.json')
 # Save the exact manifest we supersede; previous media and prior revision files stay intact.
 if not(HERE/'prior-project-manifest.json').exists():save(HERE/'prior-project-manifest.json',manifest)
 manifest.update(revision='botw-v4',status='local-review-ready',updatedAt=now,publishReady=False)
 manifest.pop('pendingRevision',None)
 manifest['delivery']['localStorageRoot']=rel(LOCAL/'delivery');manifest['paths'].update({k:rel(v)for k,v in files.items()})
 manifest['paths'].update(narrationKo=rel(P/'script/botw-v4/narration.ko.json'),narrationEn=rel(P/'script/botw-v4/narration.en.json'),scenePlan=rel(HERE/'production-plan.json'))
 manifest['plan']=rel(HERE/'production-plan.json');manifest['paths']['visualRevisionPlan']=rel(HERE/'production-plan.json');manifest['visualRevisionPlan']=rel(HERE/'production-plan.json');manifest['latestCheckpoint']=rel(HERE/'checkpoint.json')
 manifest['review']={'actualUserViewed':False,'humanWholeListening':'pending','priorFeedback':'User explicitly selected Breath of the Wild instead of Mario Kart and requested matching narration and Unity explanations. New revision awaits human review.'}
 manifest['finalRender']={'status':'complete-local-review-ready','knownIssues':[],'openItems':['사용자의 새 완성본 전체 시청·최종 청취 검수 대기']}
 save(P/'project.json',manifest)
 subprocess.run(['node','scripts/collect-video-output.cjs',SLUG],cwd=ROOT,check=True)
 delivery=read(P/'production/delivery-output.json');count=sum(c['kind']=='explanation'for c in plan['cuts']);seconds=plan['totalFrames']/60
 review={'slug':SLUG,'revision':'botw-v4','status':'local-review-ready','updatedAt':now,'fourOutputsVerified':True,'captionedSha256':hashes['videoBurnedCaptions'],'durationSeconds':seconds,'technicalSummary':f"1920×1080 ·60fps ·{plan['totalFrames']}frames. Both complete streams/frame timestamps and identical finalAAC verified; body60%actual/40%explanation.",'visualSummary':f'Breath of the Wild replaces Mario Kart; Unpacking and A Short Hike are retained. {count} editable native Unity explanation cuts, actual game before/action/result and final captioned1080p/375px review.','audioSummary':'New continuous own-voice ElevenLabs SampleB. Full unprompted ASR/script comparison and encoded mix verification; same licensed Nimbus BGM and source-specific synchronized gameplay sound.','reviewFocus':['처음 게임을 해 보는 사람도 예시의 상황을 이해하는지','야숨의 문제 신호·방한 선택·정리·탐험의 행동과 결과가 설명과 맞는지','새 음성의 발음·호흡·BGM 균형'],'humanWholeReview':'pending','humanWholeListening':'pending','nativeReplacedCutCount':count,'savedScenePaths':native['savedScenePaths'],'directory':delivery['directory'],'localOutputDirectory':delivery['directory'],'outputs':delivery['files'],'directQA':{'native':rel(HERE/'native-review.json'),'pixels':rel(HERE/'pixel-review.json'),'audio':rel(HERE/'audio-review.json'),'structure':rel(LOCAL/'edit/structural-verification.json'),'voice':rel(HERE/'voice-generation-record.json'),'timing':rel(HERE/'timing-lock-receipt.json')},'platformMutation':False,'oldVersionsPreserved':True}
 save(HERE/'review-status.json',review);save(HERE/'checkpoint.json',{'slug':SLUG,'revision':'botw-v4','status':'local-review-ready','updatedAt':now,'outputIndex':delivery['directory']+'/index.html','captionedSha256':hashes['videoBurnedCaptions'],'humanWholeReview':'pending','platformMutation':False,'priorOutputsPreserved':True})
 production=read(HERE/'production-plan.json');production['status']='local-review-ready';production['quality'].update(technicalReview='complete; native, sampled final pixels, caption clocks, full stream decode, source and final-mix text comparison verified',humanWholeReview='pending',captionExactTextValidation='113 KO/EN cues retain all23 paragraphs; paired plain-text reconstruction, fixed48px layout and all113 encoded Korean cue midpoints reviewed at1080/375. Unchanged caption input QA reused after two-mark correction.',nativePreflight='Complete22 native captures and saved scenes verified; no outstanding capture work.',realizedSpeechVisualReview='Locked speech/caption clock matched to observed native/game state sequences; final full AAC/script comparison and continuity passed. Actual human listening remains pending.')
 for item in production.get('pendingEvidence',[]):
  item['status']='resolved-source-and-final-sampled-pixels-reviewed';item['finalReview']=rel(HERE/'pixel-review.json')
 for cut in production['cuts']:
  if cut['kind']=='independent-gameplay':cut['annotationState']='final sampled pixels reviewed; two corrected marks rechecked on final master; see pixel-review.json'
 production['finalDeliveryReview']=rel(HERE/'review-status.json');save(HERE/'production-plan.json',production)
 manifest['localFinalReview']={'index':delivery['directory']+'/index.html','durationSeconds':seconds,'captionedSha256':hashes['videoBurnedCaptions'],'actualUserViewed':False,'humanWholeListening':'pending','internalQa':'complete','reviewRecord':rel(HERE/'review-status.json')};save(P/'project.json',manifest)
 # Collection generated rebuild.json before the final localFinalReview fields.
 # Refresh only this project's metadata after the last authoritative save.
 subprocess.run(['node','scripts/build-rebuild-manifests.cjs',SLUG],cwd=ROOT,check=True)
 assert read(P/'rebuild.json')['projectSettings']==read(P/'project.json'),'Final rebuild settings are stale'
 ledger_path=P/'production/review-ledger.json';old_ledger=read(ledger_path)
 history=list(old_ledger.get('revisionHistory',[]))
 if old_ledger.get('revision')!='botw-v4':history.append({k:v for k,v in old_ledger.items()if k!='revisionHistory'})
 checks=[]
 for name,scope in [('source-script-review.json','Full independent script and reference teaching-order preservation'),('sources.json','Independent FHD game sources, exact ranges and provenance'),('native-review.json','22 editable native scenes; sampled full-sequence pixels with explicit unchanged-input reuse'),('pixel-review.json','53 cuts and113 caption cues; final two-mark correction and adjacent boundaries'),('audio-review.json','Continuous own voice, whole text comparison, Nimbus/game audio and encoded level/continuity'),('review-status.json','Four exact local deliverables; user whole viewing/listening pending')]:
  file=HERE/name;checks.append({'id':'botw-v4-'+file.stem,'scope':scope,'result':'technical-and-sampled-review-complete-human-review-pending','evidence':rel(file),'sha256':sha(file)})
 checks.append({'id':'actual-human-user-review','scope':'New exact full captioned deliverable','result':'not-performed','inferredFromTechnicalChecks':False})
 save(ledger_path,{'schemaVersion':1,'slug':SLUG,'revision':'botw-v4','status':'local-review-ready-human-viewing-listening-pending','updatedAt':now,'currentMasterSha256':hashes['videoBurnedCaptions'],'checks':checks,'platform':old_ledger.get('platform',{}),'revisionHistory':history})
 print('Local botw-v4 delivery ready',hashes['videoBurnedCaptions'])
if __name__=='__main__':main()

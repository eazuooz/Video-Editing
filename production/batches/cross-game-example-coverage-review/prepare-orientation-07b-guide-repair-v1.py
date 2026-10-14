"""Seal completed21a splice review and prepare one bounded guide-phrase repair."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,wave
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,x):
 assert not p.exists(),p;p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
at=datetime.now(timezone.utc).isoformat();sp=O/'post-splice-current-voice-asr-execution-v1.json';s=read(sp);old=read(O/'narration-cross-game-repair-execution-v1.json')
assert s['actualOuterSession']==10938 and s['actualOuterExitCode']==0 and s['actualCompletion']=='de2fff' and s['completed']==3 and s['protectedAndAllCurrentPcmShaMatched']
for x in old['protectedInputs']+old['results']+s['results']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
whole,seam,alternative=s['results'];assert whole['id']=='21a-spliced-whole' and seam['id']=='21a-spliced-seam'
normalize=lambda t:''.join(c for c in t if c.isalnum())
assert normalize(whole['text'])==normalize(' '.join(whole['expectedKo'])) and normalize(seam['text'])==normalize(' '.join(seam['expectedKo']))
splice=read(O/'21a-first-paragraph-splice-execution-v1.json')
def raw(path):
 with wave.open(str(ROOT/path),'rb') as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2);return w.readframes(w.getnframes())
data=raw(splice['outputPath']);prefix=raw(splice['candidatePath']);original=raw(splice['originalPath']);gap=b'\x00\x00'*splice['quietGapSamples'];assert data==prefix+gap+original[splice['originalP2OnwardStartSample']*2:]
proof=O/'21a-spliced-whole-and-seam-direct-review-v1.json'
save(proof,dict(reviewedAt=at,actualOuterSession=10938,actualOuterExitCode=0,actualCompletion='de2fff',closureRecorder='6b4fc6 exit0',fullTextDirectRead='1c8323 exit0 and current saved state reread',execution=rel(sp),executionSha256=sha(sp),wholeAndCompleteFirstTwoParagraphSeamCompared=True,allWordLandmarksRead=True,rows=[dict(id=r['id'],expectedKo=r['expectedKo'],recognized=r['text'],pcmPath=r['path'],pcmSha256=r['sha256'],firstWords=r['chunks'][:2],lastWords=r['chunks'][-2:]) for r in s['results'][:2]],new21aAdoptedPath=splice['outputPath'],new21aAdoptedSha256=splice['outputSha256'],seconds=14.28,lineStarts=[0,5.66,11.6],originalP2OnwardAllBytesPreserved=True,originalOverwritten=False,current21aCompletenessApproved=True,humanListeningApproved=False,humanPronunciationApproved=False,currentMixedApproved=False,finalCuePixelsApproved=False,ratioApproved=False))
ko='카메라도 움직이니까, 화면에 그린 선은 관찰용 표시입니다. 앞서 계산한 구십 도는 따로 정한 수학 예입니다.'
en='The camera also moves, so the lines drawn on the screen are observation guides. The ninety-degree calculation shown earlier is a separately defined mathematical example.'
newfolder=ROOT/'shared/output/narration/game-math-orientation-matrices/07b-guide-repair-v1';assert not newfolder.exists()
kos=O/'script/07b-guide-repair-v1.ko.json';ens=O/'script/07b-guide-repair-v1.en.json'
save(kos,dict(title='비행 표식의 관찰 범위 · 마지막 문단 보정 후보',scenes=[dict(id='07r',title='화면 선과 별도의 계산을 구분',lines=[ko])]))
save(ens,dict(title='비행 표식의 관찰 범위 · 마지막 문단 보정 후보',scenes=[dict(id='07r',title='화면 선과 별도의 계산을 구분',lines=[en])]))
reviewp=O/'07b-guide-paired-script-direct-review-v1.json'
save(reviewp,dict(reviewedAt=at,ko=ko,en=en,koPath=rel(kos),koSha256=sha(kos),enPath=rel(ens),enSha256=sha(ens),oldExpected=alternative['expectedKo'][0],wholeAndTwoIndependentAlternativesHeld=alternative['text'],reason='The current whole, independent and alternatebeam3 do not recover 화면의 선은. Clarify the subject 화면에 그린 선 and split two clauses into complete sentences within this single new paragraph. No confirmed acoustic or human pronunciation failure is inferred.',sameCameraObservationAndSeparateMathModelClaims=True,measurementOrEngineClaimsAdded=False,firstFiveParagraphsAndAllOriginal24PcmPreserved=True,originalAllWordingAndOrderPreserved=True,contentReadyForApprovedVoiceMeasurement=True,humanListeningApproved=False,sourcePlanningOnly=True))
manifest=read(O/'tts-cross-game-repair-manifest-v1.json');manifest['paths']['script']=rel(kos);manifest['paths']['scriptEn']=rel(ens);manifest['tts'].update(outputDir=rel(newfolder),filenameStem='orientation-07b-guide-repair-v1');manifest['revision'].update(status='one-paragraph-candidate-only') if 'revision' in manifest else None
manifestp=O/'tts-07b-guide-repair-manifest-v1.json';save(manifestp,manifest)
protected=old['protectedInputs']+old['results']+[dict(path=rel(p),sha256=sha(p)) for p in [proof,O/'cross-game-whole-and-independent-direct-review-v1.json',O/'21a-first-paragraph-splice-execution-v1.json',kos,ens,reviewp,manifestp]]
requestp=O/'narration-07b-guide-repair-request-v1.json';save(requestp,dict(preparedAt=at,slug='game-math-orientation-matrices',total=1,paragraphs=1,pairedWholeTextReview=True,overviewPromiseReview=True,baselineApprovedPcmRegeneration=0,existing6AdditivePcmRegeneration=0,scriptReview=rel(reviewp),sourceReview='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/cross-game-native-direct-review-v1.json',manifest=rel(manifestp),protectedInputs=protected,scenes=[dict(id='07r',text=ko,path=rel(newfolder/'chunks/07r-scene.wav'))],candidateAdopted=False,modelStarted=False))
wrapper=(B/'render-orientation-cross-game-repair-v1.py').read_text('utf-8')
for oldtext,newtext in [
 ('narration-cross-game-repair-execution-v1','narration-07b-guide-repair-execution-v1'),('narration-cross-game-repair-request-v1','narration-07b-guide-repair-request-v1'),('narration-cross-game-repair-session-v1','narration-07b-guide-repair-session-v1'),('resource-before-cross-game-repair-voice-v1','resource-before-07b-guide-repair-voice-v1'),('narration-cross-game-repair-waiting-v1','narration-07b-guide-repair-waiting-v1'),('cross-game-repair-owned-idle-guard-v1','07b-guide-repair-owned-idle-guard-v1'),('narration-cross-game-repair-v1.log','narration-07b-guide-repair-v1.log'),("request['total']==5 and request['paragraphs']==19","request['total']==1 and request['paragraphs']==1"),("source_review['sourcePlanningMayProceed']","source_review['all217NativeSamplesAnd45BoardsDirectlyRead']"),('total=5','total=1'),('total=5','total=1'),("len(state['results'])==5","len(state['results'])==1"),('five-items','one-guide-candidate'),('Five items','One guide candidate'),('Prepared5items/19pairedparagraphs','Prepared1item/1pairedparagraph')]:wrapper=wrapper.replace(oldtext,newtext)
source=read(ROOT/read(requestp)['sourceReview'])
# Existing native direct-review receipt has explicit count and planning scope.
wrapper=wrapper.replace("assert source_review['all217NativeSamplesAnd45BoardsDirectlyRead']","assert source_review['all217NativeSamplesAnd45BoardsDirectlyRead'] and source_review['exactNativePtsVerified']")
save_wrapper=B/'render-orientation-07b-guide-repair-v1.py';assert not save_wrapper.exists();save_wrapper.write_text(wrapper,'utf-8')
observer=(B/'observe-orientation-cross-game-voice-resource-v1.py').read_text('utf-8').replace('resource-before-cross-game-repair-voice-v1','resource-before-07b-guide-repair-voice-v1').replace('narration-cross-game-repair-request-v1','narration-07b-guide-repair-request-v1').replace('assert len(protected)==61','assert len(protected)==76')
(B/'observe-orientation-07b-guide-voice-resource-v1.py').write_text(observer,'utf-8')
cp=read(O/'latest-checkpoint.json');cp.update(stage='21a-splice-approved-one-07b-guide-clarification-prepared',currentAsrHeldParagraphs=['07b-p06'],spliced21CurrentReview=rel(proof),activeOwnedWorkers=0,ownedJob=None,next='Verify exact native receipt field/currentduplicate, freshGPU idle observation, then one new07b lastparagraph candidate only. Preserve all original/newPCM. MeasuredManim and finaltracking remain pending.');(O/'latest-checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
qp=B/'queue.json';qraw=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=0,ownedJob=None,spliced21CurrentReview=rel(proof),next=cp['next']);assert qp.read_bytes()==qraw;qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(spliced21Approved=True,guideKo=ko,guideEn=en,protected=len(protected),preparedOnly=True,model0=True,sourceReceiptKeys=list(source))))

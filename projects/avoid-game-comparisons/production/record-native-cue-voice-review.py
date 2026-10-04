"""Record direct new15 whole/context review; preserve all14 existing PCM."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
now=datetime.now(timezone.utc).isoformat();request=read(BASE/'native-cue-narration-request.json')
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
tts=read(BASE/'native-cue-narration-tts-execution.json');full=read(BASE/'native-cue-whole-asr-execution.json');ctx=read(BASE/'native-cue-context-asr-execution.json')
assert tts['exitCode']==full['exitCode']==ctx['exitCode']==0 and tts['generationComplete'] and full['readbackComplete'] and ctx['readbackComplete']
new=tts['results'][0];assert new['id']=='15' and sha(ROOT/new['path'])==new['sha256']
notes={
 '15-first-paragraph':'Whole readback has 책의; independent readback has 각 책의 and both have 말의 versus written 말에. Full page approach/fighting/platform movement and bright/dark-space meaning remains present. Exact initial consonant/particle pronunciation remains pending human review; this is not an invented greeting or a new gameplay claim.',
 '15-desk-pepper-context':'Desk clause ending and the complete Pepper water/lava/movement/firing/target statements are present in their original order. No omission or repeated sentence observed.',
 '15-target-mine-context':'Target instruction and whole mine approach/avoidance/attack/general-rule caveat are present; final 않습니다 ending is present. No added greeting or repeated sentence observed.'}
for s in [full,ctx]:
 for x in s['results']:
  assert x['audioSha256']==new['sha256'];x['directReview']=True
  x['reviewNote']=notes.get(x['id'],'All four current-hash paragraphs directly compared: page-space distinction, desk actions, Pepper movement/target and mine-rule caveat remain in order. Particle/initial-consonant uncertainty is retained from the independent first paragraph.')
 s.update(directWholeScriptReview=True,status='direct-whole-and-context-review-complete-technical-only',updatedAt=now,cpuJobs=0,actualWorkerClosed=True,narrationApproved=True,humanWholeListening='pending',humanPronunciation='pending')
save(BASE/'native-cue-whole-asr-execution.json',full);save(BASE/'native-cue-context-asr-execution.json',ctx)
review=dict(schemaVersion=1,reviewedAt=now,wholeCurrentHashAsrDirectReview=True,allFourParagraphsTechnicallyReviewed=True,independentContextsDirectlyReviewed=3,audioPath=new['path'],audioSha256=new['sha256'],seconds=new['seconds'],original14PcmPreserved=True,observations=[x['reviewNote'] for x in full['results']+ctx['results']],wholeAsr=rel(BASE/'native-cue-whole-asr-local/15.json'),independentContexts=[dict(id=x['id'],path=rel(BASE/'native-cue-context-asr-local'/f"{x['id']}.json"),text=x['text'],audioSha256=x['audioSha256'],directReview=True,note=x['reviewNote']) for x in ctx['results']],sentenceOmissionObserved=False,sentenceRepetitionObserved=False,addedGreetingObserved=False,endingMissingObserved=False,exactPronunciationApproved=False,humanWholeListening='pending',humanPronunciation='pending',finalMixAsrReviewed=False,allFinalCaptionPixelsReviewed=False,bodyRatioApproved=False)
save(BASE/'native-cue-narration-direct-review.json',review)
tts.update(wholeNewAsrDirectReview=True,finalNarrationApproved=False,currentScene15TechnicalAsrReview=True,status='new15-current-hash-technical-review-complete-final-mix-pending',updatedAt=now);save(BASE/'native-cue-narration-tts-execution.json',tts)
index=read(BASE/'narration-expanded-index.json')
for x in index['measurements']:assert sha(ROOT/x['path'])==x['sha256']
index['measurements'].insert(next(i for i,x in enumerate(index['measurements']) if x['scene']=='12'),dict(scene='15',path=new['path'],sha256=new['sha256'],frames=new['samples'],sampleRate=new['sampleRate'],seconds=new['seconds'],text=new['text'],tailRatio=new['tailRatio'],tailDecayMs=new['tailDecayMs'],fullAsrReview=True,humanListening='pending',readbackEvidence=rel(BASE/'native-cue-narration-direct-review.json')))
index.update(updatedAt=now,createdAt=now,version='current15-preserved14-plus-new15',sceneCount=15,paragraphCount=60,paragraphs=60,speechSeconds=sum(x['seconds'] for x in index['measurements']),totalSeconds=sum(x['seconds'] for x in index['measurements']),technicalScope='Current15 scenes/60 paired paragraphs:14 unchanged current-hash full/context reviews plus new15 whole and3 independent contexts. Human full listening/exact pronunciation remain pending.',status='current15-scene-technical-ASR-reviewed-final-timing-pending',fullCurrentHashAsrApproved=True,allOriginal14PcmPreserved=True,finalMixAsrApproved=False,measuredFinalBodyRatioApproved=False)
save(BASE/'narration-expanded15-index.json',index)
measured=read(BASE/'measured-paragraphs-expanded14.json');newm=read(BASE/'measured-paragraphs-new15.json')
measured['scenes'].insert(next(i for i,x in enumerate(measured['scenes']) if x['id']=='12'),newm)
measured.update(createdAt=now,scope='expanded15',scriptKoSha256=sha(BASE.parent/'script/narration.ko.json'),scriptEnSha256=sha(BASE.parent/'script/narration.en.json'),original14MeasurementsPreserved=True,finalTimingApproved=False,finalRatioApproved=False)
save(BASE/'measured-paragraphs-expanded15.json',measured)
p=BASE.parent/'project.json';d=read(p);d.update(status='current15-voice-technically-reviewed-exact-native-cue-review')
d['production'].update(pendingNarrationExpansion=False,currentVoiceApproved=True,currentVoiceApprovalScope='Technical full current-hash ASR and ambiguous independent context readback only; human whole listening/pronunciation and final mix review pending.',newScene15VoiceApproved=True,currentNarrationIndex=rel(BASE/'narration-expanded15-index.json'),narrationSpeechMeasurements=rel(BASE/'measured-paragraphs-expanded15.json'),currentNarrationTechnicalReview=rel(BASE/'native-cue-narration-direct-review.json'),finalTimingApproved=False);save(p,d)
p=BASE/'script-source-review.json';d=read(p);d.update(updatedAt=now,status='15-scenes60-paragraphs-current-voice-technically-reviewed-native-cue-review-pending',current15PcmTechnicalReview=rel(BASE/'native-cue-narration-direct-review.json'));save(p,d)
qpath=PROOF.parent/'queue.json';q=read(qpath);task=next(x for x in q['items'] if x['slug']=='avoid-game-comparisons')
task.update(stage='current15-voice-approved-exact-native-cue-review',updatedAt=now,nextAction='Inspect new native cut edges and remaining distinct official actions; resolve short montage/cue mismatches before frame60:40 approval. Preserve all15 current PCM and original six white explanations. Final mix, every fixed cue, subtitles, render/QA/collection/private save remain pending.')
task['nativeCueNarration'].update(newSceneIds=['15'],generationComplete=True,wholeNewAsrDirectReview=True,independentContextsReviewed=3,current15Index=rel(BASE/'narration-expanded15-index.json'),speechSeconds=index['totalSeconds'],new15Seconds=new['seconds'],originalAll14PcmPreserved=True,scriptScenes=15,paragraphs=60,review=rel(BASE/'native-cue-narration-direct-review.json'))
task['execution'].update(observedAt=now,status='closed-new15-TTS-full-and-context-ASR-technically-reviewed',alive=False,activeTasks=[],secondaryTasks=[],gpuSynthesisJobs=0,cpuProductionJobs=0,primaryCpuProductionJobs=0,renderJobs=0,uploads=0)
q.update(updatedAt=now,lastProgressAt=now);save(qpath,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
 d=read(p)
 for k in ['stage','updatedAt','nextAction','nativeCueNarration','execution']:d[k]=task[k]
 save(p,d)
print(json.dumps(dict(currentScenes=15,paragraphs=60,speechSeconds=index['totalSeconds'],new15Seconds=new['seconds'],unchangedOriginal14=True,bodyRatioApproved=False)))

from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,wave,numpy as np,os,subprocess
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
proof=BASE/'paired-selective-script-direct-review-v1.json';assert not proof.exists()
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
k=read(BASE/'script/narration.ko.json');e=read(BASE/'script/narration.en.json');audit=read(BASE/'selective-script-change-audit-v1.json');selection=read(BASE/'pcm-preservation-selection-v1.json')
assert len(k['scenes'])==len(e['scenes'])==19
assert sum(len(s['lines']) for s in k['scenes'])==39
for ks,es in zip(k['scenes'],e['scenes']):assert ks['id']==es['id'] and len(ks['lines'])==len(es['lines'])
boundary=[]
for r in selection['preservedRanges']:
 p=ROOT/r['sourcePath'];assert sha(p)==r['sourceSha256']
 if r['id']=='07-name-and-unit' and r['paragraph']==3:
  r['sourceStartSample']=268800;r['samples']=r['sourceEndSampleExclusive']-268800;r['seconds']=r['samples']/24000
  with wave.open(str(p),'rb') as w:pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype('float64')
  a=268800;window=pcm[a-120:a+120];rms=float(np.sqrt(np.mean(window**2)));peak=int(np.max(np.abs(window)));assert rms<15 and peak<50
  boundary.append({'id':r['id'],'sample':a,'seconds':11.2,'rms10ms':rms,'peak10ms':peak,'currentWholeWords':'있죠 ends10.98; 어떤 starts11.30; actual PCM quiet11.20 before signal rises11.25','method':'direct whole ASR word text plus actual current PCM gap; no alteration of preserved samples','completeJoinedContextReviewStillRequired':True})
selection['07BoundaryNote']='Use actual PCM quiet11.20s(sample268800), before 어떤 starts and after 있죠. Original11.30 boundary would lose an onset; no source PCM changed. Independent complete joined ASR remains pending.'
selection['boundaryInspection']=boundary;save(BASE/'pcm-preservation-selection-v1.json',selection)
now=datetime.now(timezone.utc).isoformat()
review={'schemaVersion':1,'reviewedAt':now,'completeSavedKoEnScenesDirectlyRead':19,'completeSavedKoEnParagraphsDirectlyCompared':39,'allWholeTextsDirectlyCompared':True,'newVoiceItems':11,'pairedWholeTextReview':True,'overviewPromiseReview':True,'overviewSentences':3,'overviewTargetSeconds':[20,30],'overviewMeasuredSeconds':None,'actualOrder':['Tetris quantity/evaluation','Balatro contribution and hand/round','Tetris opponent comparison','Balatro labels/feedback hierarchy','audit/coaching'],'sourceEvidence':'projects/presenting-game-scores/production/revision-balatro60-v2/source-content-adoption-v7.json','matchingClaims':['04 selected extra six is not scoring; chips/mult changes shown by cards/Joker','05 hand560 and stable round1327 are distinct; transient count-up not final','07 hand type/calculation/round/target labels have different roles','08 existing reaction/contribution narration stays valid for selected scoring actions','09 stable704 vs target1200 does not claim victory','10 debuffed diamond marker and contribution audit; no full run win/optimal strategy claim'],'genericConceptsPreserved':True,'unchangedPcmRequired':True,'allBaselineFilesPreserved':True,'contentReadyForApprovedVoiceMeasurement':True,'humanListening':'pending','humanPronunciation':'pending','finalPublicRightsApproved':False,'finalMixedAsrApproved':False,'finalTimingApproved':False,'finalPixelsApproved':False,'newAudioCreated':False,'baselineWrites':0}
save(proof,review)
items=read(BASE/'script/changed-voice.ko.json')['scenes'];out='shared/output/narration/presenting-game-scores/qwen3-balatro60-revision-v1'
protected=[]
paths=[BASE/'script/narration.ko.json',BASE/'script/narration.en.json',BASE/'script/changed-voice.ko.json',BASE/'script/changed-voice.en.json',BASE/'voice-manifest-v1.json',BASE/'source-content-adoption-v7.json',BASE/'sources/game-candidates.json',BASE/'description-credit-approval-v1.json',BASE/'pcm-preservation-selection-v1.json']
paths += [ROOT/x['path'] for x in read(ROOT/'projects/presenting-game-scores/production/current-voice-selection-v7.json')['scenes']]
paths += [ROOT/'projects/presenting-game-scores/script/narration.ko.json',ROOT/'projects/presenting-game-scores/script/narration.en.json',ROOT/'projects/presenting-game-scores/production/final-v1/plan.json']
for p in paths:protected.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)})
request={'schemaVersion':1,'preparedAt':now,'slug':'presenting-game-scores','revision':'balatro60-tetris40-v2','manifestOverride':(BASE/'voice-manifest-v1.json').relative_to(ROOT).as_posix(),'pairedWholeTextReview':True,'overviewPromiseReview':True,'scriptReview':proof.relative_to(ROOT).as_posix(),'protectedInputs':protected,'scenes':[{'id':s['id'],'path':out+'/chunks/'+s['id']+'-scene.wav','text':' '.join(s['lines']),'paragraphs':len(s['lines'])} for s in items],'unchangedSelectedPcmRegenerated':False,'ttsStarted':False,'gpuResearchPolicy':'Finish current training checkpoint/validation/done, cooperative owned boundary pause, single TTS, restore original command/cwd/queue on success and failure and verify actual resumed job.','humanListening':'pending','humanPronunciation':'pending','publicRights':'pending'}
save(BASE/'narration-tts-request-v1.json',request)
audit.update(pairedWholeTextDirectReview=True,overviewPromiseDirectReview=True,readyForTts=True,pairedReview=proof.relative_to(ROOT).as_posix());save(BASE/'selective-script-change-audit-v1.json',audit)
req=read(BASE/'request.json');req['checkpoints']['pairedScript']=True;req['stage']='selective-script-approved-single-TTS-prepared';req['nextAction']='Fresh resource/CIM verification and one owned cooperative training-boundary handoff for11 changed voice items; preserve all unchanged PCM. Measure and whole/context-review new audio, verify original research resumes.';save(BASE/'request.json',req)
cpPath=ROOT/'projects/presenting-game-scores/production/latest-checkpoint.json';cp=read(cpPath);cp.update(recordedAt=now,stage=req['stage'],revisionCheckpoints=req['checkpoints'],revisionTtsRequest=(BASE/'narration-tts-request-v1.json').relative_to(ROOT).as_posix(),nextAction=req['nextAction']);save(cpPath,cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='presenting-game-scores');item.update(stage=req['stage'],revisionCheckpoints=req['checkpoints'],nextAction=req['nextAction']);q['updatedAt']=now;q['lastProgressAt']=now;save(qp,q)
print(json.dumps({'pairedSceneCount':19,'pairedParagraphs':39,'newVoiceItems':11,'protectedInputs':len(protected),'07Boundary':boundary,'newGpuJobs':0},ensure_ascii=False))

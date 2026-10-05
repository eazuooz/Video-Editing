"""Expose the current candidate without granting final timing/pixel approval."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;PROJECT=BASE.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
rel=lambda p:p.relative_to(ROOT).as_posix()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
batch=ROOT/'production/batches/sakurai-planning-game-design';proof=batch/'proof-avoid-game-comparisons'
plan=read(BASE/'measured-edit-v5/plan.json');bankPath=proof/'source-research/source-action-bank-v7.json';bank=read(bankPath)
voice=read(BASE/'narration-expanded15-index.json');tracks=read(BASE/'measured-edit-v5/caption-tracks-v1.json')
assert plan['actualSourceCuts']==111 and plan['allCurrent15PcmPreserved'] and len(tracks['koRows'])==199 and len(tracks['enRows'])==160
candidate={'path':rel(BASE/'measured-edit-v5/plan.json'),'sha256':sha(BASE/'measured-edit-v5/plan.json'),
 'actualFrames':plan['actualFrames'],'explanationFrames':plan['explanationFrames'],'bodyFrames':plan['bodyFrames'],'finalFrames':plan['finalFrames'],
 'candidateFinalSeconds':plan['finalFrames']/60,'ratioErrorFrames':plan['body60_40ErrorFrames'],'nativeCuts':111,
 'allCurrent15PcmPreserved':True,'originalSixExplanationMinimumFrames':plan['originalSixExplanationMinimumFrames'],
 'finalTimingApproved':False,'bodyRatioApproved':False,'allCaptionPixelsReviewed':False,'finalMixBuilt':False}
trial={'path':rel(BASE/'framing-corrections-direct-review-v5.json'),'imagesDirectlyRead':124,'sheetsDirectlyRead':21,
 'earlierAllActualCueImagesRead':461,'earlierTargetedFramingImagesRead':91,'finalPixelsApproved':False,
 'remainingCuts':['02-p1-action-10-600-630','02-p4-action-21-1410-1455','06-p2-action-31-900-945','10-p2-action-75-1464-1530'],
 'remainingRawContext':'13p1 action88 layered book transition','remainingCaptionBoundary':'06p3/4 cup cue about1.2frames early',
 'remainingJoinReadbacks':['10p1/2 quiet Pepper-name boundary','12p1 inserted quiet/general-to-specific boundary','12p2 cost/observed-action boundary']}
caption={'tracks':rel(BASE/'measured-edit-v5/caption-tracks-v1.json'),'layout':rel(BASE/'measured-edit-v5/caption-layout-v1.json'),
 'koCues':199,'enCues':160,'all60ParagraphsLiteralTextPreserved':True,'fixedCenterPx':[960,970],'fontSize':48,
 'allFinalCueTimingApproved':False,'allFinalCuePixelsApproved':False,'optionalTracksPublished':False}
m=read(PROJECT/'project.json');m['status']='current15-word-aligned-candidate-targeted-framing-pending'
e=m['editing'];e.setdefault('historicalTimingStatus',e['timingStatus']);e['timingStatus']='Current15 PCM475.2601667s preserved. Candidate v5:18833 actual/12555 explanation frames,0.2frame ratio error,535.133333s including branding/outro. Final framing, cue timing, mix and body ratio approval pending.'
e['sourceActionBank']=rel(bankPath);e['plannedCandidateActualSeconds']=sum(c['seconds'] for c in bank['clips']);e['measuredEditCandidate']=candidate
e['openingOverview']['measuredVoiceReview']='23.44s overview preserved; all current15 whole/context technical ASR directly compared. Human pronunciation/whole listening and final mix readback pending.'
p=m['production'];p.update(currentSourceBank=rel(bankPath),nativeCueProposal=rel(BASE/'native-cue-proposal-v5.json'),measuredEditCandidate=candidate,
 captionCandidate=caption,framingTrialReview=trial,current15TechnicalAsrApproved=True,finalTimingApproved=False,finalMixCreated=False,finalRendered=False)
m['paths']['timeline']=candidate['path'];m['paths']['candidateTimeline']=candidate['path']
write(PROJECT/'project.json',m)
a=read(PROJECT/'sources/action-map.json');a.setdefault('historical88ClipAssignment',{'candidateActualSeconds':a['candidateActualSeconds'],'sourceBankMaximumSeconds':a['sourceBankMaximumSeconds'],'sourceBank':a['sourceBank']})
a.update(status='current15-candidate111-native-cuts-final-framing-pending',updatedAt=now,sourceBank=rel(bankPath),sourceActionBank=rel(bankPath),
 sourceBankMaximumSeconds=e['plannedCandidateActualSeconds'],candidateActualSeconds=plan['actualFrames']/60,nativeCueProposal=p['nativeCueProposal'],nativeCueUniqueSecondsProposed=e['plannedCandidateActualSeconds'],
 measuredEditCandidate=candidate,ratioApproved=False,bodyRatioApproved=False,finalCutAndCaptionApproval=False)
a['historicalClipListScope']='The retained88 clip entries are the pre-integer assignment; current111 cut/source/paragraph mappings are in measuredEditCandidate.path.'
write(PROJECT/'sources/action-map.json',a)
c=read(PROJECT/'planning/chapter-plan.json');c.update(updatedAt=now,nativeCueProposal=p['nativeCueProposal'],measuredEditCandidate=candidate,finalCutAndCaptionApproval=False);write(PROJECT/'planning/chapter-plan.json',c)
nextAction='Repair only four remaining source-framing collisions; inspect action88 layered-entry raw continuity and the06 cup caption boundary. Preserve all15 PCM, original six explanations and23.44s overview. Review new quiet joins, then approve final timing/cue pixels and build final mix with both KO/EN tracks. Final render/QA/collection/private save pending.'
q=read(batch/'queue.json');i=next(x for x in q['items'] if x['slug']=='avoid-game-comparisons')
i.update(stage=m['status'],updatedAt=now,nextAction=nextAction,measuredEditCandidate=candidate,captionCandidate=caption,framingTrialReview=trial)
i['checkpoints']['current15TechnicalNarration']=True
ex=i['execution'];ex.update(observedAt=now,phase=m['status'],status='closed-current-candidate-compile-and124-framing-images-directly-read',pid=None,childPid=None,sessionId=None,alive=False,
 activeTasks=[],secondaryTasks=[],gpuSynthesisJobs=0,cpuProductionJobs=0,primaryCpuProductionJobs=0,renderJobs=0,uploads=0,sourceDownloadJobs=0,sourceNativeJobs=0,nextAction=nextAction)
ex.setdefault('closedTasks',[])
for folder,sid in [('measured-edit-v5/native-review-v1',89192),('measured-edit-v5/framing-corrections-local',74580)]:
 st=read(BASE/folder/'execution.json');assert st['exitCode']==0 and st.get('endedAt')
 rec={'state':rel(BASE/folder/'execution.json'),'pid':st['pid'],'sessionId':sid,'alive':False,'exitCode':0,'status':st['status'],'endedAt':st['endedAt'],'closureObservedAt':now}
 if not any(x.get('state')==rec['state'] for x in ex['closedTasks']):ex['closedTasks'].append(rec)
 ex['doNotWaitClosedSessions']=sorted(set(ex.get('doNotWaitClosedSessions',[])+[sid]))
ex['framingCorrections'].update(allDirectlyRead=True,review=trial['path'],finalApproved=False)
ex['foreignTrainingObservation']={'observedAt':now,'pids':[51764,22692],'command':'train_v2.py --target xray --scope vi --out_root lora_experiment/output_v2sw_vi','untouched':True,'basis':'Fresh CIM command-line observation; PID identity must be checked again before any action.'}
q['updatedAt']=now;write(batch/'queue.json',q)
for path in [BASE/'latest-checkpoint.json',proof/'latest-checkpoint.json']:
 cp=read(path);cp.update(stage=m['status'],updatedAt=now,nextAction=nextAction,execution=ex,measuredEditCandidate=candidate,captionCandidate=caption,framingTrialReview=trial,
 nativeCueProposal=p['nativeCueProposal'],current15TechnicalNarrationApproved=True,bodyRatioApproved=False,finalMixComplete=False,renderComplete=False,qaComplete=False,collected=False,privateUploadSaved=False,completedVideoDelivery=False)
 cp['actualCuePixelTrials']={'state':rel(BASE/'measured-edit-v3/cue-review-local-v1/execution.json'),'completedCuts':108,'images':461,'allDirectlyRead':True,'review':rel(BASE/'all-actual-cue-trial-direct-review-v3.json'),'finalApproved':False}
 cp['nativeCuePlanning']={'proposal':p['nativeCueProposal'],'bankCandidates':93,'proposalSplitCandidates':105,'candidateNativeCuts':111,'candidateActualSeconds':plan['actualFrames']/60,'currentSpeechSeconds':475.2601666667,'bodyRatioApproved':False,'allCaptionPixelsReviewed':False,'newDiagramLayoutReview':rel(BASE/'new-diagram-lookdev-review.json'),'newDiagramFinalPixelsReviewed':False}
 write(path,cp)
note='''Current15/60 independent KOEN paragraphs and all475.2601667s PCM remain preserved, including23.44s overview and all six original explanations. The current candidate is measured-edit-v5/plan.json:111 unique native cuts,18833 actual/12555 explanation frames,0.2frame rounding error and32108 total frames (535.133333s).106 compiled cuts were reused byte-for-byte; only five new source reallocations were encoded/decoded. This is a candidate, with final timing/body ratio approval false.

All461 earlier actual cue samples,91 v4 framing trials and124 v5 correction trials were directly read. Rocket ascent now matches the spoken rocket phrase, and the Pepper name now begins on Pepper footage. Four source-framing collisions, a distinct layered-entry raw context, a roughly1.2frame cup-caption boundary and new quiet-join ASR remain pending.199 KO/160 EN candidate cues preserve all60 paragraphs; every final cue and composite still requires approval. Eight new white diagram layouts were directly read, with final timed caption pixels pending.

No final mix/render/QA/output collection/private upload exists for this11th video. All completed workers are closed; no media or new image is added to Git. Ten completed videos, one confirmed duplicate and twelve queued remain unchanged. Human listening/pronunciation/rights/Nimbus/handles/backup remain pending. See production/latest-checkpoint.json and production/framing-corrections-direct-review-v5.json.
'''
for path in [PROJECT/'README.md',batch/'README.md']:
 text=path.read_text(encoding='utf-8-sig');heading='## '+now+' measured candidate/framing checkpoint'
 path.write_text(text.rstrip()+'\n\n'+heading+'\n\n'+note,encoding='utf-8')
print(json.dumps({'candidateFrames':32108,'finalApproved':False,'ownProductionJobs':0,'newGitImages':0}))

"""Record closed worker evidence and a truthful next production checkpoint."""
import json,hashlib,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
BATCH=ROOT/'production/batches/sakurai-planning-game-design';PROOF=BATCH/'proof-avoid-game-comparisons';SR=PROOF/'source-research'
def read(p): return json.loads(p.read_text('utf-8'))
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p): return p.relative_to(ROOT).as_posix()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
current=read(BASE/'narration-current-index.json');bank=read(SR/'source-action-bank-v3.json');q=read(BATCH/'queue.json');i=next(x for x in q['items'] if x['slug']=='avoid-game-comparisons')
states=[BASE/'narration-tts-execution.json',BASE/'narration-asr-execution.json',BASE/'independent-context-asr-execution.json',BASE/'targeted-clarity-execution.json',BASE/'targeted-candidate-asr-execution.json',BASE/'post-repair-asr-execution.json',SR/'acquisition-plucky-mine.json',SR/'discovery-plucky-mine.json',SR/'native-review-plucky-mine.json']
closed=[]
for p in states:
    d=read(p)
    assert d.get('exitCode',d.get('actualWorkerExitCode'))==0,p
    command=subprocess.run(['powershell','-NoProfile','-Command',f'Get-CimInstance Win32_Process -Filter "ProcessId={d["pid"]}" | Select-Object -ExpandProperty CommandLine'],capture_output=True,text=True).stdout
    assert not ('avoid-game-comparisons' in command and ('python' in command.lower() or 'acquire-official' in command)),p
    closed.append({'state':rel(p),'pid':d['pid'],'sessionId':d.get('sessionId'),'alive':False,'exitCode':0,'status':d['status'],'endedAt':d.get('endedAt'),'closureObservedAt':now})
before=i.get('execution',{});i.setdefault('executionHistory',[]).append(before)
execution={**before,'phase':'repaired-current-narration-and-unique-native-source-bank-reviewed','status':'closed-workers-next-additive-script-and-timeline-planning',
 'observedAt':now,'pid':None,'sessionId':None,'alive':False,'activeTasks':[],'secondaryTasks':[],
 'gpuSynthesisJobs':0,'primaryCpuProductionJobs':0,'cpuProductionJobs':0,'renderJobs':0,'uploads':0,
 'newNarrationCreated':True,'newSceneCreated':True}
execution['completedWorkers']=before.get('completedWorkers',[])+closed
next_action='Write paired independent additive narration for selected Mine actions between existing explanations; preserve original explanation PCM/duration and all old files. Measure new narration with the approved voice, finalize native cut/cue framing and60:40, then mix/current-hash ASR/KOEN SRT/render/QA/4file collection/private save and selected normal Git delivery.'
i.update(stage='current-12-scene-ASR-approved-additive-source-bank-v3-planning',execution=execution,updatedAt=now,nextAction=next_action)
i['narrationReadback']={'state':rel(BASE/'post-repair-asr-execution.json'),'readbackComplete':True,'wholeDirectScriptReview':True,'current12SceneTechnicalApproval':True,'directReview':rel(BASE/'narration-current-full-review.json'),'humanWholeListening':'pending','finalMixAsrReviewed':False}
i['targetedClarity']={'state':rel(BASE/'targeted-clarity-execution.json'),'status':'two-paragraphs-adopted-full-and-join-ASR-directly-reviewed','candidateGenerationCompleted':True,'candidatesApproved':True,'originalPCMChanged':False,'adoption':rel(BASE/'targeted-clarity-adoption.json'),'tenUnaffectedPcmAndSixExplanationDurationsPreserved':True}
i['postRepairReadback']={'state':rel(BASE/'post-repair-asr-execution.json'),'status':'closed-all4-current-hash-readbacks-directly-reviewed','results':4,'directReview':True,'review':rel(BASE/'post-repair-direct-review.json')}
i['sourceActionBank']={'path':rel(SR/'source-action-bank-v3.json'),'sha256':sha(SR/'source-action-bank-v3.json'),'planningIntervals':95,'planningUniqueSeconds':bank['uniqueSourceSeconds'],'newMinePlanningIntervals':15,'newMinePlanningSeconds':bank['bySourceSeconds']['CJ0_Xh59b98'],'projectAssignedIntervals':68,'projectAssignedSeconds':192.7,'sourceAudioUsed':False,'selfCreatedGames':0,'measuredRatioApproved':False,'finalCutAndCaptionApproval':False}
i['sourceExpansionNativeReview']={'status':'all-additional19-native/9-cross-comparison/31-Mine-sheets-directly-read','mine':rel(SR/'direct-plucky-mine-review.json'),'crossSource':rel(SR/'direct-additional-cross-source-review.json'),'newMinePlanningSeconds':bank['bySourceSeconds']['CJ0_Xh59b98'],'approvedFinalActualSeconds':0,'finalCaptionApproval':False}
i['narrationMeasurement']={'currentIndex':rel(BASE/'narration-current-index.json'),'original12FilesPreserved':True,'current12SceneSpeechSeconds':sum(x['seconds'] for x in current['measurements']),'explanationSpeechSeconds':current['explanationSpeechSeconds'],'actualSpeechSeconds':current['actualSpeechSeconds'],'overviewSpeechSeconds':23.44,'wholeCurrent12SceneAsrReview':True,'additiveNarrationPending':True,'finalRatioApproved':False}
i['independentScript']['voiceAsrReviewed']=True;i['independentScript']['finalPixelsReviewed']=False
q['updatedAt']=now;save(BATCH/'queue.json',q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','execution','nextAction','narrationReadback','targetedClarity','postRepairReadback','sourceActionBank','sourceExpansionNativeReview','narrationMeasurement','independentScript']:d[k]=i[k]
    d.update(updatedAt=now,completedVideoDelivery=False,finalMixComplete=False,renderComplete=False,qaComplete=False,collected=False,privateUploadSaved=False)
    save(p,d)
candidate_path=ROOT/'projects/avoid-game-comparisons/sources/game-candidates.json';c=read(candidate_path)
c.update(updatedAt=now,status='current-voice-reviewed-native-additive-bank-v3-not-final-timeline',narrationCreated=True,scenesCreated=True,
 actionBank=rel(SR/'source-action-bank-v3.json'),sourceActionBank=rel(SR/'source-action-bank-v3.json'),planningIntervals=95,planningUniqueSeconds=bank['uniqueSourceSeconds'],
 approvedIntervals=[],selectedPlanningIntervals=95,selectedPlanningSeconds=bank['uniqueSourceSeconds'],nextAction=next_action)
c.setdefault('additionalSourceReviews',[]).append({'sourceId':'CJ0_Xh59b98','title':'The Plucky Squire | Sneak Peek: Mine Puzzle Gameplay | Wishlist Now!',
 'selected':'15 unique native-reviewed planning intervals97.54745seconds; exact final framing/timeline pending','acquisition':rel(SR/'acquisition-plucky-mine.json'),
 'directReview':rel(SR/'direct-plucky-mine-review.json'),'rights':'Actual Devolver official monetization permission already read; original source audio excluded; final public rights pending.',
 'recentUse':'New source ID not present in earlier bank-v2. All new source region is distinct mine action, separate from prior town/castle/rocket/assist examples.',
 'rejected':'Cover, ESRB/early idle, dialogue, dissolve, prolonged closed-blue-chest idle, ending/title. No automatic chest success or control rule inferred.',
 'normalUiDate':'2024-02-22','downloaderDate':'20240221','dateDifferencePreserved':True})
save(candidate_path,c)
project_path=ROOT/'projects/avoid-game-comparisons/project.json';project=read(project_path)
project['status']=i['stage'];project['production']['currentNarrationIndex']=rel(BASE/'narration-current-index.json');project['production']['currentSourceBank']=rel(SR/'source-action-bank-v3.json');project['production']['currentNarrationTechnicalReview']=rel(BASE/'narration-current-full-review.json');project['production']['finalTimingApproved']=False
save(project_path,project)
print(json.dumps({'stage':i['stage'],'closedWorkersVerified':len(closed),'current12SceneSpeechSeconds':i['narrationMeasurement']['current12SceneSpeechSeconds'],'planningSourceSeconds':bank['uniqueSourceSeconds'],'finalComplete':False}))

"""Persist current14 reviewed speech and visible-role/source-alignment work still required."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;P=BASE.parent
BATCH=ROOT/'production/batches/sakurai-planning-game-design';PROOF=BATCH/'proof-avoid-game-comparisons'
def read(p):return json.loads(p.read_text('utf-8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (BASE/'expanded-visual-role-plan.json').exists(),'Read the existing role plan/checkpoint instead of duplicating it.'
stamp=datetime.now(timezone.utc).isoformat();m=read(BASE/'measured-paragraphs-expanded14.json');by={x['id']:x for x in m['scenes']};idx=read(BASE/'narration-expanded-index.json');review=read(BASE/'additive-narration-direct-review.json');assert review['allSixParagraphsTechnicallyReviewed']
roles=[]
for sid in ['13','14']:
    s=by[sid];boundary=s['paragraphs'][2]['pcmFromSample']
    roles.append({'id':sid,'firstTwoParagraphs':'full-screen-actual-existing-game','thirdParagraph':'white2.5D-explanation','actualSpeechSamples':boundary,'explanationSpeechSamples':s['samples']-boundary,'sampleRate':24000,'proposedBoundarySeconds':boundary/24000,'reason':'The first2 paragraphs describe inspected game action and observation limits. The third explicitly teaches our writing/listener-check exercise, so its diagram is explanation, preserving the visible-content classification.','sourceFrameCaptionReviewComplete':False,'finalMeasuredFrames':False})
actual=idx['historicalOriginal12ActualSpeechSeconds']+sum(x['actualSpeechSamples']/24000 for x in roles)
explanation=idx['historicalOriginal12ExplanationSpeechSeconds']+sum(x['explanationSpeechSamples']/24000 for x in roles)
role_review={'schemaVersion':1,'createdAt':stamp,'status':'speech-role-proposal-before-final-native-cut-and-cue-review','roles':roles,'speechOnlyActualSeconds':actual,'speechOnlyExplanationSeconds':explanation,'speechTotalSeconds':actual+explanation,'sourceCandidateAssignedIntervals':88,'sourceCandidateAssignedSeconds':300.24745,'bodyRatioApproved':False,'finalFramesMeasured':False,'allOriginal12PcmAndSixExplanationDurationsPreserved':True,'newGitImages':0,'sourceTimingNotes':[
 {'scene':'06','finding':'Reviewed16.5s spool/ledge/portal action and4.5s mug action must be aligned with the current measured paragraph3/4 windows; a fixed bank ordering is insufficient. Use distinct native excerpts or genuine action observation pauses; no source slowing/loop/idle and no speech truncation.'},
 {'scene':'10','finding':'The two distinct vehicle shots total4.6s while paragraph2 is11.052s PCM. The reflective continuous-chase caveat can use a separate white2.5D cut comparison, counted as explanation, after the relevant normal-speed shots. Final exact cue/shot alignment remains required.'},
 {'scene':'13','finding':'Match approach/departure, left/right key motion and the two conservative separate source portions before the paragraph3 diagram; keep exact input/all-object rules undecided.'},
 {'scene':'14','finding':'Re-read native sheets15/16: enemies remain visible through164.03s, avatar approaches the red chest164.53s and the open chest/card graphic is visible165.03s. Align the red-chest/card sentence to those actions rather than starting it over the earlier combat. Source bank95 ends165.5s; a larger interval is not approved.'},
 {'source':'KWDk-csu460','finding':'Re-read discovery-sheet04 and native-action-sheet03: water/reeds become an editorial wipe at52.5s and a cauldron level mockup follows53s. Keep the existing51–52.5 interval; it cannot be expanded into52.5–57.3 as more water action.'}],
 'nextAction':'Build a proposal from current14 measured PCM and native frame intervals. Resolve the specific06/10/13/14 action-cue alignment first, use real actions at normal speed, classify any new diagram as explanation and preserve all PCM. Then verify exact body60:40, every cut/caption/UI boundary and final mix before rendering.'}
save(BASE/'expanded-visual-role-plan.json',role_review)
mc=ROOT/'motion-canvas/src/projects/avoid-game-comparisons';plan=read(mc/'production-plan.json')
for x in plan['scenes']:
    if x['id'] in ['13','14']:x.update(role='mixed-actual-explanation',actualFrames=0,diagramFrames=0,diagramParagraphs=[3],actualParagraphs=[1,2])
plan.update(status='14-independent-scene-code-current-voice-reviewed-final-native-timing-pending',currentFinalTimingApproved=False,bodyRatioApproved=False)
save(mc/'production-plan.json',plan)
design=read(BASE/'independent-scene-design.json');ko=read(P/'script/narration.ko.json')
for sid in ['13','14']:
    s=next(x for x in ko['scenes'] if x['id']==sid);at=next(i for i,x in enumerate(design['scenes']) if x['id']==('07' if sid=='13' else '11'))+1
    design['scenes'].insert(at,{'id':sid,'title':s['title'],'paragraphs':3,'role':'full-screen-actual-then-white2.5D-explanation','entrypoint':f'motion-canvas/src/projects/avoid-game-comparisons/scenes/scene{sid}.tsx','pixelReview':False,'actualParagraphs':[1,2],'diagramParagraphs':[3]})
design.update(updatedAt=stamp,status='14-independent-entrants-authored-final-timing-and-new-diagram-pixels-pending',currentPcmTechnicalReview=BASE.joinpath('narration-expanded-index.json').relative_to(ROOT).as_posix(),finalTimingApproved=False,finalRatioApproved=False);save(BASE/'independent-scene-design.json',design)
for p in [P/'planning/chapter-plan.json',P/'sources/action-map.json']:
    d=read(p)
    for c in d['chapters']:
        if c['id'] in ['13','14']:c.update(role='mixed-actual-explanation',actualParagraphs=[1,2],explanationParagraphs=[3],measuredNarrationSeconds=by[c['id']]['speechSeconds'],finalScreenClassificationApproved=False)
    d.update(updatedAt=stamp,finalCutAndCaptionApproval=False);save(p,d)
outline=P/'planning/outline.md';outline.write_text(outline.read_text('utf-8')+f'\n\n## 추가 음성 실측과 화면 역할 — {stamp}\n\n'+
 '새13장28.56초·14장26.560042초만 같은 승인Qwen/reference로 CPU 합성했다. 현재14장56문단 총441.580167초이며 원래12개의 현재PCM/여섯설명 길이/도입23.44초는 그대로다. 두 전체음성과 세 독립문맥의 ASR를 전 문장·끝부분과 직접 대조했고 적되/적대와 조사 표기 차이는 사람 발음검토pending으로 보존했다. 원래12해시의 직접검토도 이어 받되 최종믹스 검수로 대신하지 않는다.\n\n'+
 '13/14의 첫 두 문단은 전체화면 실제게임, 마지막 우리 기획 작성/청자 확인 문단은 독립 흰2.5D도식으로 제안한다. 이 마지막 설명을 실제게임60%에 넣지 않는다. 원래 설명을 줄이지 않으며 화면별 실측프레임과 전체60:40은 다음 컷계획에서 계산한다. 06의 긴 로켓동작/컵,10의4.6초 물위 두컷과11초 해설,14의165.03초 상자·카드 표시를 음성 큐와 먼저 맞춰야 한다. KWD52.5초 이후는 물 장면이 아니라 wipe와level-mockup이므로 물컷을 늘리는 근거로 쓰지 않는다.\n',encoding='utf-8')
text_review=read(BASE/'script-source-review.json');text_review.update(updatedAt=stamp,current14PcmTechnicalReview=BASE.joinpath('narration-expanded-index.json').relative_to(ROOT).as_posix(),voiceAsrReview='Current14/56 all whole ASR and ambiguous independent contexts directly compared; transcription/particle uncertainty and human listening preserved. Final mix not yet reviewed.',visualRolePlan=BASE.joinpath('expanded-visual-role-plan.json').relative_to(ROOT).as_posix())
for x in text_review['inputs']:x['sha256']=sha(ROOT/x['path'])
save(BASE/'script-source-review.json',text_review)
project=read(P/'project.json');project['status']='current14-voice-technically-reviewed-native-cue-alignment-planning';project['production'].update(currentNarrationIndex=BASE.joinpath('narration-expanded-index.json').relative_to(ROOT).as_posix(),currentNarrationTechnicalReview=BASE.joinpath('additive-narration-direct-review.json').relative_to(ROOT).as_posix(),currentVoiceApproved=True,currentVoiceApprovalScope='Technical whole/context ASR only; exact human pronunciation/full listening pending.',narrationSpeechMeasurements=BASE.joinpath('measured-paragraphs-expanded14.json').relative_to(ROOT).as_posix(),pendingNarrationExpansion=False,finalTimingApproved=False,finalMixCreated=False,finalRendered=False);save(P/'project.json',project)
q=read(BATCH/'queue.json');task=next(x for x in q['items'] if x['slug']=='avoid-game-comparisons')
workers=[]
for name,kind in [('additive-narration-tts','two-new-scene-CPU-Qwen'),('additive-whole-asr','two-full-scene-CPU-ASR'),('additive-context-asr','three-independent-context-CPU-ASR')]:
    state=read(BASE/(name+'-execution.json'));assert state['exitCode']==0;workers.append({'kind':kind,'pid':state['pid'],'sessionId':state['sessionId'],'status':'closed-exit0-directly-reviewed','exitCode':0,'endedAt':state['endedAt'],'state':BASE.joinpath(name+'-execution.json').relative_to(ROOT).as_posix(),'log':state['log']})
ex=dict(task.get('execution',{}));ex.setdefault('completedWorkers',[]).extend(workers);ex.update(observedAt=stamp,phase='current14-whole-ASR-reviewed-final-native-cue-plan',status='closed-workers-next-native-cue-timeline-planning',pid=None,sessionId=None,alive=False,activeTasks=[],gpuSynthesisJobs=0,cpuProductionJobs=0,primaryCpuProductionJobs=0,renderJobs=0,uploads=0,secondaryTasks=[])
task.update(stage='current14-voice-approved-native-cue-alignment-planning',updatedAt=stamp,execution=ex,nextAction=role_review['nextAction'],additiveNarration={'state':BASE.joinpath('additive-narration-tts-execution.json').relative_to(ROOT).as_posix(),'newSceneIds':['13','14'],'generationComplete':True,'wholeNewAsrDirectReview':True,'independentContextsDirectReview':True,'newSeconds':55.120041666666665,'originalAll12PcmPreserved':True,'scriptScenes':14,'paragraphs':56},narrationMeasurement={'currentIndex':BASE.joinpath('narration-expanded-index.json').relative_to(ROOT).as_posix(),'current14SpeechSeconds':idx['speechSeconds'],'explanationSpeechSecondsProposed':explanation,'actualSpeechSecondsProposed':actual,'overviewSpeechSeconds':23.44,'original12FilesAndCurrentHashesPreserved':True,'current14TechnicalAsrReview':True,'finalMixAsrReviewed':False,'additiveNarrationPending':False,'finalRatioApproved':False},independentScenes={**task.get('independentScenes',{}),'independentBodyEntrypoints':14,'whiteDiagramParts':8,'original6LookdevPreserved':True,'new13_14DiagramPixelReview':False,'finalMeasuredTiming':False,'newGitImages':0})
task.setdefault('narrationReadback',{}).update(current14SceneTechnicalApproval=True,wholeDirectScriptReview=True,currentIndex=BASE.joinpath('narration-expanded-index.json').relative_to(ROOT).as_posix(),additiveReview=BASE.joinpath('additive-narration-direct-review.json').relative_to(ROOT).as_posix(),finalMixAsrReviewed=False,humanWholeListening='pending')
q.update(updatedAt=stamp,lastProgressAt=stamp);save(BATCH/'queue.json',q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for key in ['stage','updatedAt','execution','nextAction','additiveNarration','narrationMeasurement','independentScenes','narrationReadback']:d[key]=task[key]
    save(p,d)
for p in [BATCH/'README.md',ROOT/'production/batches/private-review-expansion/README.md']:
    txt=p.read_text('utf-8');head,rest=txt.split('\n',1)
    update=f'\n\n{stamp} 최신: 완료10편과 중복제외1편·12queued를 보존한다. avoid-game-comparisons는 현재14장56독립한영문단/441.580167초 PCM의 전체·독립문맥ASR 직접대조를 마쳤다. 새13/14 두장55.120042초만CPU로 더 만들었으며 기존12PCM·여섯설명길이·도입23.44초는 그대로다. 적되/적대와 조사 표기 차이는 사람 발음검토pending에 남겼다.14독립MC코드와 새 마지막 설명도식을 제안했으나 정확한 실제컷/고정자막큐/60:40/최종믹스·렌더QA·수집·비공개전달은 아직없다. 현재12-only 기록은 보존한 이전이력이며 narration-expanded-index.json/expanded-visual-role-plan.json/latest-checkpoint.json을 우선한다. 종료51711(PID55828),19685(PID53116),86774(PID31812)를 기다리거나 다시 합성/ASR하지 않는다. 새이미지/미디어Git추가0, 다른사용자GPU학습을 중단하지 않았다. 아래는 역사기록이다.\n'
    p.write_text(head+update+rest,encoding='utf-8')
print(json.dumps({'currentScenes':14,'currentParagraphs':56,'speechSeconds':idx['speechSeconds'],'proposedActualSpeech':actual,'proposedExplanationSpeech':explanation,'finalRatioApproved':False,'newGitImages':0,'allOurProductionJobs':0}))

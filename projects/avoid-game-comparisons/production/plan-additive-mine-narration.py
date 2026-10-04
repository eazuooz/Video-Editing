"""Source-first additive text; preserve all twelve reviewed scene texts and PCM."""
import copy,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;P=BASE.parent
SR=ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/source-research'
MC=ROOT/'motion-canvas/src/projects/avoid-game-comparisons'
def read(p):return json.loads(p.read_text('utf-8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
stamp=datetime.now(timezone.utc).isoformat()
if (BASE/'additive-mine-script-review.json').exists():raise RuntimeError('Inspect existing additive plan; do not duplicate')
ko=read(P/'script/narration.ko.json');en=read(P/'script/narration.en.json');current=read(BASE/'narration-current-index.json')
assert len(ko['scenes'])==len(en['scenes'])==12 and current['fullCurrentHashAsrApproved']
original_ko=copy.deepcopy(ko);original_en=copy.deepcopy(en)
save(BASE/'narration-script-ko-v2.json',ko);save(BASE/'narration-script-en-v2.json',en)
save(BASE/'script-source-review-v2.json',read(BASE/'script-source-review.json'))
bank=read(SR/'source-action-bank-v3.json');bank['previousBank']=rel(SR/'source-action-bank-v3.json')
extra=[(300,434,'Yellow vertical cave bends and emergence'),(434,555,'Yellow column/rope platform traversal'),(1530,1575,'Metal water vehicle movement and attack by dark reeds')]
for start,end,action in extra:
    bank['clips'].append({'id':f'action-{len(bank["clips"])+1:02}','sourceVideoId':'KWDk-csu460','sourceUrl':'https://www.youtube.com/watch?v=KWDk-csu460',
      'sourceSha256':'6ffdcb41a4a2b852d9b15ef8de726b09560d36f1ff8132f64dd2747ed0ed4efd','nativeFrameRate':'30/1','nativeFps':30,
      'startFrame':start,'endFrameExclusive':end,'inSeconds':start/30,'outSeconds':end/30,'seconds':(end-start)/30,
      'visibleAction':action,'planningClaim':'Specify observed terrain and movement; different actions are not one general running rule.',
      'viewerFocus':'Avatar trajectory, terrain edge and water surface','diagramConnection':'Space + visible verb + observed change',
      'insertionPoint':'02cave and06waterside narration support, exact cue alignment pending',
      'caution':'Native n434 edit retained as separate clips. Final-gameplay bottom label must be removed with reviewed framing; no alpha/test/slowdown/source sound.',
      'directReview':[rel(SR/'direct-native-additional-measured-actions.json'),rel(SR/'direct-additional-cross-source-review.json')],
      'status':'unique-native-reviewed-planning-candidate','finalCaptionFramingApproved':False})
bank.update(createdAt=stamp,status='98-conservative-unique-planning-candidates-not-final-timeline',uniqueSourceSeconds=sum(x['seconds'] for x in bank['clips']),bodyRatioApproved=False,finalCutAndCaptionApproval=False)
bank['bySourceSeconds']['KWDk-csu460']=10.0
bank['directReview'] += [rel(SR/'direct-native-additional-measured-actions.json'),rel(SR/'direct-additional-cross-source-review.json')]
save(SR/'source-action-bank-v4.json',bank)
additions=[
 {'id':'13','after':'07','titleKo':'실제 행동 · 캐릭터 이동과 책의 기울기','titleEn':'Actual action: character movement and book tilt',
  'linesKo':[
   '광산 장면에서는 그림면의 진입 지점으로 다가가 책상 쪽으로 나옵니다. 캐릭터가 걷는 행동과 책이 기울어지는 변화를 따로 보세요.',
   '왼쪽으로 기운 책에서는 노란 열쇠가 왼쪽으로, 다른 구간에서는 오른쪽으로 움직입니다. 보인 방향은 적되, 정확한 입력이나 모든 물체의 규칙은 이 시연으로 정하지 않습니다.',
   '새 기획도 무엇이 움직이고 어떤 변화가 생기는지 풀어 말해 보세요. 작품명이 채워 줄 거라 생각했던 조건이 그 문장에서 드러납니다.'],
  'linesEn':[
   'In the mine sequence, the character approaches an entry point on the illustrated surface and emerges onto the desk. Distinguish the character walking from the book itself tilting.',
   'When the book tilts left, the yellow key moves left; in another portion, it moves right. Record the visible directions, but this demonstration does not establish the exact input or a rule for every object.',
   'For your new concept, spell out what moves and what changes. That sentence exposes conditions you may have expected a familiar title to supply.'],
  'claim':'Moving character, moving space and moving object are different visible subjects. Describe the subject and change; leave unseen input/universal rules undecided.',
  'paragraphActions':[['action-88','action-89','action-92','action-85-b'],['action-90','action-93'],['action-83-b']],
  'diagram':'07 observed fact / undecided question cards;09 goal-action-condition exercise',
  'limit':'No exact button/control input, all-object behavior or chest success inferred. Left/right motions come from separate conservative native ranges.'},
 {'id':'14','after':'11','titleKo':'실제 행동 · 진입과 전투와 결과를 나누기','titleEn':'Actual action: separate entry, combat and visible results',
  'linesKo':[
   '그림면 안에서는 적을 때리고 길을 따라 움직입니다. 진입할 때의 이동과 들어온 뒤의 전투를 같은 한 동작으로 묶지 마세요.',
   '뒤의 빨간 상자가 열리고 카드 그림이 나타나는 변화도 보입니다. 앞선 열쇠 이동만으로 모든 상자가 열린다거나 전투가 끝난다고 약속할 근거는 아닙니다.',
   '설명을 듣는 사람이 이 차이를 자기 말로 나눌 수 있는지 확인하세요. 보인 결과와 아직 정할 연결 조건을 구별하면, 빠진 질문이 드러납니다.'],
  'linesEn':[
   'On the illustrated surface, the character strikes enemies and moves along the route. Do not bundle entry movement and the combat after entry into one action.',
   'A later red chest opens and a card graphic appears. The earlier movement of the key does not justify promising that every chest opens or that combat ends.',
   'Check whether a listener can separate these differences in their own words. Distinguishing the visible result from a connection condition still to be decided reveals missing questions.'],
  'claim':'Entry, combat and the observed red-chest/card result have different verbs. An observed result is not a universal completion rule.',
  'paragraphActions':[['action-82','action-86','action-87'],['action-95'],['action-94']],
  'diagram':'11 listener restatement questions;12 apply the goal/action/condition exercise',
  'limit':'No universal chest-opening/combat-ending rule. Closed blue-chest idle excluded. Red chest/card is a local observed outcome, not proof of a whole-game victory.'}
]
for language,script,key,title in [('ko',ko,'linesKo','titleKo'),('en',en,'linesEn','titleEn')]:
    for a in additions:
        idx=next(i for i,s in enumerate(script['scenes']) if s['id']==a['after'])+1
        script['scenes'].insert(idx,{'id':a['id'],'title':a[title],'lines':a[key]})
    assert [s for s in script['scenes'] if s['id'] not in ['13','14']]==(original_ko if language=='ko' else original_en)['scenes']
    save(P/f'script/narration.{language}.json',script)
chapter=read(P/'planning/chapter-plan.json');action_map=read(P/'sources/action-map.json')
save(BASE/'action-map-v2-preserved.json',action_map)
save(BASE/'chapter-plan-v2-preserved.json',chapter)
lookup={x['id']:copy.deepcopy(x) for x in bank['clips']}
split_defs={'action-83-a':('action-83',None,1133),'action-83-b':('action-83',1133,None),
 'action-85-a':('action-85',None,2413),'action-85-b':('action-85',2413,None)}
for key,(parent,lo,hi) in split_defs.items():
    c=copy.deepcopy(lookup[parent]);c['id']=key;c['parentActionId']=parent
    c['startFrame']=c['startFrame'] if lo is None else lo;c['endFrameExclusive']=c['endFrameExclusive'] if hi is None else hi
    assert c['startFrame']<c['endFrameExclusive']
    for target,value in [('inSeconds',c['startFrame']/c['nativeFps']),('outSeconds',c['endFrameExclusive']/c['nativeFps']),('seconds',(c['endFrameExclusive']-c['startFrame'])/c['nativeFps'])]:c[target]=value
    lookup[key]=c
support={'02':['action-96','action-97'],'04':['action-84','action-85-a'],'06':['action-98'],'10':['action-91'],'12':['action-81','action-83-a']}
for scene_id,ids in support.items():
    for d in [chapter,action_map]:next(c for c in d['chapters'] if c['id']==scene_id)['sourceActionIds']+=ids
    for key in ids:
        c=copy.deepcopy(lookup[key]);c.update(sceneId=scene_id,explainedClaim=next(c for c in chapter['chapters'] if c['id']==scene_id)['claim'],finalCutAndCaptionApproval=False);action_map['clips'].append(c)
for a in additions:
    ids=[x for xs in a['paragraphActions'] for x in xs]
    new={'id':a['id'],'title':a['titleKo'],'role':'actual-existing-game','claim':a['claim'],'diagram':a['diagram'],'sourceActionIds':ids,'measuredSeconds':None,'sourceClaimLimit':a['limit']}
    for d in [chapter,action_map]:
        idx=next(i for i,c in enumerate(d['chapters']) if c['id']==a['after'])+1;d['chapters'].insert(idx,copy.deepcopy(new))
    for key in ids:
        c=copy.deepcopy(lookup[key]);c.update(sceneId=a['id'],explainedClaim=a['claim'],finalCutAndCaptionApproval=False);action_map['clips'].append(c)
    (MC/f'scenes/scene{a["id"]}.tsx').write_text("import {actualScene} from './actual-scene';\nexport default actualScene('"+a['id']+"');\n",encoding='utf-8')
used=action_map['clips'];assert len({x['id'] for x in used})==len(used)
for a in used:
    for b in used:
        if a['id']!=b['id'] and a['sourceVideoId']==b['sourceVideoId']:
            assert min(a['endFrameExclusive'],b['endFrameExclusive'])<=max(a['startFrame'],b['startFrame']),(a['id'],b['id'])
action_map.update(updatedAt=stamp,sourceBank=rel(SR/'source-action-bank-v4.json'),candidateActualSeconds=sum(x['seconds'] for x in used),sourceBankMaximumSeconds=bank['uniqueSourceSeconds'],ratioApproved=False,finalCutAndCaptionApproval=False,status=f'{len(used)}-assigned-unique-native-planning-candidates-timing-and-caption-review-pending')
chapter.update(updatedAt=stamp,sceneOrder=[s['id'] for s in ko['scenes']]);chapter['overview'].update(measuredSeconds=23.44,independentMotionCanvasSceneCreated=True,fullBodyPromiseReviewComplete=True)
chapter['planningBudget'].update(selectedConservativeSourceSeconds=action_map['candidateActualSeconds'],measured=False)
save(P/'planning/chapter-plan.json',chapter);save(P/'sources/action-map.json',action_map)
plan=read(MC/'production-plan.json')
for a in additions:
    idx=next(i for i,s in enumerate(plan['scenes']) if s['id']==a['after'])+1
    plan['scenes'].insert(idx,{'id':a['id'],'role':'actual-existing-game','paragraphs':3,'frames':0,'seconds':0,'paragraphEnds':[],'actualVideo':'','actualMediaVerified':False,'actualAudioStreams':0})
save(MC/'production-plan.json',plan)
project_ts=MC/'project.ts';txt=project_ts.read_text('utf-8')
txt=txt.replace("import outro from", "import scene13 from './scenes/scene13?scene';\nimport scene14 from './scenes/scene14?scene';\nimport outro from")
txt=txt.replace('scene07,scene08','scene07,scene13,scene08').replace('scene11,scene12','scene11,scene14,scene12');project_ts.write_text(txt,encoding='utf-8')
outline=P/'planning/outline.md'
outline.write_text(outline.read_text('utf-8')+f'\n\n## 실측 뒤 추가할 실제 사례 — {stamp}\n\n'+
 '현재 12장 50문단의 한영 대본과 승인 PCM, 여섯 설명의 길이를 보존하고 07 뒤에 독립 13장, 11 뒤에 독립 14장의 한영 3문단씩을 추가한다. 13은 광산의 그림면에서 게임 속 책상으로 나오는 이동과 책의 좌우 기울기·노란 열쇠 이동을 관찰하여 움직이는 대상과 보인 변화를 나눈다. 14는 진입·전투·빨간 상자와 카드의 국소적 결과를 나누며 모든 상자의 열림이나 전투 종료를 약속하지 않는다. 게임 속 가상 책상을 실물 광고로 설명하지 않고 닫힌 파란 상자 앞의 대기·대화는 제외한다. 기획 설명 연습과 청자의 다시 말하기는 우리의 제안이다.\n\n'+
 f'출처의 정확한 프레임·행동·관찰점·도식 연결·삽입 위치는 추가 계획과 action-map에 기록했다. 기존 02/04/06/10/12의 음성보다 짧은 후보 시간은 새 동굴·물가·광산의 고유 행동을 더 배정해 보완한다. 현재 배정 {len(used)}개 구간 {action_map["candidateActualSeconds"]:.6f}초는 최종 컷·고정 자막·60:40 승인이 아니다. 13/14만 같은 승인 목소리로 새로 측정하며 기존 12 PCM은 재합성하지 않는다.\n\n'+
 '도입의 중심 질문은 03, 행동의 구체화는 02/04/05, 조건과 관찰 범위는 06/07/13, 세 문장 설명은 09, 청자의 다시 말하기는 11/14, 적용 결론은 12에 실제로 있다. 도입 4문장·23.44초는 보존한다. 추가 후의 약속·실제 설명 순서·첫 사례 연결도 직접 대조했다.\n',encoding='utf-8')
game_candidates=read(P/'sources/game-candidates.json')
game_candidates.update(updatedAt=stamp,status='14-scene-additive-text-reviewed-two-new-voice-scenes-pending',stage='additive-independent-bilingual-script-reviewed',sourceActionBank=rel(SR/'source-action-bank-v4.json'),actionBank=rel(SR/'source-action-bank-v4.json'),selectedPlanningIntervals=len(bank['clips']),planningIntervals=len(bank['clips']),selectedPlanningSeconds=bank['uniqueSourceSeconds'],planningUniqueSeconds=bank['uniqueSourceSeconds'],projectAssignedIntervals=len(used),projectAssignedSeconds=action_map['candidateActualSeconds'])
game_candidates['limitations']=[x for x in game_candidates['limitations'] if 'whole KO/EN scripts' not in x]
game_candidates['limitations'].append('All14 scenes/56 paragraphs are independently paired and overview promises reviewed. Only additive13/14 synthesis/current-hash ASR and final timeline/caption/framing approval remain pending.')
game_candidates['additionalSourceReviews'].append({'sourceId':'KWDk-csu460','selected':'3 unique native/cross-source-reviewed planning intervals10seconds','selectedActionIds':['action-96','action-97','action-98'],'directReview':rel(SR/'direct-additional-cross-source-review.json'),'rights':'Observed official Devolver posting/monetization permission; source sound excluded; public-rights review pending.','recentUse':'Source regions directly compared with earlier Pepper trailers; distinct cave/column/water terrain and avatar motion. No repeated region counted.','rejected':'Alpha overlay, test screen, flash/logo and final-gameplay bottom label pending reviewed crop. No continuous causality across native edits inferred.'})
game_candidates['nextAction']='Measure only additive13/14 with approved voice on CPU; preserve all12 reviewed PCM. Review full new voices and finalize unique native cuts/cue framing and60:40 before mix/subtitles/render/QA/collection/private save.'
save(P/'sources/game-candidates.json',game_candidates)
review=read(BASE/'script-source-review.json');review.update(reviewedAt=stamp,sceneCount=14,paragraphs=56,wholeBilingualScriptReviewed=True,overviewTextPromisesFulfilled=True,
 status='14-scenes56-paragraphs-independent-bilingual-review; only13/14 synthesis-pending',voiceAsrReview='Original current12 scenes reviewed; additive13/14 current-hash ASR pending')
for a in additions:
    paras=[]
    for n,(k,e,ids) in enumerate(zip(a['linesKo'],a['linesEn'],a['paragraphActions']),1):
        paras.append({'paragraph':n,'koSha256':hashlib.sha256(k.encode()).hexdigest(),'enSha256':hashlib.sha256(e.encode()).hexdigest(),'sourceActionIds':ids,'meaningOrderAndClaimScopeDirectlyCompared':True})
    idx=next(i for i,c in enumerate(review['scenes']) if c['id']==a['after'])+1
    review['scenes'].insert(idx,{'id':a['id'],'role':'actual-existing-game','paragraphs':paras,'directReview':a['limit'],'planningSourceSeconds':sum(lookup[x]['seconds'] for xs in a['paragraphActions'] for x in xs),'measuredNarrationSeconds':None})
for x in review['inputs']:x['sha256']=sha(ROOT/x['path'])
review['inputs'] += [{'path':rel(SR/'source-action-bank-v4.json'),'sha256':sha(SR/'source-action-bank-v4.json')},{'path':rel(SR/'direct-plucky-mine-review.json'),'sha256':sha(SR/'direct-plucky-mine-review.json')},{'path':rel(SR/'direct-additional-cross-source-review.json'),'sha256':sha(SR/'direct-additional-cross-source-review.json')}]
review['previousTextReview']=rel(BASE/'script-source-review-v2.json');save(BASE/'script-source-review.json',review)
plan_record={'schemaVersion':1,'reviewedAt':stamp,'additions':additions,'sceneOrder':[s['id'] for s in ko['scenes']],
 'originalCurrent12KoEnTextsUnchanged':True,'originalAll12PcmPreserved':True,'allSixExplanationPcmAndDurationsPreserved':True,
 'overviewOriginal4SentencesAnd23_44SecondsPreserved':True,'overviewPromisesMatchedActualBody':True,
 'koSha256':sha(P/'script/narration.ko.json'),'enSha256':sha(P/'script/narration.en.json'),
 'sourceBank':rel(SR/'source-action-bank-v4.json'),'uniqueAssignedSourceSeconds':action_map['candidateActualSeconds'],
 'assignedIntervals':len(used),'bodyRatioApproved':False,'newGitImages':0,'sourceAudioUsed':False,
 'historicalDemoDatePreserved':True,'wholePairedSixParagraphMeaningReview':True,'ttsStarted':False,'finalVideoComplete':False}
save(BASE/'additive-mine-script-review.json',plan_record)
protected=review['inputs']+[{'path':x['path'],'sha256':x['sha256']} for x in current['measurements']]
save(BASE/'additive-narration-request.json',{'schemaVersion':1,'reviewedAt':stamp,'model':'qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base',
 'reference':'shared/voice-reference/reference-15-35s.wav','device':'cpu','reason':'Other user GPU training observed5930MiB/71percent; preserve it and render only two new scenes with approved CPU voice.',
 'protectedInputs':protected,'scenes':[{'id':a['id'],'text':' '.join(a['linesKo']),'paragraphs':a['linesKo'],'path':f'shared/output/narration/avoid-game-comparisons/qwen3-1.7b-balanced-v3/chunks/{a["id"]}-scene.wav'} for a in additions],
 'pairedWholeTextReview':True,'overviewPromiseReview':True,'allPriorScenePcmPreserved':True})
project=read(P/'project.json');project.update(status='additive-two-scene-text-reviewed-pre-TTS')
project['production'].update(pendingNarrationExpansion=rel(BASE/'additive-narration-request.json'),currentSourceBank=rel(SR/'source-action-bank-v4.json'))
save(P/'project.json',project)
print(json.dumps({'scenes':14,'paragraphs':56,'newCharacters':sum(len(' '.join(a['linesKo'])) for a in additions),'assignedIntervals':len(used),'uniqueAssignedSourceSeconds':action_map['candidateActualSeconds'],'finalRatioApproved':False}))

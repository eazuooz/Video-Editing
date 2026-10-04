"""Propose sentence-matched native cuts; add only independent scene15 commentary.
All current14 texts/PCM remain unchanged. No final-frame or caption approval here.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROJECT=BASE.parent;PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons'
MC=ROOT/'motion-canvas/src/projects/avoid-game-comparisons'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
now=datetime.now(timezone.utc).isoformat()
assert not (BASE/'native-cue-proposal.json').exists(),'Do not repeat a saved planning/voice request.'
bank=read(PROOF/'source-research/source-action-bank-v4.json');clips={x['id']:x for x in bank['clips']}
measured=read(BASE/'measured-paragraphs-expanded14.json');pcm=read(BASE/'narration-expanded-index.json')
assert len(pcm['measurements'])==14
for x in pcm['measurements']:assert sha(ROOT/x['path'])==x['sha256'],x['scene']
groups=[]
def add(scene,paragraph,ids,explanation_tail=False,audio_from=None,audio_to=None,note=''):
 cuts=[]
 for value in ids:
  if isinstance(value,tuple):id,start,end=value
  else:id=value;start=clips[id]['startFrame'];end=clips[id]['endFrameExclusive']
  c=copy.deepcopy(clips[id]);c.update(startFrame=start,endFrameExclusive=end)
  fps=float(c['nativeFps']);c.update(inSeconds=start/fps,outSeconds=end/fps,seconds=(end-start)/fps,sceneId=scene,paragraph=paragraph,finalCutAndCaptionApproval=False)
  c['nativeBoundaryExtension']=start<clips[id]['startFrame'] or end>clips[id]['endFrameExclusive']
  c['newExactBoundaryPixelReview']=False
  cuts.append(c)
 source_seconds=sum(c['seconds'] for c in cuts)
 voice=None
 if scene!='15':
  s=next(x for x in measured['scenes'] if x['id']==scene)
  p=next(x for x in s['paragraphs'] if x['paragraph']==paragraph)
  if audio_from is None:audio_from=p['pcmFromSample']/24000
  if audio_to is None:audio_to=p['pcmToSample']/24000
  voice=audio_to-audio_from
 groups.append(dict(sceneId=scene,paragraph=paragraph,sourceCuts=cuts,sourceSeconds=source_seconds,audioFromSeconds=audio_from,audioToSeconds=audio_to,voiceSeconds=voice,whiteExplanationTail=explanation_tail,minimumActionObservationExtraSeconds=None if voice is None else max(0,source_seconds-voice),unresolvedVoiceCoverageSeconds=None if voice is None else max(0,voice-source_seconds) if not explanation_tail else 0,note=note,finalFramesApproved=False))
def A(n):return 'action-'+str(n).zfill(2)
add('02',1,[A(n) for n in [1,2,3,4,9,10,19]])
add('02',2,[A(n) for n in [20,22,30,97]])
add('02',3,[A(n) for n in [72,96,25]])
add('02',4,[A(n) for n in [28,32,8,21,11]])
# The two extended page shots have known edits at14s/16.5s; exact native edge triplets remain required.
add('04',1,[(A(81),210,268),(A(35),720,839),(A(36),840,989),A(38)],note='Book/page approach, music-page walk, visible gap and city-page walk. Preserve one-native-frame margin before the14/16.5 edits. No credits/title9–11s used.')
add('04',2,[A(43),A(44),A(45)])
add('04',3,[A(60),A(61)])
add('04',4,[A(84),(A(85),2170,2413)])
add('04',5,[(A(85),2413,2547),A(89)])
add('06',1,[A(n) for n in [5,6,15,18,26,27,33,34]])
add('06',2,[A(73),A(74),A(31)],True,note='After actual curve/ice/snow shots, the scope-of-description sentence uses a white2.5D comparison; never stretch the1.1s ice action.')
add('06',3,[(A(63),4320,4542),(A(64),4770,4860),(A(64),5270,5370)],note='Spool/card ascent → separate enemy-hit excerpt → separate wall approach. Exact native edges/action timestamps must be checked; an excerpt is not uninterrupted input evidence.')
add('06',4,[A(66)],True,note='4.5s normal-speed mug movement corresponds to first sentence; ascent/descent/space diagram follows and counts as explanation.')
add('06',5,[(A(63),4542,4710),(A(64),4860,5270)],note='Different non-overlapping rocket portions accompany the unresolved fuel/reuse-rule caveat; no fuel rule asserted.')
add('08',1,[A(59)]);add('08',2,[A(65)])
add('08',3,[A(67),(A(91),5995,6175)])
add('08',4,[(A(91),6175,6527)])
add('10',1,[A(n) for n in [37,40,41,42,39]])
add('10',2,[A(75),A(76)],True,note='Two distinct normal-speed vehicle shots total4.6s; the remaining sentence is a white cut comparison, not invented continuous pursuit.')
add('10',3,[A(68),(A(69),7800,7980),(A(70),8460,8625)])
add('10',4,[A(49)],True,note='Actual industrial-page action comes from the official accessibility video. The white contextual caveat explains that source context is not default difficulty/portal visibility.')
add('10',5,[(A(69),7980,8430),(A(70),8625,8910)])
add('13',1,[A(88),A(92)])
add('13',2,[A(90),A(93)])
# Scene14's first actual block crosses the paragraph boundary without changing PCM or adding silence.
add('14',1,[(A(95),9347,9920)],audio_from=0,audio_to=(9920-9347)/(60000/1001),note='Continuous current audio0–9.55955s; native red-chest/card appears near9.09s, matching the spoken result clause. White observed-result/undecided-condition diagram follows for all remaining14 PCM. No end-card freeze counts as actual.')
add('12',1,[A(47),A(57),A(52),(A(71),9690,9990)])
add('12',2,[A(n) for n in [77,78,79,80,16,29]]+[(A(95),9189,9347)])
add('12',3,[(A(82),480,796),(A(81),268,479)])
add('12',4,[A(86),(A(87),3513,3711)])
add('12',5,[(A(87),3711,3866),A(94)])
add('15',1,[A(n) for n in [48,50,51,54,55,56]])
add('15',2,[A(53),A(46),A(58),(A(71),9300,9690),A(62)])
add('15',3,[A(n) for n in [98,14,23,24,7,17,12,13]])
add('15',4,[(A(83),960,1276),(A(82),796,959)])
allcuts=[c for g in groups for c in g['sourceCuts']]
for sid in {c['sourceVideoId'] for c in allcuts}:
 cuts=sorted((c for c in allcuts if c['sourceVideoId']==sid),key=lambda c:c['startFrame'])
 for a,b in zip(cuts,cuts[1:]):assert a['endFrameExclusive']<=b['startFrame'],(sid,a['id'],b['id'])
used={c['id'] for c in allcuts};unassigned=sorted(set(clips)-used)
assert not unassigned,unassigned
proposal=dict(schemaVersion=1,createdAt=now,status='native-and-audio-cue-proposal-awaiting-new15-voice-and-exact-boundary-pixels',groups=groups,sourceUniqueSeconds=sum(c['seconds'] for c in allcuts),sourceAllNonOverlapping=True,original14PcmPreserved=True,sourceAudioUsed=False,selfCreatedGameExamples=0,bodyRatioApproved=False,allCaptionPixelsReviewed=False,exactNewNativeEdgesReviewed=False,sourceNotes=['Source14 shows combat through164.03s, red chest approach164.53s, opened chest/card165.03s; no interval after165.5s.','KWDwater51–52.5s only;52.5wipe and later mockup remain excluded.','New scene15 uses already directly reviewed unique native actions to keep the additional examples narrated; it does not replace any14-scene PCM or original six white explanations.'])
save(BASE/'native-cue-proposal.json',proposal)
ko=['책의 그림면에서는 적에게 다가가 싸우고, 다른 발판으로 이동합니다. 밝은 길과 어두운 길을 따로 보면, 싸운다는 말에 숨은 공간도 드러나죠.',
'책상에서는 길을 따라 걷거나 물체 가까이서 공격합니다. 그림면을 나오는 컷과 책상에서 움직이는 컷을 나눠 보면, 어디서 무엇을 하는지 더 구체적으로 말할 수 있습니다.',
'페퍼도 물가와 용암 위로 나오는 이동과 적을 향한 발사가 다릅니다. 움직임과 대상을 함께 말해 보세요.',
'광산에서는 다가오는 적을 피해 움직이며 공격합니다. 이 장면의 동작을 모든 전투의 규칙으로 옮기지는 않습니다.']
en=['On the illustrated page, the character approaches enemies, fights and moves to another platform. Separating the bright path from the dark one also brings out the setting hidden by the single word fight.',
'On the desk, the character walks along a route or attacks near objects. Treat the exit from the illustrated page and the movement on the desk as separate shots, and you can describe where each action happens.',
'Pepper’s movement out near water and above lava is different from firing toward an enemy. Describe the movement and its target together.',
'In the mine, the character moves to avoid an approaching enemy and attacks. These actions do not establish every condition of combat.']
for lang,lines in [('ko',ko),('en',en)]:
 p=PROJECT/f'script/narration.{lang}.json';d=read(p);assert len(d['scenes'])==14 and not any(x['id']=='15' for x in d['scenes'])
 save(BASE/f'narration-script-{lang}-14-preserved.json',d)
 n=next(i for i,x in enumerate(d['scenes']) if x['id']=='12');d['scenes'].insert(n,dict(id='15',title='실제 행동으로 공간과 대상을 덧붙이기' if lang=='ko' else 'Add the setting and target through observed actions',lines=lines));save(p,d)
review=dict(schemaVersion=1,reviewedAt=now,pairedWholeTextReview=True,allOriginal14TextUnchanged=True,original14PcmPreserved=True,newSceneId='15',paragraphs=[dict(ko=k,en=e,meaningAndOrderReviewed=True,sourceCuts=[dict(id=c['id'],sourceVideoId=c['sourceVideoId'],startFrame=c['startFrame'],endFrameExclusive=c['endFrameExclusive']) for c in g['sourceCuts']],visibleActionScopeOnly=True) for k,e,g in zip(ko,en,[g for g in groups if g['sceneId']=='15'])],overviewPromiseReview=True,overviewNote='The existing overview promises verbs, settings/conditions and listener checks. This extra action application supports those same promises before the unchanged conclusion; no new overview/TTS rewrite.',finalTimingApproved=False,humanWholeListening='pending')
save(BASE/'native-cue-commentary-text-review.json',review)
p=PROJECT/'planning/outline.md';p.write_text(p.read_text(encoding='utf-8')+'\n\n## 새15 · 실제 동작으로 공간과 대상을 덧붙이기\n\n기존14장 모든 대사/PCM과 여섯 흰설명 길이는 보존한다. 14뒤/12앞에 이미 직접 본 그림면의 밝은/어두운 전투·발판, 가상책상의 이동/물체공격, 페퍼의 용암이동/발사, 광산의 회피/공격을 독립한영4문단과 독립MC15로 추가한다. 새 문장은 native-cue-proposal.json의 네문단 출처인아웃/실제행동/대상에만 근거하고 버튼·승리·보편규칙을 확정하지 않는다. 원래전체안내의 동사·공간·조건/청자확인 약속과 기존12결론을 유지하며 도입23.44초를 재합성하지 않는다. 후보 재배치는 최종화면60:40이 아니며06의컵/조건,10의짧은탈것/접근성맥락,14의빨간상자결과에 새도식시간을 분리한다. 정확한 native경계·현재새15실측·모든고정큐/UI 검수 뒤에만 프레임계획을 확정한다.\n',encoding='utf-8')
p=MC/'project.ts';s=p.read_text(encoding='utf-8');s=s.replace("import scene12 from './scenes/scene12?scene';","import scene12 from './scenes/scene12?scene';\nimport scene15 from './scenes/scene15?scene';");s=s.replace('scene14,scene12','scene14,scene15,scene12');assert 'scene14,scene15,scene12' in s; p.write_text(s,encoding='utf-8')
(MC/'scenes/scene15.tsx').write_text("import {actualScene} from './actual-scene';\nexport default actualScene('15');\n",encoding='utf-8')
p=MC/'production-plan.json';d=read(p);i=next(i for i,x in enumerate(d['scenes']) if x['id']=='12');d['scenes'].insert(i,dict(id='15',title='실제 행동으로 공간과 대상을 덧붙이기',role='actual-footage',frames=0,seconds=0,actualVideo=None,actualMediaVerified=False,actualAudioStreams=0));d['currentFinalTimingApproved']=False;save(p,d)
# Lock only prepared current texts/plan and every existing14 PCM. The new output does not exist yet.
protected=[PROJECT/'script/narration.ko.json',PROJECT/'script/narration.en.json',PROJECT/'planning/outline.md',BASE/'native-cue-proposal.json',BASE/'native-cue-commentary-text-review.json']+[ROOT/x['path'] for x in pcm['measurements']]
out='shared/output/narration/avoid-game-comparisons/qwen3-1.7b-balanced-v4/chunks/15-scene.wav'
request=dict(schemaVersion=1,reviewedAt=now,model='qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base',reference='shared/voice-reference/reference-15-35s.wav',device='cpu',reason='Only new scene15 commentary for distinct already-inspected actions; preserve concurrent GPU training and all current14PCM.',protectedInputs=[dict(path=rel(x),sha256=sha(x)) for x in protected],pairedWholeTextReview=True,overviewPromiseReview=True,allPriorScenePcmPreserved=True,scenes=[dict(id='15',path=out,text=' '.join(ko))])
save(BASE/'native-cue-narration-request.json',request)
runner=(BASE/'render-additive-narration.py').read_text(encoding='utf-8').replace('additive-narration','native-cue-narration').replace('13/14','15').replace('current12','current14').replace('two-new','one-new').replace('two-new-scenes','one-new-scene').replace('new13/14','new15').replace('originalAll12PcmPreserved','originalAll14PcmPreserved').replace("['13','14']","['15']").replace("scriptScenes':14,'paragraphs':56","scriptScenes':15,'paragraphs':60").replace('original12','original14').replace('additive13-14','native-cue15').replace('new6 paragraphs','new4 paragraphs')
runner=runner.replace('additiveNarration','nativeCueNarration').replace('all new6 paragraphs','all new4 paragraphs')
(BASE/'render-native-cue-narration.py').write_text(runner,encoding='utf-8')
asr=(BASE/'review-additive-narration.py').read_text(encoding='utf-8').replace('additive-narration','native-cue-narration').replace('additive-whole','native-cue-whole').replace('additive-context','native-cue-context').replace('new13/14','new15').replace('new6 paragraphs','new4 paragraphs').replace('original12','original14')
asr=asr.replace('additiveNarration','nativeCueNarration')
(BASE/'review-native-cue-narration.py').write_text(asr,encoding='utf-8')
print(json.dumps({'sourceUniqueSecondsProposal':proposal['sourceUniqueSeconds'],'newScene':15,'newParagraphs':4,'current14PcmPreserved':True,'unresolvedGroupCoverage':[(x['sceneId'],x['paragraph'],x['unresolvedVoiceCoverageSeconds']) for x in groups if x['unresolvedVoiceCoverageSeconds']],'finalRatioApproved':False},ensure_ascii=False))

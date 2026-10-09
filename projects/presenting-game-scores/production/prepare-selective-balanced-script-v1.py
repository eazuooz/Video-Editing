from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
assert read(BASE/'source-content-adoption-v7.json')['footageAdoptedForScript']
dest=BASE/'script';assert not dest.exists();dest.mkdir()
ko=read(ROOT/'projects/presenting-game-scores/script/current-voice-v7.ko.json');en=read(ROOT/'projects/presenting-game-scores/script/current-voice-v7.en.json')
changes={
 '01-overview':([
 '게임의 점수 화면은 무엇을 세고, 무엇을 평가하는지 어떻게 알려 줄까요?',
 '먼저 테트리스의 줄 수와 점수를 구분하고, 발라트로에서 카드 한 장의 기여가 이번 손패와 누적 점수로 이어지는 과정을 보겠습니다.',
 '그다음 상대와 비교하는 기준을 확인하고, 점수의 이름과 피드백 순서를 정리해 플레이어가 다음 행동을 판단할 수 있는 화면을 설계해 보겠습니다.'],[
 'How can a score display tell us what a game counts and what it evaluates?',
 'We will first separate line counts from points in Tetris, then follow how a card contributes to a hand result and a running round score in Balatro.',
 'Next, we will examine the reference used to compare opponents, then organize score labels and feedback so players can judge what to do next.']),
 '04-evaluation-weights':(1,'발라트로에서는 먼저 족보가 계산의 출발점을 정하고, 점수를 만드는 카드와 조커가 칩과 배수를 바꿉니다. 선택한 카드가 모두 점수를 만들지는 않습니다.','In Balatro, the hand type sets the starting calculation, and contributing cards and Jokers change chips and the multiplier. Selecting a card does not guarantee that it contributes to the score.'),
 '05-events-and-total':(1,'한 손패의 결과가 정해진 뒤 라운드 점수에 더해집니다. 이번 결과와 누적값, 숫자가 더해지는 중의 중간값을 구분해야 합니다.','Once a hand result is established, it is added to the round score. Separate this result, the running total, and the intermediate numbers shown while the addition animates.'),
 '07-name-and-unit':(1,'발라트로의 라운드 점수와 목표 점수는 서로 다른 역할입니다. 회수한 물품 수와 종합 평가 점수도 서로 다른 정보를 말할 수 있죠.','Balatro’s round score and target score serve different purposes. Likewise, the number of recovered items and an overall evaluation score can communicate different information.'),
 '09-feedback-hierarchy':(1,'이번 손패의 계산과 누적 라운드 점수, 넘어야 할 목표를 나누어 보세요. 숫자가 반응하더라도 다시 읽을 위치는 안정적으로 유지됩니다.','Separate the current hand calculation, the running round score, and the target to beat. Even while numbers react, the places to read them again stay stable.'),
 '10-audit-and-close':(1,'테트리스에서는 줄 수와 평가 점수, 상대와의 차이를 구분했습니다. 발라트로에서는 카드의 기여, 이번 손패와 누적 점수, 그 값을 읽는 순서를 확인했죠.','In Tetris, we distinguished line counts, evaluation points, and the gap between opponents. In Balatro, we examined card contributions, hand results versus round totals, and the order in which to read them.'),
 '13-observe-action-label':(0,'숫자 칠 카드 세 장은 점수에 더해지지만, 함께 선택한 육 카드는 더해지지 않습니다. 선택과 기여를 구분해 보세요.','The three sevens contribute chips, but the six selected with them does not. Distinguish selection from contribution.'),
 '14-observe-notice-and-record':(0,'이번 손패 오백육십 점과 라운드 누적값 천삼백이십칠 점을 따로 읽어 보세요. 움직이는 중간값은 최종 점수가 아닙니다.','Read the 560-point hand result separately from the running round total of 1,327. Intermediate animated values are not the final score.'),
 '24-observe-named-fields-clear-start':(0,'먼저 이번 손패의 족보와 계산값을 읽고, 결과가 더해진 라운드 점수를 확인해 보세요. 이름이 다르면 숫자를 읽는 목적도 달라집니다.','First read the hand type and its calculation, then check the round score after the result is added. Different labels give numbers different purposes.'),
 '18-observe-stable-reading':(0,'라운드 점수 칠백사 점과 목표 천이백 점을 따로 읽어 보세요. 계산에 반응하는 숫자가 사라진 뒤에도 비교 기준은 남습니다.','Read the round score of 704 separately from the target of 1,200. The comparison remains available after the reacting calculation disappears.'),
 '19-observe-reading-audit':(0,'다이아몬드 카드의 표시와 반응을 함께 보세요. 선택한 카드가 점수에 기여하는지, 어떤 이름의 값을 보고 있는지 확인하는 점검입니다.','Read the diamond card’s marker together with its reaction. Check whether a selected card contributes and which named value you are observing.')}
originalKo=copy.deepcopy(ko);originalEn=copy.deepcopy(en);items=[];changedRows=[]
for ident,change in changes.items():
 ks=next(s for s in ko['scenes'] if s['id']==ident);es=next(s for s in en['scenes'] if s['id']==ident)
 if ident=='01-overview':ks['lines'],es['lines']=change;voiceId='r01-overview';lines=ks['lines'];enlines=es['lines']
 else:
  n,kt,et=change;oldk=ks['lines'][n];olde=es['lines'][n];ks['lines'][n]=kt;es['lines'][n]=et
  changedRows.append({'id':ident,'paragraph':n+1,'oldKo':oldk,'newKo':kt,'oldEn':olde,'newEn':et})
  voiceId='r'+ident+'-p'+str(n+1);lines=[kt];enlines=[et]
 items.append({'id':voiceId,'title':ks['title'],'lines':lines,'targetScene':ident,'replacementParagraph':None if ident=='01-overview' else n+1,'enLines':enlines})
save(dest/'narration.ko.json',ko);save(dest/'narration.en.json',en)
save(dest/'changed-voice.ko.json',{'title':ko.get('title'),'scenes':[{k:v for k,v in s.items() if k not in ['enLines','targetScene','replacementParagraph']} for s in items]})
save(dest/'changed-voice.en.json',{'title':en.get('title'),'scenes':[{'id':s['id'],'title':s['title'],'lines':s['enLines']} for s in items]})
voice=read(ROOT/'projects/presenting-game-scores/production/current-voice-selection-v7.json');oldplan=read(ROOT/'projects/presenting-game-scores/production/final-v1/plan.json');preserved=[]
for v in voice['scenes']:
 p=ROOT/v['path'];assert sha(p)==v['sha256'];ident=v['id']
 if ident=='01-overview' or ident in ['13-observe-action-label','14-observe-notice-and-record','24-observe-named-fields-clear-start','18-observe-stable-reading','19-observe-reading-audit']:continue
 if ident in changes:
  bounds=oldplan['paragraphBoundaries'][ident][:]
  if ident=='07-name-and-unit':bounds[2]=268800 #11.20s actual PCM quiet boundary; joined context review still required
  ranges=[(0,bounds[1],1),(bounds[2],v['samples'],3)]
 else:ranges=[(0,v['samples'],'whole')]
 for a,b,para in ranges:preserved.append({'id':ident,'paragraph':para,'sourcePath':v['path'],'sourceSha256':v['sha256'],'sourceStartSample':a,'sourceEndSampleExclusive':b,'samples':b-a,'sampleRate':24000,'seconds':(b-a)/24000,'pcmBytesMustRemainExact':True,'completeContextReviewRequiredForNewJoins':True})
save(BASE/'pcm-preservation-selection-v1.json',{'schemaVersion':1,'baselineSelection':'projects/presenting-game-scores/production/current-voice-selection-v7.json','allBaselineWavsUnchanged':True,'wholePreservedScenes':['02-score-and-lines','03-same-count','06-relative-gap','08-scoring-feedback','11-observe-separate-updates','12-observe-equal-quantity','15-observe-equal-lines-gap','16-observe-later-point-lead'],'preservedRanges':preserved,'newVoiceItems':len(items),'newPcmGenerated':False,'newJoinContextApproval':False,'07BoundaryNote':'Historical11.30s boundary falls on 어떤 onset; actual quiet11.20s lies in actual ASR sentence gap10.98–11.30. PCM RMS and complete independent context must be checked before joining.'})
manifest=read(ROOT/'projects/presenting-game-scores/project.json');out='shared/output/narration/presenting-game-scores/qwen3-balatro60-revision-v1'
manifest['tts'].update(outputDir=out,filenameStem='balatro60-revision-v1',renderMode='scene')
manifest['paths'].update(script=(dest/'changed-voice.ko.json').relative_to(ROOT).as_posix(),scriptEn=(dest/'changed-voice.en.json').relative_to(ROOT).as_posix(),narration=out+'/balatro60-revision-v1.wav',captionsKo=out+'/balatro60-revision-v1.srt',captionsEn=out+'/balatro60-revision-v1.en.srt')
manifest['status']='selective-Balatro60-voice-measurement-only';manifest['publishReady']=False;manifest['approvals'].update(voice='reuse-approved-Qwen1.7B/reference',humanListening='pending',humanPronunciation='pending',publicRights='pending',finalMixedAsr=False,allFinalPixels=False)
save(BASE/'voice-manifest-v1.json',manifest)
save(BASE/'selective-script-change-audit-v1.json',{'schemaVersion':1,'preparedAt':datetime.now(timezone.utc).isoformat(),'changedParagraphs':changedRows,'changedOverview':True,'unchangedOriginalScenes':['02-score-and-lines','03-same-count','06-relative-gap','08-scoring-feedback'],'completeKoEnScenes':len(ko['scenes']),'completeParagraphs':sum(len(s['lines']) for s in ko['scenes']),'newVoiceItems':items,'sourceContentAdoption':'projects/presenting-game-scores/production/revision-balatro60-v2/source-content-adoption-v7.json','pairedWholeTextDirectReview':False,'overviewPromiseDirectReview':False,'readyForTts':False,'baselineScriptWrites':0,'baselineWavWrites':0,'newGpuJobs':0,'newAudio':0})
planning=BASE/'planning';planning.mkdir(exist_ok=True)
(planning/'outline.md').write_text('# 게임 점수 디자인 · Balatro60:Tetris40 수정\n\n검정 2.5D 설명과 기존 모든 개념을 보존합니다. 01 안내 → 02 줄 수와 점수 → 03 같은 수와 다른 평가 → 04 카드별 기여 → 05 손패와 라운드 누적 → 06 상대와 차이 → 07 이름·단위·목표 → 08 계산 반응 → 09 정보 우선순위 → 10 점검·과외 안내 순서입니다.\n\n안내는 중심 질문, 계산 과정을 읽는 성과, 실제 사례 순서와 첫 테트리스 사례를 연결하는 독립 3문장입니다. 목표20–30초이며 실측 전입니다. 본편 actual60:explanation40과 실제 게임 내부 Balatro60:Tetris40은 별도 실측합니다. 기존 설명7333프레임을 최소로 보존하고 유용한 설명과 승인된 불변 PCM을 자르지 않습니다. 충분한 고유 정상속도 행동을 사용하며 반복·저속·무관 idle를 사용하지 않습니다.\n\n현재 새 Balatro110초는 선정된 조건부 배정입니다. 음성 실측 뒤 필요한 추가 행동은 봉인된 Hook/기타 고유 구간을 검토해 배정하고, 같은 몽타지를 하나의 연속 게임 결과로 제시하지 않습니다. 모든 수치 주장은 해당 원본 구간과 직접 비교하며, 변하는 중간값은 최종 누적값으로 읽지 않습니다.\n\n화면은 전체 원본 UI를 보존하는1600×900 균일 크기와 같은 프레임의 배경 채움으로 준비합니다. 녹화자 크레딧은 게임 UI 밖 왼쪽에 표시하고 승인된 설명 링크 한 줄을 포함합니다. 자막은960,970 고정입니다. 준비 proxy 검수는 최종 encoded 전체 cue·cut 검수가 아닙니다.\n\n원래 고양이120프레임·회원600프레임·회원 신원·연속 Nimbus를 보존합니다. 기존 oDYJlcv2Dqk는 비공개 보존하며 새 수정본만 검수·수집·게시설정·Git 전달 후 디자인 차례09:00 Asia/Seoul로 예약합니다. 사람 전체청취·발음·공개권리는 미완료입니다.\n','utf-8')
print(json.dumps({'scenes':len(ko['scenes']),'paragraphs':sum(len(s['lines']) for s in ko['scenes']),'newVoiceItems':len(items),'preservedRanges':len(preserved),'baselineChanged':False,'ttsStarted':False}))

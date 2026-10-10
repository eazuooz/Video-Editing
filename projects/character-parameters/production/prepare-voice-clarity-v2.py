"""Prepare two meaning-preserving complete-paragraph voice changes.

All baseline scripts, 12 PCM files, source/timing reviews remain untouched.
Candidate scripts are not adopted until fresh voice and ASR review.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=datetime.now(timezone.utc).isoformat()
folder=BASE/'voice-clarity-v2';assert not folder.exists();folder.mkdir()
state=read(BASE/'current-targets-asr-execution-v1.json')
assert state['exitCode']==state['actualOuterExitCode']==0 and state['actualExitObserved']
asr=read(BASE/'current-targets-asr-v1/asr.json');assert asr['complete'] and len(asr['results'])==2
ko=read(ROOT/'projects/character-parameters/script/narration.ko.json')
en=read(ROOT/'projects/character-parameters/script/narration.en.json')
replacement=[
 ('08-resources-and-actions',19.86,
  '기술의 개성은 피해량에만 있지 않습니다. 방어, 자원, 상대의 선택지를 바꾸는 효과도 역할을 만들 수 있습니다. 이때 화면의 주사위 값은 이번 턴에 쓰는 상태이며, 캐릭터에게 고정된 기본 능력치가 아닙니다.',
  'An ability’s identity is not limited to damage. Defense, resources and the opponent’s options can also define a role. The displayed dice values are used in the current turn; they are not the character’s fixed base capabilities.'),
 ('09-condition-and-time',19.19,
  '설계 문장에도 발동 조건, 바뀌는 대상, 적용 시점을 함께 적어 보세요. 그래야 실제 프로그램의 동작과 화면 설명이 서로 다른 규칙을 말하는 일을 줄일 수 있습니다.',
  'Write the trigger, affected target and application time together. This helps the program’s actual behavior and the on-screen explanation describe the same rule.')
]
tts=read(BASE/'narration-tts-execution-v2.json');assert len(tts['results'])==12
protected=[]
for r in tts['results']:
 assert sha(ROOT/r['path'])==r['sha256'];protected.append(dict(path=r['path'],sha256=r['sha256'],purpose='Preserve original complete scene PCM'))
for r in read(BASE/'narration-tts-request-v1.json')['protectedInputs']:
 assert sha(ROOT/r['path'])==r['sha256'];protected.append(r)
changes=[];items=[]
for sid,start,k,e in replacement:
 ks=next(s for s in ko['scenes'] if s['id']==sid);es=next(s for s in en['scenes'] if s['id']==sid)
 r=next(s for s in tts['results'] if s['id']==sid)
 changes.append(dict(id=sid,paragraph=3,oldKo=ks['lines'][2],newKo=k,oldEn=es['lines'][2],newEn=e,meaningPreserved=True,claimReview='08: current-turn dice state differs from fixed base capabilities. 09: condition/target/time keep actual program behavior and screen explanation aligned.',originalPath=r['path'],originalSha256=r['sha256'],retainedPrefixSamples=round(start*24000),originalEndingRetainedInBaseline=True,baselineNotOverwritten=True))
 ks['lines'][2]=k;es['lines'][2]=e
 items.append(dict(id=sid+'-p3-clarity',text=k,path='shared/output/narration/character-parameters/voice-clarity-v2/'+sid+'-p3-clarity.wav'))
for lang,d in [('ko',ko),('en',en)]:
 p=folder/('narration.'+lang+'.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');protected.append(dict(path=rel(p),sha256=sha(p),purpose='Reviewed unadopted candidate full script'))
targetReview=folder/'targeted-current-direct-review-v1.json'
targetReview.write_text(json.dumps(dict(reviewedAt=stamp,actualOuterSession=43224,actualOuterExitCode=0,allExpectedAndEntireActualDirectlyRead=True,allWordTimestampsRead=True,completeContexts=2,rows=[dict(id=r['id'],expected=r['expectedKo'],actual=r['text'],sourceSha256=r['sourceSha256'],contextSha256=r['contextSha256'],observation='Entire complete paragraph and original ending represented; persistent 영구/연구 in08 and 구현/구형 in09 remain unresolved phonetic ambiguity, not automatically approved.') for r in asr['results']],humanListening='pending',humanPronunciation='pending',currentVoiceApproved=False,sourcePcmChanged=False),ensure_ascii=False,indent=2)+'\n','utf-8')
review=folder/'candidate-paired-text-direct-review-v2.json'
review.write_text(json.dumps(dict(reviewedAt=stamp,completeScenes=12,pairedParagraphs=37,allOtherParagraphsPreserved=True,changes=changes,entireChangedKoEnDirectlyCompared=True,overviewAndConclusionPromisesPreserved=True,noNewSourceClaim=True,referenceAndModelPreserved=True,contentReadyForApprovedVoiceMeasurement=True,sourceAdoptionChanged=False,mainScriptsChanged=False,candidateAdopted=False,humanListening='pending',humanPronunciation='pending'),ensure_ascii=False,indent=2)+'\n','utf-8')
protected.append(dict(path=rel(review),sha256=sha(review),purpose='Paired changed-text review before TTS'))
request=folder/'request.json'
request.write_text(json.dumps(dict(schemaVersion=1,slug='character-parameters',preparedAt=stamp,total=2,completeParagraphs=2,review=rel(review),reviewSha256=sha(review),scenes=items,protectedInputs=protected,model='qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base',reference='shared/voice-reference/reference-15-35s.wav',referenceText='shared/voice-reference/reference-15-35s.ko.txt',approvedVoiceOnly=True,actualGpuHandoffRequired=True,restoreOriginalResearchOnSuccessAndFailure=True,originalPcmOverwritten=False,candidateAdopted=False,wholeFreshAsrRequired=True,independentCompleteContextRequired=True,finalMixedAsrApproved=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(request=rel(request),changedCompleteParagraphs=2,baselinePcmPreserved=12,mainScriptsChanged=False,candidateAdopted=False),ensure_ascii=False))

"""Seal the directly read repaired whole/independent/joined content review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, wave
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
stamp=datetime.now(timezone.utc).isoformat()
dest=B/'current-complete-voice-direct-review-v3.json';assert not dest.exists()
r=read(B/'voice-joined-asr-v3/10-audit-and-close.json')
session=read(B/'voice-joined-asr-session-v3.json')
assert session['actualOuterExitCode']==0 and not session['workerExpectedRunning']
assert sha(ROOT/r['sourcePath'])==r['sourceSha256']
norm=lambda s:''.join(c for c in s if c.isalnum())
assert norm(' '.join(r['expectedKo']))==norm(r['text'])
assert r['words'][-1]['text'].strip()=='확인해주세요.'
assert any(w['text'].strip()=='테트리스에서는' for w in r['words'])
assert not any('스테트리스' in w['text'] for w in r['words'])
j=dict(schemaVersion=3,reviewedAt=stamp,actualOuterSession=33720,actualOuterExitCode=0,
    result=rel(B/'voice-joined-asr-v3/10-audit-and-close.json'),resultSha256=sha(B/'voice-joined-asr-v3/10-audit-and-close.json'),
    sourcePath=r['sourcePath'],sourceSha256=r['sourceSha256'],expectedKo=r['expectedKo'],actualWholeText=r['text'],words=r['words'],
    allWholeTextAndWordsDirectlyCompared=True,allThreeParagraphsInOrder=True,
    leadingTetrisOnsetResolvedInWholeIndependentAndJoin=True,
    findings='All three paragraphs and sentence endings retained. Tetris onset6.60–7.46s is complete; 카드의12.16–12.68s is recognized in the complete join. Only spacing differs. Last 확인해주세요 ends24.82s within24.84s PCM.',
    completeJoinedContextApproved=True,currentCompleteVoiceApproved=True,
    finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending')
save(B/'voice-joined-direct-review-v3.json',j)
refs=['voice-whole-direct-review-v1.json','voice-contexts-direct-review-v1.json','voice-joined-direct-review-v1.json',
      'voice-decoding-direct-review-v2.json','voice-whole-direct-review-v3.json','voice-contexts-direct-review-v3.json','voice-joined-direct-review-v3.json']
vpath=B/'preserved-pcm-complete-joins-v3.json';v=read(vpath)
for x in v['scenes']:assert sha(ROOT/x['path'])==x['sha256']
for x in read(B/'narration-tts-request-v3.json')['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
for join in v['joins']:
    with wave.open(str(ROOT/join['path']),'rb') as f:pcm=f.readframes(f.getnframes());assert f.getframerate()==24000
    for x in join['preservedPieces']:
        with wave.open(str(ROOT/x['sourcePath']),'rb') as f:src=f.readframes(f.getnframes())
        a=x['sourceStartSample']*2;b=x['sourceEndSampleExclusive']*2
        assert pcm[x['joinedStartSample']*2:x['joinedEndSampleExclusive']*2]==src[a:b]
v.update(currentCompleteVoiceApproved=True,completeJoinedContextApproved=True,currentContentApprovalScope='Exact selected19 PCM; full current text/order/complete contexts and joins reviewed. Human phonetics and final mix remain pending.',directReview=rel(dest),updatedAt=stamp)
save(vpath,v)
save(dest,dict(schemaVersion=3,reviewedAt=stamp,currentCompleteVoiceApproved=True,completeJoinedContextApproved=True,
    reviewEvidence=[dict(path=rel(B/n),sha256=sha(B/n)) for n in refs],voiceSelection=rel(vpath),voiceSelectionSha256=sha(vpath),
    selectedSceneCount=19,unchangedPhysicalScenesReused=17,localizedRepairedItems=2,totalNarrationSeconds=v['totalNarrationSeconds'],
    allExactCurrentPcmHashesMatched=True,allPreservedParagraphPcmBytesMatched=True,
    oldOverviewAndAuditResultsPreserved=True,
    unresolvedHumanPronunciation=['retained baseline08 기여/기어 and 읽게/잃게 recognition alternatives','possessive 의/에 and 점수의 이름 alternatives in retained/new isolated contexts'],
    approvalScope='Technical content/order/endings of exact selected unmixed19 PCM approved; not human listening/pronunciation or final-mixed approval.',
    finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending',publicRights='pending'))
print(json.dumps(dict(currentCompleteVoiceApproved=True,scenes=19,unmixedOnly=True,finalMixedAsrApproved=False)))

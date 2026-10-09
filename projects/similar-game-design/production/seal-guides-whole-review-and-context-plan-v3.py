"""Record the directly read nine results; schedule independent complete contexts.
This records recognition differences, without turning them into audio defects
or automatically approving narration. Every context keeps the full current PCM.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, psutil, time, wave

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, x):
    t = p.with_name(p.name + f'.{os.getpid()}.writing')
    t.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(t, p)
stamp = datetime.now(timezone.utc).isoformat()
statepath = BASE/'guides-whole-asr-v3-execution.json'
state = read(statepath)
assert state['completed'] == state['total'] == 9 and state['exitCode'] == 0
if psutil.pid_exists(state['pid']):
    assert abs(psutil.Process(state['pid']).create_time()-state['createTime']) > .01, 'Worker still alive.'
assert not (BASE/'guides-whole-asr-direct-review-v3.json').exists()
state.update(actualExitObserved=True, actualExitCodeObserved=0, processIdentityAbsentVerifiedAt=stamp)
save(statepath, state)
session = read(BASE/'guides-whole-asr-v3.session.json')
session.update(status='closed-exit0-directly-observed', actualExitObserved=True, exitCode=0, observedAt=stamp)
save(BASE/'guides-whole-asr-v3.session.json', session)
asrpath = BASE/'guides-whole-asr-v3/asr.json'
asr = read(asrpath)
assert asr['complete'] and len(asr['results']) == 9
differences = {
 '14-corridor-pursuit': 'Whole ASR adds 자 at 0–0.18s and reads 사이의 as 사이에. Preserve full PCM from sample0; independently test the complete onset/body/end. No inferred audio greeting and no onset trimming.',
 '15-corridor-to-open': 'All expected sentences and complete ending present; spacing/punctuation only.',
 '16-effects-and-position': 'All expected sentences and complete ending present; spacing/punctuation only.',
 '17-rock-and-route': 'All expected sentences including 있습니다12.46–12.86s present. Bad ending heuristic is retained as history and is not the approval criterion.',
 '18-target-and-effects': 'All expected sentences and complete ending present; spacing/punctuation only.',
 '19-visible-destination': '귀환 reads 귀한1.10–1.60s. Independently compare the whole statement; pronunciation remains human-pending.',
 '20-moving-relationships': '회피 reads 회피의10.88–11.22s. Independently compare both complete paragraphs; do not silently alter the script.',
 '21-read-before-ranking': 'Expected initial 적 is absent from whole ASR; 무리를 covers0–0.94s. Preserve all onset PCM and independently verify the full statement.',
 '22-mining-opening-repair': 'All expected words present, including 딥록0–0.56s and full 장면입니다8.90–9.66s. Original04 has not been replaced; complete context and preserved-tail join are still required.'
}
rows=[]; contexts=[]
for row in asr['results']:
    path=ROOT/row['sourcePath']; assert sha(path)==row['sourceSha256']==row['audioSha256']
    with wave.open(str(path),'rb') as w:
        assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2)
        samples=w.getnframes(); pcm=w.readframes(samples)
    assert samples==row['sourceSamples'] and row['expectedWasRecognizerPrompt'] is False
    rows.append(dict(id=row['id'],expectedKo=row['expectedKo'],actualText=row['text'],actualWords=row['words'],
                     sourcePath=row['sourcePath'],sourceSha256=row['sourceSha256'],
                     fullExpectedActualTextAndWordsDirectlyRead=True,recognitionReview=differences[row['id']],
                     narrationApproved=False))
    contexts.append(dict(id=row['id']+'-complete-independent',sceneId=row['id'],sourcePath=row['sourcePath'],
                         sourceSha256=row['sourceSha256'],startSample=0,endSample=samples,
                         zeroPaddingSamplesEachSide=9600,expectedKo=row['expectedKo'],
                         originalFullPcmSha256=hashlib.sha256(pcm).hexdigest(),
                         boundaryReason='Full independent complete context, current whole words directly read. Original sample0 through complete tail retained; only independent0.4s zero padding each side.'))
review=dict(schemaVersion=1,reviewedAt=stamp,slug='similar-game-design',sessionId=45845,
            sourceAsr={'path':str(asrpath.relative_to(ROOT)).replace('\\','/'),'sha256':sha(asrpath)},
            allWholeTextsDirectlyCompared=True,fullResults=rows,automaticApproval=False,
            currentVoiceTextIntegrityApproved=False,independentContextsApproved=False,localized04Applied=False,
            original13Retranscribed=False,finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending')
rp=BASE/'guides-whole-asr-direct-review-v3.json';save(rp,review)
save(BASE/'guides-independent-context-plan-v3.json',dict(schemaVersion=1,createdAt=stamp,
     wholeReview=str(rp.relative_to(ROOT)).replace('\\','/'),wholeReviewSha256=sha(rp),
     boundariesDirectlyComparedWithCurrentWordsAndPCM=True,contexts=contexts,
     allCurrentSamplesRetained=True,recognizerExpectedPrompt=False,automaticApproval=False))
measurement=BASE/'current-original-paragraph-timing-v1.json'
m=read(measurement)
assert len(m['scenes'])==13 and sum(len(s['boundaries']) for s in m['scenes'])==38
save(BASE/'current-original-paragraph-boundary-direct-review-v1.json',dict(schemaVersion=1,reviewedAt=stamp,
     measurement={'path':str(measurement.relative_to(ROOT)).replace('\\','/'),'sha256':sha(measurement)},
     all38PreviousNextWordPairsAndRmsDirectlyRead=True,allOriginal51KoParagraphsDirectlyRead=True,
     allOriginalSamplesRetained=True,quietGapCaution='13p3→p4 RMS0.005777365 at28.04s; complete context words end27.8975/start28.0975. Preserve it as a measured gap, without a claim of literal zero silence.',
     boundaries=[dict(sceneId=s['id'],boundaries=s['boundaries']) for s in m['scenes']],
     localized04CandidateApplied=False,finalTimelineApproved=False,bodyRatioApproved=False,
     continuousSelectedActionReview=False,humanListening='pending',humanPronunciation='pending'))
print(json.dumps(dict(wholeDirectlyRead=9,fullIndependentContextsPrepared=9,originalBoundariesDirectlyRead=38,
                     fullVoiceApproved=False,original04Changed=False),ensure_ascii=False))

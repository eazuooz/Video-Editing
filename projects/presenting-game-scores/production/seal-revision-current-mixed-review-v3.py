"""Seal direct current mixed completeness with unresolved human pronunciation kept."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, wave
ROOT=Path(__file__).resolve().parents[3]
W=Path(__file__).resolve().parent/'revision-balatro60-v2/final-v3'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ex=read(W/'mixed-asr-execution.json')
progress=read(W/'mixed-asr-direct-progress.json')
data=read(W/'mixed-asr-v1/asr.json')
manual=read(W/'mixed-asr-completeness-assessment-v3.json')
assert ex['exitCode']==ex['outerExitCode']==0 and ex['outerExitDirectlyObserved']
assert data['complete'] and len(data['results'])==progress['directlyRead']==52
assert progress['all52WindowsDirectlyCompared']
assert manual['all52EntireTextsAndWordTimestampsDirectlyRead'] and not manual['confirmedSentenceContentDefects']
mix=W/'final-mix.wav'; settings=read(W/'mix-settings.json')
assert sha(mix)==settings['wavSha256']==data['mixSha256']==manual['currentMixedAudioSha256']
assert sha(W/'plan.json')==data['planSha256']==manual['currentPlanSha256']
assert sha(W/'final-mix.m4a')==settings['aacSha256']==data['aacSha256']
assert not (W/'full-mix-asr-review.json').exists()
rows=[]
with wave.open(str(mix),'rb') as whole:
    assert (whole.getframerate(),whole.getnchannels(),whole.getsampwidth())==(48000,2,2)
    for row in progress['windows']:
        p=ROOT/row['path'];d=read(p)
        assert sha(p)==row['sha256'] and row['directlyCompared'] and row['allWordTimestampsRead']
        whole.setpos(d['fromSample']);b=whole.readframes(d['toSample']-d['fromSample'])
        assert hashlib.sha256(b).hexdigest()==d['mixPcmSliceSha256']
        wp=ROOT/d['windowPath'];assert sha(wp)==d['windowSha256']
        with wave.open(str(wp),'rb') as clip:
            assert (clip.getframerate(),clip.getnchannels(),clip.getsampwidth())==(48000,2,2)
            assert clip.readframes(clip.getnframes())==bytes(d['padSamplesEachSide']*4)+b+bytes(d['padSamplesEachSide']*4)
        rows.append(dict(row,expectedKo=d['expectedKo'],actualText=d['text'],
            exactCurrentMixedPcmSliceReverified=True,humanPronunciation='pending'))
review=dict(schemaVersion=3,slug='presenting-game-scores',reviewedAt=datetime.now(timezone.utc).isoformat(),
    status='current-mixed-completeness-approved-with-human-pronunciation-pending',
    currentMixedAudioSha256=data['mixSha256'],currentAacSha256=data['aacSha256'],planSha256=data['planSha256'],
    windows=rows,wholeWindowCount=10,independentWindowCount=42,all52WindowsDirectlyCompared=True,
    all52CurrentMixedPcmSlicesReverified=True,unresolvedContentDefects=[],technicallyApproved=True,
    completenessAssessment=(W/'mixed-asr-completeness-assessment-v3.json').relative_to(ROOT).as_posix(),
    completenessAssessmentSha256=sha(W/'mixed-asr-completeness-assessment-v3.json'),
    unresolvedHumanPronunciationQuestions=manual['unresolvedHumanPronunciationQuestions'],
    approvalScope=manual['approvalScope'],priorUnmixedApprovalUsedAsFinalMixApproval=False,
    endingHeuristicUsedForApproval=False,expectedWasRecognizerPrompt=False,automaticApproval=False,
    humanWholeListening='pending',humanPronunciation='pending',publicRights='pending',
    allFinalPixels=False,qaApproved=False,collected=False,uploaded=False)
(W/'full-mix-asr-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(currentMixedWindows=52,technicallyApproved=True,humanPronunciation='pending',allFinalPixels=False)))

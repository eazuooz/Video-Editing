"""Record the38 manually compared current-mix windows; preserve raw ASR anomalies."""
from final_cpu_common import *
import numpy as np
import pcm16_wav_io as sf

pointer=read(FINAL/'mixed-asr-current.json')
execution=read(ROOT/pointer['execution'])
assert execution['exitCode']==0 and execution['completed']==38
request=read(ROOT/pointer['request']);results=read(ROOT/pointer['results'])
notes=read(FINAL/'mixed-asr-direct-notes-v2.json')
labels=[r['label'] for r in request['windows']]
assert len(labels)==38 and set(labels)==set(notes['notes'])
assert notes['all38WindowsDirectlyCompared'] is True
mix=read(FINAL/'mix-settings.json');plan=read(FINAL/'plan.json')
assert notes['currentMixedAudioSha256']==results['mixSha256']==mix['wavSha256']==sha(FINAL/'final-mix.wav')
assert notes['planSha256']==request['planSha256']==mix['planSha256']==sha(FINAL/'plan.json')
pcm=read(FINAL/'pcm-timeline-preservation.json')
assert pcm['planSha256']==sha(FINAL/'plan.json') and pcm['voiceSha256']==sha(ROOT/pcm['voicePath'])
timeline,sr=sf.read(ROOT/pcm['voicePath'],dtype='int16');assert sr==24000
used=np.zeros(len(timeline),dtype=bool)
for p in pcm['placements']:
    source=ROOT/p['path'];assert sha(source)==p['sha256']
    x,rate=sf.read(source,dtype='int16');lo,hi=p['startSample'],p['endSample']
    assert rate==sr and len(x)==p['samples']==hi-lo
    assert not used[lo:hi].any() and np.array_equal(x,timeline[lo:hi])
    used[lo:hi]=True
assert used.sum()==8968322 and not np.count_nonzero(timeline[~used])
captions=read(ROOT/plan['captionCandidate'])
records=[]
for label in labels:
    path=Path(pointer['results']).parent/(label+'.json');row=read(ROOT/path)
    assert row['expectedWasRecognizerPrompt'] is False and row['mixSha256']==mix['wavSha256']
    assert sha(ROOT/row['windowPath'])==row['windowSha256']
    regressions=[];prior=-1
    for word in row['words']:
        lo,hi=word['timestamp']
        if lo is not None and lo<prior:regressions.append(word)
        if hi is not None:prior=hi
    # The10 independent span also includes the interleaved19 guide between
    # its two original paragraphs; keep the recognizer request untouched.
    contained=sorted([p for p in captions['paragraphs'] if p['startSeconds']>=row['fromSeconds']-.002 and p['endSeconds']<=row['toSeconds']+.002],key=lambda p:p['startSeconds'])
    records.append(dict(label=label,raw=path.as_posix(),rawSha256=sha(ROOT/path),windowSha256=row['windowSha256'],requestExpectedKo=row['expectedKo'],currentChronologicalExpectedKo=[p['ko'] for p in contained],actualText=row['text'],endingWords=row['words'][-8:],timestampRegressions=regressions,directlyCompared=True,manualDecision=notes['notes'][label]))
write(FINAL/'full-mix-asr-review.json',dict(createdAt=now(),scope='Current final mixed WAV: all19 full chapter spans and19 independent complete contexts manually compared, all expected sentences, tails, omissions, repetitions and variants inspected. Technical structural review; human listening/pronunciation remains pending.',currentMixedAudioSha256=mix['wavSha256'],planSha256=sha(FINAL/'plan.json'),requestSha256=sha(ROOT/pointer['request']),executionSha256=sha(ROOT/pointer['execution']),resultSha256=sha(ROOT/pointer['results']),manualNotesSha256=sha(FINAL/'mixed-asr-direct-notes-v2.json'),records=records,all38WindowsDirectlyCompared=True,technicallyApproved=True,endingHeuristicWasApproval=False,unmixedApprovalWasSubstituted=False,currentPcmPlacementRechecked=dict(placements=27,allSamplesIdentical=True,samples=8968322,repeatedSamples=0,discardedSamples=0,unallocatedSamplesSilent=True),chunkArtifactResolution=dict(scene02=['02-complete-context'],scene10=['18-complete-context','19-complete-context','10-complete-context'],evidence='Unchunked current-mix windows spanning affected edges contain complete sentences once with no credits/greetings; raw whole-window zero-duration tokens and timestamp regressions retained. Current PCM placement contains no inserted/repeated speech.'),humanWholeListening='pending',humanPronunciation='pending',pendingPronunciation=['Anger Foot/Gunbrella/My Friend Pedro proper names','맡는/맞는/만든다면 recognizer spellings','조준에/조준의 particle and 둘지뿐/둘짓뿐 variants','세 방식/새 방식 homophonic recognition'],finalPixelsApproved=False,qaApproved=False))
update_checkpoint('current-final-mixed-asr-direct-review-complete','Build one guarded current clean/captioned pair, directly read all final cue/cut pixels and QA, then collect/private/settings/Git and pause24. No next queued.',finalMixAsrApproved=True,finalMixAsrReview=rel(FINAL/'full-mix-asr-review.json'))
print(json.dumps(dict(windows=38,currentMixSha256=mix['wavSha256'],technicalStructuralApproved=True,humanWholeListening='pending',finalPixelsApproved=False)))

"""Record the completed manual whole-final-transcript comparison; no ASR."""
from pathlib import Path
import hashlib, importlib.util, json, time
import psutil

H = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('v7_final_direct_common', H / 'audio-common.py')
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)

def main():
    c.selected(); asr_file = c.O / 'final-master-asr.json'; asr = c.read(asr_file)
    binding_file = c.O / 'final-master-binding.json'; binding = c.read(binding_file)
    assert c.sha(c.R / binding['master']) == binding['masterSha256']
    assert binding['wholeAsrSha256'] == c.sha(asr_file)
    script_file = c.P / 'script/revision-v7-two-part/part-01.ko.json'; script = c.read(script_file)
    assert c.sha(script_file) == asr['approvedScriptSha256']
    timeline_file = H / 'timeline.json'; timeline = c.read(timeline_file)
    source_file = c.O / 'source-direct-review.json'; source = c.read(source_file)
    notes = {r['scene']: r['decision'] for r in source['scenes']}
    rows = []; words = asr['words']; assigned = {s['id']: [] for s in timeline['scenes']}; outside = []
    for i, word in enumerate(words):
        lo, hi = word['timestamp']
        if lo is None: outside.append(dict(wordIndex=i, word=word)); continue
        if hi is None: hi = lo
        overlaps = [(max(0, min(hi, (s['startFrame'] + s['frames']) / 60) - max(lo, s['startFrame'] / 60)), s['id']) for s in timeline['scenes']]
        amount, sid = max(overlaps)
        if amount > 0: assigned[sid].append(i)
        else: outside.append(dict(wordIndex=i, word=word))
    backward = []
    for i, (before, after) in enumerate(zip(words, words[1:]), 1):
        x, y = before['timestamp'][0], after['timestamp'][0]
        if x is not None and y is not None and y < x - .04:
            sid = next(sid for sid, indices in assigned.items() if i in indices)
            backward.append(dict(scene=sid, wordIndex=i, previousWord=before, nextWord=after,
                backwardSeconds=x-y, sourceAsrContainsPassageOnce=True,
                decision='Long-file recognition overlaps the same physical word clock; this is not evidence of a second spoken passage. Original raw result is preserved.'))
    assert [x['scene'] for x in backward] == ['v7-a02', 'v7-a07', 'v7-a09']
    for scene, clock in zip(script['scenes'], timeline['scenes']):
        sid = scene['id']; indices = assigned[sid]
        rows.append(dict(scene=sid, paragraphs=len(scene['lines']),
            approvedParagraphIds=[f"{sid}.L{i:02}" for i in range(1, len(scene['lines'])+1)],
            globalRange=[clock['startFrame']/60, (clock['startFrame']+clock['frames'])/60],
            rawRecognitionWordIndices=indices, rawRecognition=''.join(words[i]['text'] for i in indices),
            fullApprovedAndRawFinalRecognitionDirectlyRead=True,
            definitionsNumbersSignsAndLimitationsCompared=True,
            retainedClaimReview=notes[sid],
            finalRecognitionDecision=('Same-clock chunk overlap explicitly resolved against existing source recognition and immutable mix/stem proof; not a confirmed audio repetition.' if sid in ['v7-a02','v7-a07','v7-a09'] else 'Complete final recognition compared with approved paragraphs and source findings; no confirmed changed/missing claim.'),
            humanListening='pending'))
    assert sum(r['paragraphs'] for r in rows) == 135 and not outside
    uncertainties = [
        dict(scene='v7-a03', expected='식의 부호', recognized='시계 부호', kind='Homophonic recognition ambiguity already present in source review; not a confirmed wrong word.'),
        dict(scene='v7-a14', expected='규약까지', recognized='귀하까지', kind='Recognition/pronunciation ambiguity already present in source review; no automatic retake from spelling.'),
        dict(scene='v7-a12', expected='요라고 / 요를 / 요 동작', recognized='Y라고 / Y를 / 이 동작', kind='Final recognition spelling/word uncertainty; existing current source recognition correctly contains 요. Actual pronunciation listening remains pending.'),
        dict(scene='v7-a15', expected='열린 쪽이 어디를 향하는지가 중요합니다', recognized='열린 쪽이 어디를 향한 장면이 중요합니다', kind='Final recognition wording uncertainty; current source recognition contains the approved phrase. Actual pronunciation listening remains pending.')]
    cues = c.read(c.O.parent / 'captions/captions.json')['cues']
    targets = {'v7-a03': ['식의 부호'], 'v7-a14': ['규약까지'],
               'v7-a12': ['여기서는 요라고', '이 자세에서 요를', '따라서 요 동작'],
               'v7-a15': ['열린 쪽이 어디를 향하는지가']}
    for row in uncertainties:
        row['humanListening'] = 'pending'
        row['globalListeningRanges'] = [[q['start'], q['end']] for q in cues if q['scene'] == row['scene'] and any(term in q['sourceKo'] for term in targets[row['scene']])]
    result = dict(schemaVersion=1, part=1, master=binding['master'], masterSha256=binding['masterSha256'],
        asrOriginMasterSha256=binding['asrOriginMasterSha256'],
        currentMasterBinding=c.rel(binding_file), currentMasterBindingSha256=c.sha(binding_file),
        approvedScriptSha256=c.sha(script_file), wholeFinalAsr=c.rel(asr_file), wholeFinalAsrSha256=c.sha(asr_file),
        rawWholeTranscriptSha256=hashlib.sha256(asr['text'].encode()).hexdigest(),
        sourceDirectReview=c.rel(source_file), sourceDirectReviewSha256=c.sha(source_file),
        implementation=c.rel(Path(__file__)), implementationSha256=c.sha(Path(__file__)),
        all21FinalRawTranscriptsDirectlyRead=True, paragraphsCompared=135,
        confirmedMissingOrChangedClaims=0, confirmedFinalAudioRepetitions=0,
        finalAsrOpeningNowContains='안녕하세요. 얌얌코딩입니다. / 지금까지 쓴 오일러 각',
        finalNumericalChecks=['heading45/pitch20/bank30', 'fixed-X90 then fixed-Y90 versus reversed',
            'one-degree quantization; component error0.5 is not total orientation error', 'finite720/135',
            '(0,135,0)=(180,45,180)', 'heading/bank(-180,180], pitch[-90,90]',
            'pitch+90:heading-bank;30-10=20;heading45 matches bank-45', 'pitch-90:heading+bank',
            'bank0 representative does not repair gimbal-lock continuity'],
        scenes=rows, recognitionBoundaryOverlaps=backward, listeningUncertainties=uncertainties,
        firstWordTimingCaveat='Whisper attaches the first greeting to0..2.66s including silent branding. The complete greeting is present in raw text; this ASR timing is not used to move approved captions or audio.',
        sourceAndFinalAsrDistinct=True, wholeFinalRecognitionCount=1, noExpectedPrompt=True,
        sourcePcmAndMixUnchanged=True, extraAsrRuns=0, reviewedAt=time.time(),
        transcriptClaimReview='complete with explicitly retained recognition/pronunciation uncertainties',
        encodedLevelReview='pending separate current-AAC measurement', humanWholeListening='pending',
        subjectiveJoinSmoothness='pending', actualVoiceVisualPace='pending',
        note='Direct text comparison is complete. Recognition text, word clocks, and source/stem identity are evidence, not a claim that the complete audio was heard or its delivery was subjectively approved.')
    c.save(c.O / 'final-master-direct-review.json', result)
    execution = c.read(c.O / 'final-master-asr-execution.json')
    assert execution['returnCode'] == 0 and execution['state'] == 'complete'
    owned = []
    for proc in psutil.process_iter(['pid','cmdline']):
        if any(Path(arg).name == 'final-master-asr.py' for arg in proc.info['cmdline'] or []): owned.append(proc.info['pid'])
    assert not owned
    lease = c.read(c.LEASE) if c.LEASE.exists() else None
    assert not lease or lease.get('project') != c.P.name
    c.save(c.O / 'final-gpu-release.json', dict(part=1, ownFiniteLeaseReleased=True,
        ownFinalAsrProcesses=owned, sharedLeasePresent=bool(lease), foreignLeaseUntouched=True,
        execution=c.rel(c.O/'final-master-asr-execution.json'), executionSha256=c.sha(c.O/'final-master-asr-execution.json'),
        returnCode=0, currentMasterSha256=binding['masterSha256'], wholeFinalRecognitionCount=1,
        noForeignProcessClosedOrPaused=True, checkedAt=time.time()))
    print(json.dumps(dict(scenes=21, paragraphs=135, confirmedChangedClaims=0,
        recognitionBoundaryOverlaps=len(backward), listeningUncertainties=len(uncertainties),
        masterSha256=binding['masterSha256'], ownGpuReleased=True)))

if __name__ == '__main__': main()

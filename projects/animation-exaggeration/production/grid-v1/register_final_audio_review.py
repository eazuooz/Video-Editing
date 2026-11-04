"""Register the A02 14-paragraph direct review completed by the current agent.

This records a specific completed text inspection, not an automatic ASR approval.
Raw recognition, narration, scripts and the mastered mix are never rewritten.
"""
import difflib
import json
from pathlib import Path
import audio_pipeline as ap
from storage_paths import HERE as H,LOCAL as L

def norm(t):return ''.join(c.lower() for c in t if c.isalnum())
ALIASES={'110cm':'백십센티미터','100cm':'백센티미터','10cm':'십센티미터','0cm':'영센티미터'}
def number_aliases(t):
    t=norm(t)
    for before,after in ALIASES.items():t=t.replace(before,after)
    return t

def main():
    edit=L/'edit';s=H.parents[1]/'script/grid-v1'
    files={
        'ko':s/'narration.ko.json','en':s/'narration.en.json','spoken':s/'narration.spoken-ko.json',
        'aac':edit/'final-mix.m4a','pcm':edit/'final-mix.wav','decodeReceipt':edit/'encoded-asr-input.json',
        'asrInput':edit/'encoded-audio-for-asr.wav','asr':edit/'final-mix-asr.json',
        'comparison':edit/'final-mix-text-comparison.json','source':L/'voice/narration-source.wav',
        'sourceAsr':L/'voice/whole-source-asr.json','sourceReview':H/'source-asr-review-v2.json',
        'sourceSelection':H/'source-asr-selection.json','stemReview':H/'source-stem-continuity-review.json',
        'aacReview':L/'qa/audio-v1/continuity.json','balanceReview':L/'qa/audio-v1/speech-mix-balance.json',
        'audioBuild':edit/'audio-build.json'}
    artifacts={k:ap.artifact(p) for k,p in files.items()}
    data={k:ap.read(p) for k,p in files.items() if p.suffix=='.json'}
    a=data['asr'];source_asr=data['sourceAsr'];build=data['audioBuild'];old=data['sourceReview'];comparison=data['comparison']
    assert a['inputs']['device']=='cpu' and a['cpuThreads']==4 and a['noExpectedPrompt'] and a['completeAudioSubmitted']
    assert data['decodeReceipt']['inputs']['encodedFile']==artifacts['aac']
    assert data['decodeReceipt']['inputs']['audioBuild']==artifacts['audioBuild']
    assert a['inputs']['audio']==artifacts['asrInput'] and a['audio_sha256']==artifacts['asrInput']['sha256']
    assert comparison['asrSha256']==artifacts['asr']['sha256']
    assert source_asr['audio_sha256']==artifacts['source']['sha256']=='7a050476e883079934cb48d8f1922d43152bc582b451e09c749440ea13306890'
    assert data['stemReview']['audioBuild']==data['aacReview']['audioBuild']==artifacts['audioBuild']
    assert data['aacReview']['aac']==artifacts['aac']
    assert norm(a['text'])==norm(source_asr['text'])
    cumulative=0
    for scene in build['scenes']:
        assert scene['voiceStartSample']==96000+cumulative
        cumulative+=scene['sourceSamples']
    assert cumulative==13072928
    all_lines=[(scene['id'],i,t) for scene in data['spoken']['scenes'] for i,t in enumerate(scene['lines'])]
    assert len(all_lines)==14
    raw=a['text'];normalized=norm(raw);raw_index=[i for i,c in enumerate(raw) if c.isalnum()]
    starts=[];cursor=0
    for scene,i,text in all_lines:
        anchor=norm(text)[:14];pos=normalized.find(anchor,cursor)
        assert pos>=0,(scene,i,anchor)
        starts.append(raw_index[pos]);cursor=pos+len(anchor)
    paragraphs=[];remaining=[]
    prior_by_id={p['paragraph']:p for p in old['paragraphs']}
    for k,(scene,i,expected) in enumerate(all_lines):
        pid=f'{scene}-p{i+1:02}'
        recognized=raw[starts[k]:starts[k+1] if k+1<len(starts) else len(raw)].strip()
        x=number_aliases(expected);y=number_aliases(recognized)
        changes=[{'kind':op,'expected':x[a0:a1],'recognized':y[b0:b1],'expectedNormalizedRange':[a0,a1],'recognizedNormalizedRange':[b0,b1]} for op,a0,a1,b0,b1 in difflib.SequenceMatcher(None,x,y,autojunk=False).get_opcodes() if op!='equal']
        prior=prior_by_id[pid]
        assert [{k:d[k] for k in ('kind','expected','recognized')} for d in changes]==prior['nonNumericDifferences']
        remaining.extend({'paragraph':pid,**d} for d in changes)
        paragraphs.append({'id':pid,'scene':scene,'line':i,'canonicalSpokenText':expected,'finalRecognizedText':recognized,'fullCanonicalAndFinalRecognizedTextCompared':True,'referenceTimingFromSourceWords':[prior['sourceStartSeconds']+2,prior['sourceEndSeconds']+2],'finalAsrTimestampUsedForParagraphTiming':False,'allSentencesPresentInCorrectSequence':True,'missingCoreSentenceFound':False,'duplicatedSentenceFound':False,'meaningRetained':prior['meaningRetained'],'differencesAfterExplicitNumericAliases':changes,'reviewNote':'Direct full-paragraph comparison completed. Only the previously documented Korean orthographic recognition differences remain.' if changes else 'Direct full-paragraph comparison completed; whitespace, punctuation and explicitly listed numeric spelling equivalences do not change the spoken content.'})
    assert len(remaining)==4
    stem=data['stemReview'];encoded=data['aacReview'];balance=data['balanceReview']
    segments=a['segments'];segment_times=[x['timestamp'] for x in segments]
    assert all(t[0] is not None and t[1] is not None and 0<=t[0]<t[1]<=build['duration'] for t in segment_times)
    assert all(segment_times[i][1]<=segment_times[i+1][0] for i in range(len(segments)-1))
    assert norm(''.join(x['text'] for x in segments))==norm(raw)
    record={
        'schemaVersion':1,'episode':'A02','revision':'grid-v1','status':'full-text-review-complete-technical-continuity-passed-final-listening-pending',
        'reviewer':'/root/a02_callouts_resume','reviewedAt':ap.now(),'clientDateKst':'2026-11-04',
        'scope':'Complete current final AAC recognized once on CPU with 4 threads, then all 14 canonical paragraphs and the entire raw recognized text read and compared. This is textual/signal QA, not listening approval.',
        'fullTextDirectReview':True,'all14ParagraphsRead':True,'allCoreSentencesFound':True,
        'newRecognitionPassRunByReviewer':True,'newTtsGenerated':False,'rawRecognitionModified':False,'sourceOrMixOrScriptsModified':False,
        'evidence':list(artifacts.values()),
        'hashChainChecks':{'finalM4aMatchesAsrDecodeReceipt':True,'decodedAsrInputMatchesRecognition':True,'sourcePcmMatchesReviewedSourceAsr':True,'audioBuildMatchesStemAndAacContinuity':True,'continuousSourceOffsetsPreservedAfterTwoSecondBranding':True,'currentSourceAndFinalRecognizedTextEqualAfterWhitespacePunctuationNormalization':True},
        'paragraphs':paragraphs,
        'recognitionIssues':[{'type':'coarse-final-asr-segment-timestamps','segmentCount':len(segments),'timestampPairs':segment_times,'maximumSegmentSeconds':max(t[1]-t[0] for t in segment_times),'allValidAndNonOverlapping':True,'allSegmentTextMatchesFullText':True,'reason':'The recognizer groups much of the body into long segments and starts the first group during branding. These are not word-level caption or shot cues.','disposition':'Keep existing reviewed complete source-word timings and the continuous +2-second offset. Final recognition verifies full text only.'}],
        'comparisonMethod':{'numericSpellingAliases':ALIASES,'numericOccurrenceCount':6,'removedCharacters':'Whitespace and punctuation for diagnostic comparison only','rawNormalizedSimilarityDiagnosticOnly':comparison['normalizedSimilarity'],'remainingCharacterSubstitutions':remaining,'normalizedSourceAndFinalTextEqual':True,'rawRecognitionOrCaptionTextRewritten':False,'scoreUsedAsApproval':False},
        'differenceReview':{'orthographicAmbiguities':[{'expected':'같게','recognized':'갖게','globalSeconds':[146.8,147.12],'assessment':'Final-consonant spelling ambiguity; intended same-target condition retained.'},{'expected':'어깨의','recognized':'어깨에','globalSeconds':[150.58,150.98],'assessment':'의/에 recognition spelling ambiguity; same complete sentence as source ASR.'},{'expected':'맡던','recognized':'맞던','globalSeconds':[201.16,201.52],'assessment':'Final-consonant spelling ambiguity before 던; intended role retained.'},{'expected':'다음의','recognized':'다음에','globalSeconds':[256.42,256.86],'assessment':'의/에 recognition spelling ambiguity; largest-to-smaller sequence retained.'}],'missingCoreSentences':[],'unexpectedGreeting':False,'repeatedSentences':[],'numericSequence':'0cm → target100cm;110cm overshoot →100cm;excess10cm. All six numeric mentions retained.','unresolvedActualAudioDefectsEstablished':[],'pronunciationCertified':False},
        'continuityEvidence':{'sourceToStem':{'status':stem['status'],'speechActiveWindows':len(stem['records']),'flags':len(stem['remainingFlags']),'minimumSampleCorrelation':min(x['correlation'] for x in stem['records']),'minimumDeltaDb':min(x['differenceDb'] for x in stem['records']),'maximumDeltaDb':max(x['differenceDb'] for x in stem['records']),'roughFlagsResolvedByIdenticalSpeechMask':len(stem['wholeWindowDiagnosticReview'])},'pcmToFinalAac':{'status':encoded['status'],'oneSecondWindows':len(encoded['rows']),'flags':len(encoded['flags']),'pcmSamples':encoded['expectedPcmSamples'],'decodedSamples':encoded['decodedAacSamples'],'integratedLufs':float(encoded['loudness']['input_i']),'truePeakDbtp':float(encoded['loudness']['input_tp']),'bgmActiveBodySecondShare':encoded['bgmActiveBodySecondShare']},'speechBalance':{'status':balance['status'],'speechActiveWindows':len(balance['windows']),'diagnosticThresholdVoiceOverBackgroundDb':balance['diagnosticThresholdVoiceOverBackgroundDb'],'flagCount':len(balance['flags']),'minimumVoiceOverBackgroundDb':balance['minimumVoiceOverBackgroundDb'],'flaggedTimelineStartSeconds':[r['timelineStart'] for r in balance['flags']],'interpretation':'Short low-level voice intervals are listening targets, not confirmed masking or a reason to regenerate narration. No scalar RMS threshold establishes intelligibility.'}},
        'finalAudioDuration':build['duration'],'humanListening':False,'pendingFinalListening':True,'userFinalReview':False,
        'listeningTargets':[{'globalSeconds':[max(2,r['timelineStart']-.75),r['timelineStart']+1.75],'reason':'Very quiet speech-window overlaps BGM; confirm natural word endings and musical balance. Signal measurement does not establish an audible fault.','voiceOverBackgroundDb':r['voiceOverBackgroundDb']} for r in balance['flags'] if r['voiceOverBackgroundDb']<0]+[{'globalSeconds':[220.5,245],'reason':'Check natural numeric/unit pronunciation through the complete 0→100→110→100 /10cm example.'},{'globalSeconds':[260,274.366667],'reason':'Check conclusion and ending cadence into the member page.'}],
        'limits':['No actual listening or human final review is claimed.','Source-to-stem and PCM-to-AAC comparisons establish signal continuity, not naturalness, voice identity quality or perceptual masking.','All raw recognizer artifacts and prior source-recognition failure records are preserved.','Final captions and picture synchronization are reviewed separately.'],
        'finalVisualCaptionReview':'Owned by parent; this report does not certify caption pixels or video motion.'}
    ap.save(H/'final-mix-asr-review.json',record)
    print(json.dumps({'status':record['status'],'paragraphs':len(paragraphs),'sourceFinalNormalizedTextEqual':True,'remainingOrthographicSubstitutions':len(remaining),'evidence':artifacts['aac'],'review':ap.artifact(H/'final-mix-asr-review.json'),'humanListening':False},ensure_ascii=False))

if __name__=='__main__':main()

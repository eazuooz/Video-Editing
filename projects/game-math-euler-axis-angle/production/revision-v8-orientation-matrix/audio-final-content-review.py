"""Record the actual whole-final76paragraph direct text audit and resolutions.

This records an audio-agent review, never a claim of human listening.
"""
from pathlib import Path
import importlib.util,json
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_final_content_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
NOTES={
 'm01':'Direction/orientation, vector lacks roll/bank, three independent changes versus nine entries retained. First recognized 게임에서 has0–2.4s timestamp crossing the branding boundary and was placed outside the scene by midpoint grouping; raw whole text retains it. Source-placement sample proof puts actual narration at2s.',
 'm02':'Reference/identity/home, state versus angular displacement, Y-up/east+X/north+Z, quarterturnaboutY and camera-up all retained. Raw repeated clauses occur at backward decoder chunk clocks,not added source PCM.',
 'm03':'Object-attached phrase 물체에 붙어 is now recognized correctly; unitorthogonal basis, co-origin upright/world-parallel frame, translation separated and row-vector-left convention retained.',
 'm04':'Critical signs(+X/-Z and firstrow0,0,-1) omitted or miscoded by wholeASR are all recovered from the two independent complete actualAAC paragraphs. Other rows0,1,0 and1,0,0,point(1,0,2)→(2,0,-1), weightedrowcombination and samephysicalpoint are retained. Do not treat wholeASR comma/axis spellings as measured audio defects.',
 'm05':'Actual wholefinal explicitly recognizes transposed inverse coordinate(2,0,-1)→(1,0,2). The earlier -1을/-2를 surface-homophone caution is resolved as a recognition ambiguity,without changing that original take. Bothspaces, pure-rotation conditions, stretch counterexample and conventions retained.',
 'm06':'3×3linear,4×4homogeneous,4×3affine, bothdirections,targetvectorversusposition,stateversuscommand, API responsibility and limitations retained. 늘이기/느리기,아핀/앞인,좌표/자표,각변위/각변이 remain spelling/pronunciation recognition cautions,not proved audio defects. The repeated finalclause has a backward decoder clock.',
 'm07':'Selected scoped pronunciation alias is directly recognized0.5 in candidate,changedscene and actualwholeAAC; display1/2 is exactly equal. Deictic 이칸 is now correctly recognized. Projection/dot product, unitlength assumption, cosine cases, directioncosinematrix and m11=0/m22=1 retained.',
 'm08':'Allnine dotproducts, P/Q/Rprime notderivatives, common orthonormal coordinates, rows/columns duality, general-linear-versus-orthogonal limit and column-vector-versus-memory-layout distinction retained. 전치/전체 spelling remains an unconfirmed pronunciation caution; canonical source/captions and explicit transpose definition inm05 remain intact.',
 'm09':'A→B→C matchingframes, rowproduct order,twoYquarterturns,noncommutativity and inverseorder retained. 세계/3개 recognized spelling varies across contexts; independentoriginal paragraph recognizes 세계. The 바깥으로 clause is still not independently resolved from ASR; preserve original approvedPCM and flag for actuallistening,not a new codec omission.',
 'm10':'Allvalues directlyread and retained:15parts×15/s=225/s;32bit=4B;9×4=36B;8100B/s;3×4=12B;2700B/s;5400B/s×30s=162000B=decimal162KB. Persecond notperframe, rawpose-only notcompressedfilesize, renderfps notsamplefrequency caveats retained.',
 'm11':'Nineentries versus3DOF, threeunit+threeorthogonality continuousconstraints, dotself1/dotcross0,det+1rotation/-1reflection all retained. Negative sign in00-1 exists in raw text. A repeated opener is a backward-clock recognition artifact.',
 'm12':'Stretchdiag(2,1,1), shear/reflection/projection distinction, mocap/conversionerrors, frameinterpretation, floatcreep and exaggeratedillustration disclaimer, reorthonormalizationbeyondindependentnormalization, reflection/tolerance/damageddata limits all retained. 일에서/이래서 is a phonetic recognition caution; no arbitrary numeric mapping.',
 'm13':'Full summary retains axes/rows/columns/dotcosine/conversions/composition/inverse/cost/validity/creep and one-row reading task. 전치/전체 and 대신자세/대체 are retained as unconfirmed pronunciation cautions rather than hidden substitutions; exact canonicalKO/EN display remains approved.'}
CAUTIONS={('m06',1):'Canonical term spelling ambiguity:동차좌표/아핀 and 늘이기;actual pronunciation listening pending.',
 ('m06',4):'각변위/각변이 recognition uncertainty;term explicitly defined earlier.',('m08',7):'전치/전체 recognition uncertainty.',
 ('m09',2):'세계/3개 variable ASR orthography; independentoriginal context recognizes세계.',('m09',7):'바깥으로 clause ASR omission remains unconfirmed;actual full-clause listening pending.',
 ('m12',4):'일에서/이래서 phonetic recognition ambiguity.',('m13',3):'전치/전체 recognition uncertainty.',('m13',4):'대신자세/대체 recognition uncertainty.'}
def main():
 c.validate();selected=c.read(H/'audio-final-input.json');master=c.R/selected['master'];assert c.sha(master)==selected['masterSha256']
 asrfile=c.O/'final-aac-asr.json';asr=c.read(asrfile);viewfile=c.O/'final-transcript-view.json';view=c.read(viewfile);levelsfile=c.O/'final-aac-level-review.json';levels=c.read(levelsfile)
 assert asr['masterSha256']==view['masterSha256']==levels['masterSha256']==selected['masterSha256'];assert asr['wholeFinalRecognitionCount']==1 and levels['actualFinalMasterBindingComplete']
 contextfile=c.O/'final-context-review.json';context=c.read(contextfile);assert context['masterSha256']==selected['masterSha256'];ctx={r['line']:r for r in context['paragraphs']}
 assert len(ctx)==2 and '플러스' in ctx[1]['text']and '마이너스' in ctx[1]['text']and '마이너스 1' in ctx[2]['text']
 sourcefile=c.O/'source-content-review.json';source=c.read(sourcefile);paragraphs=[]
 for row in view['paragraphs']:
  row=dict(row);sid,line=row['scene'],row['line'];row['directFullTextReview']='Complete rawscene text read directly against all76 approved paragraphs; useful claim order/conditions/examples checked.'
  row['finalContentAssessment']='Useful claim retained; ASR orthography is not a phoneme/listening proof.'
  if(sid,line)in CAUTIONS:row['remainingRecognitionOrPronunciationCaution']=CAUTIONS[(sid,line)]
  if sid=='m04'and line in ctx:
   row['actualCompleteContextAsr']=dict(file=c.rel(c.O/'final-context'/f'm04.L{line:02}.json'),text=ctx[line]['text'],review='Directly read;all expected axes/matrix signs recovered.');row['finalContentAssessment']='Critical axes/signs independently recovered from actualAAC completeparagraph; no source/mix edit.'
  if(sid,line)==('m05',3):row['finalContentAssessment']='ActualwholeAAC recognizes2,0,minus1 correctly; previous surface-homophone ASRwarning resolved without retake.'
  if(sid,line)==('m07',2):row['finalContentAssessment']='ActualwholeAAC recognizes0.5; exact scoped spoken equivalent of approveddisplay1/2.'
  paragraphs.append(row)
 assert len(paragraphs)==76 and all(r['actualWordCount']>0 for r in paragraphs)
 sources=c.read(c.O/'source-ready.json');execution=c.read(c.O/'final-aac-asr-execution.json');ctx_execution=c.read(c.O/'final-context-execution.json');assert execution['returnCode']==ctx_execution['returnCode']==0
 resolution='Former source-stage math ambiguity was resolved by the explicitm07.L02 1/2=0.5 pronunciation alias; laterrecognition recovers m03 attachment andm05 minus1, independent m09 context recovers worldspace, and two actualAAC m04 paragraphs recover the critical axes/signs. Remaining lexical/phonology cautions are carried into actuallistening,not silently normalized or labeled heard.'
 report=dict(revision='orientation-matrix-v8',master=selected['master'],masterSha256=selected['masterSha256'],approvedScriptSha256=c.APPROVED,
  verdict='TECHNICAL_AUDIO_INTEGRITY_PASS;usefullearningclaimsretained;SUBJECTIVE_LISTENING_PENDING',
  inputs=dict(finalInputSha256=c.sha(H/'audio-final-input.json'),wholeFinalAsrSha256=c.sha(asrfile),finalTranscriptViewSha256=c.sha(viewfile),actualLevelBindingSha256=c.sha(levelsfile),
   actualCompleteContextSha256=c.sha(contextfile),sourceContentReviewSha256=c.sha(sourcefile),sourceReadySha256=c.sha(c.O/'source-ready.json'),implementationSha256=c.sha(Path(__file__))),
  wholeFinalRecognizerInvocations=1,additionalActualAacCompleteContexts=2,automaticExpectedPrompt=False,sceneCount=13,paragraphCount=76,
  completeRawWholeTextRead=True,all76ParagraphsDirectlyCompared=True,all76HaveActualFinalAacWordEvidence=True,
  scenes=[dict(scene=s['id'],range=s['range'],directRead=True,notes=NOTES[s['id']])for s in view['scenes']],paragraphs=paragraphs,
  criticalFractionAndMatrixSignsResolved=True,previousPendingResolution=resolution,
  preservedHistoricalPendingFields='Source-stage/ASR-cache pending labels are preserved as phase history. This report is their direct-text/critical-sign resolution,except explicitly retained auditory/phonology cautions. It does not rewrite frozen sourceReady or rawrecognizer caches.',
  recognizedDecoderClockArtifacts=view['derivedClockRestartEvents'],rawAsrAndAllContextsPreserved=True,confirmedNewCodecSpeechDropOrLoop=False,
  levelVerdict=dict(actualAacLufs=levels['encodedMeasurement']['input_i'],actualAacTruePeakDbtp=levels['encodedMeasurement']['input_tp'],
   sampleShift=levels['measuredVoicedSampleShift'],decodedFullScaleSamples=levels['decodedSamplesAtOrAboveFullScale'],encoded400msTransferCandidates=levels['encodedTransferCandidateWindows'],
   exactMeasuredAacPayloadAndClockReused=levels['actualFinalMasterBindingComplete'],focusReport=c.rel(c.O/'measured-mix-focus-review.json'),focusReportSha256=c.sha(c.O/'measured-mix-focus-review.json')),
  actualAacPacketPayloadSha256=asr['aacPacketPayloadSha256'],sourceSpeed=1,addedBgm=False,sourceOrMixChangedDuringFinalQa=False,
  limitations=['A transcript/RMS match is not subjective listening. Natural pronunciation,breathing,sentence joins and actual audiovisual teachingpace remain for human review.',
   'Canonical-caption spelling is unchanged. 전치/전체, someaffineterm spellings and the m09/m13 lexical clauses remain actuallistening cautions; no unverified source replacements were made.',
   'No unseen detector confidence, voice separation, factual game coordinate or audible-quality score is invented.'],
  humanWholeListening='pending',humanReviewOfCurrentMaster='pending',actualAudiovisualPace='pending',platformMutation=False,automaticNextVideo=False)
 c.save(c.O/'final-aac-content-review.json',report)
 print(json.dumps(dict(masterSha256=selected['masterSha256'],verdict=report['verdict'],paragraphs=76,wholeAsr=1,extraCompleteContexts=2,levelBinding='actualcurrentmaster exact',humanListening='pending'),ensure_ascii=False))
if __name__=='__main__':main()

"""Record completed direct review; machine checks never stand in for listening."""
from pathlib import Path
import datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[4];V=Path(__file__).resolve().parent;P=R/'projects/avoid-game-comparisons';O=P/'production/local/reference-preserving-v2/edit';Q=O/'qa'
assert '--direct-review-complete' in sys.argv
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(p):return p.relative_to(R).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(V/'edit-plan.json');integrity=read(Q/'integrity.json');pixels=read(Q/'changed-pixels.json');proof=read(O/'retained-range-proof.json');audio=read(Q/'audio-continuity.json');levels=read(Q/'encoded-loudness.json');asr=read(O/'final-mix-text-comparison.json')
assert all(r['fullDecodePassed'] and r['ptsMonotonicAndUniform'] for r in integrity['outputs'])
assert integrity['ratioRoundingErrorFrames']==0 and proof['unchangedCutFiles']==22
assert set(proof['changedCuts'])=={'cut00.mp4','cut12.mp4','cut17.mp4','cut25.mp4'}
assert pixels['currentCaptionedSha256']==next(r['sha256'] for r in integrity['outputs'] if r['kind']=='captioned')
assert not audio['flaggedVoiceTransferWindows'] and float(levels['input_tp'])<=-1.5
ledger=read(V/'review-ledger.json');ledger['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
ledger['captionTiming']['actualFinalPixels']='passed;115 cues, fixed layout, all retained and changed ranges directly read'
ledger['visualQA'].update(completeFinalPixels='passed-direct-review',movingAnnotations='passed-direct-review; tracked actual targets and cut clearing checked',firstPassSamplesDirectlyReviewed=193,firstPassContactSheets=17,changedSamplesDirectlyReviewed=pixels['sampleCount'],changedContactSheets=pixels['sheets'],changedCutIds=['cut00','cut12','cut17','cut25'],retainedCutFiles=22,retainedRangeProof=rel(O/'retained-range-proof.json'),firstPassIndex=rel(O/'first-pass/qa/pixel-sample-index.json'),changedIndex=rel(Q/'changed-pixel-index.json'),repairs=proof['findingsRepaired'],mobileReview='375px current captioned gameplay and diagrams checked in browser; source aspect and caption band retained',coverageNote='Every caption/cut covered by direct final-frame review; moving diagrams/marks reviewed through sampled progression and playback. No claim that every encoded frame was manually watched.')
if proof.get('staticHold'):
 proof['staticHold']['finalOnlyChangedCutReview']='passed;26 current captioned samples and both joins directly reviewed'
 ledger['visualQA']['priorChanged108SamplesReview']={'samples':108,'sheets':9,'index':rel(O/'before-static-hold/qa/changed-pixel-index.json'),'passedCuts':['cut00','cut12','cut17'],'finding':'cut25 terminal glyph deletion repaired by holding its fully revealed diagram','sameRetainedCutCount':25}
 ledger['visualQA']['staticConclusionHold']=proof['staticHold']
ambiguous=ledger['fullNarration']['ambiguousRecognitionToRecheckInFinalMix']
if not any(r['expected']=='횡스크롤' for r in ambiguous):ambiguous.append({'scene':'07','expected':'횡스크롤','recognized':'펭스크롤','context':'New full-mix ASR spelling differs; source PCM unchanged. Canonical caption stays 횡스크롤. Final pronunciation listening pending.'})
ledger['audioQA'].update(sourcePcmPreserved=True,sourceStemEncodedLocalLevelComparison='completed-current-output; no additional mix-induced attenuation flags; source cadence requires listening',wholeEncodedMixAsr='complete-full-text-reviewed',wholeMixAsrSimilarity=asr['similarity'],wholeMixAsrReport=rel(O/'final-mix-text-comparison.json'),currentMixPasses=1,priorDifferentMixReport=rel(O/'first-pass/final-mix-text-comparison.json'),independentAmbiguousContexts=rel(O/'first-pass/qa/ambiguous'),asrMeaningReview='All12 sections retain explanation order and conclusions; minor particles/numeral transcription differ; five spelling/pronunciation cases retained for listening.',voiceGainRepair=read(O/'voice-gain-repair.json'),audioContinuityReport=rel(Q/'audio-continuity.json'),mixInducedVoiceTransferFlagCount=len(audio['flaggedVoiceTransferWindows']),sourceCadenceCandidateCount=len(audio['sustainedLocalDropCandidates']),sourceCadenceCandidates=audio['sustainedLocalDropCandidates'],maximumAdjacentSceneMedianDifferenceDb=max(abs(r['speechMedianDifferenceDb']) for r in audio['sceneJoins']),encodedIntegratedLufs=float(levels['input_i']),encodedTruePeakDbtp=float(levels['input_tp']),humanWholeListening='pending current local user review; not inferred from playback, ASR or levels',unresolvedTechnicalFlags=['Contextual listening of source cadence candidates and ambiguous pronunciation remains pending; do not treat automatic tests as full audio approval.'])
ledger['delivery'].update(currentUserReview='pending complete local captioned master',outputs=integrity['outputs'],frames=plan['totalFrames'],durationSeconds=plan['totalFrames']/60,resolution=[1920,1080],fps=60,actualFrames=plan['actualFrames'],explanationFrames=plan['explanationFrames'],ratioErrorFrames=0,integrityReport=rel(Q/'integrity.json'),captions=[{'language':lang,'sha256':sha(O/f'captions.{lang}.srt'),'cues':115} for lang in ['ko','en']],platformMutation=False)
write(V/'review-ledger.json',ledger)
pixels['status']='passed direct review of every changed contact sheet and affected motion';write(Q/'changed-pixels.json',pixels)
proof['finalChangedPixels']='passed direct review; see review-ledger.json';write(O/'retained-range-proof.json',proof)
integrity.update(changedPixels='passed-direct-review',fullAsrReview='complete-full-text-reviewed',humanWholeListening='pending');write(Q/'integrity.json',integrity)
asr['reviewStatus']='complete-full-text-reviewed; pronunciation listening remains pending';write(O/'final-mix-text-comparison.json',asr)
print('Current visual/text/integrity evidence recorded; human listening stays pending')

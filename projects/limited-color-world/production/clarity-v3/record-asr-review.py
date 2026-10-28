"""Record direct full-text comparison and the bounded decoder repair evidence."""
from pathlib import Path
import audio_pipeline as a
H=Path(__file__).resolve().parent
raw=a.NARRATION/'whole-source-asr.json';cmp=a.NARRATION/'whole-source-comparison.json'
d=a.read(raw);comparison=a.read(cmp)
window=a.NARRATION/'bounded-asr-02p01/source-window.json';bounded=a.NARRATION/'bounded-asr-02p01/asr.json';b=a.read(bounded)
expected=a.read(H/'narration.spoken-ko.json')['scenes'][1]['lines'][0]
_,norm=a.alignment_helpers();assert norm(b['text'])==norm(expected),'Bounded text is not a complete match'
lo=next(i for i,w in enumerate(d['words']) if w['text'].strip()=='빨간' and 47<w['timestamp'][0]<48)
hi=next(i for i,w in enumerate(d['words']) if w['text'].strip()=='이제' and w['timestamp'][0]>57)
indices=[i for i,w in enumerate(b['words']) if w['timestamp'][0]>=5.34]
assert indices and b['words'][indices[0]]['text'].strip()=='빨간'
a.save(a.NARRATION/'alignment-correction-review.json',{
 'sourceAsrSha256':a.sha(raw),'sourceAudioSha256':d['audio_sha256'],'fullRawTextCompared':True,
 'reason':'Direct full-script/full-ASR comparison found one decoder loop with consecutive zero-duration tokens at49.98s. A14.9s exact-PCM unprompted recheck fully matches paragraph02-p01. Retain full-ASR first sentence and replace only affected later words with independently measured bounded word timestamps. No audio or original ASR changed.',
 'replacements':[{'sourceWordStartIndex':lo,'sourceWordEndIndexExclusive':hi,'boundedAsr':a.artifact(bounded),'sourceWindow':a.artifact(window),'keepBoundedWordIndices':indices,'fullBoundedTextCompared':True,'expectedTextIsNotRecognizerPrompt':True,'timestampPolicy':'bounded measured word seconds + exact source offset42.5; no interpolated times'}],
 'humanListening':'not performed; ASR comparison is technical evidence only','fullPasses':1,'boundedPasses':1,'ttsRegeneration':False})
corrected,proof=a.reviewed_alignment_words(d,raw,d['audio_sha256'])
a.save(H/'source-comparison-review.json',{
 'audioSha256':d['audio_sha256'],'comparisonSha256':a.sha(cmp),'fullTextDirectlyCompared':True,
 'reviewer':'D25 revision agent, complete26paragraph source/recognized text plus all15 raw differences and bounded recognition text',
 'notes':'All26 paragraphs and original claim order are present. Numeric 2/4/3 vs 투/네/세 and 에/의 are recognizer spelling/particle differences. The second Puyo title 뿌옇뿌옇 remains a final pronunciation listening flag. The red/green repetition is a demonstrated full-ASR chunk decoder failure: independent unprompted bounded recognition exactly recovers the complete intended paragraph with positive word intervals. No audio regenerated or altered.',
 'alignmentCorrection':proof,'correctedAlignmentWordCount':len(corrected),'rawAsrPreserved':True,
 'pronunciationListeningFlags':['second 뿌요뿌요 title','Protanopia/Deuteranopia Korean names'],'humanListening':'pending',
 'newAsrScope':'one full source pass plus one concrete-failure bounded14.9s pass only'})
provenance=a.read(H/'runtime-provenance.json')
for r in provenance['files']:
 if r['newFile']=='audio_pipeline.py':r['newSha256']=a.sha(H/'audio_pipeline.py');r['postPreparationChange']='Strict hash-bound bounded-ASR correction support; raw whole ASR remains unchanged.'
a.save(H/'runtime-provenance.json',provenance)
print('Complete comparison and bounded word repair recorded; original voice and ASR unchanged.')

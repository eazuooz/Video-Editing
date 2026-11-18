"""Record mixed recognition without turning disagreements into speech corrections."""
from pathlib import Path
import difflib,hashlib,importlib.util,json,re
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent
C=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/innovation-openings-v181')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
spec=importlib.util.spec_from_file_location('source_words',H/'review-innovation-opening-voice-v182.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
def norm(s):return v.norm(s).replace('화면밖에길','화면밖의길').replace('예상밖에해결법','예상밖의해결법')
def main():
 out=C/'mixed-content-review-v183.json';assert not out.exists()
 rp=C/'mixed-asr-v182/0e25224ba7a178792c9e4db1/review.json';r=read(rp);by={x['task']['key']:x for x in r['results']};assert len(by)==36
 source=C/'voice/technical-voice-review-v182.json';sv=read(source);assert sv['approvedForConstantGainMix']and not sv['issues']
 cp=C/'mixed-context-v184/33cd29ec4fc499cdd4ca475a/review.json';context=read(cp);assert len(context['results'])==1
 rows=[]
 for ref,srow in zip(read(C/'all-mixes-v182.json')['mixes'],sv['rows']):
  assert pin(ref['path'])==ref;d=read(ref['path']);o=d['order'];key=f'o{o:02}';intro=by['intro-'+key];whole=by['take-'+key];join=by['join-'+key]
  assert all(x['rawRecognition'].get('text') for x in [intro,whole,join])
  for k in ['mix','baselineMix']:assert pin(d[k]['path'])==d[k]
  base=read(d['baselineMix']['path']);assert pin(base['mix']['path'])==base['mix']
  mix,sr=sf.read(d['mix']['path'],dtype='float32',always_2d=True);old,osr=sf.read(base['mix']['path'],dtype='float32',always_2d=True)
  assert sr==osr==24000 and np.array_equal(mix[d['introSamples']:],old)and not d['withinUtteranceEnvelopeChanged']and not d['processedParagraphTrend']['suspect']
  expected=srow['expected'];exact=norm(intro['rawRecognition']['text'])==norm(expected)or norm(whole['rawRecognition']['text']).startswith(norm(expected))
  uncertain=[]
  if not exact:
   assert o in [5,12]
   changed=expected.replace('지난 화면','진한 화면')if o==5 else expected.replace('레이싱','네이싱')
   assert norm(intro['rawRecognition']['text'])==norm(changed)
   assert norm(srow['recognized'])==norm(expected)
   uncertain=[dict(expected='지난 화면'if o==5 else'레이싱',mixedHypothesis='진한 화면'if o==5 else'네이싱',independentMixedCompleteUtterance=context['results'][0]['rawRecognition']['text']if o==5 else None,sourceCompleteContexts=srow['selectedCompleteContexts'],sourceContextRecognizedCorrectly=True,interpretation='Recognizer disagreement retained. No lexical alias, no claim of definitive TTS error or listening approval. Source utterance, scalar-only mixing, and literal caption retain the intended meaning.',requiresHumanListening=True)]
  last=d['captionCues'][-1]['ko'];joined=norm(join['rawRecognition']['text']);assert norm(last)in joined,(o,last,join['rawRecognition']['text'])
  rows.append(dict(order=o,slug=d['slug'],mix=ref,bodyPcmByteExactRechecked=True,mixedIntroRecognition=intro['rawRecognition']['text'],expectedNewIntro=expected,mixedIntroExactExceptDocumentedPronunciation=exact,sourceCompleteContexts=srow['selectedCompleteContexts'],recognizerDisagreements=uncertain,newBodyJoinRecognition=join['rawRecognition']['text'],newFinalClausePresentAtJoin=True,wholeMixHypothesis=whole['rawRecognition']['text'],wholeMixExpected=whole['task']['expected'],wholeMixSimilarity=difflib.SequenceMatcher(None,norm(whole['rawRecognition']['text']),norm(whole['task']['expected'])).ratio(),existingBodyRecognitionNotOverriddenByChunkBoundaryHypotheses=True,processedParagraphTrend=d['processedParagraphTrend'],backgroundMusicMedianDelta=d['medianIntroMusicMinusVoiceDb'],newContentSourceApproved=not srow['issues']))
 report=dict(allMixes=pin(C/'all-mixes-v182.json'),independentWholeIntroAndJoinAsr=pin(rp),independentMixedCompleteContext=pin(cp),sourceWholeWordReview=pin(source),rows=rows,completedBlindTasks=37,approvedForReviewRender=True,approvalScope='Technical local user-review candidate, with explicit unresolved machine-transcription disagreements on #5 and #12. Not human or listening approval.',documentedPronunciationEquivalence=dict(phrases=['화면 밖의 길 / 화면 밖에 길','예상 밖의 해결법 / 예상 밖에 해결법'],source='https://www.korean.go.kr/front/mcfaq/mcfaqView.do?mcfaq_seq=5716',rule='Possessive particle 의 permits pronunciation 에; no lexical-error alias.'),lexicalErrorAliasesAdded=False,completedJobsRepeated=False,bodyVideoRerenderAuthorized=False,actualFullListening=False,actualRealtimePlayback=False,humanApproval=False)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(dict(review=pin(out),rows=len(rows),unresolvedRecognizerDisagreements=sum(bool(x['recognizerDisagreements'])for x in rows),readyForLocalReviewRender=True)))
if __name__=='__main__':main()

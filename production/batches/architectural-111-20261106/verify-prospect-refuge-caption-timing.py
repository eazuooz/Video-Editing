"""Synthetic CPU contract tests only; mock PCM/ASR are never production speech.

No model, recognizer, controller, production media edit, GPU or real output build.
"""
import copy,hashlib,importlib.util,json,struct,tempfile,unittest,wave
from pathlib import Path
from unittest.mock import patch,MagicMock
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('prospect_caption_cpu',HERE/'build-prospect-refuge-caption-timing.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def dump(p,value):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False)+'\n',encoding='utf8');return p
def wav(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 with wave.open(str(p),'wb')as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(data)
 return dict(path=str(p),sha256=m.sha(p),pcmSHA256=hashlib.sha256(data).hexdigest(),sampleRate=24000,channels=1,sampleWidthBytes=2,frames=len(data)//2)

class CaptionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory(prefix='prospect-caption-cpu-only-');cls.root=Path(cls.tmp.name)
  cls.n,cls.componentPlan,cls.clauses,cls.anchors=m.sources();scenes=[];mapping=[];chunks=[];entries=[];payload=[];takes=[];position=0
  for g in cls.clauses['groups']:
   p=g['paragraph'];j=ord(g['id'][-1])-ord('a')+1;sid=f'p{p:03}-c{j:02}';words=g['ko'].split();frames=2400*(len(words)+1);data=struct.pack('<h',j)*frames
   info=wav(cls.root/'chunks'/(sid+'-scene.wav'),data);start=position;position+=frames;chunks.append(info);payload.append(data)
   scenes.append(dict(id=sid,lines=[g['ko']]));mapping.append(dict(paragraph=p,sceneId=sid,component=j,componentCount=sum(x['paragraph']==p for x in cls.clauses['groups']),sourceCharRange=g['koSourceCharRange'],canonicalText=g['ko']))
   entries.append(dict(scene_id=sid,text=g['ko'],start=start/24000,end=position/24000))
   observed=[dict(text=t,timestamp=[(start+480+i*2400)/24000,(start+1920+i*2400)/24000])for i,t in enumerate(words)]
   takes.append(dict(task=dict(sceneId=sid,expected=g['ko'],offsetSample=start,endSample=position),text=g['ko'],globalWords=observed))
  identity=dict(topicId='06.02',scenes=scenes);aggregate=wav(cls.root/'canonical/narration.wav',b''.join(payload));timing=dump(cls.root/'canonical/narration.timing.json',dict(sample_rate=24000,entries=entries))
  cls.voice=dict(topicId='06.02',fingerprint=m.digest(identity),identity=identity,sceneWavs=chunks,paragraphMapping=mapping,aggregateWav=aggregate,timing=m.pin(timing),output=str(cls.root))
  paragraphs=[]
  for p in range(1,26):
   group=[(t,e)for t,e,mp in zip(takes,entries,mapping)if mp['paragraph']==p];a=round(group[0][1]['start']*24000);b=round(group[-1][1]['end']*24000)
   paragraphs.append(dict(paragraph=p,sceneIds=[t['task']['sceneId']for t,e in group],startSample=a,endSample=b,start=a/24000,end=b/24000,expectedLiteral=cls.n['narrationKo'][p-1],recognizedLiteral=cls.n['narrationKo'][p-1],globalWords=[w for t,e in group for w in t['globalWords']],recognitionBasis='assembled-from-blind-component-takes'))
  cls.review=dict(voiceFingerprint=cls.voice['fingerprint'],aggregateSHA256=aggregate['sha256'],timingSHA256=m.sha(timing),takes=takes,boundaryWindows=[dict(synthetic=True)for i in range(95)],paragraphs=paragraphs,aliasesApplied=False,expectedPrompt=None,automaticSpeechPass=False)
  cls.binding=m.voice_binding(cls.voice,cls.review,cls.n)
  cls.result=m.build(cls.n,cls.clauses,cls.anchors,cls.review,cls.binding)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def sentence(self,text,words,frames=48000):
  return m.aligned_sentence(dict(sceneId='p001-c01',paragraph=1,sentenceIndexZeroBased=0,canonicalKo=text,startSample=0,endSample=frames,startFrame=0,endFrameExclusive=m.frame_from_sample(frames)),dict(task=dict(sceneId='p001-c01',expected=text,offsetSample=0,endSample=frames),text=' '.join(w['text']for w in words),globalWords=words))
 def test_full_synthetic96_25_and190_234(self):
  self.assertEqual(len(self.result['sentences']),96);self.assertEqual(len(self.result['paragraphs']),25);self.assertEqual({k:len(v)for k,v in self.result['captions'].items()},{'ko':190,'en':234})
  self.assertEqual(self.binding['rawSelectedTakes'],96);self.assertTrue(self.binding['canonicalExactConcatVerified']);self.assertFalse(self.result['automaticSpeechPass'])
 def test_full_component_envelopes_are_exact_samples(self):
  for i,s in enumerate(self.result['sentences']):
   self.assertEqual(s['startSample'],round(self.voice['timing']and self.review['takes'][i]['task']['offsetSample']));self.assertEqual(s['endSample'],self.review['takes'][i]['task']['endSample'])
  self.assertEqual(self.result['audioClock']['addedObservationHoldSamples'],0)
 def test_reordered26_groups_keep_whole_semantic_window(self):
  ids={c['groupId']for c in self.result['captions']['en']if c['translationReordered']};self.assertEqual(len(ids),26)
  for c in self.result['captions']['en']:
   if c['translationReordered']:self.assertEqual(c['semanticWindowKo']['kind'],'whole-component-reordered-translation')
 def test_asymmetric_language_counts_not_forced_equal(self):
  self.assertNotEqual(len(self.result['captions']['ko']),len(self.result['captions']['en']))
  for p in range(1,26):
   for lang,key in [('ko','narrationKo'),('en','paragraphsEn')]:self.assertEqual(' '.join(c['text']for c in self.result['captions'][lang]if c['paragraph']==p),self.n[key][p-1])
 def test_srt_plain_exact_singleline_content(self):
  text=m.base.srt(self.result['captions']['en'],'en');self.assertNotIn('<',text);self.assertNotIn('{\\',text);self.assertIn('a free plan',text);self.assertEqual(text.count(' --> '),234)
 def test_sample_frame_zero_and_half_up(self):
  self.assertEqual(m.frame_from_sample(0),0);self.assertEqual(m.frame_from_sample(199),0);self.assertEqual(m.frame_from_sample(200),1);self.assertEqual(m.frame_from_sample(400),1);self.assertEqual(m.ceil_frame(401),2)
 def test_nonfinite_sample_clock_declines(self):
  for value in(float('nan'),float('inf'),None,True):
   with self.subTest(value=value),self.assertRaises(m.Pending):m.sample(value)
 def test_zero_actual_word_interval_declines(self):
  with self.assertRaisesRegex(m.Pending,'Zero'):self.sentence('머리 지점',[dict(text='머리',timestamp=[.1,.1]),dict(text='지점',timestamp=[.2,.3])])
 def test_unknown_word_clock_declines(self):
  with self.assertRaisesRegex(m.Pending,'Missing'):self.sentence('머리 지점',[dict(text='머리',timestamp=[None,.1]),dict(text='지점',timestamp=[.2,.3])])
 def test_backward_word_clock_declines(self):
  with self.assertRaisesRegex(m.Pending,'backward'):self.sentence('머리 지점',[dict(text='머리',timestamp=[.3,.4]),dict(text='지점',timestamp=[.1,.2])])
 def test_within_recognizer_word_split_never_interpolates(self):
  s=self.sentence('머리 지점',[dict(text='머리 지점',timestamp=[.1,.7])]);self.assertTrue(s['unsupportedWordBoundaries'])
  with self.assertRaisesRegex(m.Pending,'No actual'):m.resolve_literal_start(s,'지점')
 def test_actual_word_gap_midpoint_is_not_text_ratio(self):
  s=self.sentence('아주긴머리표현 점',[dict(text='아주긴머리표현',timestamp=[.1,.2]),dict(text='점',timestamp=[1.,1.1])]);b=m.resolve_literal_start(s,'점');self.assertEqual(b['sample'],14400);self.assertEqual(b['method'],'actual adjacent blind-ASR word offset/onset midpoint')
 def test_word_order_reversal_not_guessed_from_english(self):
  a=self.anchors['groups'][0];self.assertTrue(a['translationReordered']);cue=next(c for c in self.result['captions']['en']if c['id']=='P1a-en1');self.assertEqual(cue['semanticWindowKo']['text'],a['ko']);self.assertIn('not English ASR',cue['timingBasis'])
 def test_real_literal_difference_retained_without_alias(self):
  s=self.sentence('머리 지점',[dict(text='머리',timestamp=[.1,.2]),dict(text='차이',timestamp=[.3,.4])]);self.assertTrue(s['alignmentReview']['comparison']['characterDifferences']);self.assertFalse(s['alignmentReview']['aliasesApplied']);self.assertFalse(s['alignmentReview']['automaticSpeechPass'])
 def test_missing_internal_literal_anchor_declines(self):
  s=self.sentence('머리 지점',[dict(text='머리',timestamp=[.1,.2]),dict(text='차이',timestamp=[.3,.4])])
  with self.assertRaises(m.Pending):m.resolve_literal_start(s,'지점')
 def test_nonunique_or_partial_word_interval_declines(self):
  s=self.sentence('머리는 지점',[dict(text='머리는',timestamp=[.1,.2]),dict(text='지점',timestamp=[.3,.4])])
  with self.assertRaises(m.Pending):m.resolve_literal_interval(s,'머리')
  with self.assertRaises(m.Pending):m.resolve_literal_start(s,'없는 말')
 def test_subframe_positive_samples_not_forced_one_frame(self):
  normal,bold,_=m.base.base.fonts();g=self.clauses['groups'][0];c=g['koCues'][0]
  with self.assertRaisesRegex(m.Pending,'positive actual frame'):m.display_cue(c,'ko',g,0,0,normal,bold)
 def test_changed_pcm_hash_declines(self):
  v=copy.deepcopy(self.voice);v['sceneWavs'][0]['pcmSHA256']='0'*64
  with self.assertRaisesRegex(m.Pending,'PCM changed'):m.voice_binding(v,self.review,self.n)
 def test_changed_component_order_declines(self):
  v=copy.deepcopy(self.voice);v['paragraphMapping'][0],v['paragraphMapping'][1]=v['paragraphMapping'][1],v['paragraphMapping'][0]
  with self.assertRaisesRegex(m.Pending,'order'):m.voice_binding(v,self.review,self.n)
 def test_changed_paragraph_seconds_clock_declines(self):
  r=copy.deepcopy(self.review);r['paragraphs'][0]['end']+=.1
  with self.assertRaisesRegex(m.Pending,'envelopes'):m.voice_binding(self.voice,r,self.n)
 def test_more_than_one_emphasis_declines(self):
  normal,bold,_=m.base.base.fonts();g=self.clauses['groups'][0];c=copy.deepcopy(g['koCues'][0]);c['emphasis']=[dict(start=0,end=1,role='term'),dict(start=2,end=3,role='result')]
  with self.assertRaisesRegex(m.Pending,'one authored'):m.display_cue(c,'ko',g,0,10,normal,bold)
 def test_width_overflow_never_shrinks(self):
  normal,bold,_=m.base.base.fonts();g=self.clauses['groups'][0];c=dict(id='bad',text='가'*50,lines=['가'*50],emphasis=[])
  with self.assertRaisesRegex(m.Pending,'exceeds800'):m.display_cue(c,'ko',g,0,10,normal,bold)
 def test_changed_translated_anchor_text_declines(self):
  a=copy.deepcopy(self.anchors);a['groups'][0]['cues'][0]['enText']='changed'
  with self.assertRaisesRegex(m.Pending,'literal semantic'):m.build(self.n,self.clauses,a,self.review,self.binding)
 def test_no_missing_review_summary_write(self):
  qa=MagicMock();qa.prepare_job.return_value=dict(output=str(self.root/'missingreview'),identity=dict(tasks=[{}]));qa.summary.side_effect=AssertionError('must not write absentreview')
  with patch.object(m,'asr_factory',return_value=qa),self.assertRaisesRegex(m.Pending,'not available'):m.verified_asr_review(self.root/'missingreview/review.json')
  qa.summary.assert_not_called()
 def test_changed_cache_review_declines(self):
  file=dump(self.root/'mockreview/review.json',dict(aliasesApplied=False,expectedPrompt=None,automaticSpeechPass=False));qa=MagicMock();qa.prepare_job.return_value=dict(output=str(file.parent),identity=dict(tasks=[{}]));qa.cached.return_value={};qa.summary.return_value={'changed':True}
  with patch.object(m,'asr_factory',return_value=qa),self.assertRaisesRegex(m.Pending,'differs'):m.verified_asr_review(file)
 def test_missing_cache_never_calls_summary(self):
  file=dump(self.root/'missingcache/review.json',{});qa=MagicMock();qa.prepare_job.return_value=dict(output=str(file.parent),identity=dict(tasks=[{}]));qa.cached.return_value=None
  with patch.object(m,'asr_factory',return_value=qa),self.assertRaisesRegex(m.Pending,'Missing independent'):m.verified_asr_review(file)
  qa.summary.assert_not_called()
 def test_scalar_clock_requires_actual_matching_proof(self):
  with self.assertRaisesRegex(m.Pending,'proof required'):m.validate_scalar_clock_reuse(None,None,self.binding)
 def supported_fixture(self):
  canonical='조망 공간을 건넌 뒤에는 새 자리에서 다시 주변을 읽죠.';raw=dict(sha256='a'*64,pcmSHA256='b'*64,sampleRate=24000,frames=78720)
  sentence=dict(sceneId='p014-c03',canonicalKo=canonical,startSample=24000,endSample=102720,startFrame=60,endFrameExclusive=257,rawWav=raw)
  text=[' 조만',' 공간을',' 건넌',' 뒤에는',' 세자리에서',' 다시',' 주변을',' 읽죠.'];edges=[.02,.24,.72,1.04,1.5,2.22,2.48,2.92,3.18];words=[dict(text=t,timestamp=[1+edges[i],1+edges[i+1]])for i,t in enumerate(text)]
  take=dict(task=dict(sceneId='p014-c03',expected=canonical,offsetSample=24000,endSample=102720),text=''.join(text),globalWords=words)
  support=dict(id='synthetic-boundary',sceneId='p014-c03',canonicalKo=canonical,canonicalCharOffsets=[13,14],canonicalLeftWord='뒤에는',rawWav=raw,recognizedWordIndex=3,recognizedWordLiteral=' 뒤에는',recognizedWordLocalSeconds=[1.04,1.5],boundaryRawSampleInTake=36000,supportProof=dict(path='synthetic-display-proof.json',sha256='c'*64))
  return sentence,take,support
 def test_explicit_exact_left_word_end_resolves_without_alias(self):
  sentence,take,support=self.supported_fixture();aligned=m.aligned_sentence(sentence,take,support)
  self.assertEqual(m.char_boundary(aligned,13)['sample'],60000);self.assertEqual(m.char_boundary(aligned,14)['sample'],60000)
  self.assertEqual(aligned['alignmentReview']['recognizedLiteral'],take['text']);self.assertTrue(aligned['alignmentReview']['alignmentDifferences']);self.assertFalse(aligned['alignmentReview']['aliasesApplied'])
 def test_no_proof_keeps_same_ambiguous_boundary_pending(self):
  sentence,take,_=self.supported_fixture();aligned=m.aligned_sentence(sentence,take)
  with self.assertRaises(m.Pending):m.char_boundary(aligned,13)
 def test_explicit_boundary_wrong_pcm_rejected(self):
  sentence,take,support=self.supported_fixture();support=copy.deepcopy(support);support['rawWav']['pcmSHA256']='0'*64
  with self.assertRaisesRegex(m.Pending,'raw source'):m.aligned_sentence(sentence,take,support)
 def test_explicit_boundary_wrong_current_word_rejected(self):
  sentence,take,support=self.supported_fixture();take['globalWords'][3]['text']=' 뒤에도';take['text']=''.join(w['text']for w in take['globalWords'])
  with self.assertRaisesRegex(m.Pending,'word literal'):m.aligned_sentence(sentence,take,support)
 def test_explicit_boundary_one_sample_timestamp_change_rejected(self):
  sentence,take,support=self.supported_fixture();take['globalWords'][3]['timestamp'][1]+=1/24000
  with self.assertRaisesRegex(m.Pending,'next onset'):m.aligned_sentence(sentence,take,support)
 def test_explicit_boundary_one_sample_next_onset_change_rejected(self):
  sentence,take,support=self.supported_fixture();take['globalWords'][4]['timestamp'][0]+=1/24000
  with self.assertRaisesRegex(m.Pending,'next onset'):m.aligned_sentence(sentence,take,support)
 def test_explicit_boundary_cannot_move_to_other_char_scope(self):
  sentence,take,support=self.supported_fixture();support['canonicalCharOffsets']=[12,14]
  with self.assertRaisesRegex(m.Pending,'edge moved'):m.aligned_sentence(sentence,take,support)
 def test_explicit_boundary_proof_source_hash_required(self):
  with patch.object(m,'BOUNDARY_SUPPORT_SHA256','0'*64),self.assertRaisesRegex(m.Pending,'proof changed'):m.boundary_support(self.binding)
 def test_optional_absent_proof_never_invents_fallback(self):
  with patch.object(m,'BOUNDARY_SUPPORT',self.root/'absent-proof.json'):self.assertEqual(m.boundary_support(self.binding),{})
 def test_actual_float_header_rejects_metadata_only_clock(self):
  path=self.root/'short-float.wav';payload=b'\x00'*32;path.write_bytes(b'RIFF'+struct.pack('<I',36+len(payload))+b'WAVEfmt '+struct.pack('<IHHIIHH',16,3,2,48000,384000,8,32)+b'data'+struct.pack('<I',len(payload))+payload)
  self.assertEqual(m.float_wav_clock(path),(48000,2,4,'FLOAT'))
  path.write_bytes(path.read_bytes()[:-1])
  with self.assertRaisesRegex(m.Pending,'complete RIFF'):m.float_wav_clock(path)
 def test_changed_mix_pin_and_clock_reuse_decline(self):
  audio=self.root/'mockaudio/audio-build.json';mix=self.root/'mockaudio/mix.wav';mix.parent.mkdir();payload=b'\x00'*(self.binding['totalSamples']*2*8);mix.write_bytes(b'RIFF'+struct.pack('<I',36+len(payload))+b'WAVEfmt '+struct.pack('<IHHIIHH',16,3,2,48000,384000,8,32)+b'data'+struct.pack('<I',len(payload))+payload);descriptor=dict(path=str(mix),sha256=m.sha(mix),sampleRate=48000,channels=2,frames=self.binding['totalSamples']*2,subtype='FLOAT');dump(audio,dict(schemaVersion='06-02-audio-build-v1',topicId='06.02',rawVoice=self.binding['aggregate'],canonicalTiming=self.binding['timing'],rawVoiceFingerprint=self.binding['voiceFingerprint'],selectedComponentCount=96,voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0,wordBoundariesShifted=False,pcmLineage=dict(voiceOffsetSamples=0,rawToPreparedSampleRatio=[2,1],voiceSpeed=1),mixWav=descriptor));proof=dict(schemaVersion='06.02-scalar-clock-reuse-proof-v1',topicId='06.02',acceptedForTimingReuse=True,audioBuild=m.pin(audio),rawAggregate=self.binding['aggregate'],rawTiming=self.binding['timing'],voiceFingerprint=self.binding['voiceFingerprint'],trimmedSamples=0,insertedSamples=0,speechSpeed=1,offsetRawSamples=0,scalarOnly=True,numericalClockVerified=True,components=[dict(sceneId=s['sceneId'],rawSampleRange=[s['startSample'],s['endSample']],preparedSampleRange=[s['startSample']*2,s['endSample']*2],constantGainDb=1.5)for s in self.binding['sentences']],mixWav=descriptor,supportingProofs=[m.pin(audio)]);file=dump(audio.parent/'proof.json',proof)
  self.assertTrue(m.validate_scalar_clock_reuse(audio,file,self.binding)['mixedAudioTimingAccepted']);mix.write_bytes(b'changed')
  with self.assertRaises(m.Pending):m.validate_scalar_clock_reuse(audio,file,self.binding)
 def test_default_readiness_does_not_call_model_or_write(self):
  with patch.object(m,'VOICE',self.root/'absent.json'),patch.object(m,'write_outputs')as write,patch.object(m,'asr_factory')as factory,patch('sys.argv',['caption']):m.main()
  write.assert_not_called();factory.assert_not_called()

if __name__=='__main__':unittest.main(verbosity=2)

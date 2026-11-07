"""Synthetic103raw/96logical clock tests only; no real media/model jobs."""
import copy,hashlib,importlib.util,io,json,struct,tempfile,unittest,wave
from pathlib import Path
from unittest.mock import patch,MagicMock
HERE=Path(__file__).resolve().parent
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
m=load('prospect_caption103_cpu',HERE/'build-prospect-refuge-caption-timing-v2.py')
fixture=load('prospect_caption103_source_fixture',HERE/'verify-prospect-refuge-voice-qa-v2.py')
def dump(p,value):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False)+'\n',encoding='utf8');return p
def wav(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 with wave.open(str(p),'wb')as w:w.setparams((1,2,24000,len(data)//2,'NONE','not compressed'));w.writeframes(data)
 return dict(path=str(p),sha256=m.sha(p),pcmSHA256=hashlib.sha256(data).hexdigest(),sampleRate=24000,channels=1,sampleWidthBytes=2,frames=len(data)//2)

class Caption103Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  fixture.Source103Tests.setUpClass();f=fixture.Source103Tests;cls.n=copy.deepcopy(f.draft);cls.plan=copy.deepcopy(f.plan);P=m.PROJECT;cls.c=m.read(P/'caption-clauses-v3.json');cls.a=m.read(P/'translated-caption-anchors-v2.json');cls.plan['sourceNarrationSHA256']=cls.c['sourceNarration']['sha256'];cls.tmp=tempfile.TemporaryDirectory(prefix='caption103-synthetic-');cls.root=Path(cls.tmp.name);qa=m.asr_factory();groups,_=qa.component_groups(cls.n,cls.plan,cls.plan['sourceNarrationSHA256']);script,mapping=qa.qa.voice.prep.make_scenes(cls.n,groups);position=0;payload=[];chunks=[];entries=[];takes=[]
  for index,s in enumerate(script['scenes']):
   sid=s['id'];text=s['lines'][0];tokens=text.split();frames=(len(tokens)+1)*2400+(1 if index==102 else 0);data=struct.pack('<h',index+1)*frames;info=wav(cls.root/'chunks'/(sid+'-scene.wav'),data);chunks.append(info);payload.append(data);start=position;position+=frames;entries.append(dict(scene_id=sid,text=text,start=start/24000,end=position/24000));words=[dict(text=token,timestamp=[(start+480+i*2400)/24000,(start+1920+i*2400)/24000])for i,token in enumerate(tokens)];takes.append(dict(task=dict(sceneId=sid,expected=text,offsetSample=start,endSample=position),text=text,globalWords=words))
  identity=dict(topicId='06.02',scenes=[dict(id=s['id'],lines=s['lines'])for s in script['scenes']]);aggregate=wav(cls.root/'canonical/narration.wav',b''.join(payload));timing=dump(cls.root/'canonical/timing.json',dict(sample_rate=24000,entries=entries));cls.voice=dict(topicId='06.02',fingerprint=m.digest(identity),identity=identity,sceneWavs=chunks,aggregateWav=aggregate,timing=m.pin(timing),paragraphMapping=mapping)
  paragraphs=[]
  for p in range(1,26):
   rows=[(t,mp)for t,mp in zip(takes,mapping)if mp['paragraph']==p];a,b=rows[0][0]['task']['offsetSample'],rows[-1][0]['task']['endSample'];paragraphs.append(dict(paragraph=p,sceneIds=[r[0]['task']['sceneId']for r in rows],expectedLiteral=cls.n['narrationKo'][p-1],startSample=a,endSample=b,start=a/24000,end=b/24000))
  cls.review=dict(voiceFingerprint=cls.voice['fingerprint'],aggregateSHA256=aggregate['sha256'],timingSHA256=m.sha(timing),takes=takes,boundaryWindows=[dict(synthetic=True)]*102,paragraphs=paragraphs,aliasesApplied=False,expectedPrompt=None,automaticSpeechPass=False);cls.binding=m.voice_binding(cls.voice,cls.review,cls.n,cls.plan);cls.result=m.build(cls.n,cls.plan,cls.c,cls.a,cls.review,cls.binding)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup();fixture.Source103Tests.tearDownClass()
 def test_actual103physical_to96logical_and190_234(self):self.assertEqual(len(self.binding['physicalComponents']),103);self.assertEqual(len(self.result['sentences']),96);self.assertEqual([len(self.result['captions'][k])for k in('ko','en')],[190,234])
 def test_all25_exact_paragraph_sample_envelopes(self):
  for row in self.result['paragraphs']:
   pp=[p for p in self.binding['physicalComponents']if p['paragraph']==row['paragraph']];self.assertEqual([row['startSample'],row['endSample']],[pp[0]['startSample'],pp[-1]['endSample']]);self.assertEqual(row['physicalSceneIds'],[p['sceneId']for p in pp])
 def test_seven_two_component_logical_groups(self):self.assertEqual({s['sceneId']for s in self.result['sentences']if len(s['physicalSceneIds'])==2},m.asr_factory().SPLIT_LOGICAL_IDS)
 def test_split_logical_word_owners_never_lost(self):
  row=next(s for s in self.result['sentences']if s['sceneId']=='p004-c04');self.assertEqual({w['sourcePhysicalSceneId']for w in row['words']},set(row['physicalSceneIds']));self.assertTrue(all('sourcePhysicalWordIndex'in w for w in row['words']))
 def test_raw_component_join_uses_two_measured_edges_no_extra_time(self):
  row=next(s for s in self.result['sentences']if s['sceneId']=='p004-c04');left,right=row['physicalComponents'];a=m.char_boundary(row,left['logicalSourceCharRange'][1]);b=m.char_boundary(row,right['logicalSourceCharRange'][0]);self.assertLess(a['sample'],b['sample']);self.assertEqual(a['sample'],row['words'][len(left['canonicalKo'].split())-1]['endSample']);self.assertEqual(b['sample'],row['words'][len(left['canonicalKo'].split())]['startSample']);self.assertEqual(self.result['audioClock']['addedObservationHoldSamples'],0)
 def test_final_one_raw_sample_uses_video_ceil_without_padding(self):self.assertEqual(self.result['totalFrames'],m.ceil_frame(self.binding['totalSamples']));self.assertEqual(self.result['sentences'][-1]['endFrameExclusive'],self.result['totalFrames']);self.assertTrue(self.result['audioClock']['noAudioTailPadding'])
 def test_raw_literal_differences_remain_per_physical_take(self):
  p=self.binding['physicalComponents'][0];t=copy.deepcopy(self.review['takes'][0]);t['globalWords'][0]['text']='디쓰아너드에서';t['text']=' '.join(w['text']for w in t['globalWords']);a=m.old.aligned_sentence(p,t);ss=self.binding['sentences'][0];logical=m.assemble_logical(ss,[p],{p['sceneId']:a});self.assertIn('디쓰',logical['alignmentReview']['recognizedLiteral']);self.assertTrue(logical['alignmentReview']['physicalLiteralReviews'][0]['alignmentDifferences']);self.assertFalse(logical['alignmentReview']['aliasesApplied'])
 def test_missing_physical_component_never_collapses_to_logical_count(self):
  voice=copy.deepcopy(self.voice);voice['sceneWavs'].pop()
  with self.assertRaises(m.Pending):m.voice_binding(voice,self.review,self.n,self.plan)
 def test_changed_physical_order_rejected(self):
  voice=copy.deepcopy(self.voice);voice['paragraphMapping'][0],voice['paragraphMapping'][1]=voice['paragraphMapping'][1],voice['paragraphMapping'][0]
  with self.assertRaises(m.Pending):m.voice_binding(voice,self.review,self.n,self.plan)
 def test_changed_pcm_pin_rejected(self):
  voice=copy.deepcopy(self.voice);voice['sceneWavs'][0]['pcmSHA256']='0'*64
  with self.assertRaises(m.Pending):m.voice_binding(voice,self.review,self.n,self.plan)
 def test_wrong_logical_char_range_rejected(self):
  plan=copy.deepcopy(self.plan);plan['logicalGroups'][0]['sourceCharRange'][1]-=1
  with self.assertRaises(m.Pending):m.voice_binding(self.voice,self.review,self.n,plan)
 def test_missing_raw_asr_take_rejected(self):
  review=copy.deepcopy(self.review);review['takes'].pop()
  with self.assertRaises(m.Pending):m.build(self.n,self.plan,self.c,self.a,review,self.binding)
 def test_changed_raw_task_clock_rejected(self):
  review=copy.deepcopy(self.review);review['takes'][0]['task']['endSample']-=1
  with self.assertRaises(m.Pending):m.build(self.n,self.plan,self.c,self.a,review,self.binding)
 def test_within_physical_asr_word_no_char_interpolation(self):
  row=self.binding['physicalComponents'][0];t=copy.deepcopy(self.review['takes'][0]);t['globalWords']=[dict(text=t['text'],timestamp=[row['startSample']/24000,row['endSample']/24000])];a=m.old.aligned_sentence(row,t);logical=m.assemble_logical(self.binding['sentences'][0],[row],{row['sceneId']:a})
  with self.assertRaises(m.Pending):m.resolve_literal_start(logical,'창 너머')
 def test_logical_phrase_boundary_retains_physical_owner(self):
  row=next(s for s in self.result['sentences']if s['sceneId']=='p004-c04');start=m.resolve_literal_start(row,'건너야 하는 거리가');self.assertEqual(start['sourcePhysicalSceneId'],row['physicalSceneIds'][1])
 def test_all_reordered_translations_remain_semantic_slots(self):self.assertEqual(sum(bool(a['translationReordered'])for a in self.a['groups']),26);self.assertTrue(all(c['translatedTimingReviewPending']for c in self.result['captions']['en']))
 def test_fixed_font_and_one_emphasis_geometry_unchanged(self):self.assertTrue(all(len(c['lines'])<=2 and len(c['emphasis'])<=1 for rows in self.result['captions'].values()for c in rows))
 def test_actualV4_source_map_and_all_caption_font_geometry(self):
  n,p,c,a=m.sources();groups,logical=m.asr_factory().component_groups(n,p,m.sha(m.NARRATION));self.assertEqual((sum(map(len,groups.values())),len(logical)),(103,96));normal,bold,_=m.old.base.base.fonts();counts=dict(ko=0,en=0)
  for g in c['groups']:
   for lang in('ko','en'):
    for cue in g[lang+'Cues']:m.old.display_cue(cue,lang,g,0,60,normal,bold);counts[lang]+=1
  self.assertEqual(counts,dict(ko=190,en=234))
 def test_srt_plain_preserves_all_source_cues(self):
  for lang,count in [('ko',190),('en',234)]:text=m.old.base.srt(self.result['captions'][lang],lang);self.assertEqual(text.count(' --> '),count);self.assertNotIn('<font',text)
 def test_missing_summary_never_created(self):
  qa=MagicMock();qa.prepare_job.return_value=dict(output=str(self.root/'absent'),identity=dict(tasks=[{}]*205))
  with patch.object(m,'asr_factory',return_value=qa),self.assertRaises(m.Pending):m.verified_asr_review(self.root/'absent/review.json')
  qa.summary.assert_not_called()
 def test_missing_one205cache_never_summary(self):
  file=dump(self.root/'missingcache/review.json',{});qa=MagicMock();qa.prepare_job.return_value=dict(output=str(file.parent),identity=dict(tasks=[{}]*205));qa.cached.return_value=None
  with patch.object(m,'asr_factory',return_value=qa),self.assertRaises(m.Pending):m.verified_asr_review(file)
  qa.summary.assert_not_called()
 def actual_p14_fixture(self):
  proof=m.read(m.SUPPORT);row=proof['bindings'][0];take=m.read(row['sourceAsrRecord']['path']);start=take['task']['offsetSample'];end=take['task']['endSample'];physical=dict(sceneId=row['sceneId'],canonicalKo=row['canonicalKo'],rawWav=row['rawWav'],startSample=start,endSample=end,startFrame=m.frame_from_sample(start),endFrameExclusive=m.frame_from_sample(end),logicalSourceCharRange=[0,len(row['canonicalKo'])]);logical=dict(physical,physicalSceneIds=[row['sceneId']]);return dict(sentences=[logical]),physical,logical,take
 def test_same_one_component_p14_measured_support_preserves_raw_differences(self):
  binding,physical,logical,take=self.actual_p14_fixture();support=m.boundary_support(binding);aligned=m.old.aligned_sentence(physical,take,support['p014-c03']);out=m.assemble_logical(logical,[physical],{'p014-c03':aligned});self.assertEqual(m.char_boundary(out,13)['sample']-physical['startSample'],36000);self.assertEqual(m.char_boundary(out,14)['sample']-physical['startSample'],36000);self.assertIn('세자리',out['alignmentReview']['recognizedLiteral']);self.assertFalse(out['alignmentReview']['aliasesApplied'])
 def test_p14_support_cannot_span_two_physical_units(self):
  binding,_,_,_=self.actual_p14_fixture();binding['sentences'][0]['physicalSceneIds']=['p014-c03','p014-c04']
  with self.assertRaises(m.Pending):m.boundary_support(binding)
 def test_p14_support_rejects_changed_raw_pcm(self):
  binding,_,_,_=self.actual_p14_fixture();binding=copy.deepcopy(binding);binding['sentences'][0]['rawWav']['pcmSHA256']='0'*64
  with self.assertRaises(m.Pending):m.boundary_support(binding)
 def test_pending_data_freeze_never_writes_model_or_timing(self):
  original=dict(m.SOURCE_PINS)
  with patch.dict(m.SOURCE_PINS,{m.NARRATION:None}),patch.object(m,'write_outputs',side_effect=AssertionError('no write')),patch.object(m,'asr_factory',side_effect=AssertionError('no job')),patch('sys.argv',['caption-v2']),patch('sys.stdout',new_callable=io.StringIO)as output:m.main()
  result=json.loads(output.getvalue());self.assertFalse(result['ready']);self.assertFalse(result['written']);self.assertFalse(result['modelStarted']);self.assertEqual(result['reason'],'New103/96 source freeze pending/changed: narration-expanded-draft-v4.json');self.assertEqual(m.SOURCE_PINS,original)

if __name__=='__main__':unittest.main(verbosity=2)

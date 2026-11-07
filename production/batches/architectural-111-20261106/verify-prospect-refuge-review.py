"""CPU-only06.02 four-output collector faults; no FFmpeg/models/staging."""
import copy,contextlib,importlib.util,io,json,math,os,re,subprocess,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('prospect_review_cpu_fixture',HERE/'collect-prospect-refuge-review.py');review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)

class ReviewTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory(prefix='yamyam-prospect-review-');self.base=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def write(self,path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False),encoding='utf8');return path
 def video(self):return dict(streams=[dict(codec_type='video',codec_name='h264',pix_fmt='yuv420p',width=1080,height=1920,r_frame_rate='60/1',avg_frame_rate='60/1',sample_aspect_ratio='1:1',duration='.1'),dict(codec_type='audio',codec_name='aac',sample_rate='48000',channels=2)],format=dict(duration='.11'))
 def caption_fixture(self):
  rows=dict(ko=[],en=[]);authored=dict(narrationKo=[],paragraphsEn=[]);paragraphs=[]
  for n in range(1,26):
   a=(n-1)*1200;b=n*1200;paragraphs.append(dict(paragraph=n,startFrame=a,endFrameExclusive=b))
   for lang,field,count in [('ko','narrationKo',8 if n<=15 else 7),('en','paragraphsEn',10 if n<=9 else 9)]:
    texts=[]
    for i in range(count):
     text=(f'문단 {n} 절 {i+1}.'if lang=='ko'else f'Paragraph {n} clause {i+1}.');texts.append(text);rows[lang].append(dict(id=f'{lang}-{n}-{i}',paragraph=n,startFrame=a+i*1200//count,endFrameExclusive=a+(i+1)*1200//count,text=text,lines=[text]))
    authored[field].append(' '.join(texts))
  tracks={lang:[dict(index=i,start=r['startFrame']/60,end=r['endFrameExclusive']/60,text=r['text'])for i,r in enumerate(rs,1)]for lang,rs in rows.items()};timing=self.write(self.base/'timing.json',dict(paragraphs=paragraphs));return dict(totalFrames=30000,captions=rows,inputs=[dict(role='caption-timing',**review.pin(timing))]),tracks,authored
 def mixed_fixture(self):
  folder=self.base/'mixed';folder.mkdir();scenes=[];tasks=[];records=[];index=0
  for p in range(1,26):
   physical=[]
   for i in range(5 if p<=3 else 4):
    sid=f'p{p:03}-c{i+1:02}';physical.append(dict(sceneId=sid));scenes.append(dict(id=sid));index+=1
   task=dict(kind='take',key=f'p{p:03}',paragraphIndex=p,beginSample=(p-1)*100,endSample=p*100,expected=f'문단 {p} 원문.',sourcePhysicalComponents=physical,sourcePhysicalSceneIds=[r['sceneId']for r in physical]);tasks.append(task);records.append(dict(task=task,text=task['expected'],globalWords=[]))
  for i in range(24):
   task=dict(kind='boundary',key=f'j{i}');tasks.append(task);records.append(dict(task=task,text='문맥',globalWords=[]))
  for r in records:self.write(folder/(r['task']['key']+'.json'),r)
  mix=dict(path='actual-mix.wav',sha256='selected-mix-sha',frames=2500);voice=dict(fingerprint='selected-raw-voice',identity=dict(scenes=scenes));job=dict(output=str(folder),fingerprint='selected-job',sourcePins=[],rawVoiceAsr=dict(path='raw-review',sha256='raw-sha'),identity=dict(tasks=tasks,mix=mix,audioBuildFingerprint='selected-build',voiceFingerprint=voice['fingerprint']))
  comparison=lambda a,b:dict(expected=a,literal=b,aliasesApplied=False)
  takes=records[:25];joins=records[25:];paragraphs=[dict(paragraph=r['task']['paragraphIndex'],sceneIds=r['task']['sourcePhysicalSceneIds'],expectedLiteral=r['task']['expected'],recognizedLiteral=r['text'],comparison=comparison(r['task']['expected'],r['text']),globalWords=r['globalWords'],recognitionBasis='independent-actual-final-mix-full-paragraph-window',sourceResult=review.pin(folder/(r['task']['key']+'.json')))for r in takes]
  value=dict(status='mixed-asr-complete-literal-and-listening-review-pending',topicId='06.02',fingerprint=job['fingerprint'],audioBuildFingerprint='selected-build',mixSHA256=mix['sha256'],mixedAudioPath=mix['path'],voiceFingerprint=voice['fingerprint'],sampleRate=48000,frames=2500,coveredSamples=2500,fullActualMixCoverage=True,rawVoiceAsr=job['rawVoiceAsr'],takes=takes,boundaryWindows=joins,paragraphs=paragraphs,physicalComponentCount=103,physicalComponentMapping=[p for r in takes for p in r['task']['sourcePhysicalComponents']],rawVoiceRecognitionReusedAsMix=False,normalizedStemRecognized=False,encodedAACChecked=False,aliasesApplied=False,pcmModified=False,automaticSpeechPass=False,humanListening=False,finalApproval=False,expectedPrompt=None,hotwords=None)
  self.write(folder/'job.json',job);path=self.write(folder/'review.json',value);bykey=copy.deepcopy({r['task']['key']:r for r in records});fake=SimpleNamespace(prepare_job=lambda _:copy.deepcopy(job),cached=lambda _,task:copy.deepcopy(bykey.get(task['key'])),raw=SimpleNamespace(comparison=comparison));return path,voice,value,job,fake
 def test_default_readiness_never_loads_or_decodes_media(self):
  args=SimpleNamespace(render_manifest=None,mixed_asr_review=None,encoded_audio_review=None,metadata='missing',semantic_review=None)
  with patch.object(review,'load_inputs',side_effect=AssertionError('No input decode')),patch.object(review.subprocess,'Popen',side_effect=AssertionError('No subprocess')):r=review.readiness(args)
  self.assertFalse(r['ready']);self.assertFalse(r['mediaStarted'])
 def test_default_main_is_readonly_and_no_worker(self):
  with patch.object(sys,'argv',[str(review.__file__)]),patch.object(review.subprocess,'Popen')as popen,contextlib.redirect_stdout(io.StringIO())as out:review.main()
  popen.assert_not_called();self.assertFalse(json.loads(out.getvalue())['ready'])
 def test_25_authored_paragraphs_keep190KO234EN_independent_cues(self):
  t,s,a=self.caption_fixture();r=review.caption_contract(t,s,a);self.assertEqual((r['koCues'],r['enCues']),(190,234));self.assertTrue(r['all25AuthoredKoEnParagraphsRetained']);self.assertFalse(r['speechQualityPass'])
 def test_exact_plainSRT_or_two_burnin_lines_both_allowed(self):
  t,s,a=self.caption_fixture();r=t['captions']['ko'][0];r['lines']=['문단 1','절 1.'];self.assertEqual(review.caption_contract(t,s,a)['koCues'],190);s['ko'][0]['text']='\n'.join(r['lines']);self.assertEqual(review.caption_contract(t,s,a)['enCues'],234)
 def test_changed_caption_glyph_or_punctuation_rejected(self):
  for altered in ['문단 1 철 1.','문단 1 절 1!']:
   t,s,a=self.caption_fixture();s['ko'][0]['text']=altered
   with self.assertRaisesRegex(ValueError,'exact authored'):review.caption_contract(t,s,a)
 def test_omitted_english_fact_rejected(self):
  t,s,a=self.caption_fixture();a['paragraphsEn'][4]+=' Extra fact.'
  with self.assertRaisesRegex(ValueError,'paragraph'):review.caption_contract(t,s,a)
 def test_unwrappedSRT_cannot_hide_changed_burnin(self):
  t,s,a=self.caption_fixture();t['captions']['ko'][0]['lines']=['문단 1','틀린 글자.']
  with self.assertRaisesRegex(ValueError,'Rendered caption'):review.caption_contract(t,s,a)
 def test_exact_current_cue_count_and_actual_frame_clock_required(self):
  t,s,a=self.caption_fixture();t['captions']['en'].pop()
  with self.assertRaisesRegex(ValueError,'190KO/234EN'):review.caption_contract(t,s,a)
  t,s,a=self.caption_fixture();s['en'][3]['start']+=.01
  with self.assertRaisesRegex(ValueError,'clock'):review.caption_contract(t,s,a)
 def test_pinned_caption_paragraph_map_tamper_rejected(self):
  t,s,a=self.caption_fixture();self.write(Path(t['inputs'][0]['path']),dict(paragraphs=[]))
  with self.assertRaisesRegex(ValueError,'Changed dependency'):review.caption_contract(t,s,a)
 def test_actual_framePTS_count_and_origin_not_nominalfps(self):
  info=self.video();pts=[i/60 for i in range(6)];self.assertEqual(review.video_contract(info,pts,6)['decodedFrames'],6)
  for altered in [pts[:-1],[x+.01 for x in pts],[0,1/60,2/60,2/60,4/60,5/60]]:
   with self.assertRaises(AssertionError):review.video_contract(info,altered,6)
 def test_nativeFHD_H264_yuv420p_stereoAAC_required(self):
  for key,value in [('width',720),('avg_frame_rate','30/1'),('sample_aspect_ratio','4:3'),('pix_fmt','yuv444p')]:
   info=self.video();info['streams'][0][key]=value
   with self.assertRaises(AssertionError):review.video_contract(info,[i/60 for i in range(6)],6)
  info=self.video();info['streams'][1]['channels']=1
  with self.assertRaises(AssertionError):review.video_contract(info,[i/60 for i in range(6)],6)
 def test_sharedAAC_requires_payload_and_clock(self):
  first=[dict(pts_time='0',dts_time='0',duration_time='.021333',data_hash='SHA256:actual',flags='K_')];self.assertTrue(review.same_audio(first,copy.deepcopy(first))['identicalPacketPayloadAndTiming'])
  for key,value in [('pts_time','.001'),('data_hash','SHA256:other'),('flags','D')]:
   second=copy.deepcopy(first);second[0][key]=value
   with self.assertRaises(AssertionError):review.same_audio(first,second)
 def test_finite_samples_include_every_KOcue_and_source_section_midpoint(self):
  t,_,_=self.caption_fixture();t.update(sections=[dict(kind='gameplay',startFrame=0,endFrameExclusive=100),dict(kind='native',startFrame=100,endFrameExclusive=30000)],catCues=[dict(startFrame=200,endFrameExclusive=300)],guideCues=[dict(startFrame=500,endFrameExclusive=600)],paragraphs=[dict(startFrame=0,endFrameExclusive=30000)]);counts,frames=review.section_contract(t);self.assertEqual(sum(counts.values()),30000);self.assertLessEqual(len(frames),512)
  for r in t['captions']['ko']:self.assertIn((r['startFrame']+r['endFrameExclusive']-1)//2,frames)
  for f in [0,29999,49,15049,249,549]:self.assertIn(f,frames)
 def test_balanced_selection_retains_membership_and_logarithmic_depth(self):
  for count in[384,512]:
   frames=[2*i for i in range(count)];expression=review.selection_expression(frames);depth=0;maximum=0
   for ch in expression:
    depth+=1 if ch=='('else-1 if ch==')'else 0;maximum=max(maximum,depth)
   self.assertEqual(depth,0);self.assertLessEqual(maximum,math.ceil(math.log2(count))+1)
   python_expr=re.sub(r'eq\(n\\,(\d+)\)',r'(n==\1)',expression);code=compile(python_expr,'synthetic-balanced-selection','eval');self.assertEqual([n for n in range(count*2)if eval(code,{'__builtins__':{}},{'n':n})],frames)
 def test_selection_rejects_duplicates_order_and_noninteger_frames(self):
  for frames in[[],[1,1],[2,1],[False,1],[0,1.5]]:
   with self.assertRaisesRegex(ValueError,'sorted unique integer'):review.selection_expression(frames)
 def tiny_ffmpeg_selection(self,count):
  frames=[2*i for i in range(count)];expression=review.selection_expression(frames)
  command=[str(review.FF),'-hide_banner','-nostdin','-v','error','-threads','2','-hwaccel','none','-f','lavfi','-i','color=c=black:s=16x16:r=60:d=18','-filter_threads','1','-vf','select='+expression,'-fps_mode','passthrough','-threads:v','2','-f','framemd5','-']
  result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30,creationflags=review.CREATE|getattr(subprocess,'BELOW_NORMAL_PRIORITY_CLASS',0));self.assertEqual(result.returncode,0,result.stderr.decode(errors='replace')[-2000:]);text=result.stdout.decode();rows=[line for line in text.splitlines()if line and not line.startswith('#')];self.assertEqual(len(rows),count);self.assertEqual([int(line.split(',')[2].strip())for line in rows],frames);self.assertIn('#tb 0: 1/60',text)
 @unittest.skipUnless(os.environ.get('YAMYAM_RUN_TINY_FFMPEG_TESTS')=='1','Explicit tiny16x16 software fixture only')
 def test_actual_tiny_16x16_384_balanced_select_count_andPTS(self):self.tiny_ffmpeg_selection(384)
 @unittest.skipUnless(os.environ.get('YAMYAM_RUN_TINY_FFMPEG_TESTS')=='1','Explicit tiny16x16 software fixture only')
 def test_actual_tiny_16x16_512_balanced_select_count_andPTS(self):self.tiny_ffmpeg_selection(512)
 def test_picture_gap_and_invalidcat_fail_closed(self):
  t=dict(totalFrames=60,sections=[dict(kind='gameplay',startFrame=0,endFrameExclusive=59)],captions=dict(ko=[]))
  with self.assertRaises(ValueError):review.section_contract(t)
  t['sections'][0]['endFrameExclusive']=60;t['catCues']=[dict(startFrame=-1,endFrameExclusive=30)]
  with self.assertRaises(ValueError):review.section_contract(t)
 def test_completed49mixedwindows_cover103_in_current_order(self):
  path,voice,v,job,fake=self.mixed_fixture()
  with patch.object(review,'module',return_value=fake):self.assertEqual(review.verified_mixed_review(path,'audio-build',voice),review.pin(path))
 def test_missing_mixedwindow_or_substituted_rawspeech_rejected(self):
  path,voice,v,job,fake=self.mixed_fixture();fake.cached=lambda *a:None
  with patch.object(review,'module',return_value=fake):
   with self.assertRaisesRegex(ValueError,'incomplete'):review.verified_mixed_review(path,'audio-build',voice)
 def test_stale_mixedSHA_or_false_speech_approval_rejected(self):
  path,voice,v,job,fake=self.mixed_fixture()
  for key,value in [('mixSHA256','old'),('aliasesApplied',True),('automaticSpeechPass',True),('humanListening',True)]:
   changed=copy.deepcopy(v);changed[key]=value;self.write(path,changed)
   with patch.object(review,'module',return_value=fake):
    with self.assertRaises(ValueError):review.verified_mixed_review(path,'audio-build',voice)
 def test_mixed_physicalmapping_or_literal_summary_cannot_be_hidden(self):
  path,voice,v,job,fake=self.mixed_fixture()
  for mutation in [lambda d:d['physicalComponentMapping'].reverse(),lambda d:d['paragraphs'][0].update(recognizedLiteral='숨김')]:
   changed=copy.deepcopy(v);mutation(changed);self.write(path,changed)
   with patch.object(review,'module',return_value=fake):
    with self.assertRaises(ValueError):review.verified_mixed_review(path,'audio-build',voice)
 def test_metadata_usescurrentV4_and_retains_exactcredits(self):
  source=review.read(review.METADATA);r=review.metadata_packet(source,'current-master');self.assertEqual(r['titles']['en'],source['titleEn']);self.assertEqual(r['descriptions']['ko'],source['descriptionKo']);self.assertFalse(r['actualHumanFinalReview'])
  source['sourceNarration']=review.pin(review.PROJECT/'narration-draft.json')
  with self.assertRaisesRegex(ValueError,'current V4'):review.metadata_packet(source,'current-master')
 def test_existing_authored_semantic_sources_project_without_media_approval(self):
  r=review.semantic_binding(None,{});self.assertTrue(r['manualSemanticReview']);self.assertTrue(r['allParagraphTextsRetained']);self.assertEqual(len(r['sourceTextReviews']),2);self.assertFalse(r['actualHumanListening']);self.assertFalse(r['humanFinalApproval'])
 def test_internal_semantic_review_does_not_accept_wrong_sourcepath(self):
  with self.assertRaisesRegex(ValueError,'exact current root'):review.semantic_binding(self.base/'arbitrary.json',{})
 def test_official25paragraph_alignment_retains_independent_counts(self):
  t,tracks,_=self.caption_fixture();stage=self.base/'stage';stage.mkdir()
  for lang in('ko','en'):(stage/(review.SLUG+'.'+lang+'.srt')).write_text('fixture',encoding='utf8')
  with patch.object(review,'ROOT',self.base):r=review.alignment_for_official(t,tracks,stage,dict(approvalScope='Internal source only'))
  self.assertEqual(len(r['paragraphs']),25);self.assertEqual([q['cues']for q in r['captions']],[190,234]);self.assertNotEqual(len(r['paragraphs'][0]['koCues']),len(r['paragraphs'][0]['enCues']));self.assertFalse(r['humanFinalApproval'])
 def test_official_alignment_cannot_invent_equal_outer_bounds(self):
  t,tracks,_=self.caption_fixture();tracks['en'][0]['start']+=.001
  with self.assertRaisesRegex(ValueError,'endpoints differ'):review.alignment_for_official(t,tracks,self.base,dict(review='internal'))
 def test_project_patch_preserves_foreign_and_existing_advanced_flags(self):
  old=dict(status='keep',humanApproval=True,unrelated={'keep':1},paths=dict(script='keep'),titles=dict(ja='keep'));r=review.project_patch(old,dict(videoClean='owned'),dict(ko='새제목',en='English'))
  for k in('status','humanApproval','unrelated'):self.assertEqual(r[k],old[k])
  self.assertEqual(r['paths']['script'],'keep');self.assertEqual(r['titles']['ja'],'keep');self.assertNotIn('videoClean',old['paths'])
 def test_existing_review_for_othermaster_cannot_be_reused(self):
  folder=self.base/'review';folder.mkdir();data=dict(fingerprint='same',pins={},metadata=dict(masterSHA256='current'),semanticAlignment={});self.write(folder/'review-receipt.json',dict(fingerprint='same',pins={},metadata=dict(masterSHA256='old')))
  with patch.object(review,'BASE',self.base):
   with self.assertRaisesRegex(ValueError,'another exact input'):review.existing_review(folder,data)
 def test_partial_or_otherproject_manifest_rejected_before_builder(self):
  for v in [dict(schemaVersion='07-04-render-manifest-v1',topicId='07.04',complete=True),dict(schemaVersion='06-02-render-manifest-v2',topicId='06.02',complete=False)]:
   path=self.write(self.base/'render.json',v)
   with patch.object(review,'BASE',self.base),patch.object(review,'authorize'),patch.object(review,'module',side_effect=AssertionError('No builder before scope check')):
    with self.assertRaisesRegex(ValueError,'Completed actual'):review.load_inputs(path,'metadata','mix')
 def integration_fixture(self):
  project=self.base/'project';project.mkdir();media=self.base/'media';media.mkdir();fp='a'*64;timeline_folder=media/'film-timelines-v2'/fp[:24];timeline_folder.mkdir(parents=True)
  self.write(project/'narration-expanded-draft-v4.json',dict(fixture='current narration'));voice=dict(fingerprint='current-raw',aggregateWav=dict(path='canonical.wav',sha256='canonical-sha',sampleRate=24000,channels=1,frames=24000),identity=dict(scenes=[dict(id=f'physical-{i}')for i in range(103)]));vp=self.write(media/'voice-proof.json',voice)
  timing=self.write(media/'caption-timing.json',dict(inputs=[dict(role='voiceEvidence',**review.pin(vp))]));inputs=[dict(role='caption-timing',**review.pin(timing)),dict(role='renderer',**review.pin(HERE/'render-prospect-refuge-film-v2.py'))]
  for name in['audio-build','mc-p04','mc-p25','annotation-plan','picture-overrides','mix-clock-proof']:q=self.write(media/(name+'.json'),dict(fixture=name));inputs.append(dict(role=name,**review.pin(q)))
  timeline=dict(fingerprint=fp,totalFrames=60,inputs=inputs,audio=dict(voice=voice['aggregateWav']));tp=self.write(timeline_folder/'timeline.json',timeline);outputs={}
  for key,suffix in review.SUFFIX.items():p=media/(review.SLUG+'.'+suffix);p.write_bytes(('synthetic-'+key).encode());outputs[key]=review.pin(p)
  manifest=dict(schemaVersion='06-02-render-manifest-v2',topicId='06.02',complete=True,format=dict(width=1080,height=1920,fps=60),totalFrames=60,outputs=outputs,inputs=inputs,timeline=review.pin(tp),gpuEncoding=False,modelsStarted=False);mp=self.write(media/'render-manifest.json',manifest)
  metadata=self.write(project/'publishing.json',dict(topicId='06.02',sourceNarration=review.pin(project/'narration-expanded-draft-v4.json'),titleKo='검수 제목',titleEn='Review title',descriptionKo='정확한 크레딧',descriptionEn='Exact credits'));encoded=self.write(media/'encoded-review.json',dict(fixture=True));return project,media,timeline,manifest,mp,metadata,encoded
 @contextlib.contextmanager
 def integration_mocks(self,project,media,timeline,encoded_call=None):
  def mod(name,path):
   if name=='prospect_collector_timeline':return SimpleNamespace(prepare=lambda *a:copy.deepcopy(timeline))
   if name=='prospect_collector_encoded_audio':return SimpleNamespace(verify_existing=encoded_call or(lambda *a,**kw:dict(fixtureEncoded=True,actualListening=False)))
   raise AssertionError('Unexpected module or model path: '+name)
  with patch.object(review,'PROJECT',project),patch.object(review,'BASE',media),patch.object(review,'METADATA',project/'publishing.json'),patch.object(review,'METADATA_SHA',review.sha(project/'publishing.json')),patch.object(review,'authorize'),patch.object(review,'module',side_effect=mod),patch.object(review,'semantic_binding',return_value=dict(topicId='06.02',approvalScope='Internal authored source only',actualHumanListening=False)),patch.object(review,'verified_mixed_review',return_value=dict(path='actual-mixed',sha256='mixed-pin')),patch.object(review.subprocess,'Popen',side_effect=AssertionError('Load must not decode/stage/launch models')):yield
 def test_actual06manifest_shape_and_existing_encoded_review_are_loaded_without_process(self):
  project,media,t,manifest,mp,metadata,encoded=self.integration_fixture();calls=[]
  def audio(path,render_manifest=None):calls.append((path,render_manifest));return dict(actualListening=False,existingTargetsCleared=False)
  with self.integration_mocks(project,media,t,audio):r=review.load_inputs(mp,metadata,'actual-mixed',encoded_audio_path=encoded)
  self.assertEqual(r['metadata']['masterSHA256'],manifest['outputs']['captioned']['sha256']);self.assertEqual(r['metadata']['version'],r['fingerprint'][:24]);self.assertEqual(r['metadata']['sourceMetadata'],review.pin(metadata));self.assertEqual(calls,[(encoded,mp.resolve())]);self.assertFalse(r['encodedAudio']['existingTargetsCleared'])
 def test_encoded_audio_report_required_instead_of_implicit_QA(self):
  project,media,t,manifest,mp,metadata,encoded=self.integration_fixture()
  with self.integration_mocks(project,media,t):
   with self.assertRaisesRegex(ValueError,'will not launch it implicitly'):review.load_inputs(mp,metadata,'actual-mixed')
 def test_changed_current_timeline_rejected_before_outputQA(self):
  project,media,t,manifest,mp,metadata,encoded=self.integration_fixture();fresh=copy.deepcopy(t);fresh['totalFrames']=61
  with self.integration_mocks(project,media,fresh):
   with self.assertRaisesRegex(ValueError,'Current ASR'):review.load_inputs(mp,metadata,'actual-mixed',encoded_audio_path=encoded)
 def test_finalfile_tamper_rejected_before_mixed_or_encoded_audio(self):
  project,media,t,manifest,mp,metadata,encoded=self.integration_fixture();Path(manifest['outputs']['clean']['path']).write_bytes(b'changed')
  with self.integration_mocks(project,media,t):
   with self.assertRaisesRegex(ValueError,'changed selected output'):review.load_inputs(mp,metadata,'actual-mixed',encoded_audio_path=encoded)
 def test_another_selectedproject_metadata_file_not_silently_accepted(self):
  project,media,t,manifest,mp,metadata,encoded=self.integration_fixture();other=self.write(project/'other.json',review.read(metadata))
  with self.integration_mocks(project,media,t):
   with self.assertRaisesRegex(ValueError,'exact root-reviewed'):review.load_inputs(mp,other,'actual-mixed',encoded_audio_path=encoded)
 def test_changed_exact_metadata_bytes_require_repin(self):
  project,media,t,manifest,mp,metadata,encoded=self.integration_fixture()
  with self.integration_mocks(project,media,t):
   v=review.read(metadata);v['descriptionEn']='Changed credit';self.write(metadata,v)
   with self.assertRaisesRegex(ValueError,'explicit repin'):review.load_inputs(mp,metadata,'actual-mixed',encoded_audio_path=encoded)
 def test_known_launch_gap_exact_command_or_unknown_argv_preserves_marker(self):
  command=[str(review.FF.resolve()),'-v','error','selected-input'];record=dict(phase='launching-owned-review-tool',launchCommand=command,child=None)
  for args,expected in[(command,True),(None,True),([command[0],'-other'],False)]:
   proc=SimpleNamespace(info=dict(name=Path(command[0]).name,cmdline=args))
   with patch('psutil.process_iter',return_value=[proc]),patch.object(review.native,'alive',return_value=False):self.assertEqual(review.owned_alive(record),expected);self.assertEqual(review.child_pending_or_alive(record),expected)
 def test_run_requires_worker_and_selected_executable_before_Popen(self):
  with patch.object(review,'ACTIVE_WORKER',None),patch.object(review.subprocess,'Popen')as popen:
   with self.assertRaisesRegex(ValueError,'owned finite'):review.run([review.FF,'-v','error'])
   popen.assert_not_called()
 def test_Popen_identity_gap_keeps_worker_marker_and_uses_owned_liveness(self):
  worker=SimpleNamespace(record=dict(pid=-123,createTime=0,child=None),closed=[])
  worker.acquire=lambda:worker;worker.update=lambda **kw:worker.record.update(kw);worker.close=lambda remove=True:worker.closed.append(remove)
  data=dict(fingerprint='e'*64,pins={},render=dict(format={}),timeline=dict(totalFrames=60),sources=dict(clean=self.base/'clean.mp4'))
  def processes(*a,**kw):return[SimpleNamespace(info=dict(name=Path(worker.record['launchCommand'][0]).name,cmdline=worker.record['launchCommand']))]
  def popen(*a,**kw):self.assertEqual(worker.record['phase'],'launching-owned-review-tool');return SimpleNamespace(pid=789)
  with patch.object(review,'BASE',self.base),patch.object(review,'authorize'),patch.object(review.native,'SingleWorker',return_value=worker)as single,patch.object(review.native,'identity',side_effect=RuntimeError('Identity query failed after Popen')),patch.object(review.native,'alive',return_value=False),patch.object(review.shutil,'which',side_effect=lambda x:str(x)if str(x)!='node'else None),patch.object(review.subprocess,'Popen',side_effect=popen),patch.object(review,'probe_video',side_effect=lambda *a:review.run([review.FF,'-v','error'])),patch('psutil.process_iter',side_effect=processes):
   with self.assertRaisesRegex(RuntimeError,'Identity query failed'):review.collect_review(data)
   self.assertEqual(worker.closed,[False]);self.assertIs(single.call_args.kwargs['is_alive'],review.owned_alive);self.assertEqual(worker.record['phase'],'launching-owned-review-tool')
 def test_Node_is_resolved_to_absolute_before_known_launch_record(self):
  node=(self.base/'node.exe').resolve();worker=SimpleNamespace(record={});worker.update=lambda **kw:worker.record.update(kw);child=SimpleNamespace(pid=789,returncode=0,communicate=lambda:(b'collected',b''));seen=[]
  def popen(command,**kw):seen.append(command);self.assertEqual(worker.record['phase'],'launching-owned-review-tool');self.assertEqual(worker.record['launchCommand'],command);return child
  with patch.object(review,'ACTIVE_WORKER',worker),patch.object(review.shutil,'which',return_value=str(node)),patch.object(review.native,'identity',return_value=dict(pid=789,createTime=1)),patch.object(review.subprocess,'Popen',side_effect=popen):r=review.run(['node',review.COLLECTOR,review.SLUG])
  self.assertEqual(seen[0][0],str(node));self.assertEqual(r.stdout,b'collected');self.assertIsNone(worker.record['child']);self.assertIsNone(worker.record['launchCommand'])
 def test_Popen_then_child_registration_failure_retains_exact_launch_pointer(self):
  worker=SimpleNamespace(record={})
  def update(**kw):
   if kw.get('phase')=='owned-review-tool':raise OSError('Simulated child registration failure')
   worker.record.update(kw)
  worker.update=update;child=SimpleNamespace(pid=789)
  with patch.object(review,'ACTIVE_WORKER',worker),patch.object(review.shutil,'which',side_effect=lambda x:str(x)if str(x)!='node'else None),patch.object(review.native,'identity',return_value=dict(pid=789,createTime=1)),patch.object(review.subprocess,'Popen',return_value=child):
   with self.assertRaisesRegex(OSError,'child registration'):review.run([review.FF,'-v','error'])
  proc=SimpleNamespace(info=dict(name=review.FF.name,cmdline=worker.record['launchCommand']))
  with patch.object(review.native,'alive',return_value=False),patch('psutil.process_iter',return_value=[proc]):self.assertTrue(review.owned_alive(worker.record));self.assertTrue(review.child_pending_or_alive(worker.record))
 def test_wrong_Node_script_cannot_launch_under_scoped_collector(self):
  node=(self.base/'node.exe').resolve();worker=SimpleNamespace(record={})
  with patch.object(review,'ACTIVE_WORKER',worker),patch.object(review.shutil,'which',return_value=str(node)),patch.object(review.subprocess,'Popen')as popen:
   with self.assertRaisesRegex(ValueError,'official collector'):review.run(['node','other.cjs',review.SLUG])
   popen.assert_not_called()
 def test_disk_decline_precedes_fourfile_stage_and_Node(self):
  folder=self.base/'review';folder.mkdir();files={}
  for k,suffix in review.SUFFIX.items():p=folder/(review.SLUG+'.'+suffix);p.write_bytes(b'fixture');files[k]=dict(file=p.name,sha256=review.sha(p))
  result=dict(metadata=dict(masterSHA256='current'),output=str(folder),deliverables=files)
  with patch.object(review,'verify_saved_review',return_value=dict(semanticAlignment={'source':'internal'})),patch.object(review,'authorize'),patch.object(review.shutil,'disk_usage',return_value=SimpleNamespace(free=0)),patch.object(review,'run',side_effect=AssertionError('No stage/node')):
   with self.assertRaisesRegex(AssertionError,'Insufficient D'):review._official_collect(result)

if __name__=='__main__':unittest.main(verbosity=2)

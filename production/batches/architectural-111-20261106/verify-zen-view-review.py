"""Synthetic CPU-only07.04 collector checks. No media subprocess/model/staging."""
import copy,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('zen_review_cpu_fixture',HERE/'collect-zen-view-review.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='yamyam-zen-review-cpu-');self.base=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def write(self,path,value):
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False),encoding='utf8');return path
    def video(self):
        return dict(streams=[dict(codec_type='video',codec_name='h264',width=1080,height=1920,r_frame_rate='60/1',avg_frame_rate='60/1',sample_aspect_ratio='1:1',duration='.1'),dict(codec_type='audio',codec_name='aac',sample_rate='48000',channels=2)],format=dict(duration='.11'))
    def caption_fixture(self):
        rows=dict(ko=[],en=[]);tracks=dict(ko=[],en=[]);authored=dict(narrationKo=[],paragraphsEn=[]);paragraphs=[]
        for n in range(1,8):
            a=(n-1)*120;b=n*120;ko=f'문단 {n} 전체.';english=[f'Paragraph {n}.','Complete.']
            authored['narrationKo'].append(ko);authored['paragraphsEn'].append(' '.join(english));paragraphs.append(dict(paragraph=n,startFrame=a,endFrameExclusive=b))
            rows['ko'].append(dict(id=f'k{n}',paragraph=n,startFrame=a,endFrameExclusive=b,text=ko,lines=[ko]))
            for part,text in enumerate(english):rows['en'].append(dict(id=f'e{n}-{part}',paragraph=n,startFrame=a+part*60,endFrameExclusive=a+(part+1)*60,text=text,lines=[text]))
        for lang in rows:
            tracks[lang]=[dict(index=i,start=r['startFrame']/60,end=r['endFrameExclusive']/60,text='\n'.join(r['lines']))for i,r in enumerate(rows[lang],1)]
        timing=self.write(self.base/'timing.json',dict(paragraphs=paragraphs,diagramCues=[]))
        return dict(totalFrames=840,captions=rows,inputs=[dict(role='caption-timing',**review.pin(timing))]),tracks,authored
    def mixed_fixture(self,count=14):
        folder=self.base/f'mixed-{count}';folder.mkdir();frames=count*100;voice=dict(fingerprint='current-voice',identity=dict(scenes=[dict(id=f't{i}')for i in range(count)]))
        tasks=[];records=[]
        for i in range(count):
            paragraph=min(7,1+i*7//count);task=dict(kind='take',key=f't{i}',beginSample=i*100,endSample=(i+1)*100,paragraphIndex=paragraph,sceneId=f't{i}',expected='벽의 틈')
            tasks.append(task);records.append(dict(task=task,text='벽의 틈',globalWords=[dict(text='벽의 틈',timestamp=[i*.1,(i+1)*.1])]))
        for i in range(count-1):
            task=dict(kind='boundary',key=f'j{i}');tasks.append(task);records.append(dict(task=task,text='맥락',globalWords=[]))
        mix=dict(path='actual-mix.wav',sha256='actual-mix-sha',frames=frames)
        job=dict(output=str(folder),fingerprint='current-job',sourcePins=[],rawVoiceAsr=dict(path='raw-review.json',sha256='raw-review-sha'),identity=dict(tasks=tasks,mix=mix,audioBuildFingerprint='accepted-build'))
        takes=records[:count];joins=records[count:]
        comparison=lambda expected,literal:dict(expected=expected,recognized=literal,aliasesApplied=False)
        paragraphs=[]
        for n in range(1,8):
            group=[r for r in takes if r['task']['paragraphIndex']==n];expected=' '.join(r['task']['expected']for r in group);literal=' '.join(r['text']for r in group)
            paragraphs.append(dict(paragraph=n,sceneIds=[r['task']['sceneId']for r in group],expectedLiteral=expected,recognizedLiteral=literal,comparison=comparison(expected,literal),globalWords=[w for r in group for w in r['globalWords']],recognitionBasis='independent-actual-final-mix-component-windows'))
        value=dict(status='mixed-asr-complete-literal-and-listening-review-pending',topicId='07.04',fingerprint=job['fingerprint'],audioBuildFingerprint='accepted-build',mixSHA256=mix['sha256'],mixedAudioPath=mix['path'],voiceFingerprint=voice['fingerprint'],sampleRate=48000,frames=frames,coveredSamples=frames,fullActualMixCoverage=True,rawVoiceAsr=job['rawVoiceAsr'],takes=takes,paragraphs=paragraphs,boundaryWindows=joins,rawVoiceRecognitionReusedAsMix=False,normalizedStemRecognized=False,encodedAACChecked=False,aliasesApplied=False,pcmModified=False,automaticSpeechPass=False,humanListening=False,finalApproval=False,expectedPrompt=None,hotwords=None)
        self.write(folder/'job.json',job);path=self.write(folder/'review.json',value)
        bykey={r['task']['key']:r for r in records}
        fake=SimpleNamespace(prepare_job=lambda _:copy.deepcopy(job),cached=lambda _,task:copy.deepcopy(bykey.get(task['key'])),raw=SimpleNamespace(comparison=comparison))
        return path,voice,value,job,fake

    def test_default_readiness_does_not_load_media_or_start_process(self):
        args=SimpleNamespace(render_manifest=None,mixed_asr_review=None,metadata=str(self.base/'missing.json'),semantic_review=None)
        with patch.object(review,'load_inputs',side_effect=AssertionError('No media readiness probe')),patch.object(review.subprocess,'Popen',side_effect=AssertionError('No subprocess')):
            result=review.readiness(args)
        self.assertFalse(result['ready']);self.assertFalse(result['mediaStarted']);self.assertFalse(result['modelStarted'])
    def test_exact_seven_paragraphs_allow_different_translation_cue_counts(self):
        timeline,tracks,authored=self.caption_fixture();result=review.caption_contract(timeline,tracks,authored)
        self.assertEqual((result['koCues'],result['enCues']),(7,14));self.assertTrue(result['allSevenAuthoredKoEnParagraphsRetained']);self.assertFalse(result['humanListening'])
    def test_subtitle_timestamp_drift_rejected(self):
        timeline,tracks,authored=self.caption_fixture();tracks['en'][3]['start']+=.01
        with self.assertRaisesRegex(ValueError,'clock'):review.caption_contract(timeline,tracks,authored)
    def test_literal_ae_e_substitution_not_hidden_by_alias(self):
        timeline,tracks,authored=self.caption_fixture();authored['narrationKo'][4]='메트릭스.';timeline['captions']['ko'][4].update(text='매트릭스.',lines=['매트릭스.']);tracks['ko'][4]['text']='매트릭스.'
        with self.assertRaisesRegex(ValueError,'paragraph'):review.caption_contract(timeline,tracks,authored)
    def test_omitted_english_clause_rejected(self):
        timeline,tracks,authored=self.caption_fixture();authored['paragraphsEn'][2]+=' Additional fact.'
        with self.assertRaisesRegex(ValueError,'paragraph'):review.caption_contract(timeline,tracks,authored)
    def test_pinned_paragraph_map_change_rejected(self):
        timeline,tracks,authored=self.caption_fixture();path=Path(timeline['inputs'][0]['path']);self.write(path,dict(paragraphs=[]))
        with self.assertRaisesRegex(ValueError,'Changed dependency'):review.caption_contract(timeline,tracks,authored)
    def test_pts_count_and_uniform_clock_not_nominal_fps(self):
        info=self.video();pts=[i/60 for i in range(6)];self.assertEqual(review.video_contract(info,pts,6)['decodedFrames'],6)
        with self.assertRaises(AssertionError):review.video_contract(info,pts[:-1],6)
        pts[3]+=.001
        with self.assertRaises(AssertionError):review.video_contract(info,pts,6)
    def test_fhd_and_stereo_aac_required(self):
        for key,value in [('width',720),('avg_frame_rate','30/1'),('sample_aspect_ratio','4:3')]:
            info=self.video();info['streams'][0][key]=value
            with self.assertRaises(AssertionError):review.video_contract(info,[i/60 for i in range(6)],6)
        info=self.video();info['streams'][1]['channels']=1
        with self.assertRaises(AssertionError):review.video_contract(info,[i/60 for i in range(6)],6)
    def test_aac_payload_and_timestamp_must_both_match(self):
        first=[dict(pts_time='0',dts_time='0',duration_time='.021333',data_hash='SHA256:actual',flags='K_')]
        self.assertTrue(review.same_audio(first,copy.deepcopy(first))['identicalPacketPayloadAndTiming'])
        for key,value in [('pts_time','.01'),('data_hash','SHA256:other')]:
            second=copy.deepcopy(first);second[0][key]=value
            with self.assertRaises(AssertionError):review.same_audio(first,second)
    def test_srt_third_line_and_overlap_rejected(self):
        path=self.base/'test.srt'
        for value in ['1\n00:00:00,000 --> 00:00:01,000\n1\n2\n3\n','1\n00:00:00,000 --> 00:00:01,000\n처음\n\n2\n00:00:00,500 --> 00:00:02,000\n중복\n']:
            path.write_text(value,encoding='utf8')
            with self.assertRaises(AssertionError):review.srt(path)
    def test_native_occlusion_boundaries_mc_cues_cat_peaks_and_endpoints_sampled(self):
        timing=self.write(self.base/'timing.json',dict(diagramCues=[dict(startFrame=552)]))
        timeline=dict(totalFrames=600,inputs=[dict(role='caption-timing',**review.pin(timing))],sections=[dict(kind='gameplay',startFrame=0,endFrameExclusive=60),dict(kind='native',startFrame=60,endFrameExclusive=540,native=dict(startNativeFrame=0,holdPolicy=None)),dict(kind='mc',startFrame=540,endFrameExclusive=600)],catCues=[dict(startFrame=100,endFrameExclusive=200,easeInFrames=9,easeOutFrames=12)])
        kinds,frames=review.section_contract(timeline)
        self.assertEqual(sum(kinds.values()),600)
        for frame in [0,59,60,60+224,60+225,60+239,60+254,60+255,539,540,552,599,149,109,187]:self.assertIn(frame,frames)
    def test_section_gap_and_invalid_cat_frame_rejected(self):
        timing=self.write(self.base/'timing.json',dict(diagramCues=[]));timeline=dict(totalFrames=60,inputs=[dict(role='caption-timing',**review.pin(timing))],sections=[dict(kind='gameplay',startFrame=0,endFrameExclusive=59)],catCues=[])
        with self.assertRaises(ValueError):review.section_contract(timeline)
        timeline['sections'][0]['endFrameExclusive']=60;timeline['catCues']=[dict(startFrame=-1,endFrameExclusive=50,easeInFrames=9,easeOutFrames=12)]
        with self.assertRaises(ValueError):review.section_contract(timeline)
    def test_completed_exact_mix_proof_accepts_14_and_34_without_hardcount(self):
        for count in (14,34):
            path,voice,value,job,fake=self.mixed_fixture(count)
            with patch.object(review,'module',return_value=fake):self.assertEqual(review.verified_mixed_review(path,'audio-build.json',voice),review.pin(path))
    def test_mixed_asr_stale_mix_hash_rejected(self):
        path,voice,value,job,fake=self.mixed_fixture();value['mixSHA256']='old';self.write(path,value)
        with patch.object(review,'module',return_value=fake),self.assertRaisesRegex(ValueError,'mixSHA256'):review.verified_mixed_review(path,'audio-build.json',voice)
    def test_missing_mixed_task_or_raw_asr_substitution_rejected(self):
        path,voice,value,job,fake=self.mixed_fixture();fake.cached=lambda _,task:None
        with patch.object(review,'module',return_value=fake),self.assertRaisesRegex(ValueError,'incomplete'):review.verified_mixed_review(path,'audio-build.json',voice)
    def test_mixed_alias_or_false_approval_rejected(self):
        path,voice,value,job,fake=self.mixed_fixture();value['aliasesApplied']=True;self.write(path,value)
        with patch.object(review,'module',return_value=fake),self.assertRaisesRegex(ValueError,'substitution'):review.verified_mixed_review(path,'audio-build.json',voice)
    def test_changed_mixed_paragraph_literal_cannot_be_hidden(self):
        path,voice,value,job,fake=self.mixed_fixture();value['paragraphs'][0]['recognizedLiteral']='문제 숨김';self.write(path,value)
        with patch.object(review,'module',return_value=fake),self.assertRaisesRegex(ValueError,'hidden'):review.verified_mixed_review(path,'audio-build.json',voice)
    def test_metadata_exact_credits_and_current_master(self):
        source=dict(topicId='07.04',titleKo='제목',titleEn='Title',descriptionKo='Mr. V-Man\nCC BY 4.0\nKevin MacLeod',descriptionEn='Exact credits\nURLs',masterSHA256=None)
        result=review.metadata_packet(source,'actual');self.assertEqual(result['descriptions']['ko'],source['descriptionKo']);self.assertFalse(result['actualHumanFinalReview'])
        source['masterSHA256']='prior'
        with self.assertRaises(AssertionError):review.metadata_packet(source,'actual')
    def test_advanced_approval_and_unrelated_project_fields_are_preserved(self):
        original=dict(status='human-reviewed',humanApproval=True,finalMovieComplete=True,unrelated=dict(keep=1),paths=dict(script='keep'),titles=dict(ja='keep'))
        result=review.project_patch(original,dict(videoClean='owned'),dict(ko='new',en='English'))
        for key in ('status','humanApproval','finalMovieComplete','unrelated'):self.assertEqual(result[key],original[key])
        self.assertEqual(result['paths']['script'],'keep');self.assertEqual(result['titles']['ja'],'keep');self.assertNotIn('videoClean',original['paths'])
    def test_semantic_source_review_requires_actual_flag_and_current_source_pins(self):
        project=self.base/'selected';project.mkdir();self.write(project/'narration-draft.json',dict(ko='exact'));self.write(project/'caption-clauses-v1.json',dict(en='exact'))
        source=dict(topicId='07.04',manualSemanticReview=True,allParagraphTextsRetained=True,reviewedBy='source-text reviewer',narration=review.pin(project/'narration-draft.json'),captionClauses=review.pin(project/'caption-clauses-v1.json'))
        path=self.write(project/'semantic-review.json',source)
        with patch.object(review,'PROJECT',project):
            self.assertEqual(review.semantic_binding(path,{}),review.pin(path));source['manualSemanticReview']=False;self.write(path,source)
            with self.assertRaises(ValueError):review.semantic_binding(path,{})
    def test_official_alignment_retains_unequal_cue_counts_without_human_media_approval(self):
        timeline,tracks,authored=self.caption_fixture();stage=self.base/'stage';stage.mkdir()
        for lang in ('ko','en'):(stage/(review.SLUG+'.'+lang+'.srt')).write_text('fixture',encoding='utf8')
        with patch.object(review,'ROOT',self.base):result=review.alignment_for_official(timeline,tracks,stage,dict(path='review',sha256='pin'))
        self.assertEqual(result['paragraphs'][0]['koCues'],[1]);self.assertEqual(result['paragraphs'][0]['enCues'],[1,2]);self.assertFalse(result['humanFinalApproval']);self.assertFalse(result['actualHumanListening'])
    def test_official_collection_disk_decline_precedes_staging_or_node(self):
        folder=self.base/'review';folder.mkdir();files={}
        for key,suffix in review.SUFFIX.items():
            path=folder/(review.SLUG+'.'+suffix);path.write_bytes(b'fixture');files[key]=dict(file=path.name,sha256=review.sha(path))
        result=dict(metadata=dict(masterSHA256='actual'),output=str(folder),deliverables=files)
        with patch.object(review,'verify_saved_review',return_value=dict(semanticAlignment=dict(path='review',sha256='pin'))),patch.object(review,'authorize',return_value=None),patch.object(review.shutil,'disk_usage',return_value=SimpleNamespace(free=0)),patch.object(review.subprocess,'Popen',side_effect=AssertionError('No node/ffmpeg')):
            with self.assertRaisesRegex(AssertionError,'Insufficient D space'):review._official_collect(result)
    def test_existing_review_metadata_change_cannot_reuse_another_master_packet(self):
        folder=self.base/'local-review';folder.mkdir();data=dict(fingerprint='same',pins=dict(proof='current'),metadata=dict(masterSHA256='current'),semanticAlignment=None,render=dict(outputs={}))
        self.write(folder/'review-receipt.json',dict(fingerprint='same',pins=data['pins'],metadata=dict(masterSHA256='prior')))
        with patch.object(review,'BASE',self.base),self.assertRaisesRegex(ValueError,'another exact input'):review.existing_review(folder,data)
    def test_load_rejects_another_project_or_partial_manifest_before_fresh_builder(self):
        for value in [dict(schemaVersion='03-02-render-manifest-v1',slug='shorts-leveldesign-03-02',topicId='03.02',complete=True),dict(schemaVersion='07-04-render-manifest-v1',slug=review.SLUG,topicId='07.04',complete=False)]:
            path=self.write(self.base/'render.json',value)
            with patch.object(review,'authorize',return_value=None),patch.object(review,'BASE',self.base),patch.object(review,'module',side_effect=AssertionError('No builder before scope proof')):
                with self.assertRaisesRegex(ValueError,'Completed actual'):review.load_inputs(path,'metadata.json','mix-review.json')
    def integration_fixture(self):
        project=self.base/'project';project.mkdir();base=self.base/'media';base.mkdir();identity='f'*64;folder=base/'film-timelines'/identity[:24];folder.mkdir(parents=True)
        aggregate=dict(path='canonical.wav',sha256='voice-sha',sampleRate=24000,channels=1,frames=24000)
        inputs=[]
        for name in ('caption-timing','audio-build','mc-p2','mc-p6','mc-p7','voice-evidence'):
            value=dict(aggregateWav=aggregate) if name=='voice-evidence' else dict(role=name)
            path=self.write(base/(name+'.json'),value);inputs.append(dict(role=name,**review.pin(path)))
        timeline=dict(schemaVersion='07-04-final-timeline-v1',topicId='07.04',fingerprint=identity,totalFrames=60,inputs=inputs,audio=dict(voice=aggregate))
        timeline_path=self.write(folder/'timeline.json',timeline);outputs={}
        for key,suffix in review.SUFFIX.items():
            path=base/(review.SLUG+'.'+suffix);path.write_bytes(('synthetic-'+key).encode());outputs[key]=review.pin(path)
        aac=base/'shared.aac';aac.write_bytes(b'synthetic-AAC')
        manifest=dict(schemaVersion='07-04-render-manifest-v1',slug=review.SLUG,topicId='07.04',complete=True,format=dict(width=1080,height=1920,fps=60,totalFrames=60),timeline=review.pin(timeline_path),inputs=inputs,outputs=outputs,audioAac=dict(**review.pin(aac),sharedPacketCopy=True),renderer=dict(path=str(HERE/'render-zen-view-film.py'),sha256=review.sha(HERE/'render-zen-view-film.py'),gpuUsed=False,modelStarted=False))
        manifest_path=self.write(base/'render-manifest.json',manifest)
        metadata=self.write(project/'publishing-draft-v1.json',dict(topicId='07.04',titleKo='제목',titleEn='Title',descriptionKo='모든 크레딧',descriptionEn='Exact credits',masterSHA256=None))
        return project,base,timeline,manifest,manifest_path,metadata
    def test_full_load_wiring_is_finite_and_never_decodes_or_models(self):
        project,base,timeline,manifest,path,metadata=self.integration_fixture();builder=SimpleNamespace(prepare=lambda *args:copy.deepcopy(timeline))
        with patch.object(review,'PROJECT',project),patch.object(review,'BASE',base),patch.object(review,'authorize',return_value=None),patch.object(review,'module',return_value=builder),patch.object(review,'verified_mixed_review',return_value=dict(path='current-mixed-review',sha256='mixed-proof')),patch.object(review.subprocess,'Popen',side_effect=AssertionError('No process during load')):
            result=review.load_inputs(path,metadata,'mixed-review.json')
        self.assertEqual(result['metadata']['masterSHA256'],manifest['outputs']['captioned']['sha256']);self.assertFalse(result['metadata']['actualHumanFinalReview']);self.assertIsNone(result['semanticAlignment'])
    def test_full_load_cannot_accept_changed_current_timeline_or_render_inputs(self):
        project,base,timeline,manifest,path,metadata=self.integration_fixture();fresh=copy.deepcopy(timeline);fresh['totalFrames']=61;builder=SimpleNamespace(prepare=lambda *args:fresh)
        with patch.object(review,'PROJECT',project),patch.object(review,'BASE',base),patch.object(review,'authorize',return_value=None),patch.object(review,'module',return_value=builder):
            with self.assertRaisesRegex(ValueError,'Current ASR'):review.load_inputs(path,metadata,'mixed-review.json')
    def test_full_load_rejects_tampered_final_output_before_mixed_validation(self):
        project,base,timeline,manifest,path,metadata=self.integration_fixture();Path(manifest['outputs']['clean']['path']).write_bytes(b'changed');builder=SimpleNamespace(prepare=lambda *args:copy.deepcopy(timeline))
        with patch.object(review,'PROJECT',project),patch.object(review,'BASE',base),patch.object(review,'authorize',return_value=None),patch.object(review,'module',return_value=builder),patch.object(review,'verified_mixed_review',side_effect=AssertionError('Do not inspect mixed audio after final file tamper')):
            with self.assertRaisesRegex(ValueError,'changed selected output'):review.load_inputs(path,metadata,'mixed-review.json')


if __name__=='__main__':unittest.main(verbosity=2)

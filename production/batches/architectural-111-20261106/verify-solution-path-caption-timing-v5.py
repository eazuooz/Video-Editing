"""Pure CPU/temp PCM fixtures. No model, recognizer, FFmpeg or real media job."""
import copy, importlib.util, json, struct, tempfile, unittest, wave
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('solution_caption_v5_cpu', HERE / 'build-solution-path-caption-timing-v5.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return path


class CaptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='solution-caption-v4-cpu-')
        cls.root = Path(cls.temp.name)
        cls.n = m.read(m.PROJECT / 'narration-final-v4.json')
        cls.c = m.read(m.PROJECT / 'caption-clauses-v1.json')
        cls.d = m.read(m.PROJECT / 'translated-caption-display-boundaries-v1.json')
        script, mapping = m.asr_adapter.prep.sentence_plan(cls.n, m.digest(cls.n))
        profile = m.read(m.asr_adapter.PROFILE_PATH)
        identity = m.asr_adapter.profile_identity([dict(id=s['id'], lines=s['lines']) for s in script['scenes']], profile)
        out = cls.root / 'voice'; fp = m.digest(identity)
        for index, scene in enumerate(script['scenes']):
            path = out / 'chunks' / (scene['id'] + '-scene.wav'); path.parent.mkdir(parents=True, exist_ok=True)
            frames = len(scene['lines'][0].split()) * 2400 + 480 + (index == len(script['scenes']) - 1)
            with wave.open(str(path), 'wb') as wav:
                wav.setparams((1, 2, 24000, frames, 'NONE', 'not compressed'))
                wav.writeframes(struct.pack('<h', index + 1) * frames)
        cls.v = m.asr_adapter.qa.voice.canonical_outputs(dict(topicId='11.05', identity=identity, fingerprint=fp, paragraphMapping=mapping), out, {})
        dump(out / 'voice-complete-proof.json', cls.v)
        tasks = m.asr_adapter.qa.build_tasks(cls.v, m.read(cls.v['timing']['path']))
        output = cls.root / 'asr'; output.mkdir()
        snapshot = output / 'adapter-source.py'; snapshot.write_bytes((HERE / 'run-solution-path-voice-qa-v4.py').read_bytes())
        cls.job = dict(protocol=m.asr_adapter.PROTOCOL, fingerprint='synthetic-blind-asr', output=str(output), voiceOutput=str(out),
                       modelPath='synthetic-not-loaded', sourcePins=[m.pin(snapshot)], voiceEvidence=m.pin(out / 'voice-complete-proof.json'),
                       identity=dict(adapterSHA256=m.sha(snapshot), tasks=tasks, voiceFingerprint=fp,
                                     aggregateSHA256=cls.v['aggregateWav']['sha256'], timingSHA256=cls.v['timing']['sha256']))
        dump(output / 'job.json', cls.job)
        for task in tasks:
            if task['kind'] == 'take':
                words = task['expected'].split()
                raw = dict(text=task['expected'], chunks=[dict(text=w, timestamp=[.01 + .1 * i, .01 + .1 * (i + 1)]) for i, w in enumerate(words)])
            else:
                raw = dict(text='', chunks=[])
            dump(output / (task['key'] + '.json'), m.asr_adapter.qa.recognition_record(cls.job, task, raw))
        cls.r = m.asr_adapter.summary(cls.job)  # Writes only synthetic TemporaryDirectory metadata.
        cls.result_pins = {t['sceneId']: m.pin(output / (t['key'] + '.json')) for t in tasks if t['kind'] == 'take'}
        cls.binding = m.voice_binding(cls.v, cls.r, cls.n)
        cls.timing = m.build(cls.n, cls.c, cls.d, cls.r, cls.binding, cls.result_pins)

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def bad(self, fn, *args):
        with self.assertRaises((m.Pending, ValueError, KeyError)): fn(*args)

    def test_full_current_source_exact_reconstruction(self):
        t = self.timing
        self.assertEqual((len(t['sentences']), len(t['groups']), len(t['paragraphs'])), (48, 43, 14))
        self.assertEqual({k:len(v) for k,v in t['captions'].items()}, dict(ko=97, en=86))
        for language, source in [('ko', self.n['narrationKo']), ('en', self.n['paragraphsEn'])]:
            for p, text in enumerate(source, 1): self.assertEqual(' '.join(c['text'] for c in t['captions'][language] if c['paragraph']==p), text)

    def test_plain_srt_preserves_all_text(self):
        for language, cues in self.timing['captions'].items():
            blocks = m.srt(cues).strip().split('\n\n')
            self.assertEqual([b.split('\n',2)[2] for b in blocks], [r['text'] for r in cues])
            self.assertNotIn('<font', m.srt(cues))

    def test_raw_clock_no_tail_padding_and_ceil(self):
        self.assertEqual(self.timing['totalFrames'], m.ceil_frame(self.v['aggregateWav']['frames']))
        self.assertNotEqual(self.v['aggregateWav']['frames'] % 400, 0)
        self.assertEqual(self.timing['paragraphs'][-1]['endFrameExclusive'], self.timing['totalFrames'])
        self.assertEqual(self.timing['audioClock']['totalRawSamples'], self.v['aggregateWav']['frames'])
        self.assertTrue(self.timing['audioClock']['noAudioTailPadding'])

    def test_translated_ordered_slots_not_reordered_meaning_windows(self):
        rows = self.timing['captions']['en']
        self.assertEqual(sum(g['originalMeaningWindowsNonordered'] for g in self.d['groups']),18)
        self.assertTrue(all(a['endSample']<=b['startSample'] and a['endFrameExclusive']<=b['startFrame'] for a,b in zip(rows,rows[1:])))
        self.assertTrue(all(not r['translatedSemanticTimingVerified'] and r['translatedTimingReviewPending'] for r in rows))

    def test_every_emphasis_local_to_exact_one_line(self):
        for cues in self.timing['captions'].values():
            for row in cues:
                for span in row['emphasis']:
                    self.assertEqual(row['lines'][span['line']][span['start']:span['end']],span['text'])
                self.assertEqual(row['sourceEmphasis'],next(c for g in self.c['groups'] for c in g[row['language']+'Cues'] if c['id']==row['id'])['emphasis'])

    def test_second_line_emphasis(self):
        self.assertEqual(m.one_line_emphasis('first second', ['first','second'], [dict(start=6,end=12,text='second',role='term')]),[dict(line=1,start=0,end=6,text='second',role='term')])

    def test_crossline_emphasis_never_shortened(self):
        self.bad(m.one_line_emphasis,'first second',['first','second'],[dict(start=0,end=12,text='first second',role='term')])

    def test_changed_emphasis_text_rejected(self):
        self.bad(m.one_line_emphasis,'first',['first'],[dict(start=0,end=5,text='other',role='term')])

    def test_one_sample_raw_timing_tamper_rejected(self):
        v=copy.deepcopy(self.v); time=m.read(v['timing']['path']);time['entries'][3]['start']+=1/24000
        p=dump(self.root/'tampered-timing.json',time);v['timing']=m.pin(p);r=copy.deepcopy(self.r);r['timingSHA256']=m.sha(p)
        self.bad(m.voice_binding,v,r,self.n)

    def test_raw_chunk_metadata_change_rejected(self):
        v=copy.deepcopy(self.v);v['sceneWavs'][0]['frames']+=1;self.bad(m.voice_binding,v,self.r,self.n)

    def test_aggregate_pcm_provenance_change_rejected(self):
        v=copy.deepcopy(self.v);v['aggregateWav']['pcmSHA256']='0'*64;self.bad(m.voice_binding,v,self.r,self.n)

    def test_mapping_reordering_rejected(self):
        v=copy.deepcopy(self.v);v['paragraphMapping'][0],v['paragraphMapping'][1]=v['paragraphMapping'][1],v['paragraphMapping'][0];self.bad(m.voice_binding,v,self.r,self.n)

    def test_missing_join_rejected(self):
        r=copy.deepcopy(self.r);r['boundaryWindows'].pop();self.bad(m.voice_binding,self.v,r,self.n)

    def test_different_asr_voice_rejected(self):
        r=copy.deepcopy(self.r);r['voiceFingerprint']='foreign';self.bad(m.voice_binding,self.v,r,self.n)

    def test_changed_voice_profile_with_rebound_identity_rejected(self):
        v=copy.deepcopy(self.v);v['identity']['tts']['speed']=1.01;v['fingerprint']=m.digest(v['identity'])
        self.bad(m.voice_binding,v,self.r,self.n)

    def test_reordered_join_and_raw_pcm_window_rejected(self):
        r=copy.deepcopy(self.r);r['boundaryWindows'][0],r['boundaryWindows'][1]=r['boundaryWindows'][1],r['boundaryWindows'][0]
        self.bad(m.voice_binding,self.v,r,self.n)
        r=copy.deepcopy(self.r);r['takes'][0]['task']['pcmIdentity']['pcmSHA256']='0'*64
        self.bad(m.voice_binding,self.v,r,self.n)

    def test_actual_paragraph_clock_tamper_rejected(self):
        r=copy.deepcopy(self.r);r['paragraphs'][2]['endSample']+=1;self.bad(m.voice_binding,self.v,r,self.n)

    def test_merged_asr_word_boundary_stays_pending(self):
        source=copy.deepcopy(self.binding['sentences'][0]);take=copy.deepcopy(self.r['takes'][0]);words=take['globalWords'];end=words[1]['timestamp'][1]
        words[0]['text']+=' '+words[1]['text'];words[0]['timestamp'][1]=end;words.pop(1)
        aligned=m.aligned_sentence(source,take);offset=len(source['canonicalKo'].split()[0])
        self.assertTrue(aligned['unsupportedWordBoundaries']);self.bad(m.char_boundary,aligned,offset)

    def test_missing_actual_word_timestamp_stays_pending(self):
        take=copy.deepcopy(self.r['takes'][0]);take['globalWords'][0]['timestamp'][1]=None
        self.bad(m.aligned_sentence,self.binding['sentences'][0],take)

    def test_within_word_requested_cut_never_interpolated(self):
        self.bad(m.paragraph_boundary,self.timing['sentences'],1,1)

    def test_nonfinite_actual_time_rejected(self):
        self.bad(m.sample,float('nan'));self.bad(m.sample,float('inf'))

    def test_literal_difference_retained_no_alias(self):
        take=copy.deepcopy(self.r['takes'][0]);take['globalWords'][0]['text']='스펠렁키이';take['text']=take['text'].replace('스펠렁키','스펠렁키이',1)
        row=m.aligned_sentence(self.binding['sentences'][0],take)
        self.assertEqual(row['alignmentReview']['recognizedLiteral'],take['text']);self.assertFalse(row['alignmentReview']['aliasesApplied'])
        self.assertTrue(row['alignmentReview']['alignmentDifferences'])

    def test_authored_translated_reversed_cuts_rejected(self):
        d=copy.deepcopy(self.d);d['groups'][0]['koDisplayBoundaryCharOffsets'][1]=d['groups'][0]['koDisplayBoundaryCharOffsets'][2]+1
        self.bad(m.validate_translated,d,self.c,self.n)

    def test_authored_translated_inside_word_rejected(self):
        d=copy.deepcopy(self.d);d['groups'][0]['koDisplayBoundaryCharOffsets'][1]=1;self.bad(m.validate_translated,d,self.c,self.n)

    def test_authored_translated_wrong_word_rejected(self):
        d=copy.deepcopy(self.d);d['groups'][0]['boundaryAnchors'][1]['leftWordKo']='다른단어';self.bad(m.validate_translated,d,self.c,self.n)

    def test_authored_translated_fake_clock_rejected(self):
        d=copy.deepcopy(self.d);d['groups'][0]['boundaryAnchors'][1]['actualSample']=100;self.bad(m.validate_translated,d,self.c,self.n)

    def test_authored_translated_source_tamper_rejected(self):
        d=copy.deepcopy(self.d);d['captionClauses']['sha256']='0'*64;self.bad(m.validate_translated,d,self.c,self.n)

    def test_authored_translated_cue_reorder_rejected(self):
        d=copy.deepcopy(self.d);d['groups'][0]['enCueIds'].reverse();self.bad(m.validate_translated,d,self.c,self.n)

    def test_exact_phrase_resolves_across_two_components(self):
        g=next(g for g in self.c['groups'] if len(g['koLogicalSentences'])==2)
        result=m.resolve_literal_interval(self.timing,g['paragraph'],g['ko'])
        self.assertNotEqual(result['actualStartBoundary']['sceneId'],result['actualEndBoundary']['sceneId'])
        self.assertFalse(result['nativeFrameOrCameraAssigned'])

    def test_nonliteral_phrase_rejected(self):
        self.bad(m.resolve_literal_interval,self.timing,1,'invented canonical alias')

    def test_current_raw_cache_reconstruction_without_writes(self):
        review_path=Path(self.job['output'])/'review.json';before={p:m.sha(p) for p in Path(self.job['output']).iterdir()}
        with patch.object(m.asr_adapter,'prepare_job',return_value=self.job): self.assertEqual(m.verified_asr_review(review_path),self.r)
        self.assertEqual(before,{p:m.sha(p) for p in Path(self.job['output']).iterdir()})

    def test_missing_actual_review_fails_before_summary(self):
        with patch.object(m.asr_adapter,'prepare_job',return_value=self.job),patch.object(m.asr_adapter,'summary',side_effect=AssertionError('No summary before complete file')):
            self.bad(m.verified_asr_review,self.root/'missing-review.json')

    def test_missing_cache_cannot_be_auto_restored(self):
        with patch.object(m.asr_adapter,'prepare_job',return_value=self.job),patch.object(m.asr_adapter,'cached',return_value=None),patch.object(m.asr_adapter,'summary',side_effect=AssertionError('No summary before all caches')):
            self.bad(m.verified_asr_review,Path(self.job['output'])/'review.json')

    def test_raw_summary_tamper_rejected(self):
        p=Path(self.job['output'])/'review.json';original=p.read_bytes();r=copy.deepcopy(self.r);r['takes'][0]['text']='invented'
        try:
            dump(p,r)
            with patch.object(m.asr_adapter,'prepare_job',return_value=self.job): self.bad(m.verified_asr_review,p)
        finally:p.write_bytes(original)

    def test_changed_raw_job_rejected(self):
        p=Path(self.job['output'])/'job.json';original=p.read_bytes();j=copy.deepcopy(self.job);j['voiceOutput']='foreign'
        try:
            dump(p,j)
            with patch.object(m.asr_adapter,'prepare_job',return_value=self.job):self.bad(m.verified_asr_review,Path(self.job['output'])/'review.json')
        finally:p.write_bytes(original)

    def test_existing_srt_tamper_rejected(self):
        folder=self.root/'captions';t=copy.deepcopy(self.timing);subs={}
        for lang,rows in t['captions'].items():
            p=folder/('narration.'+lang+'.srt');p.parent.mkdir(exist_ok=True);p.write_bytes(m.srt(rows).encode('utf-8'));subs[lang]=m.pin(p)
        t['subtitles']=subs;p=dump(folder/'caption-timing.json',t);result=dict(output=str(p),timing=t,voice=self.v,asr=self.r)
        with patch.object(m,'prepare',return_value=result):
            self.assertEqual(m.verify_existing(p)['timing'],t)
            Path(subs['en']['path']).write_text('altered',encoding='utf-8');self.bad(m.verify_existing,p)

    def test_no_false_approval_or_mix_timestamp_claim(self):
        for key in ('automaticSpeechPass','actualListening','actualFinalPlayback','actualPixelReview','humanApproval'):self.assertFalse(self.timing[key])
        self.assertFalse(self.timing['audioClock']['mixedAudioTimingAccepted']);self.assertIsNone(self.timing['audioClock']['finalMix'])
        self.assertFalse(self.timing['alignmentReview']['draftFractionTimingUsed'])

    def test_v5_migration_is_only_reviewed_binding_schema_and_output_changes(self):
        text=Path(m.__file__).read_text(encoding='utf-8')
        text=text.replace("    'build-solution-path-caption-timing-v4.py': 'ab71c9e3673bc9fff0c36169bf8a85d57f3b6294b1e3bc52372bcd614b5068cb',\n",'',1)
        text=text.replace('run-solution-path-voice-qa-v5.py','run-solution-path-voice-qa-v4.py').replace('1e03fc9b071e2542c662e2d27c6a8a5bcff65402c9e769d56dcf9d0bc7c7437c','fe1fd24796ad659f4c1b4c6e09cc1ef53732b1e912947f310c5b35b4c34ce076')
        text=text.replace('solution_caption_v5_','solution_caption_v4_').replace('11.05-selected-caption-timing-v5','11.05-selected-caption-timing-v4').replace("MEDIA / 'caption-timing-v5'","MEDIA / 'caption-timing-v4'")
        self.assertEqual(text,(HERE/'build-solution-path-caption-timing-v4.py').read_text(encoding='utf-8'))

    def test_old_v4_job_protocol_not_silently_accepted(self):
        p=Path(self.job['output'])/'job.json';original=p.read_bytes();j=copy.deepcopy(self.job);j['protocol']='architectural111-11-05-voice-asr-v4'
        try:
            dump(p,j)
            with patch.object(m.asr_adapter,'prepare_job',return_value=self.job):self.bad(m.verified_asr_review,Path(self.job['output'])/'review.json')
        finally:p.write_bytes(original)


if __name__=='__main__': unittest.main(verbosity=1)

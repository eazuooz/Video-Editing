"""Synthetic CPU numerical/provenance fixtures; never actual voice or tools."""
import contextlib,copy,importlib.util,io,json,math,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('zen_levels_cpu_fixture',HERE/'review-zen-view-audio-levels.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def rows_fixture(count=34):
    rows=[];scenes=[];position=0
    for i in range(count):
        frames=241+i;end=position+frames;text=f'실제 문장 {i}';scene_id=f'p{1+i*7//count:03}-c{i:02}'
        scenes.append(dict(id=scene_id,lines=[text]));rows.append(dict(sceneId=scene_id,paragraph=1+i*7//count,text=text,frames=frames,rate=24000,sourceSampleRange=[0,frames],destinationSampleRange=[position,end],prepared48kSampleRange=[position*2,end*2],normalization=dict(constantGainDb=3.,peakCapApplied=False,targetErrorDb=0.)))
        position=end
    voice=dict(fingerprint='current',identity=dict(scenes=scenes),aggregateWav=dict(path='canonical',sha256='raw',sampleRate=24000,frames=position))
    line=dict(componentCount=count,voiceFingerprint='current',rawCanonical=voice['aggregateWav'],components=rows,rawRate=24000,frames=position,originalRawFilesUnchanged=True,amplitudeOnlyScalarCopies=True,wordBoundariesShifted=False,voiceOffsetSeconds=0.,insertedSamples=0,trimmedSamples=0,voiceSpeed=1.,compressorUsed=False,voiceSideDuck=False)
    return voice,line,copy.deepcopy(rows)

def numerical_fixture(decline=False,stem_drop=False,music_close=False):
    rate=24000;per=9600;count=18;frames=per*count;times=np.arange(per)/rate
    amplitudes=np.geomspace(.16,.035,count)if decline else np.full(count,.1)
    raw=np.concatenate([a*np.sin(2*np.pi*317*times)for a in amplitudes]).astype(np.float32)[:,None]
    normalized=raw*2.;prepared=np.repeat(np.repeat(normalized,2,axis=0),2,axis=1);voice=prepared*.5
    if stem_drop:voice[len(voice)//2:]*=.15
    music=np.repeat(((.035 if music_close else .00005)*np.sin(2*np.pi*137*np.arange(len(voice))/48000)).astype(np.float32)[:,None],2,axis=1)
    arrays=dict(normalized=normalized,prepared=prepared,voice=voice,music=music,mix=voice+music)
    row=dict(sceneId='p001-c01',paragraph=1,frames=frames,sourceSampleRange=[0,frames],destinationSampleRange=[0,frames],prepared48kSampleRange=[0,frames*2],constantGainDb=20*math.log10(2),peakCapApplied=False,targetErrorDb=0.,rawTakeSHA256='raw',rawPcmSHA256='raw-pcm',normalizedTakeSHA256='normal')
    words=[dict(text=f'token{i}',timestamp=[i*.4,(i+1)*.4])for i in range(count)]
    ctx=dict(rows=[row],rawReview=dict(takes=[dict(globalWords=words)]),build=dict(voiceGlobalGain=dict(constantGainDb=-20*math.log10(2)),uniformMixGainDb=0.),resample=lambda x,rate:np.repeat(np.repeat(x[:,None],2,axis=0),2,axis=1))
    return ctx,arrays,[raw]

class LevelTests(unittest.TestCase):
    def test_exact_odd_raw24k_to48k_sample_grid(self):
        self.assertEqual(m.mathqa.scale_window(864001,864801,24000,48000),(1728002,1729602))
        self.assertEqual(m.mathqa.sample_window(.033333333333333333,.06666666666666667,24000),(799,1601))
    def test_variable14_and34_count_order_and_seven_paragraph_coverage(self):
        for count in (14,34):
            voice,line,proposed=rows_fixture(count);actual=m.validate_rows(voice,line,proposed)
            self.assertEqual(len(actual),count);self.assertEqual(actual[-1]['destinationSampleRange'][1],voice['aggregateWav']['frames'])
    def test_reordered_or_missing_component_rejected(self):
        voice,line,proposed=rows_fixture();line['components'][0],line['components'][1]=line['components'][1],line['components'][0]
        with self.assertRaises(ValueError):m.validate_rows(voice,line,proposed)
        voice,line,proposed=rows_fixture();line['components'].pop()
        with self.assertRaises(ValueError):m.validate_rows(voice,line,proposed)
    def test_stale_voice_and_proposal_gain_rejected(self):
        voice,line,proposed=rows_fixture();line['voiceFingerprint']='old'
        with self.assertRaises(ValueError):m.validate_rows(voice,line,proposed)
        voice,line,proposed=rows_fixture();line['components'][0]['normalization']['constantGainDb']=4.
        with self.assertRaises(ValueError):m.validate_rows(voice,line,proposed)
    def test_trim_compression_duck_or_shift_cannot_be_hidden(self):
        for key,value in [('trimmedSamples',1),('voiceOffsetSeconds',.1),('compressorUsed',True),('voiceSideDuck',True),('wordBoundariesShifted',True)]:
            voice,line,proposed=rows_fixture();line[key]=value
            with self.assertRaisesRegex(ValueError,'Forbidden speech'):m.validate_rows(voice,line,proposed)
    def test_nonconstant_or_out_of_range_gain_and_wrong_prepared_grid_rejected(self):
        row=rows_fixture()[1]['components'][0];row['normalization']['constantGainDb']=13
        with self.assertRaises(ValueError):m.scalar_row(row)
        row=rows_fixture()[1]['components'][0];row['prepared48kSampleRange'][1]+=1
        with self.assertRaises(ValueError):m.scalar_row(row)
    def test_stable_uniform_scalar_has_exact_known_stem_residuals(self):
        ctx,arrays,raws=numerical_fixture();result=m.numerical(ctx,arrays,raws)
        self.assertFalse(result['voiceFromPreparedResidual']['exceedsKnownStemTolerance']);self.assertFalse(result['mixFromKnownStemsResidual']['exceedsKnownStemTolerance'])
        self.assertEqual(result['normalizedCopyChecks'][0]['residual']['maximumAbsolute'],0)
        self.assertFalse(any(f['kind']=='sustained-word-body-decline'for f in result['suspectRegions']))
        self.assertTrue(all(abs(w['normalizedMinusCanonicalBodyDb']-20*math.log10(2))<1e-4 for w in result['words']))
    def test_within_take_decline_survives_global_scalar_not_hearing_pass(self):
        ctx,arrays,raws=numerical_fixture(decline=True);result=m.numerical(ctx,arrays,raws)
        stages={f['stage']for f in result['suspectRegions']if f['kind']=='sustained-word-body-decline'}
        self.assertTrue({'canonical','normalized','voice','mix'}<=stages)
    def test_processed_drop_distinguished_from_stable_raw(self):
        ctx,arrays,raws=numerical_fixture(stem_drop=True);result=m.numerical(ctx,arrays,raws)
        stages={f['stage']for f in result['suspectRegions']if f['kind']=='sustained-word-body-decline'}
        self.assertIn('voice',stages);self.assertNotIn('canonical',stages);self.assertTrue(result['voiceFromPreparedResidual']['exceedsKnownStemTolerance'])
    def test_known_music_ratio_is_not_snr_or_masking_claim(self):
        ctx,arrays,raws=numerical_fixture(music_close=True);result=m.numerical(ctx,arrays,raws)
        flags=[f for f in result['suspectRegions']if f['kind']=='music-close-to-known-voice-component']
        self.assertTrue(flags);self.assertTrue(all('not estimated SNR' in f['interpretation']for f in flags))
    def test_mix_sample_arithmetic_tamper_detected(self):
        ctx,arrays,raws=numerical_fixture();arrays['mix'][150,0]+=.001;result=m.numerical(ctx,arrays,raws)
        self.assertTrue(result['mixFromKnownStemsResidual']['exceedsKnownStemTolerance'])
        self.assertTrue(any(f.get('stage')=='mix-from-known-stems'for f in result['suspectRegions']))
    def test_same_length_prepared_shift_is_detected_before_global_voice_gain(self):
        ctx,arrays,raws=numerical_fixture();arrays['prepared']=np.roll(arrays['prepared'],2,axis=0);result=m.numerical(ctx,arrays,raws)
        self.assertTrue(result['preparedFromNormalizedResidual']['exceedsKnownStemTolerance'])
        self.assertTrue(any(f.get('stage')=='prepared-from-normalized'for f in result['suspectRegions']))
    def test_missing_raw_take_never_silently_zipped_away(self):
        ctx,arrays,raws=numerical_fixture()
        with self.assertRaises(ValueError):m.numerical(ctx,arrays,[])
    def test_actual_word_timestamp_outside_source_is_not_clamped_to_fake_coverage(self):
        ctx,arrays,raws=numerical_fixture();ctx['rawReview']['takes'][0]['globalWords'][0]['timestamp']=[-.1,.1]
        with self.assertRaises(ValueError):m.numerical(ctx,arrays,raws)
    def test_aac_alignment_uses_waveform_not_assumed1024_trim(self):
        rng=np.random.default_rng(773);reference=rng.normal(0,.04,(48000*3,2)).astype(np.float32);decoded=np.pad(reference,((173,0),(0,0)))
        result,flags=m.encoded_comparison(reference,decoded,[])
        self.assertTrue(result['alignment']['supported']);self.assertEqual(result['alignment']['decodedMinusReferenceSamples'],173);self.assertFalse(result['alignment']['audioModified'])
        self.assertTrue(any(f['kind']=='encoded-nonzero-comparison-offset'for f in flags))
    def test_aac_missing_initial_word_coverage_is_flagged_not_padded(self):
        rng=np.random.default_rng(774);reference=rng.normal(0,.04,(48000*3,2)).astype(np.float32)
        word=dict(sceneId='c1',recognizedText='첫말',recognizedContext='첫말 그대로',mixSampleRange=[0,4800],durationSeconds=.1,levels=dict(mix=m.mathqa.levels(reference[:4800],48000)))
        result,flags=m.encoded_comparison(reference,reference[80:],[word])
        self.assertEqual(result['alignment']['decodedMinusReferenceSamples'],-80);self.assertTrue(any(f['kind']=='encoded-word-window-not-covered'for f in flags))
    def test_ambiguous_aac_alignment_stays_unestablished(self):
        result,flags=m.encoded_comparison(np.zeros((48000*3,2)),np.zeros((48000*3,2)),[])
        self.assertFalse(result['alignment']['supported']);self.assertTrue(any(f['kind']=='encoded-alignment-not-established'for f in flags))
    def test_atomic_move_rebases_owned_artifact_paths_preserving_historical_argv(self):
        with tempfile.TemporaryDirectory(prefix='zen-levels-cpu-')as tmp:
            work=Path(tmp)/'work';target=Path(tmp)/'final';value=dict(wav=dict(path=str(work/'aac.wav'),sha256='same'),command=['ffmpeg',str(work/'aac.wav')],source=dict(path=str(Path(tmp)/'outside.wav'),sha256='keep'))
            result=m.rebased_proof(value,work,target)
            self.assertEqual(result['wav']['path'],str(target/'aac.wav'));self.assertEqual(result['wav']['producedAtPath'],str(work/'aac.wav'));self.assertEqual(result['command'],value['command']);self.assertEqual(result['source'],value['source'])
    def test_default_noargs_has_no_media_or_model_process(self):
        with patch.object(sys,'argv',['review-zen-view-audio-levels.py']),patch.object(m.subprocess,'Popen',side_effect=AssertionError('No process')),patch.object(m,'verify_bundle',side_effect=AssertionError('No actual media')),contextlib.redirect_stdout(io.StringIO())as out:m.main()
        result=json.loads(out.getvalue());self.assertFalse(result['ready']);self.assertFalse(result['mediaStarted']);self.assertFalse(result['modelStarted'])
    def test_media_process_requires_owned_worker(self):
        with patch.object(m.mathqa,'ffmpeg_path',return_value='ffmpeg'),patch.object(m.subprocess,'Popen',side_effect=AssertionError('No subprocess without owner')):
            with self.assertRaisesRegex(ValueError,'owned finite CPU worker'):m.run_tool(['ffmpeg','-i','fake'],'not-written.log')


if __name__=='__main__':unittest.main(verbosity=2)

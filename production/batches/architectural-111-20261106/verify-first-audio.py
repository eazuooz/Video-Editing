"""CPU synthetic fixtures only. No production mix, model, GPU or listening claim."""
import copy, importlib.util, json, math, sys, tempfile, unittest
from pathlib import Path
import numpy as np

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('first_audio_cpu_fixture',HERE/'prepare-first-audio.py')
audio=importlib.util.module_from_spec(spec);spec.loader.exec_module(audio)


class FirstAudioTests(unittest.TestCase):
    def tone(self,amplitude=.04,frames=24000):
        return (amplitude*np.sin(2*np.pi*300*np.arange(frames)/24000)).astype(np.float32)

    def test_single_scalar_preserves_prosody_silence_and_every_sample_position(self):
        samples=np.concatenate([np.zeros(113,np.float32),self.tone(.1),self.tone(.04),np.zeros(517,np.float32)])
        result,record=audio.match_paragraph(samples,24000)
        self.assertEqual(len(result),len(samples));self.assertEqual(record['trimmedSamples'],0)
        self.assertEqual(record['insertedSamples'],0);self.assertTrue(record['afterUsesSameRawActiveFrameMask'])
        gain=10**(record['constantGainDb']/20)
        np.testing.assert_allclose(result,samples*gain,rtol=1e-6,atol=1e-9)
        self.assertAlmostEqual(record['afterMedianDbfs'],-22,places=4)
        self.assertTrue(np.all(result[:113]==0));self.assertTrue(np.all(result[-517:]==0))

    def test_gain_limit_and_peak_limit_are_uniform_not_dynamic_compression(self):
        tiny=self.tone(.0003);result,record=audio.match_paragraph(tiny,24000)
        self.assertTrue(record['gainCapApplied']);self.assertEqual(record['constantGainDb'],12)
        loud=self.tone(.99);loud[13]=.999
        profile=copy.deepcopy(audio.PROFILE);profile['targetMedianDbfs']=-1
        result,record=audio.match_paragraph(loud,24000,profile)
        self.assertTrue(record['peakCapApplied']);self.assertLessEqual(float(np.max(np.abs(result))),.980001)
        np.testing.assert_allclose(result,loud*10**(record['constantGainDb']/20),rtol=1e-6,atol=1e-8)
        with self.assertRaises(ValueError):audio.match_paragraph(np.zeros(24000,np.float32),24000)

    def boundary_fixture(self):
        # Two odd-sized paragraphs retain the real aggregate's two extra samples.
        counts=[445441,384000,506880,468480,489600,433921];rate=24000;pos=0;entries=[];chunks=[]
        for i,n in enumerate(counts,1):
            entries.append(dict(scene_id=f's{i:02}',text='문단',start=pos/rate,end=(pos+n)/rate))
            chunks.append(dict(path=f'raw{i}.wav',sha256=f'hash{i}',pcmSHA256=f'pcm{i}',sampleRate=rate,channels=1,frames=n))
            pos+=n
        return dict(aggregateWav=dict(sampleRate=rate,frames=pos),sceneWavs=chunks),dict(entries=entries)

    def test_boundaries_retain_all_samples_without_rounding_or_adding_gap(self):
        evidence,timing=self.boundary_fixture();rows=audio.exact_boundaries(evidence,timing)
        self.assertEqual(rows[-1]['destinationSampleRange'][1],2728322)
        self.assertAlmostEqual(rows[-1]['endSeconds'],113.68008333333333)
        for left,right in zip(rows,rows[1:]):self.assertEqual(left['destinationSampleRange'][1],right['destinationSampleRange'][0])
        timing['entries'][3]['start']+=.28
        with self.assertRaises(AssertionError):audio.exact_boundaries(evidence,timing)

    def test_long_quiet_join_is_retained_verbatim(self):
        left=np.concatenate([self.tone(),np.zeros(57600,np.float32)])
        right=np.concatenate([np.zeros(6480,np.float32),self.tone()])
        a,_=audio.match_paragraph(left,24000);b,_=audio.match_paragraph(right,24000)
        combined=np.concatenate([a,b]);boundary=len(a)
        self.assertEqual(len(combined),len(left)+len(right))
        self.assertTrue(np.all(combined[boundary-57600:boundary+6480]==0))
        self.assertEqual((57600+6480)/24000,2.67)

    def test_only_bgm_is_ducked_and_recovers_after_speech(self):
        rate=48000
        voice=np.zeros((rate*3,2),np.float32);voice[rate//2:rate]=.1
        original=voice.copy();curve=audio.duck_curve(voice,rate)
        np.testing.assert_array_equal(voice,original)
        self.assertGreaterEqual(float(curve.min()),10**(-4/20)-1e-6)
        self.assertLess(float(curve[rate*3//4]),.64)
        self.assertGreater(float(curve[-1]),.995)
        self.assertTrue(np.all(curve<=1));self.assertTrue(np.all(curve>0))

    def test_music_is_one_continuous_native_speed_excerpt_with_end_fades(self):
        rate=1000;count=2000;source=np.repeat(np.arange(3000,dtype=np.float32)[:,None],2,axis=1)
        result=audio.music_bed(source,count,rate,1.,np.ones(count,np.float32))
        np.testing.assert_array_equal(result[500:1500],source[500:1500])
        self.assertEqual(result[0,0],0);self.assertEqual(result[-1,0],0)
        with self.assertRaises(ValueError):audio.music_bed(source,count+2000,rate,1.,np.ones(count+2000,np.float32))

    def test_normal_rate_resampling_keeps_impulse_and_odd_sample_boundaries(self):
        samples=np.zeros(1001,np.float32);samples[701]=.5
        result=audio.stereo_voice(samples,24000)
        self.assertEqual(result.shape,(2002,2));self.assertEqual(int(np.argmax(result[:,0])),1402)
        np.testing.assert_array_equal(result[:,0],result[:,1])

    def test_receipted_version_reuses_only_verified_files_and_never_overwrites(self):
        with tempfile.TemporaryDirectory(prefix='yamyam-first-audio-cpu-') as name:
            folder=Path(name)/'version';folder.mkdir();artifact=folder/'voice.wav';artifact.write_bytes(b'fixture')
            recipe=dict(fingerprint='fp')
            receipt=dict(fingerprint='fp',artifacts={'voice':dict(file='voice.wav',sha256=audio.sha(artifact))})
            audio.save(folder/'audio-build.json',receipt)
            self.assertEqual(audio.reuse(folder,recipe),receipt)
            artifact.write_bytes(b'changed')
            with self.assertRaises(AssertionError):audio.reuse(folder,recipe)
            self.assertEqual(artifact.read_bytes(),b'changed')

    def legacy_fixture(self):
        raw=((np.arange(4000,dtype=np.int32)-2000)/32768).astype(np.float32)
        aggregate,n=audio.legacy_fade_pcm16(raw,24000)
        contract=dict(auditedEngineSHA256=audio.LEGACY_ENGINE_SHA,currentEngineSHA256=audio.LEGACY_ENGINE_SHA,
            requestedEdgeFadeSeconds=0,voiceIdentityEdgeFadeSeconds=0,aggregateSampleWidthBytes=2,rawSampleWidthBytes=2)
        return raw,aggregate,contract,n

    def test_exact_pinned_legacy_fade_quantization_is_proven_without_touching_raw(self):
        raw,aggregate,contract,n=self.legacy_fixture();original=raw.copy()
        result=audio.aggregate_comparison(raw,aggregate,24000,contract)
        self.assertFalse(result['exactRawAggregateEquality']);self.assertTrue(result['legacyAggregateFadeProven'])
        self.assertTrue(result['deterministicExpectedAggregateEquality']);self.assertEqual(n,144)
        self.assertTrue(all(i<n or i>=len(raw)-n for i in result['rawLocalDifferenceSampleIndices']))
        np.testing.assert_array_equal(raw,original)
        normalized,_=audio.match_paragraph(raw,24000)
        self.assertEqual(len(normalized),len(raw));self.assertFalse(result['aggregateModified']);self.assertFalse(result['hearingPerformed'])

    def test_legacy_exception_rejects_interior_edge_tampering_and_changed_raw(self):
        raw,aggregate,contract,_=self.legacy_fixture()
        for index in (9,500,len(raw)-9):
            changed=aggregate.copy();changed[index]+=1/32768
            with self.assertRaises(AssertionError):audio.aggregate_comparison(raw,changed,24000,contract)
        changed_raw=raw.copy();changed_raw[500]+=1/32768
        with self.assertRaises(AssertionError):audio.aggregate_comparison(changed_raw,aggregate,24000,contract)

    def test_legacy_exception_rejects_other_engine_or_nonzero_manifest_profile(self):
        raw,aggregate,contract,_=self.legacy_fixture()
        for key,value in [('auditedEngineSHA256','other'),('currentEngineSHA256','other'),
            ('requestedEdgeFadeSeconds',.006),('voiceIdentityEdgeFadeSeconds',.006),('aggregateSampleWidthBytes',4),('rawSampleWidthBytes',4)]:
            changed=dict(contract,**{key:value})
            with self.assertRaisesRegex(AssertionError,'outside pinned legacy'):
                audio.aggregate_comparison(raw,aggregate,24000,changed)

    def test_exact_unchanged_aggregate_is_described_as_exact_without_claiming_legacy_fade(self):
        raw,_,contract,_=self.legacy_fixture();result=audio.aggregate_comparison(raw,raw.copy(),24000,contract)
        self.assertTrue(result['exactRawAggregateEquality']);self.assertEqual(result['differingSamples'],0)
        self.assertNotIn('legacyAggregateFadeProven',result)


if __name__=='__main__':unittest.main(verbosity=2)

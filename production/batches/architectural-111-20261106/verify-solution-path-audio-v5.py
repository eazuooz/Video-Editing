"""Pure/synthetic CPU fixtures for the no-execute11.05 audio preparation adapter."""
from pathlib import Path
import copy, hashlib, importlib.util, json, sys, tempfile, unittest, wave
from unittest.mock import patch
import numpy as np
import soundfile as sf
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('solution_audio_v5_cpu',HERE/'prepare-solution-path-audio-v5.py')
m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)

def fixture(root,extra=False):
    scenes=[]; takes=[]; entries=[]; mapping=[]; arrays=[]; position=0
    for paragraph in range(1,15):
        count=3 if extra and paragraph==1 else 2
        for component in range(1,count+1):
            sid=f'p{paragraph:03d}-c{component:02d}'; text=f'합성 문장 {paragraph}의 {component}입니다.'
            values=(np.sin(np.arange(2400)*.07)*(.04+component*.005)).astype(np.float32)
            path=root/(sid+'.wav'); sf.write(path,values,24000,subtype='PCM_16')
            with wave.open(str(path),'rb') as f: pcm=f.readframes(f.getnframes())
            frames=len(pcm)//2; take=dict(path=str(path),sha256=m.sha(path),pcmSHA256=hashlib.sha256(pcm).hexdigest(),frames=frames,sampleRate=24000,channels=1,sampleWidthBytes=2)
            scenes.append(dict(id=sid,lines=[text])); takes.append(take)
            entries.append(dict(scene_id=sid,text=text,start=position/24000,end=(position+frames)/24000))
            mapping.append(dict(sceneId=sid,paragraph=paragraph,canonicalText=text))
            arrays.append(sf.read(path,dtype='float32')[0]); position+=frames
    aggregate=root/'aggregate.wav'; sf.write(aggregate,np.concatenate(arrays),24000,subtype='PCM_16')
    voice=dict(fingerprint='f'*64,identity=dict(scenes=scenes),sceneWavs=takes,paragraphMapping=mapping,
               aggregateWav=dict(path=str(aggregate),frames=position,sha256=m.sha(aggregate)),timing=dict(path='synthetic-timing',sha256='a'*64))
    return voice,dict(entries=entries)

class AudioPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.audio,cls.qa=m.primitives()
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='11-05-audio-cpu-'); self.addCleanup(self.temp.cleanup); self.root=Path(self.temp.name)
    def test_no_voice_stops_before_profile_modules_or_pcm(self):
        with patch.object(m,'VOICE',self.root/'missing.json'),patch.object(m,'primitives',side_effect=AssertionError('no profile/model/PCM imports')):
            with self.assertRaisesRegex(m.Pending,'actual completed'): m.prepare()
    def test_variable_complete_component_count(self):
        voice,timing=fixture(self.root,extra=True); rows=m.exact_components(voice,timing)
        self.assertEqual(len(rows),29); self.assertEqual(rows[-1]['prepared48kSampleRange'][1],voice['aggregateWav']['frames']*2)
    def test_one_raw_sample_clock_shift_rejected(self):
        voice,timing=fixture(self.root); timing['entries'][3]['end']+=1/24000
        with self.assertRaisesRegex(m.Pending,'sample clock'): m.exact_components(voice,timing)
    def test_reordered_raw_mapping_rejected(self):
        voice,timing=fixture(self.root); voice['paragraphMapping'][0],voice['paragraphMapping'][1]=voice['paragraphMapping'][1],voice['paragraphMapping'][0]
        with self.assertRaisesRegex(m.Pending,'ordered sentence'): m.exact_components(voice,timing)
    def test_sustained_word_decline_held_before_reading_any_audio(self):
        with self.assertRaisesRegex(m.Pending,'Sustained within-take'):
            m.scalar_proposal(self.audio,{},[],{},dict(flags=[dict(kind='sustained-take-word-body-decline')]),[])
    def proposal(self):
        voice,timing=fixture(self.root); rows=m.exact_components(voice,timing)
        review=dict(takes=[dict(task=dict(sceneId=r['sceneId']),text=r['text'],comparison=dict(recognizedLiteral=r['text'])) for r in rows])
        before={str(p):m.sha(p) for p in self.root.glob('*.wav')}
        result=m.scalar_proposal(self.audio,voice,rows,review,dict(flags=[]),[])
        return result,before
    def test_working_scalar_proposal_preserves_original_pcm_and_all_frames(self):
        result,before=self.proposal(); rows=result['identity']['components']
        self.assertEqual(before,{str(p):m.sha(p) for p in self.root.glob('*.wav')})
        self.assertEqual(len(rows),28); self.assertEqual(rows[-1]['destinationSampleRange'][1],result['identity']['canonicalWav']['frames'])
        self.assertTrue(all(r['normalization']['trimmedSamples']==r['normalization']['insertedSamples']==0 and r['normalization']['speechSpeed']==1 for r in rows))
        self.assertFalse(result['audioWritten']); self.assertFalse(result['automaticSpeechPass'])
    def test_stale_or_held_disposition_cannot_enable_normalization(self):
        result,_=self.proposal(); path=self.root/'decisions.json'; path.write_text(json.dumps(dict(topicId='06.02')),encoding='utf-8')
        with self.assertRaisesRegex(m.Pending,'exact current proposal'): m.component_dispositions(result,path,{}, {})
    def test_music_crossfade_preserves_rate_phase_and_target_length(self):
        # Two native-rate source copies overlap music only, never voice.
        signal=np.repeat(np.linspace(-.1,.1,120,dtype=np.float32)[:,None],2,axis=1)
        out,proof=self.audio.loop_music(signal,200,20)
        self.assertEqual(out.shape,(200,2)); self.assertEqual(proof['crossfadeSamples'],20)
        self.assertEqual(proof['repeatCount'],1); self.assertFalse(proof['speechSamplesChanged'])
    def test_same_pinned_profile_and_music_only_shortfall(self):
        self.assertEqual(self.audio.PROFILE['voiceTargetLufs'],-16.); self.assertEqual(self.audio.PROFILE['musicTargetLufs'],-35.)
        c=self.audio.music_headroom_compensation(dict(constantGainDb=2.,desiredGainDb=7.))
        self.assertEqual(c['compensationDb'],-5.); self.assertFalse(c['voicePcmOrGainChanged'])
        self.assertLessEqual(c['linearFactor'],1.)
    def test_current_text_and_real_licensed_asset_plan_match_profile(self):
        result=m.asset_binding(self.audio,m.read(m.PROJECT/'narration-final-v4.json'))
        self.assertTrue(result['currentTextMatchesAssetPlan']); self.assertEqual(result['rights']['license'],'CC BY4.0')
        self.assertFalse(result['actualListening'])
    def test_none_is_not_an_internal_review_note(self): self.assertFalse(m.note(None)); self.assertFalse(m.note(' '))
    def test_no_execute_or_foreign_producer_entry_reused(self):
        source=Path(m.__file__).read_text(encoding='utf-8')
        self.assertNotIn('def execute(',source); self.assertNotIn('audio.prepare(',source); self.assertNotIn('audio.execute(',source)
    def test_v5_migration_reverses_exactly_to_frozen_v4_no_dsp_change(self):
        text=Path(m.__file__).read_text(encoding='utf-8')
        text=text.replace("PINS={'prepare-solution-path-audio-v4.py':'88757e286c682e00bcdab64141762f17664bd534765922694bf3307a780d36c5',",'PINS={',1)
        text=text.replace('run-solution-path-voice-qa-v5.py','run-solution-path-voice-qa-v4.py').replace('1e03fc9b071e2542c662e2d27c6a8a5bcff65402c9e769d56dcf9d0bc7c7437c','fe1fd24796ad659f4c1b4c6e09cc1ef53732b1e912947f310c5b35b4c34ce076')
        text=text.replace('architectural111-11-05-audio-preparation-v5','architectural111-11-05-audio-preparation-v4')
        self.assertEqual(text,(HERE/'prepare-solution-path-audio-v4.py').read_text(encoding='utf-8'))
    def test_old_review_path_rejected_before_summary_or_any_write(self):
        from types import SimpleNamespace
        old=self.root/'old-v4'/'review.json';old.parent.mkdir();old.write_text('{}',encoding='utf-8')
        qa=SimpleNamespace(prepare_job=lambda:dict(output=str(self.root/'new-v5')),summary=lambda job:(_ for _ in ()).throw(AssertionError('No old review promotion')))
        with self.assertRaisesRegex(m.Pending,'Exact current complete blind-ASR'):m.verified_asr(qa,old)

if __name__=='__main__': unittest.main(verbosity=1)

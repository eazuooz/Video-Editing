"""Synthetic CPU tests only; no real PCM/ASR/FFmpeg/model/resource query."""
from pathlib import Path
import copy, hashlib, importlib.util, json, sys, tempfile, unittest
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
import soundfile as sf
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('solution_mix_cpu',HERE/'prepare-solution-path-audio-mix-v4.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)

class MixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prep=m.dependencies();cls.audio,_=cls.prep.primitives()
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='11-05-mix-cpu-');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
    def voice(self,size=4801):return (np.sin(np.arange(size)*.04)*.06).astype(np.float32)
    def music(self,size=144001):return np.repeat((np.sin(np.arange(size)*.03)*.05).astype(np.float32)[:,None],2,axis=1)
    def build(self):return m.assemble_stems(self.audio,self.voice(),self.music(),dict(input_i='-20',input_tp='-18'),dict(input_i='-20',input_tp='-18'))
    def test_absent_dispositions_stop_before_modules_decode_or_worker(self):
        with patch.object(m,'dependencies',side_effect=AssertionError('No PCM/profile import')):
            with self.assertRaisesRegex(m.Pending,'before PCM decode'):m.prepare(None,None,None)
    def test_current_odd_raw_clock_preserves_last_sample(self):
        frames=5088001
        self.assertEqual(frames*2,10176002);self.assertEqual((frames*60+23999)//24000,12721)
        built=self.build();self.assertEqual(built['prepared'].shape,(9602,2));self.assertEqual(built['mix'].shape,(9602,2))
    def test_one_whole_voice_resample_and_sum_exact(self):
        normalized=self.voice();expected=self.audio.base.stereo_voice(normalized,24000);built=self.build()
        self.assertTrue(np.array_equal(expected,built['prepared']))
        self.assertTrue(np.array_equal(built['voice']+built['music'],built['mix']))
        self.assertEqual(m.float_sha(built['mix']),hashlib.sha256(np.asarray(built['mix'],dtype='<f4').tobytes()).hexdigest())
    def test_scalar_source_arrays_unchanged(self):
        normalized=self.voice();music=self.music();a=normalized.copy();b=music.copy()
        m.assemble_stems(self.audio,normalized,music,dict(input_i=-20,input_tp=-18),dict(input_i=-20,input_tp=-18))
        self.assertTrue(np.array_equal(normalized,a));self.assertTrue(np.array_equal(music,b))
    def test_peak_failure_holds_without_global_attenuation(self):
        # Force a nominal music bed that would exceed the mix ceiling.
        with patch.object(self.audio.base,'music_bed',side_effect=lambda source,count,*args:np.ones((count,2),np.float32)):
            with self.assertRaisesRegex(m.Pending,'without attenuating voice'):self.build()
    def test_nonfinite_measurement_cannot_enter_gain_math(self):
        with self.assertRaisesRegex(m.Pending,'Finite actual loudness'):
            m.assemble_stems(self.audio,self.voice(),self.music(),dict(input_i=float('nan'),input_tp=-18),dict(input_i=-20,input_tp=-18))
    def test_music_loop_boundary_proof_is_exact_rebuild(self):
        source=self.music(144000);a,plan=self.audio.loop_music(source,240001,48000)
        b,again=self.audio.loop_music(source,240001,48000)
        self.assertTrue(np.array_equal(a,b));self.assertEqual(plan,again);self.assertEqual(plan['repeatCount'],2)
        self.assertFalse(plan['speechSamplesChanged']);self.assertEqual(plan['seams'][0]['actualMusicBoundarySamples']['at'],a[96000].tolist())
    def test_immutable_outputs_never_replace_differing_bytes(self):
        path=self.root/'test.bin';m.immutable(path,b'one');m.immutable(path,b'one')
        with self.assertRaisesRegex(m.Pending,'Preserve differing'):m.immutable(path,b'two')
        self.assertEqual(path.read_bytes(),b'one')
    def test_artifact_escape_and_changed_hash_rejected(self):
        source=self.root/'good.bin';source.write_bytes(b'good')
        for name,row in [('../escape',dict(file='../escape',sha256='0'*64)),('good.bin',dict(file='good.bin',sha256='0'*64))]:
            with self.assertRaises(m.Pending):m.verify_artifacts(self.root,dict(artifacts={name:row}))
    def test_source_or_input_snapshot_tamper_rejected(self):
        with patch.object(m,'SELF_SHA','0'*64):
            with self.assertRaisesRegex(m.Pending,'changed after import'):m.check_sources()
    def tool_receipt(self):
        folder=self.root;request=folder/'tool-receipts/a.request.json';request.parent.mkdir()
        command=['C:/ffmpeg.exe','-i','source.mp3']
        m.immutable_json(request,dict(command=command,producerSHA256=m.SELF_SHA,recipeFingerprint='f'*64))
        stdout=folder/'tool-receipts/a.stdout.bin';stderr=folder/'tool-receipts/a.stderr.bin';stdout.write_bytes(b'decoded');stderr.write_bytes(b'log')
        result=folder/'tool-receipts/a.result.json';m.immutable_json(result,dict(request=m.local_pin(folder,request),exitCode=0,stdout=m.local_pin(folder,stdout),stderr=m.local_pin(folder,stderr)))
        artifacts={p.relative_to(folder).as_posix():m.local_pin(folder,p) for p in folder.rglob('*') if p.is_file()}
        return folder,m.local_pin(folder,result),artifacts,command
    def test_tool_receipt_binds_actual_command_source_and_outputs(self):
        folder,row,artifacts,command=self.tool_receipt()
        self.assertEqual(m.verify_tool_receipt(folder,row,artifacts,command,'f'*64),(b'decoded',b'log'))
        with self.assertRaises(m.Pending):m.verify_tool_receipt(folder,row,artifacts,command+['changed'],'f'*64)
    def test_live_launch_gap_preserves_marker_after_coordinator_dies(self):
        process=SimpleNamespace(info=dict(name='ffmpeg.exe',cmdline=['C:/ffmpeg.exe','-i','own.wav']))
        runtime=SimpleNamespace(psutil=SimpleNamespace(process_iter=lambda fields:[process],NoSuchProcess=LookupError,AccessDenied=PermissionError),alive=lambda record:False)
        record=dict(phase='launching-owned-audio-tool',child=None,launchCommand=['C:/ffmpeg.exe','-i','own.wav'])
        self.assertTrue(m.owned_alive(runtime,record))
    def test_new_producer_uses_no_gpu_lease_acquire_or_foreign_delete(self):
        source=Path(m.__file__).read_text(encoding='utf-8')
        self.assertNotIn('recover_own_lease(',source);self.assertNotIn('LEASE.unlink',source);self.assertNotIn('.terminate(',source)
        self.assertIn('resource.busy_reason()',source)

    def synthetic_complete(self):
        """Small independent raw/stem files plus fake tool receipts; no tool runs."""
        rawdir=self.root/'raw';rawdir.mkdir();parts=[];rows=[];position=0
        for p in range(1,15):
            sid=f'p{p:03d}-c01';path=rawdir/(sid+'.wav');sf.write(path,self.voice(2400+(p==14)),24000,subtype='PCM_16')
            samples,_=sf.read(path,dtype='float32');matched,gain=self.audio.base.match_paragraph(samples,24000,self.audio.PROFILE)
            row=dict(sceneId=sid,paragraph=p,text='Synthetic source.',rawTake=str(path),rawTakeSHA256=m.sha(path),
                rawPcmSHA256='a'*64,sourceSampleRange=[0,len(samples)],destinationSampleRange=[position,position+len(samples)],
                prepared48kSampleRange=[position*2,(position+len(samples))*2],frames=len(samples),rate=24000,normalization=gain)
            rows.append(row);parts.append(samples);position+=len(samples)
        aggregate=rawdir/'canonical.wav';sf.write(aggregate,np.concatenate(parts),24000,subtype='PCM_16')
        canonical=dict(path=str(aggregate),sha256=m.sha(aggregate),frames=position,sampleRate=24000,channels=1,sampleWidthBytes=2,pcmSHA256='b'*64)
        timing=dict(path=str(rawdir/'timing.json'),sha256='c'*64)
        proposal=dict(identity=dict(canonicalWav=canonical,canonicalTiming=timing,voiceFingerprint='d'*64,componentCount=14,components=rows))
        snapshot=rawdir/'proof.json';snapshot.write_text('{}',encoding='utf-8')
        recipe_identity=dict(sourcePins=[m.pin(snapshot)],syntheticOnly=True)
        recipe=dict(identity=recipe_identity,fingerprint=m.digest(recipe_identity))
        dest=self.root/'dest';folder=dest/recipe['fingerprint'][:24];folder.mkdir(parents=True)
        work=dest/('work-'+recipe['fingerprint'][:16]+'-'+'a'*10)
        normalized,records=m.normalized_voice(self.audio,proposal)
        built=m.assemble_stems(self.audio,normalized,self.music(),dict(input_i='-20',input_tp='-18'),dict(input_i='-20',input_tp='-18'))
        for row in records:
            a,b=row['destinationSampleRange'];name=row['sceneId']+'-normalized.wav';sf.write(folder/name,normalized[a:b],24000,subtype='FLOAT')
            row.update(normalizedTake=name,normalizedTakeSHA256=m.sha(folder/name),normalizedTakeFloat32PcmSHA256=m.float_sha(normalized[a:b]),
                normalizationScope='One reviewed scalar over the complete selected raw sentence; natural lead/tail unchanged')
        m.immutable_json(folder/'input-recipe.json',recipe)
        m.immutable(folder/'source-snapshots/000.bin',snapshot.read_bytes())
        m.immutable_json(folder/'line-levels.json',dict(schemaVersion='11.05-line-levels-v4',componentCount=14,components=records,
            rawCanonical=canonical,voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0,voiceSpeed=1.,wordBoundariesShifted=False))
        for name,values,rate in [('narration-component-normalized.wav',normalized,24000),('narration-prepared-stem.wav',built['prepared'],48000),
            ('narration-stem.wav',built['voice'],48000),('music-stem.wav',built['music'],48000),('final-mix.wav',built['mix'],48000),('music-source-decoded.wav',self.music(),48000)]:sf.write(folder/name,values,rate,subtype='FLOAT')
        measures=dict(voice=dict(input_i='-20',input_tp='-18'),music=dict(input_i='-20',input_tp='-18'),mix=dict(input_i='-16',input_tp='-2'))
        m.immutable_json(folder/'loudness-measurements.json',measures);m.immutable_json(folder/'music-loop-plan.json',built['loop'])
        def receipt(role,command,stdout,stderr):
            stem=folder/'tool-receipts'/role;request=stem.with_suffix('.request.json');out=stem.with_suffix('.stdout.bin');err=stem.with_suffix('.stderr.bin');result=stem.with_suffix('.result.json')
            m.immutable_json(request,dict(command=command,producerSHA256=m.SELF_SHA,recipeFingerprint=recipe['fingerprint']));m.immutable(out,stdout);m.immutable(err,stderr)
            m.immutable_json(result,dict(request=m.local_pin(folder,request),exitCode=0,stdout=m.local_pin(folder,out),stderr=m.local_pin(folder,err)))
            return m.local_pin(folder,result)
        measurements={}
        for role,path in [('voice',work/'narration-prepared-stem.wav'),('music',self.audio.MUSIC),('mix',work/'final-mix.wav')]:
            measurements[role]=receipt(role,m.tool_command(self.audio.base.FF,m.loudness_args(path)),b'',json.dumps(measures[role]).encode())
        decoded=receipt('decode',m.tool_command(self.audio.base.FF,['-v','error','-i',self.audio.MUSIC,'-map','0:a:0','-ar','48000','-ac','2','-f','f32le','pipe:1']),self.music().astype('<f4').tobytes(),b'')
        assets=dict(rights=dict(requiredDescriptionCredit='Synthetic CC attribution',license='synthetic-only'))
        ctx=dict(proposal=proposal,_audio=self.audio,decisionPin=dict(path='syntheticdecisions',sha256='e'*64),asrPin=dict(path='syntheticASR',sha256='f'*64),levelPin=dict(path='syntheticlevels',sha256='0'*64),assets=assets)
        artifacts={p.relative_to(folder).as_posix():m.local_pin(folder,p) for p in folder.rglob('*') if p.is_file()}
        lineage=dict(normalized24kMonoFloat32SHA256=m.float_sha(normalized),prepared48kStereoFloat32SHA256=m.float_sha(built['prepared']),
            finalVoice48kStereoFloat32SHA256=m.float_sha(built['voice']),finalMusic48kStereoFloat32SHA256=m.float_sha(built['music']),finalMix48kStereoFloat32SHA256=m.float_sha(built['mix']),voiceOffsetSamples=0,rawToPreparedSampleRatio=[2,1],voiceSpeed=1.)
        report=dict(schemaVersion=m.SCHEMA,topicId='11.05',fingerprint=recipe['fingerprint'],output=str(folder),workOrigin=str(work),artifacts=artifacts,
            rawVoice=canonical,canonicalTiming=timing,rawVoiceFingerprint='d'*64,selectedComponentCount=14,acceptedComponentsReview=ctx['decisionPin'],rawVoiceAsr=ctx['asrPin'],rawNumericalLevelReview=ctx['levelPin'],
            pcmLineage=lineage,voiceGlobalGain=built['voiceGain'],musicNominalGain=built['nominalMusicGain'],musicGain=built['musicGain'],musicOnlyCompensation=built['musicCompensation'],
            musicLoopPlan=built['loop'],musicLoops=0,musicContinuousExcerpt=True,musicPlaybackRate=1.,musicPlaybackContinuous=True,musicAttribution='Synthetic CC attribution',musicRights=assets['rights'],
            mixWav=m.artifact(folder,'final-mix.wav'),durationSeconds=position/24000,videoFrameTarget=dict(fps=60,totalFrames=(position*60+23999)//24000,noAudioTailPadding=True),
            measuredPcmMix=measures['mix'],measurementReceipts=measurements,musicDecodeReceipt=decoded,voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0,voiceSpeed=1.,
            compressorUsed=False,voiceSideDuck=False,uniformMixGainDb=0.,originalRawFilesUnchanged=True,wordBoundariesShifted=False,
            engineAggregatePreservedSeparately=True,finalMixedAsr='pending',encodedAacTruePeak='pending',finalMovieComplete=False,
            status='mix-prepared-mixed-ASR-encoded-AAC-listening-pending',platformActions=[],actualListening=False,automaticSpeechPass=False,humanApproval=False)
        path=folder/'audio-build.json';m.immutable_json(path,report);return dest,path,report,ctx,recipe
    def test_complete_verifier_rebuilds_actual_small_float_files(self):
        dest,path,report,ctx,recipe=self.synthetic_complete()
        with patch.object(m,'DEST',dest),patch.object(m,'prepare',return_value=(ctx,recipe)):
            self.assertEqual(m.verify_existing_core(path),report)
    def test_rebound_final_voice_pcm_tamper_is_rejected(self):
        dest,path,report,ctx,recipe=self.synthetic_complete();stem=path.parent/'narration-stem.wav';samples,rate=sf.read(stem,dtype='float32');samples[10,0]+=.01;sf.write(stem,samples,rate,subtype='FLOAT')
        report['artifacts'][stem.name]=m.local_pin(path.parent,stem);path.write_text(json.dumps(report),encoding='utf-8')
        with patch.object(m,'DEST',dest),patch.object(m,'prepare',return_value=(ctx,recipe)):
            with self.assertRaisesRegex(m.Pending,'stem/sample math differs'):m.verify_existing_core(path)
    def test_immutable_output_path_cannot_be_rebound(self):
        dest,path,report,ctx,recipe=self.synthetic_complete();other=path.parent/'foreign.json';other.write_bytes(path.read_bytes())
        with patch.object(m,'DEST',dest),patch.object(m,'prepare',return_value=(ctx,recipe)):
            with self.assertRaisesRegex(m.Pending,'path/recipe'):m.verify_existing_core(other)
    def test_rebound_music_plan_cannot_change_native_rate(self):
        dest,path,report,ctx,recipe=self.synthetic_complete();loop=path.parent/'music-loop-plan.json';changed=m.read(loop);changed['sourceCopies']=99
        loop.write_text(json.dumps(changed),encoding='utf-8');report['musicLoopPlan']=changed;report['artifacts'][loop.name]=m.local_pin(path.parent,loop);path.write_text(json.dumps(report),encoding='utf-8')
        with patch.object(m,'DEST',dest),patch.object(m,'prepare',return_value=(ctx,recipe)):
            with self.assertRaisesRegex(m.Pending,'music phase/seam'):m.verify_existing_core(path)
    def test_rebound_input_snapshot_cannot_change_recipe_source(self):
        dest,path,report,ctx,recipe=self.synthetic_complete();source=path.parent/'source-snapshots/000.bin';source.write_bytes(b'changed')
        report['artifacts']['source-snapshots/000.bin']=m.local_pin(path.parent,source);path.write_text(json.dumps(report),encoding='utf-8')
        with patch.object(m,'DEST',dest),patch.object(m,'prepare',return_value=(ctx,recipe)):
            with self.assertRaisesRegex(m.Pending,'source/input snapshot'):m.verify_existing_core(path)
    def test_known_live_asr_marker_blocks_before_resource_or_launch(self):
        m.immutable_json(self.root/'11-05-asr-v4-worker.json',dict(pid=999,child=dict(pid=1000)))
        runtime=SimpleNamespace(alive=lambda record:bool(record))
        resource=SimpleNamespace(busy_reason=lambda:(_ for _ in ()).throw(AssertionError('Known ASR should block first')))
        with patch.object(m,'MEDIA',self.root),patch.object(m,'authorize'):
            with self.assertRaisesRegex(m.Pending,'Another live/unknown111 worker'):m.fresh_serial_gate(runtime,resource)
    def test_documentary_music_and_pending_review_fields_cannot_drift(self):
        dest,path,report,ctx,recipe=self.synthetic_complete()
        for key,value in [('musicRights',{}),('musicAttribution','differentcredit'),('musicLoops',99),('musicContinuousExcerpt',False),
            ('musicPlaybackRate',2.),('finalMixedAsr','passed'),('encodedAacTruePeak','passed'),('finalMovieComplete',True),('actualListening',True)]:
            with self.subTest(key=key):
                changed=copy.deepcopy(report);changed[key]=value;path.write_text(json.dumps(changed),encoding='utf-8')
                with patch.object(m,'DEST',dest),patch.object(m,'prepare',return_value=(ctx,recipe)):
                    with self.assertRaises(m.Pending):m.verify_existing_core(path)
    def test_explicit_v5_proposal_binding_preserves_frozen_v4(self):
        self.assertEqual(m.PINS['prepare-solution-path-audio-v5.py'],'b3a5e4566e1b304cdabc8f0e13d1dad2e0711d1dc8775665e1bd4bf88c664217')
        self.assertEqual(m.sha(HERE/'prepare-solution-path-audio-v4.py'),'88757e286c682e00bcdab64141762f17664bd534765922694bf3307a780d36c5')

if __name__=='__main__':unittest.main(verbosity=1)

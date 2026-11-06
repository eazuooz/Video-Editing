"""CPU-only, finite03.02 paragraph matching and BGM stems; never changes raw PCM.

Default prints a read-only preflight. --execute writes a new immutable C-media
version after exact raw-voice ASR evidence exists. It neither encodes a movie nor
performs ASR, TTS, GPU work, actual listening or a platform operation.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, io, json, math, os, re, subprocess, uuid
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from initialize import HERE, ROOT, MEDIA, read, save


def module(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


asr=module('first_audio_asr_prerequisite',HERE/'run-first-asr.py')
SLUG=asr.SLUG;PROJECT=asr.PROJECT
DEST=MEDIA/SLUG/'audio-preparation-v1'
WORKER=MEDIA/'first-audio-worker.json'
MUSIC=ROOT/'shared/assets/music/incompetech/Pixel-Peeker-Polka-faster.mp3'
LICENSE=MUSIC.with_suffix('.LICENSE.md')
MUSIC_SHA='b2609a077fae292679f25b83519f470ed308abb40d11f89bff8c6f896deefed3'
LEGACY_ENGINE_SHA='cde46536ba7f4050b2677c3d8d12379d447675b353cf7b843441049abd7489dc'
FF=Path(os.environ.get('YAMYAM_FFMPEG','C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe'))
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
PROFILE=dict(policy='line-level-takes-v1',frameSeconds=.05,gateMaximumDbfs=-25.,adaptiveGateBelowPeakDb=25.,
    targetMedianDbfs=-22.,maximumGainDb=12.,paragraphSamplePeakCeilingDbfs=20*math.log10(.98),
    voiceTargetLufs=-16.,voiceSamplePeakCeilingDbfs=-3.,musicTargetLufs=-35.,musicSamplePeakCeilingDbfs=-12.,
    backgroundSpeechDuckDb=4.,duckAttackMs=15.,duckReleaseMs=280.,speechEnvelopeFloorDbfs=-42.,
    speechEnvelopeFullDbfs=-30.,musicFadeSeconds=.45,musicSpeed=1.,voiceSpeed=1.,voiceOffsetSeconds=0.,
    mixSamplePeakCeilingDbfs=-2.3,mixTruePeakMaximumDbtp=-1.5,mixRate=48000,mixChannels=2,
    silenceInsertedSamples=0,trimmedSamples=0,narrationCompressor=None,voiceSideDuck=False)


def sha(path):return asr.voice.sha(path)
def digest(value):return asr.digest(value)
def db(value):return 20*math.log10(max(float(value),1e-12))


def run(args):
    result=subprocess.run([str(a) for a in args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=CREATE)
    if result.returncode:raise RuntimeError(result.stderr.decode(errors='replace')[-5000:])
    return result


def frame_levels(samples,rate,seconds=.05):
    hop=max(1,round(rate*seconds))
    return np.array([db(np.sqrt(np.mean(samples[i:i+hop].astype(np.float64)**2)))
                     for i in range(0,len(samples),hop)])


def match_paragraph(samples,rate,profile=PROFILE):
    if samples.ndim!=1 or not len(samples) or not np.isfinite(samples).all():raise ValueError('Invalid raw mono paragraph')
    levels=frame_levels(samples,rate,profile['frameSeconds'])
    if float(levels.max())<=-100:raise ValueError('Silent paragraph is not a speech take')
    gate=min(profile['gateMaximumDbfs'],float(levels.max())-profile['adaptiveGateBelowPeakDb'])
    mask=levels>=gate;before=float(np.median(levels[mask]))
    desired=profile['targetMedianDbfs']-before
    capped=float(np.clip(desired,-profile['maximumGainDb'],profile['maximumGainDb']))
    peak_limit=profile['paragraphSamplePeakCeilingDbfs']-db(np.max(np.abs(samples)))
    gain=min(capped,peak_limit)
    matched=(samples*10**(gain/20)).astype(np.float32)
    after=float(np.median(frame_levels(matched,rate,profile['frameSeconds'])[mask]))
    return matched,dict(frameSeconds=profile['frameSeconds'],gateDbfs=gate,activeFrameIndices=np.flatnonzero(mask).tolist(),
        beforeMedianDbfs=before,afterMedianDbfs=after,targetMedianDbfs=profile['targetMedianDbfs'],
        targetErrorDb=after-profile['targetMedianDbfs'],desiredGainDb=desired,constantGainDb=gain,
        gainCapApplied=abs(capped-desired)>.0001,peakCapApplied=peak_limit<capped,
        peakBeforeDbfs=db(np.max(np.abs(samples))),peakAfterDbfs=db(np.max(np.abs(matched))),
        afterUsesSameRawActiveFrameMask=True,rawSamplesRetained=True,trimmedSamples=0,insertedSamples=0,speechSpeed=1.)


def exact_boundaries(evidence,timing):
    rate=evidence['aggregateWav']['sampleRate'];position=0;rows=[]
    assert rate==24000 and len(timing['entries'])==len(evidence['sceneWavs'])==6
    for i,(entry,chunk) in enumerate(zip(timing['entries'],evidence['sceneWavs']),1):
        assert entry['scene_id']==f's{i:02}' and chunk['sampleRate']==rate and chunk['channels']==1
        start=position;position+=chunk['frames']
        assert abs(entry['start']*rate-start)<.0001 and abs(entry['end']*rate-position)<.0001
        rows.append(dict(sceneId=entry['scene_id'],text=entry['text'],rawTake=chunk['path'],rawTakeSha256=chunk['sha256'],
            rawPcmSha256=chunk['pcmSHA256'],sourceSampleRange=[0,chunk['frames']],destinationSampleRange=[start,position],
            startSeconds=start/rate,endSeconds=position/rate,frames=chunk['frames'],rate=rate))
    assert position==evidence['aggregateWav']['frames'],'No rounded duration or lost boundary samples'
    return rows


def legacy_fade_pcm16(samples,rate):
    """Exact narrow reproduction of the pinned engine's bound0.006s default.

    Do not import/execute the shared engine. Its assembler reads float32 takes,
    applies these ramps, then writes a default PCM16 WAV via libsndfile.
    """
    values=samples.copy();n=min(int(rate*.006),len(values)//2)
    if n>1:
        ramp=np.linspace(0.,1.,n,dtype=np.float32);values[:n]*=ramp;values[-n:]*=ramp[::-1]
    memory=io.BytesIO();sf.write(memory,values,rate,format='WAV',subtype='PCM_16');memory.seek(0)
    decoded,sr=sf.read(memory,dtype='float32');assert sr==rate
    return decoded,n


def aggregate_comparison(raw,aggregate_slice,rate,contract):
    assert raw.ndim==aggregate_slice.ndim==1 and len(raw)==len(aggregate_slice),'Aggregate/take shape differs'
    differences=np.flatnonzero(raw!=aggregate_slice)
    record=dict(exactRawAggregateEquality=not len(differences),differingSamples=len(differences),
        rawLocalDifferenceSampleIndices=differences.tolist(),maximumAbsoluteDifference=float(np.max(np.abs(raw-aggregate_slice))),
        comparisonSampleRate=rate,canonicalSamplesForNormalization='unchanged verified raw scene take',
        aggregateModified=False,rawTakeModified=False,hearingPerformed=False,automaticSpeechPass=False)
    if not len(differences):return record
    assert (contract['auditedEngineSHA256']==contract['currentEngineSHA256']==LEGACY_ENGINE_SHA
        and contract['requestedEdgeFadeSeconds']==contract['voiceIdentityEdgeFadeSeconds']==0
        and contract['aggregateSampleWidthBytes']==contract['rawSampleWidthBytes']==2
        and rate==24000),'Aggregate mismatch is outside pinned legacy zero-fade compatibility contract'
    expected,n=legacy_fade_pcm16(raw,rate)
    assert np.array_equal(expected,aggregate_slice),'Aggregate must contain each exact original take or its proven pinned legacy6ms PCM16 fade'
    assert np.all((differences<n)|(differences>=len(raw)-n)),'Interior differences are never a fade compatibility exception'
    record.update(exactRawAggregateEquality=False,legacyAggregateFadeProven=True,deterministicExpectedAggregateEquality=True,
        legacyFadeSeconds=.006,legacyFadeSamplesPerEdge=n,engineSHA256=LEGACY_ENGINE_SHA,
        manifestRequestedEdgeFadeSeconds=0,quantization='float32 fade then libsndfile WAV PCM_16 write/read',
        soundfileVersion=sf.__version__,libsndfileVersion=sf.__libsndfile_version__,
        reason='Pinned shared-engine default argument retained6ms despite selected manifest zero. Preserve historical aggregate; normalize from natural unchanged raw edges.')
    return record


def inputs():
    output,evidence,timing=asr.exact_voice()  # Selected authorization + exact immutable raw hashes.
    manifest=read(PROJECT/'voice-manifest.json');profile=manifest['tts']['paragraphLevelNormalization']
    for key in ('policy','frameSeconds','gateMaximumDbfs','adaptiveGateBelowPeakDb','targetMedianDbfs','maximumGainDb'):
        assert profile[key]==PROFILE[key],f'Changed paragraph contract: {key}'
    assert profile['preserveRawPcm'] and profile['speechSpeed']==1
    assert sha(MUSIC)==MUSIC_SHA and LICENSE.exists(),'Approved continuous CC-BY music/credit required'
    credit=LICENSE.read_text(encoding='utf-8')
    assert 'Creative Commons Attribution 4.0' in credit and 'Kevin MacLeod' in credit
    rows=exact_boundaries(evidence,timing)
    receipt=read(output/'voice-inputs.json')
    aggregate_contract=dict(auditedEngineSHA256=evidence['audit']['engineSHA256'],currentEngineSHA256=sha(asr.voice.ENGINE),
        requestedEdgeFadeSeconds=manifest['tts']['edgeFadeSeconds'],voiceIdentityEdgeFadeSeconds=receipt['identity']['tts']['edgeFadeSeconds'],
        aggregateSampleWidthBytes=evidence['aggregateWav']['sampleWidthBytes'])
    identity=dict(protocol='architectural111-first-audio-v1',voiceFingerprint=evidence['fingerprint'],
        aggregateSHA256=evidence['aggregateWav']['sha256'],aggregatePcmSHA256=evidence['aggregateWav']['pcmSHA256'],
        timingSHA256=evidence['timing']['sha256'],paragraphs=rows,profile=PROFILE,musicSHA256=MUSIC_SHA,
        processorSHA256=sha(__file__),aggregateComparisonContract=aggregate_contract)
    audit=dict(voiceEvidenceSHA256=sha(asr.PROOF),voiceManifestSHA256=sha(PROJECT/'voice-manifest.json'),
        musicPath=str(MUSIC),musicLicensePath=str(LICENSE),musicLicenseSHA256=sha(LICENSE),
        sourceFootageAudio='No source soundtrack adopted; both selected gameplay sources are video-only or commentary excluded.',
        rawLevelsReport='production/batches/architectural-111-20261106/first-voice-raw-levels-v1.json',
        rawLevelsReportRole='Historical v1 audit only; normalization measures current verified raw takes directly',
        visualOnlyProvenance=evidence.get('audit',{}))
    # Nonspoken visual/QA/manifest metadata does not invalidate matched PCM.
    return output,evidence,dict(identity=identity,fingerprint=digest(identity),audit=audit)


def raw_asr_prerequisite(evidence):
    if not asr.STATE.exists():raise RuntimeError('Complete exact raw-voice independent ASR before audio preparation')
    state=read(asr.STATE)
    assert state.get('completed') and not asr.native.alive(state.get('child')),'Independent ASR is not finished'
    path=Path(state['review']).resolve()
    assert path.is_relative_to(asr.voice.OUTPUT.resolve()/'review/independent-asr-v1')
    result=read(path)
    assert result['voiceFingerprint']==evidence['fingerprint'] and result['aggregateSHA256']==evidence['aggregateWav']['sha256']
    assert result['status']=='independent-asr-complete-content-review-pending'
    assert len(result['paragraphs'])==6 and len(result['boundaryWindows'])==5
    assert result['aliasesApplied'] is False and result['expectedPrompt'] is None
    return dict(path=str(path),sha256=sha(path),automaticSpeechPass=False,humanListening=False,
        status='Independent raw ASR exists; actual content judgment is retained separately, never inferred from this numerical mix.')


def loud(path):
    # Only read input_* measurements; transformed loudnorm samples go to null.
    result=run([FF,'-hide_banner','-i',path,'-map','0:a:0','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'])
    blocks=re.findall(r'\{\s*"input_i"[\s\S]*?\}',result.stderr.decode(errors='replace'))
    if not blocks:raise RuntimeError('No finite loudness measurement: '+str(path))
    measured=json.loads(blocks[-1])
    if not all(math.isfinite(float(measured[k])) for k in ('input_i','input_tp')):raise RuntimeError('Nonfinite audio loudness')
    return measured


def fixed_gain(samples,measured,target,ceiling):
    desired=target-float(measured['input_i']);peak_limit=ceiling-db(np.max(np.abs(samples)))
    gain=min(desired,peak_limit)
    return 10**(gain/20),dict(targetLufs=target,constantGainDb=gain,desiredGainDb=desired,
        samplePeakCeilingDbfs=ceiling,peakReserveLimitedTarget=peak_limit<desired,measuredBefore=measured)


def stereo_voice(samples,rate):
    target=PROFILE['mixRate'];g=math.gcd(rate,target)
    values=resample_poly(samples,target//g,rate//g).astype(np.float32)
    assert len(values)==len(samples)*target//rate and len(samples)*target%rate==0
    return np.repeat(values[:,None],2,axis=1)


def duck_curve(voice,rate,profile=PROFILE):
    hop=max(1,rate//100);pad=(-len(voice))%hop
    data=np.pad(voice,((0,pad),(0,0)))
    rms=np.sqrt(np.mean(data.reshape(-1,hop,2).astype(np.float64)**2,axis=(1,2)))
    levels=20*np.log10(np.maximum(rms,1e-12))
    target=np.clip((levels-profile['speechEnvelopeFloorDbfs'])/(profile['speechEnvelopeFullDbfs']-profile['speechEnvelopeFloorDbfs']),0,1)
    envelope=np.empty_like(target);last=0.
    for i,value in enumerate(target):
        coeff=math.exp(-1000*hop/rate/(profile['duckAttackMs'] if value>last else profile['duckReleaseMs']))
        last=coeff*last+(1-coeff)*value;envelope[i]=last
    full=np.interp(np.arange(len(voice)),np.arange(len(envelope))*hop,envelope)
    return (10**(-profile['backgroundSpeechDuckDb']*full/20)).astype(np.float32)


def music_bed(source,count,rate,gain,duck,profile=PROFILE):
    if len(source)<count:raise ValueError('One continuous music excerpt must cover full unrounded voice duration')
    bed=source[:count].copy()*gain
    fade=min(round(profile['musicFadeSeconds']*rate),count//2)
    if fade:
        bed[:fade]*=np.linspace(0,1,fade,dtype=np.float32)[:,None]
        bed[-fade:]*=np.linspace(1,0,fade,dtype=np.float32)[:,None]
    return bed*duck[:,None]


def reuse(folder,recipe):
    receipt=folder/'audio-build.json'
    if not folder.exists():return None
    assert receipt.exists(),'Unreceipted audio version preserved; inspect rather than overwrite'
    result=read(receipt);assert result['fingerprint']==recipe['fingerprint']
    for pin in result['artifacts'].values():
        path=(folder/pin['file']).resolve();assert path.is_relative_to(folder.resolve())
        assert sha(path)==pin['sha256'],'Existing audio artifact changed; never overwrite'
    return result


def execute():
    worker=asr.native.SingleWorker(WORKER).acquire();worker.update(stage='audio',stageOwner='architectural111-first-audio-v1',topicId='03.02')
    try:
        _,evidence,recipe=inputs();asr_evidence=raw_asr_prerequisite(evidence)
        folder=DEST/recipe['fingerprint'][:24]
        assert folder.resolve().is_relative_to((MEDIA/SLUG).resolve())
        old=reuse(folder,recipe)
        if old:return old
        work=DEST/('work-'+recipe['fingerprint'][:16]+'-'+uuid.uuid4().hex[:8]);work.mkdir(parents=True,exist_ok=False)
        save(work/'input-recipe.json',dict(**recipe,rawVoiceAsr=asr_evidence))
        rows=[];parts=[];rate=evidence['aggregateWav']['sampleRate']
        aggregate,sr=sf.read(evidence['aggregateWav']['path'],dtype='float32');assert sr==rate
        for row in recipe['identity']['paragraphs']:
            assert sha(row['rawTake'])==row['rawTakeSha256'],'Canonical raw take changed before matching'
            samples,sr=sf.read(row['rawTake'],dtype='float32');a,b=row['destinationSampleRange']
            assert sr==rate
            contract=dict(recipe['identity']['aggregateComparisonContract'],rawSampleWidthBytes=evidence['sceneWavs'][len(rows)]['sampleWidthBytes'])
            comparison=aggregate_comparison(samples,aggregate[a:b],rate,contract)
            comparison.update(historicalAggregateSHA256=evidence['aggregateWav']['sha256'],rawTakeSHA256=row['rawTakeSha256'],
                destinationSampleRange=[a,b],aggregateGlobalDifferenceSampleIndices=[a+i for i in comparison['rawLocalDifferenceSampleIndices']])
            matched,levels=match_paragraph(samples,rate);name=row['sceneId']+'-normalized.wav'
            sf.write(work/name,matched,rate,subtype='FLOAT');parts.append(matched)
            rows.append(dict(**row,**levels,normalizedTake=name,normalizedTakeSha256=sha(work/name),aggregateComparison=comparison))
        normalized=np.concatenate(parts);assert len(normalized)==len(aggregate)==evidence['aggregateWav']['frames']
        norm_path=work/'narration-paragraph-normalized.wav';sf.write(norm_path,normalized,rate,subtype='FLOAT')
        line_levels=dict(policy=PROFILE['policy'],voiceFingerprint=evidence['fingerprint'],rawVoiceSha256=evidence['aggregateWav']['sha256'],
            voiceSha256=sha(norm_path),paragraphs=rows,rawRate=rate,frames=len(normalized),durationSeconds=len(normalized)/rate,
            joins=[dict(previous=a['sceneId'],next=b['sceneId'],boundarySample=a['destinationSampleRange'][1],
                insertedSamples=0,trimmedSamples=0,contextListening='pending',
                note='All current raw quiet lead/tail retained without energy-based trim or added gaps. Historical v1 s03→s04≈2.67s is not a measurement of a retaken paragraph or a trim instruction.')
                for a,b in zip(rows,rows[1:])],allRawPcmPreserved=True,allOriginalWordBoundariesPreserved=True,
            normalizedCopyOnly=True,automaticSpeechPass=False,actualListeningPerformed=False)
        line_levels.update(canonicalSpeechSource='Six unchanged verified raw scene takes; historical aggregate is only an identity/timing reference',
            rawVoiceSha256Role='Historical engine aggregate identity, not an assertion of raw-take aggregate PCM equality',
            legacyAggregateFadeRestoredFromRawTakes=any(r['aggregateComparison'].get('legacyAggregateFadeProven') for r in rows),
            historicalAggregateAndAllRawTakesPreserved=True)
        save(work/'line-levels.json',line_levels)
        prepared=stereo_voice(normalized,rate)
        prepared_path=work/'narration-prepared-stem.wav';sf.write(prepared_path,prepared,PROFILE['mixRate'],subtype='FLOAT')
        voice_gain,voice_levels=fixed_gain(prepared,loud(prepared_path),PROFILE['voiceTargetLufs'],PROFILE['voiceSamplePeakCeilingDbfs'])
        stem=prepared*voice_gain
        native_info=json.loads(run([FF.with_name('ffprobe.exe'),'-v','error','-select_streams','a:0','-show_entries','stream=sample_rate,channels,duration','-of','json',MUSIC]).stdout)['streams'][0]
        data=run([FF,'-v','error','-i',MUSIC,'-map','0:a:0','-ar',PROFILE['mixRate'],'-ac','2','-f','f32le','pipe:1']).stdout
        music=np.frombuffer(data,dtype='<f4').reshape(-1,2).copy();assert np.isfinite(music).all()
        music_gain,music_levels=fixed_gain(music,loud(MUSIC),PROFILE['musicTargetLufs'],PROFILE['musicSamplePeakCeilingDbfs'])
        bed=music_bed(music,len(stem),PROFILE['mixRate'],music_gain,duck_curve(stem,PROFILE['mixRate']))
        combined=stem+bed;overall=min(1.,10**((PROFILE['mixSamplePeakCeilingDbfs']-db(np.max(np.abs(combined))))/20))
        measured=None
        for attempt in range(2):
            trial=work/f'mix-measurement-{attempt+1}.wav';sf.write(trial,combined*overall,PROFILE['mixRate'],subtype='FLOAT')
            measured=loud(trial)
            if float(measured['input_tp'])<=PROFILE['mixTruePeakMaximumDbtp']:break
            overall*=10**((PROFILE['mixTruePeakMaximumDbtp']-float(measured['input_tp'])-.35)/20)
        else:raise RuntimeError('CPU mix true peak remains unsafe; preserved version needs review')
        for name,values in [('narration-stem.wav',stem*overall),('music-stem.wav',bed*overall),('final-mix.wav',combined*overall)]:
            assert np.isfinite(values).all();sf.write(work/name,values,PROFILE['mixRate'],subtype='FLOAT')
        assert inputs()[2]['fingerprint']==recipe['fingerprint'],'Inputs changed; preserve staging rather than publishing stale stems'
        names=[p.name for p in work.iterdir() if p.is_file()]
        artifacts={name:dict(file=name,sha256=sha(work/name)) for name in names}
        result=dict(status='audio-prepared-final-mix-review-pending',fingerprint=recipe['fingerprint'],artifacts=artifacts,
            rawVoiceFingerprint=evidence['fingerprint'],rawVoiceSha256=evidence['aggregateWav']['sha256'],
            output=str(folder),normalizedVoiceFrames=len(normalized),normalizedVoiceRate=rate,mixFrames=len(stem),mixRate=PROFILE['mixRate'],
            durationSeconds=len(normalized)/rate,voiceGlobalGain=voice_levels,musicGain=music_levels,musicNativeStream=native_info,
            musicPlaybackRate=1.,musicContinuousExcerpt=True,musicLoops=0,musicSourceStartSeconds=0.,musicFadeSeconds=.45,
            musicAttribution='Pixel Peeker Polka - faster Kevin MacLeod (incompetech.com)\nLicensed under Creative Commons: By Attribution 4.0 License\nhttp://creativecommons.org/licenses/by/4.0/',
            musicSpeechDuckDb=4.,voiceSideDuck=False,compressorUsed=False,uniformMixGainDb=db(overall),measuredPcmMix=measured,
            rawPcmModified=False,wordBoundariesShifted=False,voiceOffsetSeconds=0.,insertedSamples=0,trimmedSamples=0,
            canonicalSpeechSource='unchanged raw scene takes',historicalEngineAggregatePreserved=True,
            legacyAggregateFadeRestoredFromRawTakes=line_levels['legacyAggregateFadeRestoredFromRawTakes'],
            rawVoiceAsr=asr_evidence,actualListeningPerformed=False,finalMixedAsr='pending',
            encodedAacTruePeak='pending',encodedAlignedLevelReview='pending',finalMovieComplete=False,humanApproval=False)
        save(work/'audio-build.json',result);assert not folder.exists();work.rename(folder)
        return result
    finally:worker.close(remove=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if args.execute:
        result=execute();print(json.dumps(dict(status=result['status'],output=result['output'],fingerprint=result['fingerprint'])))
    else:
        _,evidence,recipe=inputs();print(json.dumps(dict(ready=True,fingerprint=recipe['fingerprint'],
            rawVoiceFrames=evidence['aggregateWav']['frames'],sampleRate=evidence['aggregateWav']['sampleRate'],
            output=str(DEST/recipe['fingerprint'][:24]),audioPrepared=False,gpuUsed=False)))


if __name__=='__main__':main()

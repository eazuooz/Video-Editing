"""CPU-only, finite03.02 paragraph matching and BGM stems; never changes raw PCM.

Default prints a read-only preflight. --execute writes a new immutable C-media
version after exact raw-voice ASR evidence exists. It neither encodes a movie nor
performs ASR, TTS, GPU work, actual listening or a platform operation.
"""
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, io, json, math, os, re, shutil, subprocess, uuid
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


def sentence_gaps(text,words,offset,rate):
    sentences=[s.strip() for s in re.findall(r'[^.!?]+[.!?]?',text) if s.strip()]
    assert len(sentences)==3 and ' '.join(sentences)==text,'Exactly three unchanged canonical sentences are required'
    useful=[(i,w,asr.folded(w['text'])) for i,w in enumerate(words) if asr.folded(w['text'])]
    assert ''.join(v for _,_,v in useful)==asr.folded(text),'ASR word literals differ; no pronunciation aliases may hide them'
    result=[];boundary=0
    for sentence in sentences[:-1]:
        boundary+=len(asr.folded(sentence));position=0;found=None
        for j,(index,word,chars) in enumerate(useful):
            position+=len(chars)
            if position==boundary:found=(j,index,word);break
        assert found is not None,'Canonical sentence end is not an exact ASR word end'
        j,index,left=found;right_index,right,_=useful[j+1]
        a,b=left['timestamp'][1],right['timestamp'][0]
        assert a is not None and b is not None and a<b,'Sentence boundary has no actual blind-ASR word gap'
        begin=math.ceil((a-offset)*rate-1e-6);end=math.floor((b-offset)*rate+1e-6)
        result.append(dict(previousWordIndex=index,nextWordIndex=right_index,previousWord=left,nextWord=right,
            asrGapGlobalSeconds=[a,b],asrGapLocalSampleRange=[begin,end]))
    return sentences,result


def safe_sentence_cut(samples,rate,gap):
    inset=round(.005*rate);a,b=gap['asrGapLocalSampleRange'];lo=a+inset;hi=b-inset
    assert 0<lo<=hi<len(samples),'No guarded actual word gap available'
    indices=np.arange(lo,hi+1);score=np.maximum(np.abs(samples[indices-1]),np.abs(samples[indices]));minimum=float(score.min())
    choices=indices[score==minimum];mid=(a+b)/2
    cut=int(min(choices,key=lambda k:(abs(float(k)-mid),int(k))))
    window=round(.01*rate)
    assert cut-window>=0 and cut+window<=len(samples)
    left=db(np.sqrt(np.mean(samples[cut-window:cut].astype(np.float64)**2)))
    right=db(np.sqrt(np.mean(samples[cut:cut+window].astype(np.float64)**2)))
    assert samples[cut-1]==0 and samples[cut]==0,'Selected sentence gain step is not between exact zero-valued raw samples'
    return dict(gap,guardedSearchSampleRangeInclusive=[lo,hi],cutSample=cut,
        previousSample=float(samples[cut-1]),nextSample=float(samples[cut]),minimumMaximumAdjacentMagnitude=minimum,
        rawLeft10msRmsDbfs=left,rawRight10msRmsDbfs=right)


def pcm16_slice_sha(samples):
    integers=np.rint(samples.astype(np.float64)*32768)
    assert np.min(integers)>=-32768 and np.max(integers)<=32767
    assert np.array_equal(samples,integers.astype(np.float32)/32768),'Expected exact decoded canonical PCM16 samples'
    return hashlib.sha256(integers.astype('<i2').tobytes()).hexdigest()


def validate_sentence_cut_plan(path,evidence,rows):
    path=Path(path).resolve();assert path.parent==HERE.resolve(),'Cut plan must be the explicit selected batch-local proof'
    plan=read(path);assert plan['schemaVersion']=='architectural111-sentence-cut-plan-v1' and plan['topicId']=='03.02' and plan['sceneId']=='s02'
    assert digest({k:v for k,v in plan.items() if k!='fingerprint'})==plan['fingerprint'],'Cut-plan fingerprint changed'
    assert plan['voiceFingerprint']==evidence['fingerprint'] and plan['actualAudioModified'] is False and plan['automaticSpeechPass'] is False
    row=next(r for r in rows if r['sceneId']=='s02');source=plan['sourceWav']
    assert Path(source['path']).resolve()==Path(row['rawTake']).resolve()
    actual=asr.voice.wav_info(source['path'])
    assert all(actual[k]==source[k] for k in ('sha256','pcmSHA256','sampleRate','channels','sampleWidthBytes','frames'))
    assert source['sha256']==row['rawTakeSha256'] and source['pcmSHA256']==row['rawPcmSha256'] and source['frames']==row['frames']
    assert (source['sampleRate'],source['channels'],source['sampleWidthBytes'])==(24000,1,2)
    narration=plan['narration'];assert Path(narration['path']).resolve()==(PROJECT/'narration-voice-v1.json').resolve() and sha(narration['path'])==narration['sha256']
    selected=read(narration['path'])['scenes'][1];assert selected['id']=='s02' and ' '.join(selected['lines'])==row['text']==plan['canonicalText']
    raw=plan['rawASR'];pins={}
    for name in ('job','review','cache'):
        pin=raw[name];p=Path(pin['path']).resolve()
        assert p.is_relative_to(asr.voice.OUTPUT.resolve()/'review/independent-asr-v1') and sha(p)==pin['sha256'],'Raw ASR proof changed'
        pins[name]=p
    job=read(pins['job']);assert digest(job['identity'])==job['fingerprint'] and job['identity']['profile']==asr.PROFILE
    assert job['identity']['voiceFingerprint']==evidence['fingerprint'] and job['identity']['aggregateSHA256']==evidence['aggregateWav']['sha256']
    assert job['identity']['timingSHA256']==evidence['timing']['sha256']
    assert pins['job']==(asr.voice.OUTPUT/'review/independent-asr-v1'/job['fingerprint'][:24]/'job.json').resolve()
    task=next(t for t in job['identity']['tasks'] if t['key']=='paragraph-s02');cache=asr.read_cache(job,task)
    assert cache is not None and pins['cache']==pins['job'].parent/'paragraph-s02.json' and read(pins['cache'])==cache
    review=read(pins['review']);assert review['fingerprint']==job['fingerprint'] and review['paragraphs'][1]==cache
    assert task['expected']==row['text'] and task['audioSHA256']==source['sha256']==raw['taskAudioSHA256']
    assert raw['sourceOffsetSeconds']==task['offsetSeconds'] and raw['recognizedLiteral']==cache['text']
    assert raw['rawRecognitionSHA256']==digest(cache['rawRecognition'])
    assert not cache['boundaryFlags'] and cache['aliasesApplied'] is False and raw['aliasesApplied'] is False
    assert asr.folded(cache['text'])==asr.folded(row['text']),'Substantive ASR difference requires explicit review before cuts'
    words,flags=asr.words_from_raw(cache['rawRecognition'],task);assert words==cache['globalWords'] and not flags
    sentences,gaps=sentence_gaps(row['text'],words,task['offsetSeconds'],source['sampleRate'])
    assert sentences==plan['canonicalSentences']
    samples,rate=sf.read(source['path'],dtype='float32');computed=[safe_sentence_cut(samples,rate,g) for g in gaps]
    cuts=[0,*[c['cutSample'] for c in computed],len(samples)]
    assert cuts==plan['sampleCuts'] and len(plan['cuts'])==2
    for actual_cut,pin in zip(computed,plan['cuts']):
        for key,value in actual_cut.items():
            if isinstance(value,float):assert abs(value-pin[key])<1e-8,'Cut waveform proof changed: '+key
            else:assert value==pin[key],'Cut word-gap proof changed: '+key
    assert plan['algorithm']['insetSamples']==120 and plan['algorithm']['fade'] is False
    assert plan['algorithm']['trimmedSamples']==plan['algorithm']['insertedSamples']==0
    assert all(PROFILE[k]==v for k,v in plan['scalarProfile'].items()),'Sentence matcher profile changed'
    assert [s['index'] for s in plan['segments']]==[1,2,3]
    for i,segment in enumerate(plan['segments']):
        a,b=cuts[i:i+2]
        assert segment['canonicalText']==sentences[i] and segment['sourceSampleRange']==[a,b]
        assert segment['destinationSampleRange']==[row['destinationSampleRange'][0]+a,row['destinationSampleRange'][0]+b]
        assert segment['rawSlicePcmSHA256']==pcm16_slice_sha(samples[a:b])
        assert segment['insertedSamples']==segment['trimmedSamples']==0 and segment['speechSpeed']==1 and segment['withinSpeechFade'] is False
    return dict(path=str(path),sha256=sha(path),fingerprint=plan['fingerprint'],plan=plan,
        verifiedGapCuts=computed,rawAsrReviewedForCutLiteralOnly=True,humanListening=False,automaticSpeechPass=False)


def match_sentence_segments(samples,rate,row,cut):
    plan=cut['plan'];assert row['sceneId']=='s02' and len(samples)==plan['sourceWav']['frames'] and rate==24000
    parts=[];segments=[]
    for item in plan['segments']:
        a,b=item['sourceSampleRange'];source=samples[a:b]
        assert len(source)==b-a and pcm16_slice_sha(source)==item['rawSlicePcmSHA256']
        matched,levels=match_paragraph(source,rate)
        for key,value in item['predictedLevels'].items():
            if isinstance(value,bool):assert levels[key]==value
            else:assert abs(levels[key]-value)<1e-6,'Predicted sentence scalar gain changed: '+key
        parts.append(matched);segments.append(dict(index=item['index'],canonicalText=item['canonicalText'],sourceSampleRange=[a,b],
            destinationSampleRange=item['destinationSampleRange'],rawSlicePcmSHA256=item['rawSlicePcmSHA256'],**levels))
    values=np.concatenate(parts);assert len(values)==len(samples)
    joins=[];window=round(.01*rate)
    for k in plan['sampleCuts'][1:-1]:
        step=float(abs(values[k]-values[k-1]));left=db(np.sqrt(np.mean(values[k-window:k].astype(np.float64)**2)));right=db(np.sqrt(np.mean(values[k:k+window].astype(np.float64)**2)))
        assert step==0 and max(left,right)<=-45,'Sentence gain change is not safely inside the measured quiet gap'
        joins.append(dict(sample=k,postGainStep=step,left10msRmsDbfs=left,right10msRmsDbfs=right))
    return values,dict(normalizationMode='per-sentence-constant-gains-v1',sentenceCutPlan={k:cut[k] for k in ('path','sha256','fingerprint')},
        segments=segments,constantGainPerSegment=True,postGainJoins=joins,rawSamplesRetained=True,trimmedSamples=0,insertedSamples=0,speechSpeed=1,
        voiceFades=False,compressorUsed=False,levelContinuityReview='pending; individual peak caps do not imply stable within-sentence level',humanListening=False)


def baseline_normalized_pins(path,evidence,rows):
    """Only copy the five already measured pre-global FLOAT files, byte for byte."""
    path=Path(path).resolve();folder=path.parent
    assert path.name=='audio-build.json' and folder.is_relative_to(DEST.resolve()),'Baseline must be an explicit selected03.02 audio version'
    build=read(path);assert Path(build['output']).resolve()==folder
    assert build['rawVoiceFingerprint']==evidence['fingerprint'] and build['rawVoiceSha256']==evidence['aggregateWav']['sha256']
    assert build['normalizedVoiceFrames']==evidence['aggregateWav']['frames'] and build['normalizedVoiceRate']==24000
    def artifact(name):
        pin=build['artifacts'][name];source=(folder/pin['file']).resolve()
        assert source.parent==folder and source.name==name and sha(source)==pin['sha256'],'Baseline artifact changed'
        return source
    recipe_path=artifact('input-recipe.json');recipe=read(recipe_path)
    assert recipe['fingerprint']==build['fingerprint'] and digest(recipe['identity'])==build['fingerprint']
    assert recipe['identity']['profile']==PROFILE,'Baseline scalar normalization profile changed'
    assert recipe['identity']['voiceFingerprint']==evidence['fingerprint']
    levels_path=artifact('line-levels.json');levels=read(levels_path)
    assert levels['voiceFingerprint']==evidence['fingerprint']
    old_rows={r['sceneId']:r for r in levels['paragraphs']};pins=[]
    for row in rows:
        sid=row['sceneId']
        if sid=='s02':continue
        old=old_rows[sid]
        for key in ('rawTakeSha256','rawPcmSha256','sourceSampleRange','destinationSampleRange','frames','rate'):assert old[key]==row[key],'Unselected normalized source changed: '+sid
        source=artifact(sid+'-normalized.wav');assert old['normalizedTakeSha256']==sha(source)
        info=sf.info(source);assert info.subtype=='FLOAT' and info.channels==1 and info.samplerate==24000 and info.frames==row['frames']
        pins.append(dict(sceneId=sid,path=str(source),sha256=sha(source),metadata=old))
    assert [p['sceneId'] for p in pins]==['s01','s03','s04','s05','s06']
    return dict(buildPath=str(path),buildSHA256=sha(path),fingerprint=build['fingerprint'],
        inputRecipePath=str(recipe_path),inputRecipeSHA256=sha(recipe_path),lineLevelsPath=str(levels_path),lineLevelsSHA256=sha(levels_path),
        priorGlobalVoiceGainDb=build['voiceGlobalGain']['constantGainDb'],priorUniformMixGainDb=build['uniformMixGainDb'],
        unchangedNormalizedScenes=pins,scope='Exact five normalized FLOAT stems before common global gain; no promise that final globally scaled voice samples are unchanged')


def copy_normalized_scene(pin,row,baseline,destination,rate):
    destination=Path(destination);assert sha(pin['path'])==pin['sha256']
    if destination.exists():assert sha(destination)==pin['sha256'],'Different normalized output must be preserved'
    else:shutil.copyfile(pin['path'],destination)
    assert sha(destination)==pin['sha256']
    matched,matched_rate=sf.read(destination,dtype='float32')
    assert matched_rate==rate and matched.ndim==1 and len(matched)==row['frames']
    record=copy.deepcopy(pin['metadata']);record.update(**row,normalizedTake=destination.name,normalizedTakeSha256=sha(destination),
        normalizedReuse=dict(sourceBuildPath=baseline['buildPath'],sourceBuildSHA256=baseline['buildSHA256'],sourcePath=pin['path'],sourceSHA256=pin['sha256'],preGlobalFloatBytesIdentical=True))
    return matched,record


def inputs(sentence_level_scenes=(),sentence_cut_plan=None,reuse_normalized_from=None):
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
    if sentence_level_scenes:
        assert tuple(sentence_level_scenes)==('s02',) and sentence_cut_plan and reuse_normalized_from,'Only the explicitly selected S02 sentence correction is supported'
        cut=validate_sentence_cut_plan(sentence_cut_plan,evidence,rows)
        baseline=baseline_normalized_pins(reuse_normalized_from,evidence,rows)
        expected=cut['plan']['reuseNormalizedFrom']
        assert Path(expected['path']).resolve()==Path(baseline['buildPath']).resolve() and expected['sha256']==baseline['buildSHA256'] and expected['fingerprint']==baseline['fingerprint'],'Cut plan baseline selection changed'
        assert [{k:p[k] for k in ('sceneId','path','sha256')} for p in baseline['unchangedNormalizedScenes']]==[
            dict(sceneId=p['sceneId'],path=p['sourcePath'],sha256=p['sourceSHA256']) for p in expected['exactOtherScenes']],'Cut plan other-five normalized pins changed'
        identity['normalizationOverride']=dict(policy='per-sentence-constant-gains-v1',sceneIds=['s02'],cutPlan=cut,baseline=baseline,
            noCompressor=True,voiceFades=False,insertedSamples=0,trimmedSamples=0,rawPcmModified=False)
    else:assert sentence_cut_plan is None and reuse_normalized_from is None,'Sentence plan/baseline requires explicit --sentence-level-scenes s02'
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


def execute(sentence_level_scenes=(),sentence_cut_plan=None,reuse_normalized_from=None):
    worker=asr.native.SingleWorker(WORKER).acquire();worker.update(stage='audio',stageOwner='architectural111-first-audio-v1',topicId='03.02')
    try:
        current_inputs=lambda:inputs(sentence_level_scenes,sentence_cut_plan,reuse_normalized_from)
        _,evidence,recipe=current_inputs();asr_evidence=raw_asr_prerequisite(evidence)
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
            override=recipe['identity'].get('normalizationOverride');name=row['sceneId']+'-normalized.wav'
            if override and row['sceneId']!='s02':
                pin=next(p for p in override['baseline']['unchangedNormalizedScenes'] if p['sceneId']==row['sceneId'])
                matched,record=copy_normalized_scene(pin,row,override['baseline'],work/name,rate)
                assert matched.shape==samples.shape;record['aggregateComparison']=comparison
            else:
                matched,levels=(match_sentence_segments(samples,rate,row,override['cutPlan']) if override else match_paragraph(samples,rate))
                sf.write(work/name,matched,rate,subtype='FLOAT')
                record=dict(**row,**levels,normalizedTake=name,normalizedTakeSha256=sha(work/name),aggregateComparison=comparison)
            parts.append(matched);rows.append(record)
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
        if recipe['identity'].get('normalizationOverride'):
            line_levels['normalizationOverride']=recipe['identity']['normalizationOverride']
            line_levels['sentenceConstantGainsAppliedOnlyTo']=['s02']
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
        assert current_inputs()[2]['fingerprint']==recipe['fingerprint'],'Inputs changed; preserve staging rather than publishing stale stems'
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
        if recipe['identity'].get('normalizationOverride'):
            override=recipe['identity']['normalizationOverride'];baseline=override['baseline']
            result['normalizationOverride']=dict(policy=override['policy'],sceneIds=['s02'],cutPlan=override['cutPlan'],
                unchangedNormalizedScenes=[{k:p[k] for k in ('sceneId','path','sha256')} for p in baseline['unchangedNormalizedScenes']],
                baselineAudioBuildPath=baseline['buildPath'],baselineAudioBuildSHA256=baseline['buildSHA256'],
                otherFivePreGlobalNormalizedBytesIdentical=True,otherFiveFinalScaledSamplesIdenticalNotAsserted=True,
                previousCommonFinalVoiceGainDb=baseline['priorGlobalVoiceGainDb']+baseline['priorUniformMixGainDb'],
                currentCommonFinalVoiceGainDb=voice_levels['constantGainDb']+db(overall),
                commonFinalVoiceGainChangeDb=voice_levels['constantGainDb']+db(overall)-baseline['priorGlobalVoiceGainDb']-baseline['priorUniformMixGainDb'],
                levelContinuityReview='pending; peak-limited sentence medians and internal slope are not an automatic pass',actualListeningPerformed=False)
        save(work/'audio-build.json',result);assert not folder.exists();work.rename(folder)
        return result
    finally:worker.close(remove=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true')
    parser.add_argument('--sentence-level-scenes',choices=['s02']);parser.add_argument('--sentence-cut-plan');parser.add_argument('--reuse-normalized-from');args=parser.parse_args()
    options=dict(sentence_level_scenes=(args.sentence_level_scenes,) if args.sentence_level_scenes else (),sentence_cut_plan=args.sentence_cut_plan,reuse_normalized_from=args.reuse_normalized_from)
    if args.execute:
        result=execute(**options);print(json.dumps(dict(status=result['status'],output=result['output'],fingerprint=result['fingerprint'])))
    else:
        _,evidence,recipe=inputs(**options);print(json.dumps(dict(ready=True,fingerprint=recipe['fingerprint'],
            rawVoiceFrames=evidence['aggregateWav']['frames'],sampleRate=evidence['aggregateWav']['sampleRate'],
            output=str(DEST/recipe['fingerprint'][:24]),audioPrepared=False,gpuUsed=False)))


if __name__=='__main__':main()

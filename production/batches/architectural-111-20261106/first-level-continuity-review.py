"""Read-only, word-window continuity review of the exact first03.02 audio build.

Default checks bindings only. --analyze computes local sample/body levels;
--decode-aac explicitly permits one cached CPU audio decode from an actual
captioned render. No TTS/model/GPU, audio repair, video encode, project state,
platform operation or inferred human listening. Whole-voice LUFS is context,
never a substitute for local continuity or listening.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import wave
from fractions import Fraction
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import correlate

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
PROJECT_MEDIA=MEDIA/'shorts-leveldesign-03-02'
DEST=PROJECT_MEDIA/'level-continuity-review'
METHOD='03-02-word-window-continuity-v1'
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
POLICY=dict(bodyFrameMilliseconds=20,bodyHopMilliseconds=10,bodyRank='median of upper-half frame RMS values',
    longTrendMinimumWords=9,longTrendMinimumSeconds=6.,lateMinusEarlyWarningDb=-4.,projectedSlopeWarningDb=-3.,
    paragraphBelowMedianWarningDb=-4.,musicToVoiceRmsWarningDb=-12.,normalizedGainToleranceDb=.15,
    normalizationTargetShortfallWarningDb=-2.,
    knownStemMaximumResidual=2e-6,encodedWordLevelDeltaWarningDb=2.,alignmentMinimumCorrelation=.90,
    alignmentMaximumAnchorSpreadSamples=4,alignmentMaximumLagSeconds=.10,alignmentMinimumPeakMargin=.005)


def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf8')).hexdigest()
def sha(path):
    value=hashlib.sha256()
    with Path(path).open('rb') as file:
        for block in iter(lambda:file.read(1024*1024),b''):value.update(block)
    return value.hexdigest()
def db(value):return 20*math.log10(max(float(value),1e-12))
def pin(path):return dict(path=str(Path(path).resolve()),sha256=sha(path))
def verify_pin(record,label):
    path=Path(record['path'])
    if not path.is_file() or sha(path)!=record['sha256']:raise ValueError('Missing/changed '+label+': '+str(path))
    return path


def sample_window(start_seconds,end_seconds,rate):
    """Half-open ASR interval expanded by <1 sample on each edge, explicitly."""
    start=Fraction(str(start_seconds))*rate;end=Fraction(str(end_seconds))*rate
    if start<0 or end<=start:raise ValueError('Finite increasing nonnegative word timestamps required')
    return start.numerator//start.denominator,-(-end.numerator//end.denominator)


def scale_window(start,end,source_rate,target_rate,offset=0):
    if not all(type(x) is int for x in (start,end,source_rate,target_rate,offset)) or not 0<=start<end or min(source_rate,target_rate)<=0:
        raise ValueError('Exact sample-grid mapping required')
    a=Fraction(start*target_rate,source_rate);b=Fraction(end*target_rate,source_rate)
    return a.numerator//a.denominator+offset,-(-b.numerator//b.denominator)+offset


def scalar_segments(row):
    frames=row.get('frames',row['destinationSampleRange'][1]-row['destinationSampleRange'][0])
    mode=row.get('normalizationMode')
    if mode is None:
        return [dict(index=1,sourceSampleRange=[0,frames],constantGainDb=row['constantGainDb'],
            targetErrorDb=row.get('targetErrorDb'),peakCapApplied=row.get('peakCapApplied'))]
    if mode!='per-sentence-constant-gains-v1' or row['sceneId']!='s02' or len(row.get('segments',[]))!=3:
        raise ValueError('Only the scoped three-sentence S02 scalar extension is supported')
    position=0
    for segment in row['segments']:
        a,b=segment['sourceSampleRange'];gain=segment['constantGainDb']
        if (type(a) is not int or type(b) is not int or a!=position or not a<b<=frames or
            not isinstance(gain,(int,float)) or not math.isfinite(gain) or abs(gain)>12.000001 or
            segment['destinationSampleRange']!=[row['destinationSampleRange'][0]+a,row['destinationSampleRange'][0]+b]):
            raise ValueError('Sentence scalar segments do not preserve the exact canonical sample grid')
        position=b
    if position!=frames:raise ValueError('Sentence scalars do not cover the canonical scene')
    return row['segments']


def expected_normalized(raw,row):
    output=np.asarray(raw,dtype=np.float32).copy()
    for segment in scalar_segments(row):
        a,b=segment['sourceSampleRange'];output[a:b]=(raw[a:b]*10**(segment['constantGainDb']/20)).astype(np.float32)
    return output


def levels(samples,rate):
    x=np.asarray(samples,dtype=np.float64)
    if x.ndim==1:x=x[:,None]
    if x.ndim!=2 or not len(x) or not np.isfinite(x).all():raise ValueError('Finite nonempty sample window required')
    rms=math.sqrt(float(np.mean(x*x)));peak=float(np.max(np.abs(x)))
    size=max(1,round(rate*POLICY['bodyFrameMilliseconds']/1000));hop=max(1,round(rate*POLICY['bodyHopMilliseconds']/1000))
    starts=list(range(0,len(x)-size+1,hop)) if len(x)>=size else [0]
    frames=np.array([math.sqrt(float(np.mean(x[s:min(len(x),s+size)]**2))) for s in starts])
    body=float(np.median(frames[frames>=np.median(frames)]))
    return dict(rmsDbfs=db(rms),bodyDbfs=db(body),samplePeakDbfs=db(peak),samples=len(x),bodyFrames=len(frames))


def trend(words,field):
    usable=[w for w in words if w['durationSeconds']>=.06 and field in w['levels']]
    if not usable:return dict(words=0,suspect=False,reason='No valid word-body windows')
    times=np.array([(w['startSeconds']+w['endSeconds'])/2 for w in usable]);values=np.array([w['levels'][field]['bodyDbfs'] for w in usable])
    slopes=[(values[j]-values[i])/(times[j]-times[i]) for i in range(len(times)) for j in range(i+1,len(times)) if times[j]-times[i]>=.5]
    slope=float(np.median(slopes)) if slopes else 0.;span=float(times[-1]-times[0]);n=max(1,len(values)//3)
    early=float(np.median(values[:n]));late=float(np.median(values[-n:]));delta=late-early;projected=slope*span
    suspect=len(usable)>=POLICY['longTrendMinimumWords'] and span>=POLICY['longTrendMinimumSeconds'] and delta<=POLICY['lateMinusEarlyWarningDb'] and projected<=POLICY['projectedSlopeWarningDb']
    return dict(words=len(usable),spanSeconds=span,medianBodyDbfs=float(np.median(values)),earlyThirdMedianDbfs=early,
        lateThirdMedianDbfs=late,lateMinusEarlyDb=delta,medianPairwiseSlopeDbPerSecond=slope,projectedChangeDb=projected,
        suspect=bool(suspect),interpretation='Numerical body-level trend across differing recognized words; not a listening judgment')


def residual_summary(actual,expected):
    a=np.asarray(actual,dtype=np.float64);b=np.asarray(expected,dtype=np.float64)
    if a.shape!=b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():raise ValueError('Known-stem shapes/values differ')
    error=a-b;maximum=float(np.max(np.abs(error)));rms=math.sqrt(float(np.mean(error*error)))
    return dict(maximumAbsolute=maximum,rmsDbfs=db(rms),exceedsKnownStemTolerance=maximum>POLICY['knownStemMaximumResidual'],
        interpretation='Arithmetic residual against actual known stems, not acoustic noise or estimated SNR')


def estimate_alignment(reference,decoded,rate):
    """Numerical common-waveform alignment; no assumed AAC1024-sample trim."""
    a=np.asarray(reference,dtype=np.float64);b=np.asarray(decoded,dtype=np.float64)
    if a.ndim==2:a=a.mean(axis=1)
    if b.ndim==2:b=b.mean(axis=1)
    if a.ndim!=1 or b.ndim!=1 or min(len(a),len(b))<rate*2 or not np.isfinite(a).all() or not np.isfinite(b).all():
        return dict(supported=False,reason='Insufficient finite common waveform; no automatic padding/alignment')
    lag=max(1,round(rate*POLICY['alignmentMaximumLagSeconds']));size=max(64,round(rate*.5));anchors=[]
    for fraction in (.12,.27,.42,.57,.72,.87):
        start=max(lag,min(round(len(a)*fraction),len(a)-size-lag));template=a[start:start+size]
        lo=max(0,start-lag);hi=min(len(b),start+size+lag);search=b[lo:hi]
        if len(search)<size:continue
        template=template-template.mean();energy=float(np.dot(template,template))
        if energy<1e-12:continue
        dot=correlate(search,template,mode='valid',method='fft')
        sums=np.concatenate(([0.],np.cumsum(search)));squares=np.concatenate(([0.],np.cumsum(search*search)))
        local_sum=sums[size:]-sums[:-size];local_energy=np.maximum(squares[size:]-squares[:-size]-local_sum**2/size,1e-24)
        score=dot/np.sqrt(energy*local_energy);index=int(np.argmax(score));offset=lo+index-start
        alternatives=score.copy();guard=max(4,round(rate*.0015))
        alternatives[max(0,index-guard):min(len(alternatives),index+guard+1)]=-np.inf
        second=float(np.max(alternatives)) if np.isfinite(alternatives).any() else -1.
        anchors.append(dict(referenceStartSample=start,referenceEndSample=start+size,decodedMinusReferenceSamples=offset,
            correlation=float(score[index]),peakMargin=float(score[index])-second))
    if len(anchors)<3:return dict(supported=False,anchors=anchors,reason='Too few non-silent shared anchors; no guessed codec delay')
    offsets=[a['decodedMinusReferenceSamples'] for a in anchors];offset=int(round(float(np.median(offsets))));spread=max(offsets)-min(offsets)
    supported=(spread<=POLICY['alignmentMaximumAnchorSpreadSamples'] and min(a['correlation'] for a in anchors)>=POLICY['alignmentMinimumCorrelation']
        and min(a['peakMargin'] for a in anchors)>=POLICY['alignmentMinimumPeakMargin'])
    return dict(supported=bool(supported),decodedMinusReferenceSamples=offset,offsetSeconds=offset/rate,anchorSpreadSamples=spread,
        anchors=anchors,nonzeroOffset=offset!=0,appliedToComparisonWindowsOnly=True,audioModified=False,
        method='Normalized cross-correlation at6 separated0.5s anchors after normal demux/decoder skip handling')


def same_identity(report,identity):
    return report.get('method')==METHOD and report.get('inputIdentity')==identity and report.get('fingerprint')==digest(identity)


def assert_same_audio(build,timeline):
    if (timeline['audio']['mix']['sha256']!=build['artifacts']['final-mix.wav']['sha256'] or
        timeline.get('voiceFingerprint')!=build['rawVoiceFingerprint'] or
        timeline['audio']['voice']['sha256']!=build['rawVoiceSha256']):
        raise ValueError('Encoded render does not use this exact selected voice/mix identity')


def verify_bundle(audio_build,asr_review=None,render_manifest=None):
    path=Path(audio_build).resolve();folder=path.parent
    if not path.is_relative_to((PROJECT_MEDIA/'audio-preparation-v1').resolve()) or path.name!='audio-build.json':
        raise ValueError('Only the selected first-film audio build is in scope')
    build=read(path);pins=[pin(path)]
    if Path(build['output']).resolve()!=folder or build.get('voiceOffsetSeconds')!=0 or build.get('insertedSamples')!=0 or build.get('trimmedSamples')!=0:
        raise ValueError('Audio build offset/duration contract changed')
    for artifact in build['artifacts'].values():
        file=(folder/artifact['file']).resolve()
        if not file.is_relative_to(folder):raise ValueError('Artifact escaped its immutable audio version')
        record=dict(path=str(file),sha256=artifact['sha256']);verify_pin(record,'audio artifact');pins.append(record)
    line=read(folder/'line-levels.json');paragraphs=line['paragraphs']
    if len(paragraphs)!=6 or line['rawRate']!=24000:raise ValueError('Six exact24kHz raw paragraph takes required')
    review_pin=build['rawVoiceAsr'];asr_path=verify_pin(review_pin,'current raw ASR review')
    if asr_review and Path(asr_review).resolve()!=asr_path.resolve():raise ValueError('ASR review must be the build-bound exact review')
    review=read(asr_path);pins.append(dict(path=str(asr_path.resolve()),sha256=review_pin['sha256']))
    if (review.get('voiceFingerprint')!=build['rawVoiceFingerprint'] or review.get('aggregateSHA256')!=build['rawVoiceSha256'] or
        review.get('aliasesApplied') is not False or review.get('expectedPrompt') is not None or review.get('pcmModified') is not False or len(review.get('paragraphs',[]))!=6):
        raise ValueError('Raw ASR identity/content provenance does not match this audio')
    if review.get('status')!='independent-asr-complete-content-review-pending' or len(review.get('boundaryWindows',[]))!=5:
        raise ValueError('Complete current raw ASR paragraphs and5 joins are required')
    current=MEDIA/'first-voice-evidence.json';voice=read(current);pins.append(pin(current))
    if voice.get('fingerprint')!=build['rawVoiceFingerprint'] or voice['aggregateWav']['sha256']!=build['rawVoiceSha256']:
        raise ValueError('Build is historical, not the current selected voice identity')
    selected_receipt=Path(voice['output'])/'voice-inputs.json';selected=read(selected_receipt);pins.append(pin(selected_receipt))
    checkpoint=read(ROOT/'projects/shorts-leveldesign-03-02/checkpoint.json')
    if selected.get('fingerprint')!=build['rawVoiceFingerprint'] or checkpoint.get('currentVoiceFingerprint')!=build['rawVoiceFingerprint']:
        raise ValueError('A newer selected voice/repair is pending; the previous build is not current')
    position=0;origins={}
    for i,(row,recognized,chunk) in enumerate(zip(paragraphs,review['paragraphs'],voice['sceneWavs']),1):
        start,end=row['destinationSampleRange'];task=recognized['task']
        if row['sceneId']!=f's{i:02}' or start!=position or end-start!=row['frames'] or row['rate']!=24000 or row['sourceSampleRange']!=[0,row['frames']]:
            raise ValueError('Canonical paragraph sample grid changed')
        position=end;raw=dict(path=row['rawTake'],sha256=row['rawTakeSha256']);verify_pin(raw,'canonical raw take');pins.append(raw)
        info=sf.info(row['rawTake'])
        if (info.samplerate,info.channels,info.frames)!=(24000,1,row['frames']) or chunk['sha256']!=row['rawTakeSha256']:
            raise ValueError('Current raw-take sample properties/identity differ')
        segments=scalar_segments(row)
        if row.get('normalizationMode'):
            plan_pin=row['sentenceCutPlan'];plan_path=verify_pin(plan_pin,'sentence cut plan');pins.append(dict(path=str(plan_path),sha256=plan_pin['sha256']))
            plan=read(plan_path)
            if (plan['sourceWav']['sha256']!=row['rawTakeSha256'] or plan['voiceFingerprint']!=build['rawVoiceFingerprint'] or
                [s['sourceSampleRange'] for s in plan['segments']]!=[s['sourceSampleRange'] for s in segments]):
                raise ValueError('Sentence gain rows differ from their bound canonical cut plan')
            with wave.open(str(row['rawTake']),'rb') as file:
                if file.getsampwidth()!=2 or file.getnchannels()!=1:raise ValueError('Expected canonical mono PCM16')
                payload=file.readframes(file.getnframes())
            for segment in segments:
                a,b=segment['sourceSampleRange']
                if hashlib.sha256(payload[a*2:b*2]).hexdigest()!=segment['rawSlicePcmSHA256']:
                    raise ValueError('Sentence gain source PCM slice changed')
        reuse=row.get('normalizedReuse')
        if reuse:
            for label,path_key,hash_key in [('baseline build','sourceBuildPath','sourceBuildSHA256'),('unchanged normalized copy','sourcePath','sourceSHA256')]:
                record=dict(path=reuse[path_key],sha256=reuse[hash_key]);verify_pin(record,label);pins.append(record)
            if sha(folder/row['normalizedTake'])!=reuse['sourceSHA256'] or not reuse.get('preGlobalFloatBytesIdentical'):
                raise ValueError('Unselected normalized paragraph was changed')
        if (task.get('audioSHA256')!=row['rawTakeSha256'] or task.get('sceneId')!=row['sceneId'] or
            abs(task.get('offsetSeconds',-1)-start/24000)>1e-9 or recognized.get('aliasesApplied') is not False or recognized.get('expectedPrompt') is not None):
            raise ValueError('ASR words are not bound to this canonical WAV/sample offset')
        if not recognized.get('globalWords') or recognized.get('text')!=recognized.get('rawRecognition',{}).get('text'):
            raise ValueError('Actual blind recognized words are missing or replaced')
        origin=dict(canonicalUnprocessedRaw=chunk.get('canonicalUnprocessedRaw',True),
            pcmOrigin=chunk.get('pcmOrigin','Original per-scene take; canonical WAV bytes preserved'))
        if chunk.get('canonicalUnprocessedRaw') is False:
            repair=voice.get('s03LevelRepair',{})
            component_path=Path(chunk['derivedComponentReport']).resolve()
            if Path(repair.get('report','')).resolve()!=component_path:raise ValueError('Derived scene component proof missing')
            component_pin=dict(path=str(component_path),sha256=repair['sha256']);verify_pin(component_pin,'derived scene component report');pins.append(component_pin)
            component=read(component_path)
            if component['canonicalScene']['sha256']!=row['rawTakeSha256'] or component['frames']!=row['frames'] or component['sampleRate']!=24000:
                raise ValueError('Derived component identity/sample grid differs')
            cursor=0
            for part in component['components']:
                verify_pin(part['raw'],'original semantic take');pins.append(part['raw'])
                normalized_pin=dict(path=part['normalizedPath'],sha256=part['normalizedSHA256'])
                verify_pin(normalized_pin,'semantic take normalized copy');pins.append(normalized_pin)
                first,last=part['destinationSampleRange']
                if first!=cursor or last-first!=part['raw']['frames'] or part.get('insertedSamples')!=0 or part.get('trimmedSamples')!=0:
                    raise ValueError('Derived semantic takes inserted/removed samples')
                cursor=last
            if cursor!=row['frames']:raise ValueError('Derived takes do not cover the canonical scene')
            origin.update(componentReport=component_pin,components=component['components'],
                interpretation='Canonical ASR WAV is explicitly derived from preserved raw semantic takes; it is not claimed as unprocessed raw')
        origins[row['sceneId']]=origin
    if position!=line['frames'] or build['mixRate']!=48000 or build['mixFrames']!=position*2:
        raise ValueError('Exact24→48kHz, offset-zero duration must be preserved')
    manifest=None
    if render_manifest:
        mp=Path(render_manifest).resolve();manifest=read(mp);pins.append(pin(mp))
        if manifest.get('complete') is not True or manifest.get('slug')!='shorts-leveldesign-03-02':raise ValueError('Actual complete first-film render manifest required')
        timeline_path=verify_pin(manifest['timeline'],'render timeline');timeline=read(timeline_path);pins.append(manifest['timeline'])
        assert_same_audio(build,timeline)
        for role in ('clean','captioned'):
            verify_pin(manifest['outputs'][role],role+' actual video');pins.append(manifest['outputs'][role])
        verify_pin(manifest['audioAac'],'shared encoded AAC');pins.append(manifest['audioAac'])
    line['_canonicalOrigins']=origins
    return build,line,review,manifest,pins


def load_audio(path,rate,channels,frames):
    values,sr=sf.read(path,dtype='float32',always_2d=True)
    if sr!=rate or values.shape!=(frames,channels) or not np.isfinite(values).all():raise ValueError('Actual audio grid differs: '+str(path))
    return values


def word_records(paragraph,recognized,arrays,raw,raw_rate=24000,mix_rate=48000):
    out=[];a,b=paragraph['destinationSampleRange'];words=recognized['globalWords'];expected=expected_normalized(raw,paragraph)
    for index,word in enumerate(words):
        timestamp=word.get('timestamp')
        if not isinstance(timestamp,(list,tuple)) or len(timestamp)!=2 or any(not isinstance(t,(int,float)) or not math.isfinite(t) for t in timestamp):
            raise ValueError('ASR lacks an actual finite word timestamp')
        start,end=sample_window(*timestamp,raw_rate)
        if start<a-1 or end>b+1:raise ValueError('ASR word crosses its actual raw paragraph by more than sample rounding')
        expanded=(start,end);edge_clamp=dict(startSamples=max(0,a-start),endSamples=max(0,end-b))
        start,end=max(a,start),min(b,end)
        if end<=start:raise ValueError('ASR word has no canonical samples')
        mr=scale_window(start,end,raw_rate,mix_rate);local=(start-a,end-a)
        measured=dict(canonical=levels(raw[local[0]:local[1]],raw_rate))
        expected_levels=levels(expected[local[0]:local[1]],raw_rate)
        for name,values in arrays.items():
            region=(start,end) if name=='normalized' else mr
            measured[name]=levels(values[region[0]:region[1]],raw_rate if name=='normalized' else mix_rate)
        residual=residual_summary(arrays['mix'][mr[0]:mr[1]],arrays['voice'][mr[0]:mr[1]]+arrays['music'][mr[0]:mr[1]])
        row=dict(sceneId=paragraph['sceneId'],asrWordIndex=index,recognizedText=word['text'],
            recognizedContext=' '.join(w['text'].strip() for w in words[max(0,index-2):index+3]),
            originalAsrTimestamp=timestamp,asrExpandedRawSampleRange=list(expanded),comparisonWindowEdgeClampOnly=edge_clamp,
            globalRawSampleRange=[start,end],rawTakeLocalSampleRange=list(local),mixSampleRange=list(mr),
            startSeconds=start/raw_rate,endSeconds=end/raw_rate,durationSeconds=(end-start)/raw_rate,
            levels=measured,normalizedMinusCanonicalBodyDb=measured['normalized']['bodyDbfs']-measured['canonical']['bodyDbfs'],
            expectedNormalizedBodyDbfs=expected_levels['bodyDbfs'],normalizedBodyErrorVsExpectedDb=measured['normalized']['bodyDbfs']-expected_levels['bodyDbfs'],
            expectedNormalizationBodyGainDb=expected_levels['bodyDbfs']-measured['canonical']['bodyDbfs'],
            musicToVoiceWordRmsDb=measured['music']['rmsDbfs']-measured['voice']['rmsDbfs'],knownStemResidual=residual)
        out.append(row)
    return out


def continuity(paragraphs):
    flags=[];summaries=[]
    for row,words in paragraphs:
        segments=scalar_segments(row)
        summary=dict(sceneId=row['sceneId'],recognizedWords=len(words),stages={stage:trend(words,stage) for stage in ('canonical','normalized','voice','mix')},
            peakCapApplied=row.get('peakCapApplied'),normalizationMode=row.get('normalizationMode','single-paragraph-scalar'),
            recordedNormalizationGainDb=row.get('constantGainDb'),normalizationTargetErrorDb=row.get('targetErrorDb'),normalizationSegments=segments)
        summaries.append(summary)
        for stage,stats in summary['stages'].items():
            if stats['suspect']:
                flags.append(dict(kind='sustained-word-body-decline',sceneId=row['sceneId'],stage=stage,
                    startSeconds=words[0]['startSeconds'],endSeconds=words[-1]['endSeconds'],trend=stats,
                    recognizedContext=' / '.join(w['recognizedText'].strip() for w in (words[:3]+words[-3:])),
                    action='Listen to this span with adjacent context; inspect the canonical take before changing mix gain'))
        for word in words:
            if abs(word['normalizedBodyErrorVsExpectedDb'])>POLICY['normalizedGainToleranceDb']:
                flags.append(dict(kind='unexpected-normalized-window-gain',sceneId=row['sceneId'],word=word['recognizedText'],context=word['recognizedContext'],sampleRange=word['globalRawSampleRange']))
            if word['musicToVoiceWordRmsDb']>POLICY['musicToVoiceRmsWarningDb'] and word['durationSeconds']>=.08:
                flags.append(dict(kind='music-close-to-known-voice-component',sceneId=row['sceneId'],word=word['recognizedText'],context=word['recognizedContext'],
                    startSeconds=word['startSeconds'],endSeconds=word['endSeconds'],componentRmsRatioDb=word['musicToVoiceWordRmsDb'],
                    interpretation='Known-stem RMS ratio; possible review target, not estimated SNR or proof of masking'))
        for segment in segments:
            error=segment.get('targetErrorDb')
            if error is not None and error<POLICY['normalizationTargetShortfallWarningDb']:
                flags.append(dict(kind='normalization-target-shortfall',sceneId=row['sceneId'],segment=segment.get('index'),
                    sourceSampleRange=segment['sourceSampleRange'],targetErrorDb=error,peakCapApplied=segment.get('peakCapApplied'),
                    action='Declared peak/gain limits prevented the target; inspect actual normalized voice, never infer a level pass'))
    medians=[s['stages']['voice'].get('medianBodyDbfs') for s in summaries]
    finite=[x for x in medians if x is not None]
    if finite:
        center=float(np.median(finite))
        for summary in summaries:
            value=summary['stages']['voice'].get('medianBodyDbfs')
            if value is not None and value-center<=POLICY['paragraphBelowMedianWarningDb']:
                flags.append(dict(kind='paragraph-body-below-other-paragraphs',sceneId=summary['sceneId'],medianBodyDbfs=value,
                    otherParagraphMedianDbfs=center,deltaDb=value-center,action='Review the same voice in surrounding paragraphs; words and emphasis naturally differ'))
    return summaries,flags


def component_summaries(row,words,origin):
    summaries=[];flags=[]
    for component in origin.get('components',[]):
        a,b=component['destinationSampleRange'];base=row['destinationSampleRange'][0];rate=row['rate']
        selected=[w for w in words if a<=((sum(w['originalAsrTimestamp'])/2)*rate-base)<b]
        stats={stage:trend(selected,stage) for stage in ('canonical','normalized','voice','mix')}
        item=dict(sceneId=row['sceneId'],componentId=component['componentId'],canonicalLocalSampleRange=[a,b],
            recognizedWords=len(selected),membership='Original ASR word midpoint; a floor/ceil borrowed boundary sample does not move a word into the next take',stages=stats)
        summaries.append(item)
        for stage,value in stats.items():
            if value['suspect']:
                flags.append(dict(kind='derived-component-word-body-decline',sceneId=row['sceneId'],componentId=component['componentId'],stage=stage,
                    startSeconds=selected[0]['startSeconds'],endSeconds=selected[-1]['endSeconds'],trend=value,
                    recognizedContext=' / '.join(w['recognizedText'].strip() for w in (selected[:3]+selected[-3:])),
                    action='The whole paragraph may hide a take reset; inspect this component with adjacent context before approval'))
    return summaries,flags


def ffmpeg_path():
    path=os.environ.get('YAMYAM_FFMPEG') or shutil.which('ffmpeg')
    if not path:raise RuntimeError('ffmpeg is required only for explicitly requested optional audio measurement/decode')
    return path


def decode_encoded(manifest,rate,channels):
    source=manifest['outputs']['captioned'];verify_pin(source,'actual captioned movie')
    folder=DEST/'decoded-aac'/(source['sha256'][:24]+f'-{rate}-{channels}');proof=folder/'decode.json';wav=folder/'decoded.wav'
    identity=dict(source=source,rate=rate,channels=channels,method='default demux/codec skip handling; no manual priming trim or padding')
    if proof.exists():
        old=read(proof)
        if old['identity']!=identity:raise ValueError('Existing decoded AAC identity changed')
        verify_pin(old['wav'],'cached decoded AAC');return wav,old
    if folder.exists():raise ValueError('Preserve incomplete prior decode; inspect it instead of overwriting')
    folder.mkdir(parents=True,exist_ok=False);ff=ffmpeg_path()
    command=[ff,'-hide_banner','-nostdin','-i',source['path'],'-map','0:a:0','-vn','-ar',str(rate),'-ac',str(channels),'-c:a','pcm_f32le',str(wav)]
    response=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=CREATE)
    (folder/'decode.log').write_bytes(response.stderr)
    if response.returncode:raise RuntimeError('AAC audio decode failed; incomplete immutable attempt preserved')
    receipt=dict(identity=identity,wav=pin(wav),command=command,decoder=pin(ff),manualSkipSamples=0,
        alignment='Not assumed from encoder frame size; subsequent shared-waveform anchors decide comparison offset')
    proof.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8');return wav,receipt


def loudness(path):
    command=[ffmpeg_path(),'-hide_banner','-nostdin','-i',str(path),'-map','0:a:0','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-']
    result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=CREATE)
    blocks=re.findall(r'\{\s*"input_i"[\s\S]*?\}',result.stderr.decode(errors='replace'))
    if result.returncode or not blocks:raise RuntimeError('Optional full-file loudness measurement failed')
    values=json.loads(blocks[-1])
    return dict(inputLufs=float(values['input_i']),inputTruePeakDbtp=float(values['input_tp']),source=pin(path),
        audioChanged=False,method='FFmpeg loudnorm input_* measurement only; transformed samples discarded',qualityPass=False)


def analyze(audio_build,asr_review=None,render_manifest=None,decode_aac=False,measure_loudness=False,reuse_report=None):
    build,line,review,manifest,pins=verify_bundle(audio_build,asr_review,render_manifest);folder=Path(audio_build).resolve().parent
    identity=dict(method=METHOD,reviewerSHA256=sha(__file__),inputs=pins,policy=POLICY,decodeAac=bool(decode_aac),measureLoudness=bool(measure_loudness))
    if reuse_report:
        old=read(reuse_report)
        if not same_identity(old,identity):raise ValueError('Prior level review does not match current mix/raw-ASR/reuse pins')
        return old
    n=line['frames'];m=build['mixFrames'];raw_rate=line['rawRate'];rate=build['mixRate']
    arrays=dict(normalized=load_audio(folder/'narration-paragraph-normalized.wav',raw_rate,1,n),
        prepared=load_audio(folder/'narration-prepared-stem.wav',rate,2,m),voice=load_audio(folder/'narration-stem.wav',rate,2,m),
        music=load_audio(folder/'music-stem.wav',rate,2,m),mix=load_audio(folder/'final-mix.wav',rate,2,m))
    grouped=[];all_words=[];normal_checks=[]
    for row,recognized in zip(line['paragraphs'],review['paragraphs']):
        raw=load_audio(row['rawTake'],raw_rate,1,row['frames']);a,b=row['destinationSampleRange']
        normal_checks.append(dict(sceneId=row['sceneId'],residual=residual_summary(arrays['normalized'][a:b],expected_normalized(raw,row))))
        words=word_records(row,recognized,arrays,raw,raw_rate,rate);grouped.append((row,words));all_words.extend(words)
    summaries,flags=continuity(grouped)
    derived=[]
    for row,words in grouped:
        values,extra=component_summaries(row,words,line['_canonicalOrigins'][row['sceneId']]);derived.extend(values);flags.extend(extra)
    voice_gain=build['voiceGlobalGain']['constantGainDb']+build['uniformMixGainDb']
    voice_residual=residual_summary(arrays['voice'],arrays['prepared']*10**(voice_gain/20))
    mix_residual=residual_summary(arrays['mix'],arrays['voice']+arrays['music'])
    for name,item in [('voice-from-prepared',voice_residual),('mix-from-known-stems',mix_residual)]+[(x['sceneId']+'-normalized-from-raw',x['residual']) for x in normal_checks]:
        if item['exceedsKnownStemTolerance']:flags.append(dict(kind='known-stage-arithmetic-mismatch',stage=name,measurement=item))
    encoded=dict(status='pending actual encoded audio',alignment=None)
    if decode_aac:
        if not manifest:raise ValueError('Actual render manifest required before encoded AAC comparison')
        wav,decode_proof=decode_encoded(manifest,rate,2);decoded,sr=sf.read(wav,dtype='float32',always_2d=True)
        if sr!=rate or decoded.shape[1]!=2:raise ValueError('Decoded AAC sample grid differs')
        alignment=estimate_alignment(arrays['mix'],decoded,rate);comparisons=[]
        if alignment.get('supported'):
            offset=alignment['decodedMinusReferenceSamples']
            for word in all_words:
                a,b=word['mixSampleRange'];a+=offset;b+=offset
                if a<0 or b>len(decoded):
                    flags.append(dict(kind='encoded-word-window-not-covered',sceneId=word['sceneId'],word=word['recognizedText'],decodedSampleRange=[a,b]));continue
                measured=levels(decoded[a:b],rate);delta=measured['bodyDbfs']-word['levels']['mix']['bodyDbfs']
                item=dict(sceneId=word['sceneId'],word=word['recognizedText'],context=word['recognizedContext'],decodedSampleRange=[a,b],
                    bodyDeltaVsMixDb=delta,rmsDeltaVsMixDb=measured['rmsDbfs']-word['levels']['mix']['rmsDbfs'],levels=measured)
                comparisons.append(item)
                if abs(delta)>POLICY['encodedWordLevelDeltaWarningDb'] and word['durationSeconds']>=.08:flags.append(dict(kind='encoded-local-level-delta',**item))
            if alignment['nonzeroOffset']:flags.append(dict(kind='encoded-nonzero-comparison-offset',alignment=alignment,action='Check codec skip/edit-list evidence; comparison offset did not modify audio'))
        else:flags.append(dict(kind='encoded-alignment-not-established',alignment=alignment))
        encoded=dict(status='numerically-compared-listening-pending' if alignment.get('supported') else 'alignment-not-established-listening-required',decode=decode_proof,alignment=alignment,
            decodedFrames=len(decoded),mixFrames=len(arrays['mix']),wordComparisons=comparisons,
            packetIdentity='Actual captioned file was hash-bound; clean/captioned shared-packet identity remains the collector’s separate check')
    full=dict(status='not requested',qualityPass=False)
    if measure_loudness:
        full=dict(voice=loudness(folder/'narration-stem.wav'),mix=loudness(folder/'final-mix.wav'),qualityPass=False)
        if decode_aac:full['decodedAac']=loudness(wav)
    for record in pins:verify_pin(record,'input recheck')
    if read(ROOT/'projects/shorts-leveldesign-03-02/checkpoint.json').get('currentVoiceFingerprint')!=build['rawVoiceFingerprint']:
        raise ValueError('Selected voice changed during numerical review')
    return dict(method=METHOD,inputIdentity=identity,fingerprint=digest(identity),status='suspect-regions-listening-required' if flags else 'numerical-screen-complete-listening-pending',
        paragraphSummaries=summaries,words=all_words,suspectRegions=flags,normalizedCopyChecks=normal_checks,
        derivedComponentSummaries=derived,
        canonicalOrigins=line['_canonicalOrigins'],
        voiceFromPreparedResidual=voice_residual,mixFromKnownStemsResidual=mix_residual,encoded=encoded,fullFileLoudness=full,
        sampleGrid=dict(rawRate=raw_rate,mixRate=rate,voiceOffsetSeconds=0,window='Half-open raw sample grid; floor start / ceil end; exact rational rate mapping',
            noSpeechTimingInvented=True,noAudioTrimOrPadding=True),
        scope='Same raw-ASR-recognized words at all actual stages; stage RMS/component ratios are not perceptual speech levels or SNR',
        rawAggregateNote='Voice aggregate identifies current ASR timing; verified per-scene canonical WAVs are the normalization source. Derived S03 origins/components are reported explicitly.',
        aliasesApplied=False,automaticSpeechPass=False,actualListening=False,actualVideoPlayback=False,humanApproval=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio-build',required=True);parser.add_argument('--asr-review');parser.add_argument('--render-manifest')
    parser.add_argument('--analyze',action='store_true');parser.add_argument('--decode-aac',action='store_true');parser.add_argument('--measure-loudness',action='store_true');parser.add_argument('--reuse-report')
    args=parser.parse_args()
    if not args.analyze:
        build,_,_,_,pins=verify_bundle(args.audio_build,args.asr_review,args.render_manifest)
        print(json.dumps(dict(ready=True,analyzed=False,voiceFingerprint=build['rawVoiceFingerprint'],boundInputs=len(pins),processesStarted=0)));return
    result=analyze(args.audio_build,args.asr_review,args.render_manifest,args.decode_aac,args.measure_loudness,args.reuse_report)
    folder=DEST/result['fingerprint'][:24];folder.mkdir(parents=True,exist_ok=True);target=folder/'review.json'
    data=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    if target.exists() and target.read_bytes()!=data:raise ValueError('Preserve differing existing level review')
    if not target.exists():target.write_bytes(data)
    print(json.dumps(dict(status=result['status'],suspectRegions=len(result['suspectRegions']),report=str(target),sha256=sha(target),actualListening=False)))


if __name__=='__main__':main()

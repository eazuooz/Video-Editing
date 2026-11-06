"""07.04 exact-word PCM/mix/AAC numerical review; default readiness only.

--analyze reads actual current immutable audio. --decode-aac and
--measure-loudness additionally permit bounded software-only audio tools.
No synthesis/model/engine/GPU/lease, audio repair, source-state edits, platform
actions or inferred human hearing. Original PCM and failed attempts survive.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,math,os,re,subprocess,sys,uuid
from pathlib import Path
import numpy as np
import soundfile as sf

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
BASE=MEDIA/'shorts-leveldesign-07-04';DEST=BASE/'level-continuity-review'
METHOD='07-04-exact-take-word-window-levels-v1'
PRIMITIVE_SHA='545104df16cf26af0c0637faa76750bea1e5b70f424cc13820f13baa8b773544'
AUDIO_SHA='363b7e22bd99e1b860d981b12c2d91a965f740b3b77ec00935c74db456f6ed7b'
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)|getattr(subprocess,'BELOW_NORMAL_PRIORITY_CLASS',0)
ACTIVE=None

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):
    with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def pin(path):return dict(path=str(Path(path).resolve()),sha256=sha(path))
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def require(value,reason):
    if not value:raise ValueError(reason)
def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp');temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(temp,path)
def immutable(path,value):
    path=Path(path)
    if path.exists():require(read(path)==value,'Preserve differing previous numerical proof')
    else:save(path,value)
    return path
def verified(record,label):
    path=Path(record['path']).resolve();require(path.is_file()and sha(path)==record['sha256'],'Missing or changed '+label);return path

require(sha(HERE/'first-level-continuity-review.py')==PRIMITIVE_SHA,'Reviewed numeric primitive changed')
mathqa=module('zen_levels_pinned_numeric_primitives',HERE/'first-level-continuity-review.py')
POLICY=copy.deepcopy(mathqa.POLICY)
runtime=module('zen_levels_private_singleton',HERE/'run-first-native.py')
runtime.PROTOCOL='architectural111-07-04-numerical-audio-review-v1';runtime.OWNER='architectural-111-07-04-numerical-audio-review'
WORKER=MEDIA/'07-04-audio-level-review-worker.json'

def scalar_row(row):
    require(row.get('sourceSampleRange')==[0,row['frames']]and row.get('prepared48kSampleRange')==[v*2 for v in row['destinationSampleRange']],'Scalar source grid changed')
    measure=row['normalization'];gain=measure['constantGainDb']
    require(type(gain)in(int,float)and math.isfinite(gain)and abs(gain)<=12.000001,'Finite approved constant gain required')
    return dict(row,constantGainDb=gain,peakCapApplied=measure.get('peakCapApplied'),targetErrorDb=measure.get('targetErrorDb'))

def validate_rows(voice,line,proposed):
    scenes=voice['identity']['scenes'];rows=line['components'];count=len(scenes)
    require(count>0 and len({s['id']for s in scenes})==count and len(rows)==len(proposed)==count,'Exact current component count required')
    require(line.get('componentCount')==count and line.get('voiceFingerprint')==voice['fingerprint']and line.get('rawCanonical')==voice['aggregateWav'],'Stale component lineage')
    position=0;paragraphs=[];adapted=[]
    for scene,row,source in zip(scenes,rows,proposed):
        require(row['sceneId']==scene['id']==source['sceneId']and row['text']==' '.join(scene['lines']),'Component identity/order/text changed')
        require(all(row.get(k)==v for k,v in source.items()),'Line-level source proposal differs')
        end=position+row['frames'];require(row['destinationSampleRange']==[position,end]and row['rate']==24000,'Canonical source samples missing/repeated')
        adapted.append(scalar_row(row));paragraphs.append(row['paragraph']);position=end
    require(paragraphs==sorted(paragraphs)and list(dict.fromkeys(paragraphs))==list(range(1,8))and position==voice['aggregateWav']['frames'],'Exact ordered seven-paragraph coverage required')
    for key,value in dict(rawRate=24000,frames=position,originalRawFilesUnchanged=True,amplitudeOnlyScalarCopies=True,wordBoundariesShifted=False,voiceOffsetSeconds=0.,insertedSamples=0,trimmedSamples=0,voiceSpeed=1.,compressorUsed=False,voiceSideDuck=False).items():
        require(line.get(key)==value,'Forbidden speech processing/grid change: '+key)
    return adapted

def verify_bundle(audio_path,asr_path=None,render_path=None):
    require(sha(HERE/'prepare-zen-view-audio.py')==AUDIO_SHA,'Reviewed07.04 audio producer changed')
    path=Path(audio_path).resolve();require(path.name=='audio-build.json'and path.is_relative_to((BASE/'audio-preparation-v1').resolve()),'Only selected07.04 audio build supported')
    build=read(path);folder=path.parent
    require(build.get('schemaVersion')=='07-04-audio-build-v1'and build.get('topicId')=='07.04'and Path(build['output']).resolve()==folder,'Wrong selected audio build')
    if asr_path is not None:require(Path(asr_path).resolve()==Path(build['rawVoiceAsr']['path']).resolve(),'Requested raw ASR is not this exact audio source')
    audio=module('zen_levels_current_audio_proof',HERE/'prepare-zen-view-audio.py')
    ctx,recipe=audio.prepare(build['rawVoiceAsr']['path'],build['rawNumericalLevelReview']['path'],build['acceptedComponentsReview']['path'])
    require(recipe is not None and recipe['fingerprint']==build['fingerprint']and path==audio.DEST/recipe['fingerprint'][:24]/'audio-build.json','Current accepted scalar recipe required')
    require(audio.reuse_audio(folder,recipe)==build,'Existing audio build differs from accepted current source')
    voice=ctx['voice'];raw_review=read(verified(build['rawVoiceAsr'],'exact raw ASR'))
    line=read(folder/'line-levels.json');rows=validate_rows(voice,line,ctx['proposal']['identity']['components'])
    require(build['rawVoice']==voice['aggregateWav']and build['rawVoiceFingerprint']==voice['fingerprint']and build['canonicalTiming']==voice['timing'],'Current canonical voice clock differs')
    require(build['mixRate']==48000 and build['mixFrames']==2*voice['aggregateWav']['frames']and build['normalizedVoiceFrames']==voice['aggregateWav']['frames'],'Exact24k→48k grid changed')
    require(len(raw_review['takes'])==len(rows)and len(raw_review['boundaryWindows'])==len(rows)-1,'Exact current-N raw recognition required')
    for row,recognized in zip(rows,raw_review['takes']):
        task=recognized['task'];a,b=row['destinationSampleRange']
        require(task['sceneId']==row['sceneId']and task['audioSHA256']==row['rawTakeSHA256']and task['offsetSample']==a and task['endSample']==b and task['expected']==row['text'],'Raw recognized words use another take/grid')
        verified(dict(path=row['rawTake'],sha256=row['rawTakeSHA256']),'raw component')
        verified(dict(path=str(folder/row['normalizedTake']),sha256=row['normalizedTakeSHA256']),'normalized copy')
    pins=[pin(path),pin(folder/'line-levels.json'),build['rawVoiceAsr'],build['rawNumericalLevelReview'],build['acceptedComponentsReview'],voice['aggregateWav'],voice['timing'],pin(HERE/'first-level-continuity-review.py'),pin(HERE/'prepare-zen-view-audio.py'),pin(HERE/'run-selected-voice-qa.py')]
    manifest=None
    if render_path:
        p=Path(render_path).resolve();require(p.is_relative_to(BASE.resolve()),'Actual selected render required');manifest=read(p)
        require(manifest.get('schemaVersion')=='07-04-render-manifest-v1'and manifest.get('topicId')=='07.04'and manifest.get('slug')==BASE.name and manifest.get('complete')is True,'Actual complete07.04 renderer receipt required')
        t=read(verified(manifest['timeline'],'rendered timeline'));builder=module('zen_levels_current_timeline_proof',HERE/'build-zen-view-film-timeline.py')
        byrole={r['role']:r for r in t['inputs']}
        fresh=builder.prepare(byrole['caption-timing']['path'],byrole['audio-build']['path'],[byrole['mc-'+s]['path']for s in ('p2','p6','p7')])
        require(t==fresh and t['audio']['voice']==voice['aggregateWav']and t['audio']['mix']==build['mixWav']and t['audio']['build']==pin(path),'Movie is not the current accepted voice/mix/timeline')
        require(manifest['format']==dict(width=1080,height=1920,fps=60,totalFrames=math.ceil(build['mixFrames']*60/48000))and manifest['inputs']==t['inputs'],'Rendered clock/source snapshot changed')
        for key in ('clean','captioned','ko','en'):verified(manifest['outputs'][key],'actual '+key)
        verified(manifest['audioAac'],'shared encoded AAC');pins.extend([pin(p),manifest['timeline'],manifest['outputs']['captioned'],manifest['audioAac']])
    return dict(build=build,voice=voice,line=line,rows=rows,rawReview=raw_review,manifest=manifest,inputs=pins,resample=audio.base.stereo_voice,truePeakMaximumDbtp=audio.PROFILE['mixTruePeakMaximumDbtp'])

def unregistered(record):
    if not record or record.get('phase')!='launching-owned-cpu-measurement':return False
    command=record.get('launchCommand')
    if not command:return True
    for process in runtime.psutil.process_iter(['name','cmdline']):
        try:
            if(process.info.get('name')or'').lower()!=Path(command[0]).name.lower():continue
            if process.info['cmdline'] is None:return True
            if process.info['cmdline']==command:return True
        except runtime.psutil.NoSuchProcess:continue
        except runtime.psutil.AccessDenied:return True
    return False
def owned_alive(record):return runtime.alive(record)or unregistered(record)

def run_tool(command,log):
    command=[str(x)for x in command];ff=Path(mathqa.ffmpeg_path()).resolve()
    require(Path(command[0]).resolve()==ff,'Only installed CPU FFmpeg audio measurement/decode allowed')
    require(ACTIVE is not None,'An owned finite CPU worker is required before media processing')
    ACTIVE.update(phase='launching-owned-cpu-measurement',launchCommand=command,child=None)
    child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=CREATE);ACTIVE.update(child=runtime.identity(child.pid),phase='owned-cpu-measurement')
    out,err=child.communicate();ACTIVE.update(child=None,phase='numerical-analysis');Path(log).write_bytes(err)
    if child.returncode:raise RuntimeError('Owned CPU audio tool failed; immutable attempt/log preserved')
    return subprocess.CompletedProcess(command,child.returncode,out,err)

def decode(manifest,work):
    source=manifest['outputs']['captioned'];verified(source,'actual encoded captioned audio')
    wav=work/'decoded-encoded-aac.wav';ff=mathqa.ffmpeg_path()
    command=[ff,'-hide_banner','-nostdin','-n','-threads','2','-filter_threads','2','-hwaccel','none','-i',source['path'],'-map','0:a:0','-vn','-ar','48000','-ac','2','-c:a','pcm_f32le',str(wav)]
    run_tool(command,work/'aac-decode.log')
    return wav,dict(source=source,wav=pin(wav),command=command,decoder=pin(ff),manualSkipSamples=0,audioModified=False,alignment='No assumed AAC1024 trim; separated waveform anchors determine comparison offset only')

def loudness(path,work,label):
    ff=mathqa.ffmpeg_path();command=[ff,'-hide_banner','-nostdin','-threads','2','-filter_threads','2','-hwaccel','none','-i',str(path),'-map','0:a:0','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-']
    result=run_tool(command,work/(label+'-loudness.log'));blocks=re.findall(r'\{\s*"input_i"[\s\S]*?\}',result.stderr.decode(errors='replace'))
    require(blocks,'Actual loudness input measurement missing');values=json.loads(blocks[-1])
    require(math.isfinite(float(values['input_i']))and math.isfinite(float(values['input_tp'])),'Whole-file input level measurement is not finite')
    return dict(inputLufs=float(values['input_i']),inputTruePeakDbtp=float(values['input_tp']),source=pin(path),audioChanged=False,qualityPass=False,method='Input measurement only; FFmpeg transformed output discarded')

def numerical(ctx,arrays,raws):
    rows=ctx['rows'];recognized=ctx['rawReview']['takes'];grouped=[];checks=[];allwords=[]
    require(len(rows)==len(recognized)==len(raws)>0,'Missing actual source/recognized component')
    for row,record,raw in zip(rows,recognized,raws):
        a,b=row['destinationSampleRange'];expected=mathqa.expected_normalized(raw,row)
        checks.append(dict(sceneId=row['sceneId'],rawTakeSHA256=row['rawTakeSHA256'],rawPcmSHA256=row['rawPcmSHA256'],normalizedTakeSHA256=row['normalizedTakeSHA256'],globalRawSampleRange=[a,b],mixSampleRange=[a*2,b*2],residual=mathqa.residual_summary(arrays['normalized'][a:b],expected)))
        words=mathqa.word_records(row,record,arrays,raw,24000,48000);grouped.append((row,words));allwords.extend(words)
    summaries,flags=mathqa.continuity(grouped);build=ctx['build']
    gain=build['voiceGlobalGain']['constantGainDb']+build['uniformMixGainDb']
    prepared_residual=mathqa.residual_summary(arrays['prepared'],ctx['resample'](arrays['normalized'][:,0],24000))
    voice_residual=mathqa.residual_summary(arrays['voice'],arrays['prepared']*10**(gain/20));mix_residual=mathqa.residual_summary(arrays['mix'],arrays['voice']+arrays['music'])
    for name,residual in [('prepared-from-normalized',prepared_residual),('voice-from-prepared',voice_residual),('mix-from-known-stems',mix_residual)]+[(r['sceneId']+'-scalar-copy',r['residual'])for r in checks]:
        if residual['exceedsKnownStemTolerance']:flags.append(dict(kind='known-stage-arithmetic-mismatch',stage=name,measurement=residual))
    paragraph_summaries=[]
    for n in range(1,8):
        selected=[w for row,words in grouped if row['paragraph']==n for w in words]
        paragraph_summaries.append(dict(paragraph=n,stages={stage:mathqa.trend(selected,stage)for stage in ('canonical','normalized','voice','mix')}))
    return dict(componentSummaries=summaries,paragraphSummaries=paragraph_summaries,words=allwords,suspectRegions=flags,normalizedCopyChecks=checks,preparedFromNormalizedResidual=prepared_residual,voiceFromPreparedResidual=voice_residual,mixFromKnownStemsResidual=mix_residual)

def rebased_proof(value,work,target):
    """Receipt locations follow an atomic directory move; actual command argv stays historical."""
    if isinstance(value,list):return[rebased_proof(row,work,target)for row in value]
    if not isinstance(value,dict):return value
    result={key:rebased_proof(row,work,target)for key,row in value.items()}
    if isinstance(value.get('path'),str):
        path=Path(value['path']).resolve()
        if path.is_relative_to(work.resolve()):
            result['producedAtPath']=value['path'];result['path']=str(target/path.relative_to(work.resolve()))
    return result

def encoded_comparison(reference,decoded,words):
    alignment=mathqa.estimate_alignment(reference,decoded,48000);comparisons=[];flags=[]
    if alignment.get('supported'):
        offset=alignment['decodedMinusReferenceSamples']
        for word in words:
            a,b=[v+offset for v in word['mixSampleRange']]
            if a<0 or b>len(decoded):flags.append(dict(kind='encoded-word-window-not-covered',sceneId=word['sceneId'],word=word['recognizedText'],decodedSampleRange=[a,b]));continue
            stats=mathqa.levels(decoded[a:b],48000);delta=stats['bodyDbfs']-word['levels']['mix']['bodyDbfs']
            row=dict(sceneId=word['sceneId'],word=word['recognizedText'],context=word['recognizedContext'],decodedSampleRange=[a,b],bodyDeltaVsMixDb=delta,rmsDeltaVsMixDb=stats['rmsDbfs']-word['levels']['mix']['rmsDbfs'],levels=stats);comparisons.append(row)
            if abs(delta)>POLICY['encodedWordLevelDeltaWarningDb']and word['durationSeconds']>=.08:flags.append(dict(kind='encoded-local-level-delta',**row))
        if offset:flags.append(dict(kind='encoded-nonzero-comparison-offset',alignment=alignment,audioModified=False))
    else:flags.append(dict(kind='encoded-alignment-not-established',alignment=alignment))
    return dict(status='numerical-comparison-listening-pending'if alignment.get('supported')else'alignment-not-established-listening-required',alignment=alignment,decodedFrames=len(decoded),mixFrames=len(reference),wordComparisons=comparisons),flags

def analyze(audio_path,asr_path=None,render_path=None,decode_aac=False,measure_loudness=False):
    global ACTIVE
    worker=runtime.SingleWorker(WORKER,is_alive=owned_alive).acquire();ACTIVE=worker;work=None
    try:
        ctx=verify_bundle(audio_path,asr_path,render_path);build=ctx['build'];folder=Path(audio_path).resolve().parent
        require(not decode_aac or ctx['manifest']is not None,'Actual current render required before AAC decode')
        identity=dict(method=METHOD,reviewer=pin(__file__),numericPrimitive=pin(HERE/'first-level-continuity-review.py'),policy=POLICY,inputs=ctx['inputs'],decodeAac=bool(decode_aac),measureLoudness=bool(measure_loudness))
        fp=digest(identity);target=DEST/fp[:24]
        if (target/'review.json').is_file():
            prior=read(target/'review.json');require(prior['inputIdentity']==identity and prior['fingerprint']==fp,'Existing numerical result identity changed')
            for item in prior['artifacts']:
                require(Path(item['file']).name==item['file'],'Prior numeric artifact escaped its version')
                verified(dict(path=str(target/item['file']),sha256=item['sha256']),'prior numerical artifact')
            return prior
        require(not target.exists(),'Preserve incomplete prior numerical result')
        work=DEST/('work-'+fp[:16]+'-'+uuid.uuid4().hex[:8]);work.mkdir(parents=True,exist_ok=False);save(work/'input-identity.json',identity)
        n=ctx['voice']['aggregateWav']['frames'];m=build['mixFrames']
        arrays=dict(normalized=mathqa.load_audio(folder/'narration-component-normalized.wav',24000,1,n),prepared=mathqa.load_audio(folder/'narration-prepared-stem.wav',48000,2,m),voice=mathqa.load_audio(folder/'narration-stem.wav',48000,2,m),music=mathqa.load_audio(folder/'music-stem.wav',48000,2,m),mix=mathqa.load_audio(folder/'final-mix.wav',48000,2,m))
        raws=[mathqa.load_audio(row['rawTake'],24000,1,row['frames'])for row in ctx['rows']]
        result=numerical(ctx,arrays,raws);encoded=dict(status='pending actual encoded-audio request');full=dict(status='not requested',qualityPass=False)
        if decode_aac:
            wav,proof=decode(ctx['manifest'],work);decoded,sr=sf.read(wav,dtype='float32',always_2d=True);require(sr==48000 and decoded.shape[1]==2,'Decoded stereo sample grid differs')
            encoded,flags=encoded_comparison(arrays['mix'],decoded,result['words']);encoded['decode']=proof;result['suspectRegions'].extend(flags)
        if measure_loudness:
            full=dict(voice=loudness(folder/'narration-stem.wav',work,'voice'),mix=loudness(folder/'final-mix.wav',work,'mix'),qualityPass=False)
            if decode_aac:full['decodedAac']=loudness(wav,work,'aac')
            for stage in ('mix','decodedAac'):
                if stage in full and full[stage]['inputTruePeakDbtp']>ctx['truePeakMaximumDbtp']:
                    result['suspectRegions'].append(dict(kind='whole-input-true-peak-above-approved-limit',stage=stage,inputTruePeakDbtp=full[stage]['inputTruePeakDbtp'],maximumDbtp=ctx['truePeakMaximumDbtp'],audioChanged=False))
        fresh=verify_bundle(audio_path,asr_path,render_path);require(fresh['inputs']==ctx['inputs'],'Current audio/voice/ASR changed during analysis')
        artifacts=[dict(file=p.name,sha256=sha(p),bytes=p.stat().st_size)for p in sorted(work.iterdir())if p.is_file()]
        result.update(method=METHOD,topicId='07.04',fingerprint=fp,inputIdentity=identity,status='suspect-regions-listening-required'if result['suspectRegions']else'numerical-screen-complete-listening-pending',componentCount=len(ctx['rows']),voiceFingerprint=ctx['voice']['fingerprint'],rawAsrLiteralComparisons=[dict(sceneId=r['task']['sceneId'],recognizedLiteral=r['text'],comparison=r['comparison'])for r in ctx['rawReview']['takes']],encoded=rebased_proof(encoded,work,target),fullFileLoudness=rebased_proof(full,work,target),artifacts=artifacts,output=str(target),sampleGrid=dict(rawRate=24000,mixRate=48000,voiceOffsetSeconds=0,window='Actual word timestamps→floor/ceil raw samples→exact2x prepared/mix samples',insertedSamples=0,trimmedSamples=0),originalPcmUnchanged=True,aliasesApplied=False,automaticSpeechPass=False,actualListening=False,actualVideoPlayback=False,humanApproval=False,platformActions=[],interpretation='Known-stem/component RMS ratios and numerical trends are review targets, never estimated SNR or proof of perceived masking or hearing.')
        save(work/'review.json',result);require(not target.exists(),'Version appeared concurrently; preserve both attempts');work.rename(target);return result
    except BaseException as error:
        if work and work.exists()and not(work/'failed.json').exists():save(work/'failed.json',dict(complete=False,error=str(error),actualListening=False,sourcePcmUnchanged=True))
        raise
    finally:
        ACTIVE=None;worker.close(remove=not runtime.alive(worker.record.get('child'))and not unregistered(worker.record))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--audio-build');p.add_argument('--asr-review');p.add_argument('--render-manifest');p.add_argument('--analyze',action='store_true');p.add_argument('--decode-aac',action='store_true');p.add_argument('--measure-loudness',action='store_true');a=p.parse_args()
    if not a.audio_build:
        require(not a.analyze,'Actual selected audio-build required; nothing started');print(json.dumps(dict(ready=False,reason='Current accepted07.04 audio-build and raw-ASR required',mediaStarted=False,modelStarted=False)));return
    require(a.analyze or not(a.decode_aac or a.measure_loudness),'Decode/whole-level measurement needs explicit --analyze')
    if a.analyze:result=analyze(a.audio_build,a.asr_review,a.render_manifest,a.decode_aac,a.measure_loudness)
    else:
        ctx=verify_bundle(a.audio_build,a.asr_review,a.render_manifest);result=dict(ready=True,componentCount=len(ctx['rows']),voiceFingerprint=ctx['voice']['fingerprint'],mediaStarted=False,modelStarted=False,numericalAnalysisPerformed=False)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()

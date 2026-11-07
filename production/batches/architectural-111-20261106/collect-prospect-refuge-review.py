"""Finite06.02 future technical QA and official four-output collection adapter.

No-argument/default mode only previews prerequisites/writes. After actual render:
  python collect-prospect-refuge-review.py --render-manifest <C-media/render-manifest.json> --execute
  ... --execute --official-collect
The second form stages ONLY four final files on D, updates selected paths/titles,
and invokes unchanged scripts/collect-video-output.cjs. No render, model, GPU,
platform, Git mutation or human-listening claim occurs here.
"""
from __future__ import annotations
import argparse, hashlib, html, importlib.util, json, math, os, re, shutil, subprocess, time, unicodedata, uuid
from pathlib import Path
from fractions import Fraction
from initialize import HERE, ROOT, MEDIA, AUTH_KEY, read, save

spec=importlib.util.spec_from_file_location('prospect_review_native_util',HERE/'run-first-native.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
SLUG='shorts-leveldesign-06-02';PROJECT=ROOT/'projects'/SLUG;BASE=MEDIA/SLUG
METADATA=PROJECT/'publishing-draft-v4.json';WORKER=MEDIA/'06-02-review-worker.json'
METADATA_SHA='53eb604a620bd88e4cf332d4d676484b1d940cb26cf96e60b2e30e8abd886374'
BUILDER_SHA='eba41b08c40d88eff7aca81ce2f0c714614f638ef15ea544ef51cb48d93030e7'
RENDERER_SHA='3ba569d8b8340e338f5ab58e2be1c0944af58e6466bca8b1b69f8d75b421abe9'
MIXED_SHA='566155e4164f6884366de2141fdfa480b84d1df39c65dd876836d8f97a9ff3db'
ENCODED_AUDIO_SHA='904d72a386255033bfc99592e3cdca8eb463bf958cbc181f38270266f425e783'
COLLECTOR=ROOT/'scripts/collect-video-output.cjs'
BIN=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin')
FF=Path(os.environ.get('YAMYAM_FFMPEG',str(BIN/'ffmpeg.exe')));PROBE=FF.with_name('ffprobe.exe')
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
SUFFIX={'clean':'clean.mp4','captioned':'captioned.mp4','ko':'ko.srt','en':'en.srt'}
ACTIVE_WORKER=None
native.PROTOCOL='architectural111-06-02-final-review-v1';native.OWNER='architectural-111-06-02-final-review'


def sha(path):
    with Path(path).open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()


def run(args):
    require(ACTIVE_WORKER is not None,'An owned finite review worker is required before media/Node tools')
    command=[str(a)for a in args];executable=shutil.which(command[0]);require(executable is not None,'Selected CPU tool executable is missing')
    command[0]=str(Path(executable).resolve());allowed={FF.resolve(),PROBE.resolve()};node=shutil.which('node')
    if node and Path(command[0])==Path(node).resolve():require(command[1:]==[str(COLLECTOR),SLUG],'Only unchanged official collector for selected06.02 may run')
    else:require(Path(command[0])in allowed,'Only selected CPU FFmpeg/probe or official collector may run')
    flags=CREATE|getattr(subprocess,'BELOW_NORMAL_PRIORITY_CLASS',0)
    ACTIVE_WORKER.update(phase='launching-owned-review-tool',launchCommand=command,launchStartedAt=time.time(),child=None)
    child=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=flags)
    ACTIVE_WORKER.update(child=native.identity(child.pid),phase='owned-review-tool')
    stdout,stderr=child.communicate()
    ACTIVE_WORKER.update(child=None,phase='review-processing',launchCommand=None)
    if child.returncode:raise RuntimeError(stderr.decode(errors='replace')[-6000:])
    return subprocess.CompletedProcess(command,child.returncode,stdout,stderr)


def unrecorded_child_alive(record):
    """Fail closed during the known Popen->identity gap; never terminate peers."""
    if not record or record.get('phase')!='launching-owned-review-tool':return False
    command=record.get('launchCommand')
    if not command:return True
    import psutil
    for process in psutil.process_iter(['name','cmdline']):
        try:
            if(process.info.get('name')or'').lower()!=Path(command[0]).name.lower():continue
            if process.info.get('cmdline')is None or process.info['cmdline']==command:return True
        except psutil.NoSuchProcess:continue
        except psutil.AccessDenied:return True
    return False


def owned_alive(record):return native.alive(record)or unrecorded_child_alive(record)


def child_pending_or_alive(record):return bool(record)and(native.alive(record.get('child'))or unrecorded_child_alive(record))


def authorize():
    control=read(ROOT/'shared/publishing/video-production-control.json')[AUTH_KEY]
    assert control['userEvidence']=='111개 전체 제작 들어가줘' and control['status'] not in ('paused','stopped','cancelled')
    assert control['automaticAdvanceWithinExactList'] and not control['automaticAdvanceOutsideList']
    assert control['humanFinalReviewRequired'] and not control['youtubeAuthorized']
    batch=read(HERE/'batch.json')
    require(batch['localFinalReviewOnly'] and any(p['topicId']=='06.02' and p['slug']==SLUG for p in batch['projects']),'06.02 is not an exact selected batch member')
    require(read(HERE/'checkpoint.json').get('currentTopicId')=='06.02','Only the currently selected06.02 may collect or stage outputs')


def scoped(path):
    result=Path(path).resolve()
    assert result.is_relative_to(BASE.resolve()),'Final render/review escaped selected C-media project'
    return result


def metadata_packet(source,master_sha):
    assert source['topicId']=='06.02'
    require(source.get('sourceNarration')==pin(PROJECT/'narration-expanded-draft-v4.json'),'Publishing metadata must bind current V4 narration; preserve previous metadata versions')
    assert source.get('masterSHA256') in (None,master_sha),'Metadata belongs to another master'
    for key in ('titleKo','titleEn','descriptionKo','descriptionEn'):
        assert isinstance(source.get(key),str) and source[key].strip(),'Missing exact authored publishing metadata: '+key
    return dict(titles=dict(ko=source['titleKo'],en=source['titleEn']),
        descriptions=dict(ko=source['descriptionKo'],en=source['descriptionEn']),masterSHA256=master_sha,
        sourceMetadataState=source.get('status'),metadataFinalCutConformance='pending-root-review',
        actualHumanFinalReview=False,youtubeAuthorized=False,driveAuthorized=False)


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


def pin(path):return dict(path=str(Path(path).resolve()),sha256=sha(path))


def require(value,reason):
    if not value:raise ValueError(reason)


def role(timeline,name):
    rows=[r for r in timeline['inputs'] if r.get('role')==name]
    require(len(rows)==1,'One exact current input required: '+name)
    row=rows[0];require(sha(row['path'])==row['sha256'],'Changed dependency: '+name)
    return row


def verified_mixed_review(path,audio_path,voice):
    """Re-derive cached evidence only; never summary()/recognize()/write/reuse raw ASR."""
    helper=HERE/'run-prospect-refuge-mix-asr.py';require(sha(helper)==MIXED_SHA,'Reviewed independent actual-mix adapter changed')
    mixed=module('prospect_collector_mixed_proof',helper)
    job=mixed.prepare_job(audio_path);output=Path(job['output']).resolve()
    path=Path(path).resolve();require(path==output/'review.json','Exact current mixed-ASR output required')
    stored_job=read(output/'job.json')
    require(stored_job==job,'Independent mixed-ASR job/provenance changed')
    for source in job['sourcePins']:
        require(sha(source['path'])==source['sha256'],'Mixed ASR source changed')
    records=[mixed.cached(job,task) for task in job['identity']['tasks']]
    require(all(r is not None for r in records),'Actual mixed ASR has incomplete task caches')
    value=read(path);takes=[r for r in records if r['task']['kind']=='take'];joins=[r for r in records if r['task']['kind']=='boundary']
    count=len(voice['identity']['scenes']);mix=job['identity']['mix']
    require(count==103 and len(takes)==25 and len(joins)==24 and [r['task']['paragraphIndex']for r in takes]==list(range(1,26)),'Current103 components /25 mixed paragraphs /24 joins required')
    require(value.get('takes')==takes and value.get('boundaryWindows')==joins,'Literal mixed recognition records changed')
    require(value.get('status')=='mixed-asr-complete-literal-and-listening-review-pending' and value.get('topicId')=='06.02','Wrong completed mixed review')
    for key,expected in dict(fingerprint=job['fingerprint'],audioBuildFingerprint=job['identity']['audioBuildFingerprint'],mixSHA256=mix['sha256'],mixedAudioPath=mix['path'],voiceFingerprint=voice['fingerprint'],sampleRate=48000,frames=mix['frames'],coveredSamples=mix['frames'],fullActualMixCoverage=True,rawVoiceAsr=job['rawVoiceAsr']).items():
        require(value.get(key)==expected,'Stale or incomplete actual-mix proof: '+key)
    require(takes[0]['task']['beginSample']==0 and takes[-1]['task']['endSample']==mix['frames'] and all(a['task']['endSample']==b['task']['beginSample'] for a,b in zip(takes,takes[1:])),'Every final mixed sample must be covered exactly once')
    physical=[p for r in takes for p in r['task']['sourcePhysicalComponents']]
    require(len(physical)==103 and [p['sceneId']for p in physical]==[s['id']for s in voice['identity']['scenes']]and value.get('physicalComponentMapping')==physical and value.get('physicalComponentCount')==103,'Final mix physical103 provenance/order differs')
    paragraphs=[dict(paragraph=r['task']['paragraphIndex'],sceneIds=r['task']['sourcePhysicalSceneIds'],expectedLiteral=r['task']['expected'],recognizedLiteral=r['text'],comparison=mixed.raw.comparison(r['task']['expected'],r['text']),globalWords=r['globalWords'],recognitionBasis='independent-actual-final-mix-full-paragraph-window',sourceResult=pin(Path(job['output'])/(r['task']['key']+'.json')))for r in takes]
    require(value.get('paragraphs')==paragraphs,'Mixed literal comparisons were hidden or rewritten')
    for key in ('rawVoiceRecognitionReusedAsMix','normalizedStemRecognized','encodedAACChecked','aliasesApplied','pcmModified','automaticSpeechPass','humanListening','finalApproval'):
        require(value.get(key) is False,'Unsupported mixed-ASR approval or input substitution: '+key)
    require(value.get('expectedPrompt') is None and value.get('hotwords') is None,'Recognition was not blind')
    return pin(path)


def semantic_binding(path,timeline):
    """Project existing actual25KO/EN source reviews; never infer media approval."""
    path=Path(path or PROJECT/'root-readthrough-v4.json').resolve()
    require(path== (PROJECT/'root-readthrough-v4.json').resolve(),'Use exact current root authored readthrough, not an arbitrary approval receipt')
    review=read(path);source=PROJECT/'source-clause-remediation-conformance-v1.json';conformance=read(source)
    require(review.get('schemaVersion')=='06-02-root-readthrough-v4' and review.get('topicId')=='06.02' and review.get('paragraphs')==25,'Existing actual25KO/EN root source review required')
    require(review.get('sourceNarration')==pin(PROJECT/'narration-expanded-draft-v4.json') and review.get('semanticComponents')==pin(PROJECT/'voice-semantic-components-v3.json') and review.get('sourceConformance')==pin(source),'Root authored readthrough belongs to another source version')
    require(review.get('retainedSourceOrder') is True and review.get('all14LearningRolesRetained') is True and review.get('independentExact103SourceCharCheck') is True and review.get('logicalViewerBeats')==96 and review.get('physicalVoiceComponents')==103,'Authored source roles/order/103logical map were not retained')
    require(conformance.get('schemaVersion')=='06-02-source-clause-remediation-conformance-v1' and conformance.get('internalSourceReviewed') is True and conformance.get('manualSourceSemanticReview') is True and conformance.get('koCueCount')==190 and conformance.get('enCueCount')==234 and conformance.get('all14SourceLearningRolesAndOrderRetained') is True,'Exact internal bilingual source-conformance review required')
    for row in conformance['newArtifacts']:require(sha(row['path'])==row['sha256'],'Current reviewed source artifact changed')
    for q in [pin(PROJECT/'narration-expanded-draft-v4.json'),pin(PROJECT/'caption-clauses-v4.json'),pin(PROJECT/'translated-caption-anchors-v3.json')]:require(q in conformance['newArtifacts'],'Current authored caption source missing from conformance proof')
    require(all(review.get(k)is False for k in ('actualListening','actualEncodedVisualReview','humanApproval')) and all(conformance.get(k)is False for k in ('actualListening','actualEncodedVisualReview','humanApproval')),'Authored source review cannot masquerade as human/media review')
    return dict(topicId='06.02',manualSemanticReview=True,allParagraphTextsRetained=True,reviewedBy='Codex root source read-through and authored clause conformance',narration=pin(PROJECT/'narration-expanded-draft-v4.json'),captionClauses=pin(PROJECT/'caption-clauses-v4.json'),translatedAnchors=pin(PROJECT/'translated-caption-anchors-v3.json'),sourceTextReviews=[pin(path),pin(source)],approvalScope='Authored25KO/ENparagraph correspondence and internal source review only;190KO/234EN independent ASR-bound display cues, not human media approval.',actualHumanListening=False,actualFullPlayback=False,humanFinalApproval=False)


def load_inputs(path,metadata_path,mixed_review_path,semantic_review_path=None,encoded_audio_path=None):
    authorize();path=scoped(path);render=read(path)
    require(render.get('schemaVersion')=='06-02-render-manifest-v2' and render.get('topicId')=='06.02' and render.get('complete') is True,'Completed actual selected06.02 renderer receipt required')
    require(render.get('format')==dict(width=1080,height=1920,fps=60) and render.get('gpuEncoding') is False and render.get('modelsStarted') is False,'Actual software portrait FHD60 provenance required')
    timeline_pin=render['timeline'];timeline_path=scoped(timeline_pin['path']);require(sha(timeline_path)==timeline_pin['sha256'],'Render timeline changed')
    timeline=read(timeline_path);bp=HERE/'build-prospect-refuge-film-timeline-v2.py';rp=HERE/'render-prospect-refuge-film-v2.py'
    require(sha(bp)==BUILDER_SHA and sha(rp)==RENDERER_SHA,'Reviewed selected timeline/renderer source changed')
    require(role(timeline,'renderer')==dict(role='renderer',**pin(rp)),'Rendered source pin differs from reviewed actual renderer')
    builder=module('prospect_collector_timeline',bp)
    fresh=builder.prepare(role(timeline,'caption-timing')['path'],role(timeline,'audio-build')['path'],[role(timeline,'mc-p%02d'%n)['path']for n in(4,25)],role(timeline,'annotation-plan')['path'],role(timeline,'picture-overrides')['path'],role(timeline,'mix-clock-proof')['path'])
    require(fresh==timeline,'Current ASR/raw PCM/scalar mix/source/crop/picture clock changed')
    require(timeline_path==BASE/'film-timelines-v2'/timeline['fingerprint'][:24]/'timeline.json','Exact selected immutable timeline location required')
    require(render.get('totalFrames')==timeline['totalFrames'] and render.get('inputs')==timeline['inputs'],'Rendered frame clock/input snapshot differs')
    sources={};require(set(render['outputs'])==set(SUFFIX),'Exactly four selected outputs required')
    for key,suffix in SUFFIX.items():
        row=render['outputs'][key];source=scoped(row['path'])
        require(source.name==SLUG+'.'+suffix and source.is_file() and sha(source)==row['sha256'],'Missing or changed selected output: '+key);sources[key]=source
    timing=read(role(timeline,'caption-timing')['path']);voice_refs=[r for r in timing['inputs']if r.get('role')=='voiceEvidence'];require(len(voice_refs)==1,'Immutable actual103 voice evidence required')
    require(sha(voice_refs[0]['path'])==voice_refs[0]['sha256'],'Raw voice evidence changed');voice=read(voice_refs[0]['path'])
    require(timeline['audio']['voice']==voice['aggregateWav'],'Canonical selected voice changed')
    mix_pin=verified_mixed_review(mixed_review_path,role(timeline,'audio-build')['path'],voice)
    helper=HERE/'review-prospect-refuge-encoded-audio.py';require(ENCODED_AUDIO_SHA and helper.is_file() and sha(helper)==ENCODED_AUDIO_SHA,'Independent encoded-audio QA source freeze pending')
    require(encoded_audio_path is not None,'Actual separate encoded-AAC/levels/truepeak report required; collector will not launch it implicitly')
    encoded=module('prospect_collector_encoded_audio',helper).verify_existing(encoded_audio_path,render_manifest=path)
    metadata_path=Path(metadata_path).resolve();require(metadata_path==METADATA.resolve()and sha(metadata_path)==METADATA_SHA,'Only exact root-reviewed publishing metadataV4 may collect; a new version requires explicit repin')
    metadata_source=read(metadata_path)
    for row in metadata_source.get('sourceBindings',[]):require(sha(row['path'])==row['sha256'],'Publishing source/rights/credit evidence changed')
    metadata=metadata_packet(metadata_source,render['outputs']['captioned']['sha256']);semantic=semantic_binding(semantic_review_path,timeline)
    pins=dict(renderManifest=pin(path),timeline=pin(timeline_path),metadata=pin(metadata_path),mixedAsrReview=mix_pin,encodedAudioReview=pin(encoded_audio_path),encodedAudioHelper=pin(helper),outputs=render['outputs'],audio=timeline['audio'],officialCollectorSHA256=sha(COLLECTOR),reviewHelperSHA256=sha(__file__),semanticReview=semantic)
    fingerprint=hashlib.sha256(json.dumps(pins,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    metadata.update(version=fingerprint[:24],reviewFingerprint=fingerprint,sourceMetadata=pin(metadata_path),timelineSHA256=timeline_pin['sha256'])
    return dict(render=render,timeline=timeline,sources=sources,metadata=metadata,pins=pins,fingerprint=fingerprint,semanticAlignment=semantic,encodedAudio=encoded)


def caption_contract(timeline,tracks,authored):
    """Independent KO/EN cue counts; exact twenty-five-paragraph semantic source order."""
    require(len(authored['narrationKo'])==len(authored['paragraphsEn'])==25,'Exactly twenty-five authored bilingual paragraphs required')
    fold=lambda value:re.sub(r'\s+','',unicodedata.normalize('NFC',value))
    paragraphs=read(role(timeline,'caption-timing')['path'])['paragraphs']
    require([r['paragraph'] for r in paragraphs]==list(range(1,26)),'Current twenty-five paragraph clocks required')
    result={}
    for language,field in [('ko','narrationKo'),('en','paragraphsEn')]:
        rows=timeline['captions'][language];cues=tracks[language]
        require(len(rows)==(190 if language=='ko'else 234),'Exact current190KO/234EN authored cue set required')
        require(len(rows)==len(cues)>0 and len({r['id'] for r in rows})==len(rows),'Caption cue omission/duplication')
        previous=0
        for i,(row,cue) in enumerate(zip(rows,cues),1):
            a,b=row['startFrame'],row['endFrameExclusive']
            require(type(a)is int and type(b)is int and previous<=a<b<=timeline['totalFrames'],'Invalid actual subtitle clock');previous=b
            require(cue['index']==i and abs(cue['start']-a/60)<=.001 and abs(cue['end']-b/60)<=.001,'SRT does not retain exact ASR-derived cue clock')
            require(1<=len(row['lines'])<=2 and fold('\n'.join(row['lines']))==fold(row['text']),'Rendered caption lines do not retain exact authored display literal')
            require(cue['text'] in (row['text'],'\n'.join(row['lines'])) and fold(cue['text'])==fold(row['text']),'SRT does not retain exact authored display literal')
        for n,p in enumerate(paragraphs,1):
            selected=[r for r in rows if r['paragraph']==n]
            require(selected and fold(' '.join(r['text'] for r in selected))==fold(authored[field][n-1]),'Authored paragraph omitted/reordered/rewritten')
            require(p['startFrame']<=selected[0]['startFrame']<selected[-1]['endFrameExclusive']<=p['endFrameExclusive'],'Caption escapes actual paragraph')
        result[language+'Cues']=len(rows)
    result.update(all25AuthoredKoEnParagraphsRetained=True,independentTranslationCueCounts=True,captionFramesBoundToTimeline=True,aliasesApplied=False,speechQualityPass=False,humanListening=False,alignmentReview='Retained in exact caption timing and mixed-ASR pins; English is translated Korean semantic alignment, not English speech recognition')
    return result


def section_contract(timeline):
    count=timeline['totalFrames'];position=0;counts={};samples={0,count-1}
    for row in timeline['sections']:
        a,b=row['startFrame'],row['endFrameExclusive'];require(type(a)is int and type(b)is int and a==position<b<=count,'Picture cuts must cover whole exact frame clock')
        require(row['kind']in('gameplay','native','mc'),'Unexpected picture kind');counts[row['kind']]=counts.get(row['kind'],0)+b-a;position=b
        samples.add((a+b-1)//2)
    require(position==count and timeline['sections'][0]['kind']=='gameplay','Opener must show selected actual gameplay')
    # Every current KO cue gets one real encoded midpoint. Additional source,
    # guide and cat samples share that finite set instead of repeated extracts.
    for row in timeline['captions']['ko']:samples.add((row['startFrame']+row['endFrameExclusive']-1)//2)
    for row in timeline.get('paragraphs',[]):samples.update((row['startFrame'],row['endFrameExclusive']-1))
    for row in timeline.get('guideCues',[]):samples.add((row['startFrame']+row['endFrameExclusive']-1)//2)
    for cue in timeline.get('catCues',[]):
        a,b=cue['startFrame'],cue['endFrameExclusive'];require(type(a)is int and type(b)is int and 0<=a<b<=count,'Invalid cat clock');samples.add((a+b-1)//2)
    require(0<len(samples)<=512 and all(type(f)is int and 0<=f<count for f in samples),'Finite encoded-sample selection exceeded its512 bound')
    return counts,sorted(samples)


def srt(path):
    blocks=re.split(r'\r?\n\s*\r?\n',Path(path).read_text(encoding='utf-8-sig').strip());rows=[]
    clock=r'(\d+):(\d{2}):(\d{2}),(\d{3})'
    for i,block in enumerate(blocks,1):
        lines=block.splitlines();assert len(lines)>=3 and lines[0]==str(i),'Invalid sequential SRT cue'
        match=re.fullmatch(clock+' --> '+clock,lines[1]);assert match,'Invalid SRT timestamp'
        values=list(map(int,match.groups()));convert=lambda j:values[j]*3600+values[j+1]*60+values[j+2]+values[j+3]/1000
        start,end=convert(0),convert(4);text='\n'.join(lines[2:])
        assert text.strip() and 0<=start<end and (not rows or start>=rows[-1]['end']-.001)
        assert len(lines[2:])<=2,'Caption exceeds current two-line contract'
        rows.append(dict(index=i,start=start,end=end,text=text))
    assert rows;return rows






def video_contract(info,pts,total_frames):
    videos=[s for s in info['streams'] if s['codec_type']=='video'];audios=[s for s in info['streams'] if s['codec_type']=='audio']
    assert len(videos)==len(audios)==1,'Exactly one video and one audio stream required'
    v,a=videos[0],audios[0]
    assert (v['width'],v['height'])==(1080,1920) and v['codec_name']=='h264'
    assert v.get('pix_fmt')=='yuv420p','Current browser-compatible H264 pixel format required'
    assert Fraction(v['r_frame_rate'])==Fraction(v['avg_frame_rate'])==60
    assert v.get('sample_aspect_ratio','1:1')=='1:1'
    assert a['codec_name']=='aac' and int(a['sample_rate'])==48000 and a['channels']==2
    assert len(pts)==total_frames,'Actual decoded frame count differs from timeline'
    assert all(math.isfinite(x) and abs(x-i/60)<=.00002 for i,x in enumerate(pts)),'Decoded PTS discontinuity or shifted origin'
    assert abs(float(v['duration'])-total_frames/60)<=1/60+.001
    return dict(width=1080,height=1920,fps=60,decodedFrames=len(pts),firstPts=pts[0],lastPts=pts[-1],
        videoDurationSeconds=float(v['duration']),formatDurationSeconds=float(info['format']['duration']),
        audioCodec='aac',audioSampleRate=48000,audioChannels=2)


def packet_signature(packets):
    return [(p.get('pts_time'),p.get('dts_time'),p.get('duration_time'),p.get('data_hash'),p.get('flags')) for p in packets]


def same_audio(first,second):
    assert first and packet_signature(first)==packet_signature(second),'AAC payload/timestamp sequence differs between masters'
    assert all(p.get('data_hash','').startswith('SHA256:') for p in first),'AAC payload hashes absent'
    return dict(identicalPacketPayloadAndTiming=True,packetCount=len(first),packetSequenceSHA256=
        hashlib.sha256(json.dumps(packet_signature(first),separators=(',',':')).encode()).hexdigest())


def probe_video(path,total_frames):
    info=json.loads(run([PROBE,'-v','error','-threads','2','-show_streams','-show_format','-of','json',path]).stdout)
    frames=json.loads(run([PROBE,'-v','error','-threads','2','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','json',path]).stdout)['frames']
    pts=[float(f['best_effort_timestamp_time']) for f in frames]
    result=video_contract(info,pts,total_frames)
    run([FF,'-v','error','-xerror','-err_detect','explode','-threads','2','-hwaccel','none','-i',path,
         '-map','0:v:0','-map','0:a:0','-f','null','-'])
    packets=json.loads(run([PROBE,'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256',
        '-show_entries','packet=pts_time,dts_time,duration_time,data_hash,flags','-of','json',path]).stdout)['packets']
    result.update(wholeVideoAndAudioDecodePassed=True,realTimePlaybackPerformed=False,humanListeningPerformed=False)
    return result,packets


def selection_expression(frames):
    """Same exact frame membership with logarithmic arithmetic-parser depth."""
    require(frames and frames==sorted(set(frames))and all(type(f)is int and f>=0 for f in frames),'Exact sorted unique integer frame selection required')
    level=[f'eq(n\\,{n})'for n in frames]
    while len(level)>1:level=['('+level[i]+'+'+level[i+1]+')'if i+1<len(level)else level[i]for i in range(0,len(level),2)]
    return level[0]


def mobile_samples(source,frames,folder,master_sha,timeline):
    from PIL import Image
    require(frames==sorted(set(frames)) and 0<len(frames)<=512 and all(type(f)is int and 0<=f<timeline['totalFrames'] for f in frames),'Finite exact unique decoded frames required')
    require(not any(folder.glob('1080-*.png')) and not any(folder.glob('375-*.png')),'Preserve previous samples; use a new empty sample destination')
    expression=selection_expression(frames)
    graph=f'[0:v]select={expression},split[full][small];[small]scale=375:-1[mobile]'
    run([FF,'-v','error','-n','-threads','2','-hwaccel','none','-i',source,'-filter_complex_threads','1','-filter_complex',graph,
        '-map','[full]','-fps_mode','passthrough',folder/'1080-%03d.png',
        '-map','[mobile]','-fps_mode','passthrough',folder/'375-%03d.png'])
    require(len(list(folder.glob('1080-*.png')))==len(frames)==len(list(folder.glob('375-*.png'))),'Actual sample decode omitted or added requested frames')
    rows=[]
    for i,frame in enumerate(frames,1):
        entry=dict(frame=frame,ptsSeconds=frame/60,captionedMasterSHA256=master_sha,
            captionIds={lang:[r['id'] for r in rows if r['startFrame']<=frame<r['endFrameExclusive']] for lang,rows in timeline['captions'].items()},
            actualAgentVisualInspection='pending',native={},mobile={})
        for key,prefix,size in [('native','1080',(1080,1920)),('mobile','375',(375,667))]:
            path=folder/f'{prefix}-{i:03d}.png'
            with Image.open(path) as image:image.load();assert image.size==size
            entry[key]=dict(file=path.name,sha256=sha(path),width=size[0],height=size[1])
        rows.append(entry)
    return dict(schemaVersion='06-02-encoded-mobile-samples-v1',samples=rows,
        imageSource='Actual encoded captioned master, selected decoded frame at native PTS',
        captionClearanceOrMobileLegibilityApproved=False,actualFullPlaybackPerformed=False,humanListening=False)


def review_page(packet,qa,samples):
    esc=html.escape;title=packet['titles']['ko'];master=packet['masterSHA256']
    notice='기술 검사와 표본 추출 결과입니다. 실제 전체 청취·실시간 재생·모바일 표본 검수·사용자 최종 검수는 별도로 확인해야 합니다.'
    links=''.join(f'<li><a href="{SLUG}.{suffix}" download>{esc(suffix)}</a></li>' for suffix in SUFFIX.values())
    gallery=''.join(f'<figure><a href="{esc(r["native"]["file"])}"><img loading="lazy" width="375" src="{esc(r["mobile"]["file"])}"></a>'
        f'<figcaption>frame {r["frame"]} · {r["ptsSeconds"]:.3f}s · visual inspection pending</figcaption></figure>' for r in samples['samples'])
    return ('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        f'<title>{esc(title)}</title><style>body{{max-width:900px;margin:28px auto;padding:16px;background:#090b0b;color:#eee;font:17px/1.6 sans-serif}}'
        'a{color:#b7d7b1}video{max-width:100%;max-height:75vh;background:black}pre{white-space:pre-wrap;overflow-wrap:anywhere}.notice{border-left:4px solid #e8cf83;padding:12px}figure{margin:24px 0}img{max-width:100%;height:auto}figcaption{font-size:14px}</style>'
        f'<h1>{esc(title)}</h1><p class="notice">{notice}</p><video controls preload="metadata" src="{SLUG}.captioned.mp4"></video>'
        f'<p>1080×1920 · 60fps · {qa["videos"]["captioned"]["decodedFrames"]} 프레임 · 검수 버전 {esc(packet["version"])}</p><pre>Master SHA256: {master}</pre>'
        f'<ul>{links}</ul><p><a href="publishing-metadata.json">정확한 한영 제목·설명</a> · <a href="technical-qa.json">검수 범위</a> · <a href="mobile-samples.json">실제 인코딩 표본 목록</a></p>'
        f'<h2>한국어 설명</h2><pre>{esc(packet["descriptions"]["ko"])}</pre><h2>English</h2><p>{esc(packet["titles"]["en"])}</p>'
        f'<pre>{esc(packet["descriptions"]["en"])}</pre><details><summary>실제 인코딩 모바일 표본 · 검수 대기</summary>{gallery}</details></html>')


def existing_review(folder,data):
    """Only this exact immutable technical review may be reused, never arbitrary paths."""
    folder=scoped(folder);prior=read(folder/'review-receipt.json')
    require(prior.get('fingerprint')==data['fingerprint'] and prior.get('pins')==data['pins'] and prior.get('metadata')==data['metadata'],'Existing review belongs to another exact input/master/metadata version')
    require(Path(prior['output']).resolve()==folder and prior.get('semanticAlignment')==data['semanticAlignment'],'Existing review location or semantic proof changed')
    require(set(prior['deliverables'])==set(SUFFIX),'Existing review is not exactly four outputs')
    for key,row in prior['deliverables'].items():
        require(row['file']==SLUG+'.'+SUFFIX[key] and row['sha256']==data['render']['outputs'][key]['sha256'],'Existing output identity changed')
        require(sha(folder/row['file'])==row['sha256'] and (folder/row['file']).stat().st_size==row['bytes'],'Existing review output bytes changed')
    artifacts=prior['reviewArtifacts'];require(len({r['file'] for r in artifacts})==len(artifacts),'Duplicated review artifact')
    for row in artifacts:
        require(Path(row['file']).name==row['file'] and sha(folder/row['file'])==row['sha256'],'Existing review artifact changed or escaped its directory')
    require(sha(folder/'index.html')==prior['indexSHA256'],'Existing review page changed')
    return prior


def collect_review(data):
    global ACTIVE_WORKER
    authorize();worker=native.SingleWorker(WORKER,is_alive=owned_alive).acquire();worker.update(stage='final-four-output-qa',topicId='06.02')
    ACTIVE_WORKER=worker
    try:
        folder=scoped(BASE/'local-final-review'/data['fingerprint'][:24]);receipt=folder/'review-receipt.json'
        if folder.exists():
            return existing_review(folder,data)
        work=scoped(BASE/'review-staging'/('qa-'+uuid.uuid4().hex));work.mkdir(parents=True,exist_ok=False)
        save(work/'input-pins.json',data['pins']);fmt=data['render']['format'];videos={};audio={}
        for key in ('clean','captioned'):videos[key],audio[key]=probe_video(data['sources'][key],data['timeline']['totalFrames'])
        identical=same_audio(audio['clean'],audio['captioned'])
        if data['render'].get('audioAac'):
            source_packets=json.loads(run([PROBE,'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256',
                '-show_entries','packet=pts_time,dts_time,duration_time,data_hash,flags','-of','json',data['render']['audioAac']['path']]).stdout)['packets']
            # Container time-base rounding may differ; immutable payload ordering must match the one encoded source.
            assert [p['data_hash'] for p in source_packets]==[p['data_hash'] for p in audio['captioned']]
        tracks={k:srt(data['sources'][k]) for k in ('ko','en')}
        caption_qa=caption_contract(data['timeline'],tracks,read(PROJECT/'narration-expanded-draft-v4.json'))
        for language in ('ko','en'):
            assert sha(data['timeline']['subtitles'][language]['path'])==data['render']['outputs'][language]['sha256']
            assert data['timeline']['subtitles'][language]['sha256']==data['render']['outputs'][language]['sha256']
        kinds,sample_frames=section_contract(data['timeline'])
        samples=mobile_samples(data['sources']['captioned'],sample_frames,work,data['metadata']['masterSHA256'],data['timeline'])
        save(work/'mobile-samples.json',samples);save(work/'encoded-audio-packets.json',audio)
        deliverables={}
        for key,source in data['sources'].items():
            target=work/source.name;shutil.copy2(source,target)
            assert sha(target)==data['render']['outputs'][key]['sha256']
            deliverables[key]=dict(file=target.name,sha256=sha(target),bytes=target.stat().st_size)
        qa=dict(status='technical-four-output-qa-complete-visual-listening-review-pending',videos=videos,sameAac=identical,
            captions=caption_qa,frameCountsBySourceKind=kinds,actualGameplayShare=kinds.get('gameplay',0)/data['timeline']['totalFrames'],
            wholeDecodePerformed=True,actualFullPlaybackPerformed=False,actualHumanListening=False,userFinalReview=False,
            encodedMobileSamplesExtracted=len(samples['samples']),encodedMobileSampleVisualInspection='pending',
            finalMixedAsr=dict(status='verified-existing-independent-exact-mix-ASR',proof=data['pins']['mixedAsrReview'],literalReviewAndHumanListeningPending=True),encodedAlignedLevels=dict(status='verified-existing-current-encoded-audio-review',proof=data['pins']['encodedAudioReview'],report=data['encodedAudio']),remainingListeningAndLiteralTargets='Retained verbatim in pinned raw/mix/encoded numerical and literal reviews; no full hearing or speech-quality pass inferred',encodedPictureContinuitySemanticReview='pending actual moving/output review; decode and sample extraction are not semantic or full-motion approval',
            pins=data['pins'],platformActions=[])
        save(work/'technical-qa.json',qa);save(work/'publishing-metadata.json',data['metadata'])
        (work/'index.html').write_text(review_page(data['metadata'],qa,samples),encoding='utf-8')
        assert load_inputs(data['pins']['renderManifest']['path'],data['pins']['metadata']['path'],data['pins']['mixedAsrReview']['path'],None,data['pins']['encodedAudioReview']['path'])['fingerprint']==data['fingerprint']
        result=dict(status=qa['status'],semanticAlignment=data['semanticAlignment'],fingerprint=data['fingerprint'],output=str(folder),deliverables=deliverables,
            metadata=data['metadata'],pins=data['pins'],indexSHA256=sha(work/'index.html'),technicalQA='technical-qa.json',
            reviewArtifacts=[dict(file=p.name,sha256=sha(p),bytes=p.stat().st_size) for p in sorted(work.iterdir()) if p.is_file()],
            humanFinalReview=False,platformActions=[])
        save(work/'review-receipt.json',result);folder.parent.mkdir(parents=True,exist_ok=True)
        assert not folder.exists();work.rename(folder);return result
    finally:
        ACTIVE_WORKER=None;worker.close(remove=not child_pending_or_alive(worker.record))


def preview(master='<captioned-SHA256>'):
    stage=PROJECT/'production/local/publishing-source'/master
    return dict(cMediaReview=str(BASE/'local-final-review'/'<version>'),fourFileStaging=str(stage),
        selectedProjectFields=['paths.videoBurnedCaptions','paths.videoClean','paths.captionsKo','paths.captionsEn','paths.captionAlignmentReview','titles.ko','titles.en'],
        officialCommand=['node','scripts/collect-video-output.cjs',SLUG],
        expectedCollectorWrites=[str(ROOT/'output'/SLUG),str(ROOT/'output/index.html'),
            str(PROJECT/'production/delivery-output.json'),str(PROJECT/'rebuild.json'),
            str(PROJECT/'production/delivery-stage-<unique>'),str(PROJECT/'production/delivery-history/<previous-version-if-present>')],
        semanticReviewRequiredForOfficialCollection='Existing current narration+caption-clauses source-text review; never human media approval',
        rawMediaBulkCopiedToD=False,platformActions=[],requiredFreeD='2 * actual four-file bytes + 2 GiB')


def project_patch(document,paths,titles):
    result=dict(document);result['paths']=dict(document.get('paths',{}),**paths);result['titles']=dict(document.get('titles',{}),**titles)
    return result


def alignment_for_official(timeline,tracks,stage,semantic_review):
    require(semantic_review is not None,'Official unequal-cue collection requires current authored semantic text review')
    paragraphs=[]
    for n in range(1,26):
        row=dict(paragraph=n)
        bounds=[]
        for language in ('ko','en'):
            rows=timeline['captions'][language];indices=[i for i,r in enumerate(rows,1) if r['paragraph']==n]
            require(indices,'Missing bilingual paragraph indices')
            row[language+'Cues']=indices
            bounds.append((tracks[language][indices[0]-1]['start'],tracks[language][indices[-1]-1]['end']))
        require(bounds[0]==bounds[1],'Paragraph caption endpoints differ; preserve and inspect before official collection')
        row.update(start=bounds[0][0],end=bounds[0][1]);paragraphs.append(row)
    return dict(status='approved-semantic-paragraph-alignment',topicId='06.02',approved=True,manualSemanticReview=True,
        allParagraphTextsRetained=True,paragraphs=paragraphs,sourceTextReview=semantic_review,
        captions=[dict(language=lang,path=(stage/(SLUG+'.'+lang+'.srt')).relative_to(ROOT).as_posix(),sha256=sha(stage/(SLUG+'.'+lang+'.srt')),cues=len(tracks[lang])) for lang in ('ko','en')],
        approvalScope='Authored KO/EN semantic paragraph correspondence only; independent clause timings remain ASR-bound',
        actualHumanListening=False,actualFullPlayback=False,humanFinalApproval=False,platformActions=[])


def verify_saved_review(result):
    folder=scoped(result['output']);require(folder.name==result['fingerprint'][:24] and folder.parent==BASE/'local-final-review','Wrong selected local-review folder')
    require(read(folder/'review-receipt.json')==result,'Local review receipt changed')
    require(set(result['deliverables'])==set(SUFFIX),'Exactly four final files required')
    for key,row in result['deliverables'].items():
        require(row['file']==SLUG+'.'+SUFFIX[key] and sha(folder/row['file'])==row['sha256'],'Changed review deliverable')
    for row in result['reviewArtifacts']:
        require(Path(row['file']).name==row['file'] and sha(folder/row['file'])==row['sha256'],'Review artifact changed')
    require(sha(folder/'index.html')==result['indexSHA256'],'Review page changed')
    pins=result['pins']
    data=load_inputs(pins['renderManifest']['path'],pins['metadata']['path'],pins['mixedAsrReview']['path'],None,pins['encodedAudioReview']['path'])
    require(data['fingerprint']==result['fingerprint'],'Current approved inputs no longer match local review')
    require(existing_review(folder,data)==result,'Only exact current immutable technical review may be staged')
    return data


def _official_collect(result):
    data=verify_saved_review(result)
    require(data['semanticAlignment'] is not None,'Current manual authored-text semantic review required before official bilingual collection')
    authorize();master=result['metadata']['masterSHA256'];folder=Path(result['output']);files=result['deliverables']
    required=2*sum((folder/r['file']).stat().st_size for r in files.values())+2*1024**3
    assert shutil.disk_usage(ROOT).free>=required,'Insufficient D space for only four sources + official copies +2GiB reserve'
    destination=ROOT/'output'/SLUG
    if destination.exists():
        prior_path=PROJECT/'production/delivery-output.json'
        assert prior_path.is_file(),'Unknown existing selected output; preserve and inspect before official collection'
        prior=read(prior_path);assert (ROOT/prior['directory']).resolve()==destination.resolve()
        expected={r['name'] for r in prior['files']}|{'index.html'}
        assert {p.name for p in destination.iterdir()}<=expected,'Unknown files in previous selected output; no wholesale archive'
        for row in prior['files']:assert sha(destination/row['name'])==row['sha256'],'Previous selected delivery changed; preserve and inspect'
    stage=PROJECT/'production/local/publishing-source'/master
    assert stage.resolve().is_relative_to((PROJECT/'production/local').resolve()) and stage.name==master
    assert stage.resolve().is_relative_to(ROOT.resolve()),'Publishing-source must be real D storage, not a junction into bulk media'
    stage.mkdir(parents=True,exist_ok=True)
    mapping={}
    for key,row in files.items():
        source=folder/row['file'];target=stage/row['file']
        assert sha(source)==row['sha256']
        if not target.exists():shutil.copy2(source,target)
        assert target.is_file() and sha(target)==row['sha256'],'Existing publishing source differs; preserve rather than overwrite'
        mapping[key]=target.relative_to(ROOT).as_posix()
    values=dict(videoBurnedCaptions=mapping['captioned'],videoClean=mapping['clean'],captionsKo=mapping['ko'],captionsEn=mapping['en'])
    tracks={lang:srt(folder/files[lang]['file']) for lang in ('ko','en')}
    alignment=alignment_for_official(data['timeline'],tracks,stage,data['semanticAlignment'])
    alignment_path=stage/'caption-alignment-review.json'
    if alignment_path.exists():require(read(alignment_path)==alignment,'Preserve differing prior semantic alignment')
    else:save(alignment_path,alignment)
    values['captionAlignmentReview']=alignment_path.relative_to(ROOT).as_posix()
    project_path=PROJECT/'project.json'
    for _ in range(5):
        before=project_path.read_bytes();current=json.loads(before.decode('utf-8-sig'))
        assert current['slug']==SLUG and current.get('localFinalReviewOnly') and not current.get('youtubeAuthorized')
        updated=project_patch(current,values,result['metadata']['titles'])
        if project_path.read_bytes()!=before:continue
        save(project_path,updated);break
    else:raise RuntimeError('Concurrent selected project edits; no metadata overwrite')
    authorize();assert sha(COLLECTOR)==result['pins']['officialCollectorSHA256'],'Official collector changed since QA'
    output=run(['node',COLLECTOR,SLUG]).stdout.decode('utf-8','replace')
    delivery=read(PROJECT/'production/delivery-output.json')
    for row in delivery['files']:
        assert row['sha256']==files[next(k for k,v in files.items() if v['file']==row['name'])]['sha256']
    receipt=dict(status='official-four-output-collection-complete-human-review-pending',masterSHA256=master,
        sourceReview=str(folder),collectorStdout=output,delivery=delivery,platformActions=[],humanFinalReview=False)
    save(folder/'official-collection.json',receipt);return receipt


def official_collect(result):
    global ACTIVE_WORKER
    authorize();worker=native.SingleWorker(WORKER,is_alive=owned_alive).acquire();ACTIVE_WORKER=worker
    worker.update(stage='official-four-output-collection',topicId='06.02')
    try:return _official_collect(result)
    finally:
        ACTIVE_WORKER=None;worker.close(remove=not child_pending_or_alive(worker.record))


def readiness(args):
    if not args.render_manifest or not args.mixed_asr_review or not Path(args.metadata).is_file() or not args.encoded_audio_review or ENCODED_AUDIO_SHA is None:
        return dict(ready=False,reason='Actual completed selected render, independent49-window exact-mix ASR, existing encoded-audio report/source freeze and current authored metadata required',preview=preview(),qaPerformed=False,mediaStarted=False,modelStarted=False,platformActions=[])
    data=load_inputs(args.render_manifest,args.metadata,args.mixed_asr_review,args.semantic_review,args.encoded_audio_review)
    return dict(ready=True,fingerprint=data['fingerprint'],preview=preview(data['metadata']['masterSHA256']),officialSemanticReviewReady=data['semanticAlignment'] is not None,qaPerformed=False,mediaStarted=False,modelStarted=False,platformActions=[])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render-manifest');parser.add_argument('--mixed-asr-review');parser.add_argument('--encoded-audio-review')
    parser.add_argument('--metadata',default=str(METADATA));parser.add_argument('--semantic-review')
    parser.add_argument('--execute',action='store_true');parser.add_argument('--official-collect',action='store_true');args=parser.parse_args()
    require(not args.official_collect or args.execute,'Official collection requires explicit --execute')
    status=readiness(args)
    if not args.execute:print(json.dumps(status,ensure_ascii=False,indent=2));return
    require(status['ready'],'Actual final media/prerequisites are not ready; no collection started')
    data=load_inputs(args.render_manifest,args.metadata,args.mixed_asr_review,args.semantic_review,args.encoded_audio_review)
    if args.official_collect:require(data['semanticAlignment'] is not None,'Provide current authored semantic text review before official staging')
    result=collect_review(data)
    official=official_collect(result) if args.official_collect else None
    print(json.dumps(dict(output=result['output'],masterSHA256=result['metadata']['masterSHA256'],officialCollection=official is not None,humanFinalReview=False,platformActions=[]),ensure_ascii=False,indent=2))


if __name__=='__main__':main()

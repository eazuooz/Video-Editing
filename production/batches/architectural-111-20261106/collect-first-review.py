"""Finite03.02 future technical QA and official four-output collection adapter.

No-argument/default mode only previews prerequisites/writes. After actual render:
  python collect-first-review.py --render-manifest <C-media/render-manifest.json> --execute
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

spec=importlib.util.spec_from_file_location('first_review_native_util',HERE/'run-first-native.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
SLUG='shorts-leveldesign-03-02';PROJECT=ROOT/'projects'/SLUG;BASE=MEDIA/SLUG
METADATA=PROJECT/'publishing-draft-v1.json';WORKER=MEDIA/'first-review-worker.json'
COLLECTOR=ROOT/'scripts/collect-video-output.cjs'
BIN=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin')
FF=Path(os.environ.get('YAMYAM_FFMPEG',str(BIN/'ffmpeg.exe')));PROBE=FF.with_name('ffprobe.exe')
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
SUFFIX={'clean':'clean.mp4','captioned':'captioned.mp4','ko':'ko.srt','en':'en.srt'}


def sha(path):
    with Path(path).open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()


def run(args):
    result=subprocess.run([str(a) for a in args],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=CREATE)
    if result.returncode:raise RuntimeError(result.stderr.decode(errors='replace')[-6000:])
    return result


def authorize():
    control=read(ROOT/'shared/publishing/video-production-control.json')[AUTH_KEY]
    assert control['userEvidence']=='111개 전체 제작 들어가줘' and control['status'] not in ('paused','stopped','cancelled')
    assert control['automaticAdvanceWithinExactList'] and not control['automaticAdvanceOutsideList']
    assert control['humanFinalReviewRequired'] and not control['youtubeAuthorized']


def scoped(path):
    result=Path(path).resolve()
    assert result.is_relative_to(BASE.resolve()),'Final render/review escaped selected C-media project'
    return result


def metadata_packet(source,master_sha):
    assert source['topicId']=='03.02'
    assert source.get('masterSHA256') in (None,master_sha),'Metadata belongs to another master'
    for key in ('titleKo','titleEn','descriptionKo','descriptionEn'):
        assert isinstance(source.get(key),str) and source[key].strip(),'Missing exact authored publishing metadata: '+key
    return dict(titles=dict(ko=source['titleKo'],en=source['titleEn']),
        descriptions=dict(ko=source['descriptionKo'],en=source['descriptionEn']),masterSHA256=master_sha,
        sourceMetadataState=source.get('status'),metadataFinalCutConformance='pending-root-review',
        actualHumanFinalReview=False,youtubeAuthorized=False,driveAuthorized=False)


def load_inputs(path,metadata_path):
    authorize();path=scoped(path);render=read(path)
    assert render['schemaVersion']=='03-02-render-manifest-v1' and render['slug']==SLUG
    assert render.get('complete') is True,'Only a completed actual renderer receipt can enter final collection'
    fmt=render['format'];assert (fmt['width'],fmt['height'],fmt['fps'])==(1080,1920,60)
    assert isinstance(fmt['totalFrames'],int) and fmt['totalFrames']>0
    timeline_path=Path(render['timeline']['path']).resolve()
    assert sha(timeline_path)==render['timeline']['sha256'];timeline=read(timeline_path)
    assert timeline['schemaVersion']=='03-02-final-timeline-v1'
    assert timeline['totalFrames']==fmt['totalFrames'] and timeline['format']['fps']==60
    sources={}
    for key,suffix in SUFFIX.items():
        row=render['outputs'][key];source=scoped(row['path'])
        assert source.name==SLUG+'.'+suffix and source.is_file()
        assert sha(source)==row['sha256'],'Renderer output hash differs: '+key
        sources[key]=source
    for pin in timeline['inputs']:assert sha(pin['path'])==pin['sha256'],'Timeline dependency changed: '+pin['role']
    audio=timeline.get('audio');assert isinstance(audio,dict) and isinstance(audio.get('mix'),dict),'Final mixed audio is missing'
    mix=audio['mix'];assert sha(mix['path'])==mix['sha256']
    import soundfile as sf
    actual_mix=sf.info(mix['path'])
    assert (actual_mix.samplerate,actual_mix.channels,actual_mix.frames)==(mix['sampleRate'],mix['channels'],mix['frames'])
    assert actual_mix.samplerate==48000 and actual_mix.channels==2
    assert fmt['totalFrames']==math.ceil(actual_mix.frames*60/actual_mix.samplerate),'Movie must retain full exact PCM with <1frame rounding'
    voice=audio['voice'];assert sha(voice['path'])==voice['sha256']
    assert abs(voice['frames']/voice['sampleRate']-actual_mix.frames/actual_mix.samplerate)<1/actual_mix.samplerate
    if render.get('audioAac'):assert sha(render['audioAac']['path'])==render['audioAac']['sha256']
    metadata=read(metadata_path);packet=metadata_packet(metadata,render['outputs']['captioned']['sha256'])
    pins=dict(renderManifest=dict(path=str(path),sha256=sha(path)),timeline=dict(path=str(timeline_path),sha256=sha(timeline_path)),
        metadata=dict(path=str(Path(metadata_path).resolve()),sha256=sha(metadata_path)),outputs=render['outputs'],audio=audio,
        officialCollectorSHA256=sha(COLLECTOR),reviewHelperSHA256=sha(__file__))
    fingerprint=hashlib.sha256(json.dumps(pins,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return dict(render=render,timeline=timeline,sources=sources,metadata=packet,pins=pins,fingerprint=fingerprint)


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


def caption_contract(timeline,tracks,authored):
    rows=timeline['captions'];assert rows and len({r['id'] for r in rows})==len(rows)
    count=timeline['totalFrames'];previous=0
    fold=lambda x:re.sub(r'\s+','',unicodedata.normalize('NFC',x))
    for row in rows:
        a,b=row['startFrame'],row['endFrameExclusive']
        assert isinstance(a,int) and isinstance(b,int) and previous<=a<b<=count
        previous=b
    for language,field in (('ko','narrationKo'),('en','paragraphsEn')):
        cues=tracks[language];assert len(cues)==len(rows)
        for i,(cue,row) in enumerate(zip(cues,rows),1):
            assert cue['index']==i and abs(cue['start']-row['startFrame']/60)<=.001
            assert abs(cue['end']-row['endFrameExclusive']/60)<=.001
            assert cue['text']=='\n'.join(row[language+'Lines']) and 1<=len(row[language+'Lines'])<=2
            assert fold(cue['text'])==fold(row[language]),'Encoded SRT display differs from authored timeline'
        for paragraph in range(1,7):
            selected=[r for r in rows if r['paragraph']==paragraph]
            assert selected and fold(''.join(r[language] for r in selected))==fold(authored[field][paragraph-1]),'Caption paragraph omitted/reordered/rewritten'
    assert [(r['start'],r['end']) for r in tracks['ko']]==[(r['start'],r['end']) for r in tracks['en']]
    assert [p['paragraph'] for p in timeline['paragraphFrames']]==list(range(1,7))
    for paragraph in timeline['paragraphFrames']:
        selected=[r for r in rows if r['paragraph']==paragraph['paragraph']]
        assert paragraph['captionIds']==[r['id'] for r in selected]
        assert paragraph['startFrame']<=selected[0]['startFrame'] and selected[-1]['endFrameExclusive']<=paragraph['endFrameExclusive']
    return dict(koCues=len(rows),enCues=len(rows),identicalCueTiming=True,allSixAuthoredKoEnParagraphsRetained=True,
        captionFramesBoundToTimeline=True,aliasesApplied=False,rawAsrDiscrepancies=timeline.get('alignmentReview'),
        speechQualityPass=False,humanListening=False)


def section_contract(timeline):
    position=0;counts={};samples={0,timeline['totalFrames']-1}
    for row in timeline['sections']:
        a,b=row['startFrame'],row['endFrameExclusive'];assert a==position and isinstance(b,int) and a<b
        assert row['kind'] in ('gameplay','native','illustration');counts[row['kind']]=counts.get(row['kind'],0)+b-a
        samples.add((a+b-1)//2);position=b
    assert position==timeline['totalFrames'] and timeline['sections'][0]['kind']=='gameplay'
    for cue in timeline.get('catCues',[]):
        a,b=cue['startFrame'],cue['endFrameExclusive']
        assert type(a) is int and type(b) is int and 0<=a<b<=timeline['totalFrames'],'Cat reaction range escaped the actual movie clock'
        samples.add((a+b-1)//2)
    assert len(samples)<=100,'Unexpected unbounded sample request'
    return counts,sorted(samples)


def video_contract(info,pts,total_frames):
    videos=[s for s in info['streams'] if s['codec_type']=='video'];audios=[s for s in info['streams'] if s['codec_type']=='audio']
    assert len(videos)==len(audios)==1,'Exactly one video and one audio stream required'
    v,a=videos[0],audios[0]
    assert (v['width'],v['height'])==(1080,1920) and v['codec_name']=='h264'
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
    info=json.loads(run([PROBE,'-v','error','-show_streams','-show_format','-of','json',path]).stdout)
    frames=json.loads(run([PROBE,'-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','json',path]).stdout)['frames']
    pts=[float(f['best_effort_timestamp_time']) for f in frames]
    result=video_contract(info,pts,total_frames)
    run([FF,'-v','error','-xerror','-err_detect','explode','-threads','2','-hwaccel','none','-i',path,
         '-map','0:v:0','-map','0:a:0','-f','null','-'])
    packets=json.loads(run([PROBE,'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256',
        '-show_entries','packet=pts_time,dts_time,duration_time,data_hash,flags','-of','json',path]).stdout)['packets']
    result.update(wholeVideoAndAudioDecodePassed=True,realTimePlaybackPerformed=False,humanListeningPerformed=False)
    return result,packets


def mobile_samples(source,frames,folder,master_sha,timeline):
    from PIL import Image
    expression='+'.join(f'eq(n\\,{n})' for n in frames)
    graph=f'[0:v]select={expression},split[full][small];[small]scale=375:-1[mobile]'
    run([FF,'-v','error','-n','-threads','2','-hwaccel','none','-i',source,'-filter_complex',graph,
        '-map','[full]','-fps_mode','passthrough',folder/'1080-%03d.png',
        '-map','[mobile]','-fps_mode','passthrough',folder/'375-%03d.png'])
    rows=[]
    for i,frame in enumerate(frames,1):
        entry=dict(frame=frame,ptsSeconds=frame/60,captionedMasterSHA256=master_sha,
            captionIds=[r['id'] for r in timeline['captions'] if r['startFrame']<=frame<r['endFrameExclusive']],
            actualAgentVisualInspection='pending',native={},mobile={})
        for key,prefix,size in [('native','1080',(1080,1920)),('mobile','375',(375,667))]:
            path=folder/f'{prefix}-{i:03d}.png'
            with Image.open(path) as image:image.load();assert image.size==size
            entry[key]=dict(file=path.name,sha256=sha(path),width=size[0],height=size[1])
        rows.append(entry)
    return dict(schemaVersion='03-02-encoded-mobile-samples-v1',samples=rows,
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
        f'<p>1080×1920 · 60fps · {qa["videos"]["captioned"]["decodedFrames"]} 프레임</p><pre>Master SHA256: {master}</pre>'
        f'<ul>{links}</ul><p><a href="publishing-metadata.json">정확한 한영 제목·설명</a> · <a href="technical-qa.json">검수 범위</a> · <a href="mobile-samples.json">실제 인코딩 표본 목록</a></p>'
        f'<h2>한국어 설명</h2><pre>{esc(packet["descriptions"]["ko"])}</pre><h2>English</h2><p>{esc(packet["titles"]["en"])}</p>'
        f'<pre>{esc(packet["descriptions"]["en"])}</pre><details><summary>실제 인코딩 모바일 표본 · 검수 대기</summary>{gallery}</details></html>')


def collect_review(data):
    authorize();worker=native.SingleWorker(WORKER).acquire();worker.update(stage='final-four-output-qa',topicId='03.02')
    try:
        folder=scoped(BASE/'local-final-review'/data['fingerprint'][:24]);receipt=folder/'review-receipt.json'
        if folder.exists():
            prior=read(receipt);assert prior['fingerprint']==data['fingerprint']
            for row in prior['deliverables'].values():assert sha(folder/row['file'])==row['sha256']
            for row in prior['reviewArtifacts']:assert sha(folder/row['file'])==row['sha256']
            assert sha(folder/'index.html')==prior['indexSHA256'];return prior
        work=scoped(BASE/'review-staging'/('qa-'+uuid.uuid4().hex));work.mkdir(parents=True,exist_ok=False)
        save(work/'input-pins.json',data['pins']);fmt=data['render']['format'];videos={};audio={}
        for key in ('clean','captioned'):videos[key],audio[key]=probe_video(data['sources'][key],fmt['totalFrames'])
        identical=same_audio(audio['clean'],audio['captioned'])
        if data['render'].get('audioAac'):
            source_packets=json.loads(run([PROBE,'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256',
                '-show_entries','packet=pts_time,dts_time,duration_time,data_hash,flags','-of','json',data['render']['audioAac']['path']]).stdout)['packets']
            # Container time-base rounding may differ; immutable payload ordering must match the one encoded source.
            assert [p['data_hash'] for p in source_packets]==[p['data_hash'] for p in audio['captioned']]
        tracks={k:srt(data['sources'][k]) for k in ('ko','en')}
        caption_qa=caption_contract(data['timeline'],tracks,read(PROJECT/'narration-draft.json'))
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
            captions=caption_qa,frameCountsBySourceKind=kinds,actualGameplayShare=kinds.get('gameplay',0)/fmt['totalFrames'],
            wholeDecodePerformed=True,actualFullPlaybackPerformed=False,actualHumanListening=False,userFinalReview=False,
            encodedMobileSamplesExtracted=len(samples['samples']),encodedMobileSampleVisualInspection='pending',
            finalMixedAsr='not-performed-by-collector; retain separate exact-mix evidence',encodedAlignedLevels='pending-separate-audio-review',
            pins=data['pins'],platformActions=[])
        save(work/'technical-qa.json',qa);save(work/'publishing-metadata.json',data['metadata'])
        (work/'index.html').write_text(review_page(data['metadata'],qa,samples),encoding='utf-8')
        assert load_inputs(data['pins']['renderManifest']['path'],data['pins']['metadata']['path'])['fingerprint']==data['fingerprint']
        result=dict(status=qa['status'],fingerprint=data['fingerprint'],output=str(folder),deliverables=deliverables,
            metadata=data['metadata'],pins=data['pins'],indexSHA256=sha(work/'index.html'),technicalQA='technical-qa.json',
            reviewArtifacts=[dict(file=p.name,sha256=sha(p),bytes=p.stat().st_size) for p in sorted(work.iterdir()) if p.is_file()],
            humanFinalReview=False,platformActions=[])
        save(work/'review-receipt.json',result);folder.parent.mkdir(parents=True,exist_ok=True)
        assert not folder.exists();work.rename(folder);return result
    finally:worker.close(remove=True)


def preview(master='<captioned-SHA256>'):
    stage=PROJECT/'production/local/publishing-source'/master
    return dict(cMediaReview=str(BASE/'local-final-review'/'<version>'),fourFileStaging=str(stage),
        selectedProjectFields=['paths.videoBurnedCaptions','paths.videoClean','paths.captionsKo','paths.captionsEn','titles.ko','titles.en'],
        officialCommand=['node','scripts/collect-video-output.cjs',SLUG],
        expectedCollectorWrites=[str(ROOT/'output'/SLUG),str(ROOT/'output/index.html'),
            str(PROJECT/'production/delivery-output.json'),str(PROJECT/'rebuild.json'),
            str(PROJECT/'production/delivery-stage-<unique>'),str(PROJECT/'production/delivery-history/<previous-version-if-present>')],
        rawMediaBulkCopiedToD=False,platformActions=[],requiredFreeD='2 * actual four-file bytes + 2 GiB')


def project_patch(document,paths,titles):
    result=dict(document);result['paths']=dict(document.get('paths',{}),**paths);result['titles']=dict(document.get('titles',{}),**titles)
    return result


def official_collect(result):
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


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--render-manifest');parser.add_argument('--metadata',default=str(METADATA))
    parser.add_argument('--execute',action='store_true');parser.add_argument('--official-collect',action='store_true');args=parser.parse_args()
    if not args.render_manifest:
        assert not args.execute;print(json.dumps(dict(ready=False,reason='Actual complete render-manifest required',preview=preview()),ensure_ascii=False));return
    data=load_inputs(args.render_manifest,args.metadata)
    if not args.execute:
        print(json.dumps(dict(ready=True,fingerprint=data['fingerprint'],preview=preview(data['metadata']['masterSHA256']),qaPerformed=False),ensure_ascii=False));return
    result=collect_review(data)
    if args.official_collect:official_collect(result)
    print(json.dumps(dict(output=result['output'],masterSHA256=result['metadata']['masterSHA256'],humanFinalReview=False),ensure_ascii=False))


if __name__=='__main__':main()

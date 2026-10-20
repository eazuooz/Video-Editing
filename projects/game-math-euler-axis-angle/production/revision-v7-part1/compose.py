"""Render selected Part1 as simultaneous game-left/model-right scenes.

Consumes exact finite visual-segment manifests. Speech is never stopped to
wait for an animation. Static states may persist under continuing narration;
native recorded game actions and controlled model steps play once at1x.
"""
from pathlib import Path
from fractions import Fraction
import argparse, hashlib, importlib.util, json, os, subprocess, time
from PIL import Image, ImageDraw, ImageFont

H=Path(__file__).resolve().parent;R=H.parents[3]
P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v7-part1';E=O/'edit'
FONT='C:/Windows/Fonts/malgun.ttf';BOLD='C:/Windows/Fonts/malgunbd.ttf'
FPS=60;WHITE='#f5f5f5';GOLD='#e8cf83';MUTED='#b8b8b8'
INTRO=R/'projects/game-reward-planning/production/local/reference-preserving-v2/edit/branding.mp4'
OUTRO=INTRO.with_name('membership.mp4')
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
MEDIA_HASHES=None
def media_fingerprint(file):
    """Hash once; reuse only the same path/size/mtime snapshot thereafter."""
    global MEDIA_HASHES
    cache=E/'media-hashes.json'
    if MEDIA_HASHES is None:MEDIA_HASHES=read(cache)if cache.exists()else{}
    file=path(file).resolve();key=rel(file);stat=file.stat();snapshot=dict(size=stat.st_size,mtimeNs=stat.st_mtime_ns)
    old=MEDIA_HASHES.get(key)
    if old and old['snapshot']==snapshot:return dict(file=key,sha256=old['sha256'])
    digest=sha(file);assert file.stat().st_size==stat.st_size and file.stat().st_mtime_ns==stat.st_mtime_ns
    MEDIA_HASHES[key]=dict(snapshot=snapshot,sha256=digest);save(cache,MEDIA_HASHES)
    return dict(file=key,sha256=digest)
def segment_media(rows):
    files=set()
    def add(row):
        files.add(row['file'])
        for layer in row.get('overlayLayers',[]):add(layer)
    for row in rows:add(row)
    return [media_fingerprint(f)for f in sorted(files)]
def digest_json(data):return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')).hexdigest()
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def path(p):return Path(p)if Path(p).is_absolute()else R/p
def timing():
    sp=importlib.util.spec_from_file_location('v7_compose_timing',H/'timing.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def authorized():return timing().authorized()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def check_video(p,frames,dimensions=(1920,1080)):
    data=probe(p);v=next(x for x in data['streams']if x['codec_type']=='video')
    assert (v['width'],v['height'])==dimensions and v['r_frame_rate']=='60/1'and int(v['nb_frames'])==frames,(str(p),v,frames)
    return v
def run(cmd,log):
    log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('wb')as stream:
        result=subprocess.run(cmd,cwd=R,stdout=stream,stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
    if result.returncode:raise RuntimeError(log.read_text(encoding='utf8',errors='replace')[-3500:])
def encoder(name):
    common=['-pix_fmt','yuv420p','-color_range','tv','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000']
    if name=='h264_nvenc':return ['-c:v',name,'-preset','p5','-tune','hq','-rc','vbr','-cq','18','-b:v','0','-bf','3',*common]
    assert name=='libx264';return ['-c:v',name,'-threads','4','-preset','veryfast','-crf','18',*common]
def backdrop(scene):
    f=E/'ui'/(scene['id']+'.png');f.parent.mkdir(parents=True,exist_ok=True)
    im=Image.new('RGB',(1920,1080),'black');d=ImageDraw.Draw(im)
    title=scene['title'];font=ImageFont.truetype(BOLD,58)
    assert d.textlength(title,font=font)<=1840,'Reflow approved title; do not silently shrink'
    d.text((40,40),title,font=font,fill=GOLD)
    d.text((40,129),'실제 게임과 함께 보는 3차원 회전',font=ImageFont.truetype(FONT,44),fill=MUTED)
    # The measured canonical-name chip supplies the right model-kind label.
    d.line((958,180,958,850),fill='#39434a',width=2)
    im.save(f);return f
def segment_list(manifest,sid):
    data=read(manifest)
    rows=data.get('segments',data.get('visualSegments'))
    if rows is None:
        rows=[r for s in data['scenes']for r in s['segments']]
    result=[r for r in rows if r.get('sceneId',r.get('scene'))==sid]
    return sorted(result,key=lambda x:x['startFrame'])
def normalize_segment(row):
    row=dict(row);row['endFrameExclusive']=row.get('endFrameExclusive',row.get('endFrame'))
    row['file']=row.get('file',row.get('path'));assert row['file']
    assert row['kind']in ['still','video']
    row['sourceStartFrame']=row.get('sourceStartFrame',0)
    assert row['endFrameExclusive']>row['startFrame']and row['sourceStartFrame']>=0
    assert path(row['file']).exists(),row['file']
    return row
VIDEO_PROBES={}
def source_frame_bound(row):
    file=path(row['file']).resolve()
    if file not in VIDEO_PROBES:
        data=probe(file);v=next(s for s in data['streams']if s['codec_type']=='video')
        assert v['r_frame_rate']=='60/1'and v['avg_frame_rate']=='60/1',(str(file),'Finite source must retain60fps')
        count=v.get('nb_frames')
        if count and count!='N/A':
            evidence=dict(limitFrames=int(count),basis='container-declared nb_frames; whole source not redecoded',exactDecodedTotal=False)
        else:
            duration=(Fraction(int(v['duration_ts']))*Fraction(v['time_base']))if v.get('duration_ts')else Fraction(v['duration'])
            derived=duration*60
            evidence=dict(limitFrames=derived.numerator//derived.denominator,
                basis='video duration times declared CFR; range bound, not whole-source decoded frame count',
                durationTs=v.get('duration_ts'),timeBase=v['time_base'],durationSeconds=float(duration),exactDecodedTotal=False)
        VIDEO_PROBES[file]=evidence
        save(E/'source-range-bounds.json',dict(sources={rel(f):value for f,value in VIDEO_PROBES.items()},
            verification='Source-header bounds only. Each finite output scene is subsequently checked for its exact encoded frame count.'))
    return VIDEO_PROBES[file]
def validate_source_range(row,n):
    if row['kind']=='video':
        evidence=source_frame_bound(row);available=evidence['limitFrames']
        assert row['sourceStartFrame']+n<=available,('Native finite source overflow',row,n,evidence)
    for layer in row.get('overlayLayers',[]):
        validate_source_range(normalize_segment(dict(layer,startFrame=row['startFrame'],endFrameExclusive=row['endFrameExclusive'])),n)
def validate_segments(rows,scene):
    assert rows,(scene['id'],'No visual segment')
    cursor=scene['startFrame']
    for row in rows:
        assert row['startFrame']==cursor,(scene['id'],cursor,row)
        cursor=row['endFrameExclusive']
        validate_source_range(row,row['endFrameExclusive']-row['startFrame'])
    assert cursor==scene['endFrame'],(scene['id'],cursor,scene['endFrame'])
def phase_inputs(row,args,filters,index,label,dimensions,alpha=False):
    n=row['endFrameExclusive']-row['startFrame'];file=path(row['file']);current=index
    if row['kind']=='still':args+=['-framerate','60','-threads','1','-i',str(file)]
    else:args+=['-ss',f'{row["sourceStartFrame"]/60:.9f}','-t',f'{n/60:.9f}','-threads','2','-i',str(file)]
    freeze='loop=loop=-1:size=1:start=0,'if row['kind']=='still'else''
    chain=f'[{index}:v]{freeze}fps=60,trim=end_frame={n},setpts=N/(60*TB),setsar=1'
    index+=1
    crop=row.get('cropRect',row.get('crop'))
    if crop:
        x,y,w,h=crop;chain+=f',crop={w}:{h}:{x}:{y}'
    w,h=dimensions
    pixel_format='rgba'if alpha else'yuv420p';pad='black@0'if alpha else'black'
    chain+=f',format={pixel_format},scale={w}:{h}:force_original_aspect_ratio=decrease:flags=lanczos,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color={pad},format={pixel_format}[{label}base]'
    filters.append(chain);previous=label+'base'
    for oi,overlay in enumerate(row.get('overlayLayers',[])):
        # Layers inherit the segment clock. They are controlled-model/UI
        # composition, never claimed to be recovered game-engine measurements.
        extra=dict(overlay);extra.update(startFrame=row['startFrame'],endFrameExclusive=row['endFrameExclusive'])
        extra=normalize_segment(extra)
        bounds=overlay.get('rect')
        iw,ih=bounds[2:]if bounds else extra.get('dimensions',dimensions)
        index,over=phase_inputs(extra,args,filters,index,label+f'layer{oi}',(iw,ih),alpha=True)
        x,y=bounds[:2]if bounds else overlay.get('position',[0,0]);out=label+f'over{oi}'
        filters.append(f'[{previous}][{over}]overlay={x}:{y}:eof_action=pass:shortest=1:format=auto[{out}]');previous=out
    return index,previous
def assemble_pane(rows,args,filters,index,prefix,size):
    names=[]
    for i,row in enumerate(rows):
        index,name=phase_inputs(row,args,filters,index,f'{prefix}{i}',size);names.append(f'[{name}]')
    out=prefix+'pane'
    if len(names)==1:filters.append(names[0]+f'null[{out}]')
    else:filters.append(''.join(names)+f'concat=n={len(names)}:v=1:a=0[{out}]')
    return index,out
def ffescape(p):return rel(p).replace('\\','/').replace(':',r'\:').replace("'",r"\'")
def scene_render(scene,left_file,right_file,codec='libx264',sample=None):
    authorized();left=[normalize_segment(r)for r in segment_list(left_file,scene['id'])];right=[normalize_segment(r)for r in segment_list(right_file,scene['id'])]
    validate_segments(left,scene);validate_segments(right,scene)
    ui=backdrop(scene);folder=E/'scenes';folder.mkdir(parents=True,exist_ok=True)
    destination=folder/(scene['id']+'.mp4');receipt=destination.with_suffix('.json')
    manifest=read(left_file);ass_by=manifest.get('sceneASS',{})
    extra_ass=ass_by.get(scene['id'])
    if isinstance(extra_ass,dict):extra_ass=extra_ass.get('file')
    terms=read(H/'semantic-term-chips.json');term_ass=terms['sceneASS'][scene['id']]['file']
    signature=dict(sceneTimingSha256=digest_json(scene),leftSceneSegmentsSha256=digest_json(left),rightSceneSegmentsSha256=digest_json(right),
        inputMedia=segment_media(left+right),
        backdropSha256=sha(ui),implementationSha256=sha(Path(__file__)),codec=codec,frames=scene['frames'],
        annotationASSsha256=sha(path(extra_ass))if extra_ass else None,canonicalTermASSsha256=sha(path(term_ass)))
    if destination.exists()and receipt.exists():
        existing=read(receipt)
        if existing.get('inputs')==signature and existing.get('sha256')==sha(destination):
            check_video(destination,scene['frames']);print('Reused exact paired scene',scene['id'],flush=True);return existing
        raise RuntimeError('Preserve differing completed scene before selected repair: '+str(destination))
    args=['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-n','-filter_complex_threads','1',
        '-framerate','60','-threads','1','-i',str(ui)]
    filters=[f'[0:v]loop=loop=-1:size=1:start=0,trim=end_frame={scene["frames"]},setpts=N/(60*TB),setsar=1[base]']
    index,left_label=assemble_pane(left,args,filters,1,'l',(896,504))
    index,right_label=assemble_pane(right,args,filters,index,'r',(900,660))
    filters.append(f'[base][{left_label}]overlay=40:250:shortest=1:eof_action=endall[pair0]')
    filters.append(f'[pair0][{right_label}]overlay=980:180:shortest=1:eof_action=endall[pair1]')
    label='pair1'
    if extra_ass:
        filters.append(f'[{label}]ass={ffescape(path(extra_ass))}[marked]');label='marked'
    filters.append(f'[{label}]ass={ffescape(path(term_ass))}[named]');label='named'
    filters.append(f'[{label}]format=yuv420p[out]')
    graph=folder/(scene['id']+'.filter.txt');graph.write_text(';\n'.join(filters),encoding='utf8')
    # FFmpeg9: file-loaded option syntax replaces filter_complex_script.
    # https://ffmpeg.org/ffmpeg.html#Options
    args+=['-/filter_complex',str(graph),'-map','[out]','-an','-frames:v',str(scene['frames']),'-r','60','-fps_mode','cfr',*encoder(codec),str(destination)]
    start=time.time();run(args,folder/(scene['id']+'.encode.log'));v=check_video(destination,scene['frames'])
    result=dict(sceneId=scene['id'],file=rel(destination),sha256=sha(destination),frames=scene['frames'],
        inputs=signature,sourceManifestsAtRender=dict(leftSha256=sha(left_file),rightSha256=sha(right_file),timelineSha256=sha(H/'timeline.json')),
        elapsedSeconds=time.time()-start,probe=v,leftSegmentCount=len(left),rightSegmentCount=len(right),
        completeMovingVisualReview='pending',captionPixelReview='pending final captioned master')
    save(receipt,result);print('Rendered simultaneous scene',scene['id'],scene['frames'],'frames',flush=True);return result
def scene_captioned(scene,clean,codec):
    """Reusable actual-caption scene; early QC pixels enter the final master."""
    authorized();folder=E/'captioned-scenes';folder.mkdir(parents=True,exist_ok=True)
    target=folder/(scene['id']+'.mp4');receipt=target.with_suffix('.json')
    cues=[dict(c)for c in read(O/'captions/captions.json')['cues']if c['scene']==scene['id']]
    for c in cues:
        c['start']-=scene['startFrame']/60;c['end']-=scene['startFrame']/60
    sp=importlib.util.spec_from_file_location('v7_local_caption_geometry',P/'production/revision-v6/captions.py')
    geom=importlib.util.module_from_spec(sp);sp.loader.exec_module(geom)
    subtitle_dir=folder/scene['id'];subtitle_dir.mkdir(exist_ok=True);geom.O=subtitle_dir
    geometry=geom.ass(cues,'ko');ass=subtitle_dir/'captions.ko.ass'
    sig=dict(cleanSceneSha256=clean['sha256'],semanticSceneCaptionSha256=digest_json(cues),
        captionAssSha256=sha(ass),approvedGeometrySha256=sha(P/'production/revision-v6/captions.py'),codec=codec,frames=scene['frames'])
    if target.exists()and receipt.exists():
        old=read(receipt)
        if old['inputs']==sig and old['sha256']==sha(target):
            check_video(target,scene['frames']);print('Reused exact captioned scene',scene['id'],flush=True);return old
        raise RuntimeError('Preserve differing completed captioned scene before repair: '+str(target))
    run(['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-n','-threads','2','-filter_threads','2','-i',str(R/clean['file']),
        '-vf','ass='+ffescape(ass),'-an','-frames:v',str(scene['frames']),'-r','60','-fps_mode','cfr',*encoder(codec),str(target)],folder/(scene['id']+'.encode.log'))
    v=check_video(target,scene['frames']);save(subtitle_dir/'geometry.json',geometry)
    result=dict(sceneId=scene['id'],file=rel(target),sha256=sha(target),frames=scene['frames'],inputs=sig,probe=v,
        sourceGlobalStartFrame=scene['startFrame'],actualCaptionedSceneReusableInFullMaster=True,earlySampleIsNotWholeVideoApproval=True)
    save(receipt,result);print('Encoded actual captions',scene['id'],flush=True);return result
def join(left_file,right_file,codec):
    authorized();t=read(H/'timeline.json');rows=[];captioned=[]
    for scene in t['scenes']:
        current=scene_render(scene,left_file,right_file,codec);rows.append(current);captioned.append(scene_captioned(scene,current,codec))
    check_video(INTRO,120);check_video(OUTRO,600)
    versions=[]
    for kind,items in [('clean',rows),('captioned',captioned)]:
        listing=E/('join-'+kind+'.txt');listing.write_text('\n'.join("file '"+str(p.resolve()).replace('\\','/')+"'"for p in[INTRO,*[R/r['file']for r in items],OUTRO])+'\n',encoding='utf8')
        visual=E/('part1-'+kind+'-visual.mp4')
        run(['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-n','-f','concat','-safe','0','-i',str(listing),'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','60000','-movflags','+faststart',str(visual)],E/('join-'+kind+'.log'))
        check_video(visual,t['totalFrames']);versions.append(dict(kind=kind,file=rel(visual),sha256=sha(visual),frames=t['totalFrames'],scenes=items))
    save(E/'visual-build.json',dict(versions=versions,frames=t['totalFrames'],introSha256=sha(INTRO),outroSha256=sha(OUTRO),audio='separate reviewed narration/game standard mix pending',captioned='actual local scene captions encoded and concatenated without repeat full re-encode'))
    print('Full paired visual joined',t['totalFrames'],'frames',flush=True)
def finish(mix_file,codec):
    authorized();t=read(H/'timeline.json');visual=E/'part1-clean-visual.mp4';captioned_visual=E/'part1-captioned-visual.mp4';check_video(visual,t['totalFrames']);check_video(captioned_visual,t['totalFrames']);mix_file=path(mix_file)
    assert mix_file.exists()
    clean=O/'part1-clean.mp4';burned=O/'part1-captioned.mp4';ass=O/'captions.ko.ass';assert ass.exists()
    audio=next(x for x in probe(mix_file)['streams']if x['codec_type']=='audio')
    exact_aac=audio['codec_name']=='aac'and int(audio['sample_rate'])==48000 and audio['channels']==2
    audio_codec=['-c:a','copy']if exact_aac else['-c:a','aac','-b:a','256k','-ar','48000','-ac','2']
    run(['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-n','-i',str(visual),'-i',str(mix_file),'-map','0:v:0','-map','1:a:0','-c:v','copy',*audio_codec,'-t',f'{t["duration"]:.9f}','-movflags','+faststart',str(clean)],E/'clean-mux.log')
    check_video(clean,t['totalFrames'])
    run(['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-n','-i',str(captioned_visual),'-i',str(clean),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-video_track_timescale','60000','-movflags','+faststart',str(burned)],E/'captioned-mux.log')
    check_video(burned,t['totalFrames']);save(E/'master-build.json',dict(schemaVersion=1,part=1,inputs=dict(timelineSha256=sha(H/'timeline.json'),visualSha256=sha(visual),captionedVisualSha256=sha(captioned_visual),mixSha256=sha(mix_file),captionAssSha256=sha(ass),implementationSha256=sha(Path(__file__))),
        outputs=[dict(kind=k,file=rel(f),sha256=sha(f),bytes=f.stat().st_size)for k,f in[('clean',clean),('captioned',burned)]],frames=t['totalFrames'],duration=t['duration'],format='1920x1080/60fps',preparedAacCopiedWithoutReencoding=exact_aac,fullDecodePtsAndAudioReview='pending',humanFinalReview='pending'))
    print('Clean and complete captioned masters encoded',flush=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--left',type=Path);ap.add_argument('--right',type=Path);ap.add_argument('--scene');ap.add_argument('--captioned-scene',action='store_true');ap.add_argument('--join',action='store_true');ap.add_argument('--finish-mix');ap.add_argument('--codec',choices=['libx264','h264_nvenc'],default='libx264');a=ap.parse_args()
    if a.scene:
        scene=next(s for s in read(H/'timeline.json')['scenes']if s['id']==a.scene);current=scene_render(scene,a.left,a.right,a.codec)
        if a.captioned_scene:scene_captioned(scene,current,a.codec)
    elif a.join:join(a.left,a.right,a.codec)
    elif a.finish_mix:finish(a.finish_mix,a.codec)
    else:ap.print_help()
if __name__=='__main__':main()

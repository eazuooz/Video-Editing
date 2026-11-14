"""Replace only opening pictures, copying source audio and all remaining pictures."""
import argparse, ast, hashlib, json, math, os, re, shutil, subprocess, sys, time, types
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from prepare import HERE, ROOT, SOURCE, WORK, OUTPUT, KEY, read, save, stamp
from artwork import build, text, WHITE, YELLOW, BG

# Reuse the exact approved geometry/event functions without importing voice jobs.
caption_file=ROOT/'projects/animation-breaking-down-attack-animations/production/grid-v1/caption_pipeline.py'
tree=ast.parse(caption_file.read_text(encoding='utf-8-sig'))
selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'measured_font','geometry','ass_events','ass_stamp'}]
ns=dict(ImageFont=ImageFont,Path=Path,math=math,FONT_SIZE=48,MAX_WIDTH=1570,LINE_HEIGHT=62,
        EMPHASIS_COLORS={'term':'0b6b66','result':'1a7f37','problem':'b42318'})
exec(compile(ast.Module(body=selected,type_ignores=[]),str(caption_file),'exec'),ns)
captions=types.SimpleNamespace(**ns)
VENC=['-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','60000']
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def run(args,capture=False):
    p=subprocess.run([str(x) for x in args],stdout=subprocess.PIPE if capture else subprocess.DEVNULL,stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
    if p.returncode:raise RuntimeError(p.stderr.decode('utf-8','replace')[-6000:])
    return p.stdout
def ff(*args,capture=False):return run(['ffmpeg','-nostdin','-hide_banner','-v','error','-y','-filter_complex_threads','2',*args],capture)
def stream(p):return json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',p],True))['streams'][0]
def frame(p,n):
    raw=ff('-threads',2,'-ss',n/60,'-i',p,'-map','0:v','-frames:v',1,'-f','rawvideo','-pix_fmt','rgb24','-',capture=True)
    return Image.frombytes('RGB',(1920,1080),raw)
def srt(p):
    def sec(s):
        h,m,s=s.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
    rows=[]
    for b in re.split(r'\n\s*\n',p.read_text(encoding='utf-8-sig').strip()):
        ls=b.strip().splitlines()
        if len(ls)>=3:
            a,z=ls[1].split(' --> ');rows.append(dict(start=sec(a),end=sec(z),ko='\n'.join(ls[2:]),emphasis={'ko':None}))
    return rows
def make_ass(row,files):
    header=(ROOT/'projects/animation-breaking-down-attack-animations/production/local/grid-v1/captions.ko.ass').read_text(encoding='utf-8-sig').split('Dialogue:')[0]
    font=captions.measured_font(Path('C:/Windows/Fonts/NotoSansKR-VF.ttf'),500)
    out=[];cues=[]
    for r in srt(files['ko.srt']):
        if r['end']<=row['startFrame']/60 or r['start']>=row['endFrame']/60:continue
        r['start']=max(r['start'],row['startFrame']/60);r['end']=min(r['end'],row['endFrame']/60)
        g=captions.geometry(r['ko'],font,None,None)
        out.append(captions.ass_events(r,g,'ko'));cues.append({**r,'box':g})
    folder=WORK/row['id'];(folder/'opening.ko.ass').write_text(header+''.join(out),encoding='utf-8')
    save(folder/'opening-cues.json',cues)

def guard(ep):
    control=read(ROOT/'shared/publishing/video-production-control.json')[KEY]
    assert ep in control['scope'] and ep not in control['excludedUploaded']
    assert control['renderAuthorized'] and not control['ttsAuthorized'] and not control['youtubeAuthorized']

def cut_after(source,minimum):
    frames=json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-skip_frame','nokey','-show_entries',
        'frame=best_effort_timestamp_time','-read_intervals','0%80','-of','json',source],True))['frames']
    return min(round(float(f['best_effort_timestamp_time'])*60) for f in frames if 'best_effort_timestamp_time' in f and round(float(f['best_effort_timestamp_time'])*60)>=minimum)

def prefix(row,files,kind):
    folder=WORK/row['id'];source=files[kind];cut=cut_after(source,row['endFrame']+12)
    dest=folder/('prefix-'+kind);info=stream(source)
    meta=folder/('prefix-'+kind+'.json')
    signature=dict(sourceSha256=sha(source),row=row,art=sha(folder/'overview.png'),roadmap=sha(folder/'roadmap.png'),ass=sha(folder/'opening.ko.ass'))
    if dest.exists() and meta.exists() and read(meta)['signature']==signature:return dest,cut
    start,end,cue=row['startFrame']/60,row['endFrame']/60,row['roadmapFrame']/60
    enable=f"gte(t,{start})*lt(t,{end})"
    # Two decoders only for captioned: the example must not inherit tiny burned captions.
    args=['-threads',2,'-i',source]
    if kind=='captioned.mp4':
        args+=['-threads',2,'-i',files['clean.mp4']];example='1:v';artidx=2
        filters='[0:v]null[base];'
    else:
        filters='[0:v]split=2[base][exsrc];';example='exsrc';artidx=1
    args+=['-i',folder/'overview.png','-i',folder/'roadmap.png']
    filters+=(f'[{example}]scale=880:495:flags=lanczos[example];'
              f'[base][{artidx}:v]overlay=0:0:enable=\'{enable}\'[canvas];'
              f'[canvas][example]overlay=980:258:enable=\'{enable}\'[withmovie];'
              f'[withmovie][{artidx+1}:v]overlay=0:0:enable=\'gte(t,{cue})*lt(t,{end})\'[withroadmap];')
    if kind=='captioned.mp4':
        ass=(folder/'opening.ko.ass').as_posix().replace(':','\\:')
        filters+=f"[withroadmap]ass=filename='{ass}'[v]"
    else:filters+='[withroadmap]null[v]'
    ff(*args,'-filter_complex',filters,'-map','[v]','-an','-frames:v',cut,*VENC,
       '-bf',0 if not info['has_b_frames'] else 3,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',dest)
    assert int(stream(dest)['nb_frames'])==cut
    save(meta,dict(signature=signature,cutFrame=cut));return dest,cut

def payload(p,kind='v',start=None):
    opts=['-ss',start] if start is not None else []
    if kind=='v':return ff(*opts,'-i',p,'-map','0:v:0','-an','-c:v','copy','-bsf:v','filter_units=remove_types=6|7|8|9','-f','hash','-hash','sha256','-',capture=True).decode().strip()
    return ff('-i',p,'-map','0:a:0','-vn','-c:a','copy','-f','hash','-hash','sha256','-',capture=True).decode().strip()

def audio_clock(p):
    packets=json.loads(run(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_entries',
        'packet=pts,dts,duration:packet_side_data=side_data_type,skip_samples,discard_padding','-of','json',p],True))['packets']
    return hashlib.sha256(json.dumps(packets,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def finish(row,files,kind):
    ep=row['id'];guard(ep);folder=WORK/ep;destdir=OUTPUT/ep;destdir.mkdir(parents=True,exist_ok=True)
    p,cut=prefix(row,files,kind);source=files[kind];tail=folder/('tail-'+kind)
    ff('-ss',cut/60,'-i',source,'-map','0:v:0','-an','-c:v','copy','-video_track_timescale',60000,tail)
    inf=stream(tail)
    assert int(inf['nb_frames'])==row['sourceFrames']-cut,(ep,kind,inf.get('nb_frames'),cut)
    assert abs(float(inf['start_time']))<1/60000,(ep,inf['start_time'])
    join=folder/(kind+'.ffconcat')
    join.write_text("ffconcat version 1.0\nfile '"+p.as_posix()+"'\nduration "+f'{cut/60:.9f}'+"\nfile '"+tail.as_posix()+"'\n",encoding='utf-8')
    dest=destdir/source.name
    ff('-f','concat','-safe',0,'-i',join,'-i',source,'-map','0:v:0','-map','1:a:0',
       '-c','copy','-video_track_timescale',60000,'-movflags','+faststart',dest)
    info=stream(dest)
    assert int(info['nb_frames'])==row['sourceFrames'] and info['width']==1920 and info['height']==1080 and info['avg_frame_rate']=='60/1'
    assert abs(float(info['duration'])-row['sourceFrames']/60)<1/60000
    ff('-threads',2,'-i',dest,'-map','0:v','-map','0:a','-f','null','-')
    audio=payload(source,'a');assert payload(dest,'a')==audio
    clock=audio_clock(source);assert audio_clock(dest)==clock,(ep,kind,'AAC timeline changed')
    tailhash=payload(tail);assert payload(dest,start=cut/60)==tailhash
    # Decoded join, final recap and original gameplay must survive stream assembly.
    comparisons=[]
    for n in [119,row['startFrame']-1,cut,cut+2,round(row['summaryAt']*60)+90,row['sourceFrames']-300]:
        a=np.asarray(frame(source,n)).astype(np.int16);b=np.asarray(frame(dest,n)).astype(np.int16)
        mae=float(np.abs(a-b).mean());assert mae<3,(ep,kind,n,mae)
        comparisons.append(dict(frame=n,meanAbsoluteError=mae))
    return dict(kind=kind,path=str(dest),sha256=sha(dest),fullDecode='passed',copiedSuffixStartFrame=cut,
                copiedSuffixVclHash=tailhash,audioPacketHash=audio,audioClockHash=clock,unchangedPictureSamples=comparisons)

def samples(row,files,preview=False):
    folder=WORK/row['id'];mid=max(row['roadmapFrame']+6,row['endFrame']-75)
    if preview:
        src=folder/'prefix-captioned.mp4'
    else:src=Path(next(f['path'] for f in files if f['kind']=='captioned.mp4'))
    pic=frame(src,mid);pic.save(folder/'opening-encoded.png');pic.resize((375,211),Image.Resampling.LANCZOS).save(folder/'opening-mobile.png')
    return pic

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--episode');ap.add_argument('--redo',nargs='*',default=[]);ap.add_argument('--prefix-only',action='store_true');args=ap.parse_args()
    rows=read(HERE/'plan.json')['episodes']
    for row in rows:
        ep=row['id']
        if args.episode and ep!=args.episode:continue
        if args.redo and ep not in args.redo:continue
        guard(ep);receipt=OUTPUT/ep/'delivery.json'
        if receipt.exists() and ep not in args.redo:
            previous=read(receipt)
            if all(Path(f['path']).is_file() and sha(f['path'])==f['sha256'] for f in previous['files']):
                print(ep+' already assembled; '+('sample review pending' if previous['visualReviewPending'] else 'verified'),flush=True);continue
        build(row);files={f['kind']:Path(f['path']) for f in row['sourceFiles']}
        for f in row['sourceFiles']:assert sha(f['path'])==f['sha256'],('baseline changed',ep,f['kind'])
        make_ass(row,files)
        print(ep+' opening pictures rendering',flush=True)
        if args.prefix_only:
            prefix(row,files,'captioned.mp4');samples(row,[],True);continue
        result=[]
        for kind in ['clean.mp4','captioned.mp4']:
            result.append(finish(row,files,kind));print(ep+' '+kind+' decoded; identical AAC and suffix',flush=True)
        for kind in ['ko.srt','en.srt']:
            out=OUTPUT/ep/files[kind].name;shutil.copy2(files[kind],out)
            assert sha(out)==sha(files[kind]);result.append(dict(kind=kind,path=str(out),sha256=sha(out)))
        save(receipt,dict(id=ep,title=row['title'],revision='overview-v7',frames=row['sourceFrames'],durationSeconds=row['sourceFrames']/60,
            files=result,overviewAt=row['startFrame']/60,overviewEnd=row['endFrame']/60,summaryAt=row['summaryAt'],summaryFrames=600,
            sourceReceipt=row['sourceReceipt'],audioChanged=False,srtChanged=False,bodyAfterOpeningBitstreamPreserved=True,
            openingArtworkSha256=sha(WORK/ep/'overview.png'),roadmapArtworkSha256=sha(WORK/ep/'roadmap.png'),openingAssSha256=sha(WORK/ep/'opening.ko.ass'),
            revisionDescription='쉬운 뜻·주제별 관계도·학습 순서를 기존 개론 음성과 연결 · 본문과 마지막 10초 정리 보존',
            internalQa='full decode, FHD60, identical AAC/SRT, exact VCL suffix and decoded brand/joins/recap/end',
            visualReviewPending=True,humanReviewed=False,platformChanged=False,updatedAt=stamp()))
        samples(row,result)
        print(ep+' files assembled; encoded visual sample pending',flush=True)

if __name__=='__main__':main()

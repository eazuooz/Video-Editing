"""Project-local, frame-exact documentary compositor. No footage decisions or TTS.

Workflow: fill timeline.json using inspected native-motion cuts, run --preflight,
then --render after the selected project's internal checks. --verify is structural
evidence, never human listening/viewing or rights clearance. All paths are relative
to the project unless absolute. Original sources are read-only.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from PIL import ImageFont

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parent
REPO=PROJECT.parents[1]
FPS,W,H,SR=60,1920,1080,48000
CAPTION_RECT=(150,892,1784,1060)
ROLE_COLORS={'focus':'73C7C2','result':'A4C6A0','problem':'EF8585','heading':'E8CF83','secondary':'B0B8B7','text':'FFFFFF'}
CODE_COLORS={'keyword':'C9A3EA','function':'73C7C2','variable':'F0F2ED','number':'E8CF83','string':'A4C6A0','comment':'A7B0AD','punctuation':'D9DED9'}
CAPTION_COLORS={'term':'0B6B66','result':'1A7F37','problem':'B42318'}
KIND_LABELS={'actual-gameplay':'벅샷 룰렛 · 직접 플레이','actual-development':'실제 작업 기록','prototype':'자체 구현 · NEON CHAMBER','analysis-visualization':'분석 결과 시각화','explanation':'설명 애니메이션'}

def load(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def save(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()
def resolve(value):
    p=Path(value)
    return p.resolve() if p.is_absolute() else (PROJECT/p).resolve()
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def tool(name,plan):
    explicit=plan.get('tools',{}).get(name) or os.environ.get(name.upper())
    if explicit:
        p=Path(explicit)
        if p.is_file():return str(p)
        raise FileNotFoundError(explicit)
    known=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin')/(name+'.exe')
    if known.is_file():return str(known)
    found=shutil.which(name)
    if found:return found
    raise FileNotFoundError(name)
def command(args,log,cwd=None):
    log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('w',encoding='utf-8') as stream:
        result=subprocess.run(list(map(str,args)),cwd=cwd or PROJECT,stdout=stream,stderr=subprocess.STDOUT,
                              creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if result.returncode:raise RuntimeError(f'Command failed ({result.returncode}): {log}\n'+log.read_text(encoding='utf-8',errors='replace')[-4000:])
def probe(path,plan,count=False):
    args=[tool('ffprobe',plan),'-v','error']
    if count:args+=['-count_frames']
    args+=['-show_streams','-show_format','-of','json',str(path)]
    return json.loads(subprocess.check_output(args,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0))
def video_stream(meta):return next(s for s in meta['streams'] if s['codec_type']=='video')
def seconds(stamp):
    h,m,s=stamp.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
def stamp(t,ass=False):
    base=100 if ass else 1000;n=round(float(t)*base)
    return f'{n//(base*3600):0{1 if ass else 2}d}:{n//(base*60)%60:02d}:{n//base%60:02d}{"." if ass else ","}{n%base:0{2 if ass else 3}d}'
def read_srt(path):
    cues=[]
    for block in re.split(r'\r?\n\s*\r?\n',Path(path).read_text(encoding='utf-8-sig').strip()):
        lines=block.splitlines()
        if len(lines)<3:raise ValueError(f'Malformed SRT block: {path}')
        a,b=lines[1].split(' --> ')
        cues.append({'id':int(lines[0]),'start':seconds(a),'end':seconds(b),'text':' '.join(lines[2:]).strip()})
    for cue in cues:
        if cue['start']<0 or cue['end']<=cue['start'] or not cue['text']:raise ValueError('Empty/invalid subtitle cue')
    if not cues:raise ValueError('Subtitles must contain at least one real cue')
    for a,b in zip(cues,cues[1:]):
        if a['end']>b['start']+.002:raise ValueError('Overlapping narration subtitles')
    return cues
def write_srt(path,cues,offset):
    Path(path).write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"]+offset)} --> {stamp(c["end"]+offset)}\n{c["text"]}' for i,c in enumerate(cues))+'\n',encoding='utf-8')
def bgr(rgb):return rgb[4:6]+rgb[2:4]+rgb[0:2]
def safe_text(text):
    if any(c in text for c in '{}\\'):raise ValueError('ASS-reserved text; use plain narration text')
    return text
def ass_header(font='Malgun Gothic',size=48):
    return ['[Script Info]','ScriptType: v4.00+','PlayResX: 1920','PlayResY: 1080','WrapStyle: 2','ScaledBorderAndShadow: yes','','[V4+ Styles]',
    'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
    f'Style: Default,{font},{size},&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1','','[Events]',
    'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
def event(lines,start,end,body,layer=2):
    if end<=start:raise ValueError('Zero-length ASS interval')
    lines.append(f'Dialogue: {layer},{stamp(start,True)},{stamp(end,True)},Default,,0,0,0,,{body}')
def wrap_caption(text,font,measure=None):
    measure=measure or font.getlength
    if measure(text)<=1570:return [text]
    words=text.split(' ');choices=[]
    for split in range(1,len(words)):
        pair=[' '.join(words[:split]),' '.join(words[split:])];widths=[measure(x) for x in pair]
        if max(widths)<=1570:choices.append((abs(widths[0]-widths[1]),pair))
    if not choices:raise ValueError('Caption needs a real clause split; font shrinking/omission prohibited: '+text)
    return min(choices,key=lambda x:x[0])[1]
def caption_ass(path,cues,offset,emphases):
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
    bold=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',48)
    out=ass_header();receipt=[]
    for cue in cues:
        text=safe_text(cue['text']);emphasis=emphases.get(str(cue['id']))
        if emphasis and (text.count(emphasis['text'])!=1 or emphasis['role'] not in CAPTION_COLORS):raise ValueError('Emphasis must name one unique visible span with semantic role')
        def measure(line):
            if emphasis and emphasis['text'] in line:
                before,after=line.split(emphasis['text'],1)
                return font.getlength(before)+bold.getlength(emphasis['text'])+font.getlength(after)
            return font.getlength(line)
        lines=wrap_caption(text,font,measure)
        width=math.ceil(max(measure(t) for t in lines))+44;height=len(lines)*62+22
        x=960-width/2;y=970-height/2;start=cue['start']+offset;end=cue['end']+offset
        shape=f'm 0 0 l {width} 0 {width} {height} 0 {height}'
        event(out,start,end,f'{{\\an7\\pos({x+14:g},{y+14:g})\\p1\\bord0\\shad0\\1c&H323C07&}}'+shape,0)
        event(out,start,end,f'{{\\an7\\pos({x:g},{y:g})\\p1\\bord3\\shad0\\1c&HFFFFFF&\\3c&H181B16&}}'+shape,1)
        emphasized=False
        for i,line in enumerate(lines):
            display=line
            if emphasis and emphasis['text'] in line:
                color=bgr(CAPTION_COLORS[emphasis['role']]);part=emphasis['text']
                display=line.replace(part,f'{{\\1c&H{color}&\\b700}}{part}{{\\1c&H090B08&\\b0}}');emphasized=True
            event(out,start,end,f'{{\\an5\\pos(960,{970+(i-(len(lines)-1)/2)*62:g})\\bord0\\shad0}}'+display)
        if emphasis and not emphasized:raise ValueError('Emphasis crosses auto line break; choose another clause/span')
        receipt.append({'cue':cue['id'],'lines':lines,'rect':[x,y,width,height],'center':[960,970],'emphasis':emphasis})
    path.write_text('\n'.join(out)+'\n',encoding='utf-8')
    return receipt

def intersects(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
def protect(rect,protected):
    if rect[0]<0 or rect[1]<0 or rect[2]>W or rect[3]>H:raise ValueError('Annotation outside frame')
    if any(intersects(rect,r) for r in [CAPTION_RECT,*protected]):raise ValueError(f'Annotation obscures protected caption/UI region: {rect}')
def interpolate_mark(mark,t):
    frames=mark.get('keyframes',[])
    if not frames:return mark
    frames=sorted(frames,key=lambda k:k['time'])
    if t<=frames[0]['time']:return dict(mark,**frames[0])
    if t>=frames[-1]['time']:return dict(mark,**frames[-1])
    a,b=next((a,b) for a,b in zip(frames,frames[1:]) if a['time']<=t<=b['time'])
    u=(t-a['time'])/(b['time']-a['time']);result=dict(mark)
    for key in ['x','y','w','h']:
        if key in a and key in b:result[key]=a[key]+(b[key]-a[key])*u
    if 'points' in a and 'points' in b:
        if len(a['points'])!=len(b['points']):raise ValueError('Tracked path topology cannot change')
        result['points']=[[v+(w-v)*u for v,w in zip(p,q)] for p,q in zip(a['points'],b['points'])]
    return result
def shape(mark):
    typ=mark['type'];x=mark.get('x',0);y=mark.get('y',0);w=mark.get('w',0);h=mark.get('h',0)
    if typ=='rect':return f'm {x:g} {y:g} l {x+w:g} {y:g} {x+w:g} {y+h:g} {x:g} {y+h:g} {x:g} {y:g}',(x-8,y-8,x+w+8,y+h+8)
    if typ=='ellipse':
        cx=x+w/2;cy=y+h/2;rx=w/2;ry=h/2;k=.55228475
        p=f'm {cx+rx:g} {cy:g} b {cx+rx:g} {cy+ry*k:g} {cx+rx*k:g} {cy+ry:g} {cx:g} {cy+ry:g} {cx-rx*k:g} {cy+ry:g} {cx-rx:g} {cy+ry*k:g} {cx-rx:g} {cy:g} {cx-rx:g} {cy-ry*k:g} {cx-rx*k:g} {cy-ry:g} {cx:g} {cy-ry:g} {cx+rx*k:g} {cy-ry:g} {cx+rx:g} {cy-ry*k:g} {cx+rx:g} {cy:g}'
        return p,(x-8,y-8,x+w+8,y+h+8)
    if typ in ['line','arrow','contour']:
        pts=mark['points']
        if len(pts)<2:raise ValueError('A visible path requires at least two points')
        reveal=mark.get('_reveal',1.0)
        if reveal<1:
            lengths=[math.dist(a,b) for a,b in zip(pts,pts[1:])];remaining=sum(lengths)*max(.001,reveal);partial=[pts[0]]
            for a,b,length in zip(pts,pts[1:],lengths):
                if remaining>=length:partial.append(b);remaining-=length
                else:
                    u=remaining/max(length,1e-9);partial.append([x+(y-x)*u for x,y in zip(a,b)]);break
            pts=partial
        p='m '+' '.join(f'{v:g}' for v in pts[0])+' l '+' '.join(f'{v:g}' for pt in pts[1:] for v in pt)
        if typ=='arrow':
            a,b=pts[-2:];ang=math.atan2(b[1]-a[1],b[0]-a[0]);size=23
            ends=[[b[0]-size*math.cos(ang+v),b[1]-size*math.sin(ang+v)] for v in [-.5,.5]]
            p+=' m '+' '.join(f'{v:g}' for v in ends[0])+' l '+' '.join(f'{v:g}' for pt in [b,ends[1]] for v in pt)
        xs=[p[0] for p in pts];ys=[p[1] for p in pts]
        return p,(min(xs)-25,min(ys)-25,max(xs)+25,max(ys)+25)
    raise ValueError('Unknown annotation type '+typ)
def overlay_ass(path,beat,kind,duration):
    out=ass_header();protected=beat.get('protectedRects',[])
    label=beat.get('pictureLabel',KIND_LABELS[kind]);safe_text(label)
    # Native documentary captures already carry their source-kind label. An explicit
    # empty pictureLabel suppresses this duplicate; it does not reclassify the source.
    if label:event(out,0,duration,'{\\an9\\pos(1872,34)\\fs28\\bord2\\3c&H101914&\\1c&HFFFFFF&}'+label,4)
    for original in beat.get('overlays',[]):
        start=float(original['start']);end=float(original['end'])
        if start<0 or end>duration+1e-6 or end<=start:raise ValueError('Overlay timing outside its cut')
        typ=original['type']
        if typ=='text':
            size=original.get('fontSize',40);text=safe_text(original['text']);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',size)
            x=original['x'];y=original['y'];protect((x,y,x+font.getlength(text),y+size*1.35),protected)
            color=bgr(ROLE_COLORS[original.get('role','text')])
            event(out,start,end,f'{{\\an7\\pos({x},{y})\\fs{size}\\bord3\\3c&H101914&\\1c&H{color}&\\fad(90,90)}}'+text,5)
        elif typ=='code':
            if original.get('provenance')!='independently-authored-pseudocode':raise ValueError('Only our authored explanatory code may be an overlay')
            x=original['x'];y=original['y'];size=original.get('fontSize',40);font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',size)
            for i,line in enumerate(original['lines']):
                xpos=float(x);ypos=y+i*(size+14)
                if line.get('executing'):
                    protect((x-18,ypos,x-13,ypos+size+5),protected)
                    event(out,start,end,f'{{\\an7\\pos({x-18},{ypos})\\p1\\bord0\\1c&H83CFE8&}}m 0 0 l 5 0 5 {size+5} 0 {size+5}',4)
                for token in line['tokens']:
                    text=safe_text(token['text']);width=font.getlength(text);protect((xpos,ypos,xpos+width,ypos+size+8),protected)
                    color=bgr(CODE_COLORS[token['role']]);event(out,start,end,f'{{\\an7\\pos({xpos:g},{ypos:g})\\fnConsolas\\fs{size}\\bord2\\3c&H101914&\\1c&H{color}&}}'+text,5);xpos+=width
        else:
            color=bgr(ROLE_COLORS[original.get('role','focus')]);width=original.get('stroke',6)
            steps=math.ceil((end-start)*20) if original.get('keyframes') or original.get('revealSeconds') else 1
            boundaries={start+(end-start)*i/steps for i in range(steps+1)}
            for hide_start,hide_end in original.get('hiddenIntervals',[]):
                if hide_end<=hide_start:raise ValueError('Invalid annotation hidden interval')
                boundaries.update(t for t in (hide_start,hide_end) if start<t<end)
            ordered=sorted(boundaries)
            for a,b in zip(ordered,ordered[1:]):
                if any(q[0]<=(a+b)/2<q[1] for q in original.get('hiddenIntervals',[])):continue
                mark=interpolate_mark(original,(a+b)/2)
                if original.get('revealSeconds'):mark['_reveal']=min(1.0,((a+b)/2-start)/original['revealSeconds'])
                path_data,rect=shape(mark);protect(rect,protected)
                event(out,a,b,f'{{\\an7\\pos(0,0)\\p1\\bord{width}\\shad0\\1a&HFF&\\3a&H00&\\3c&H{color}&}}'+path_data,3)
    path.write_text('\n'.join(out)+'\n',encoding='utf-8')

def validate(plan,plan_path,work):
    if plan.get('editReady') is not True:raise ValueError('Exact inspected source cuts/cues are not selected: editReady=false. Parent must finish the existing footage review, not invent cuts.')
    manifest=load(PROJECT/'project.json')
    if not manifest.get('startGate',{}).get('productionAllowedNow'):raise ValueError('Project manual start is not authorized')
    if plan.get('fps')!=60 or plan.get('width')!=1920 or plan.get('height')!=1080:raise ValueError('FHD60 master required')
    plan['_file_hashes']={}
    result={'checkedAt':now(),'timelineSha256':digest(plan_path),'sources':{},'cuts':[],'humanViewing':False,'humanListening':False,'rightsAudit':'uses explicit project evidence; not inferred from ffprobe'}
    for sid,source in plan['sources'].items():
        p=resolve(source['file']);actual=digest(p)
        if actual!=source['sha256']:raise ValueError('Changed source '+sid)
        plan['_file_hashes'][str(p)]=actual
        if source['kind'] not in KIND_LABELS:raise ValueError('Research references and still-padding sources cannot enter cuts')
        if source.get('motionReviewed') is not True or not source.get('evidence'):raise ValueError('Actual source motion/evidence review absent for '+sid)
        meta=probe(p,plan);v=video_stream(meta)
        if v['width']<1920 or v['height']<1080:raise ValueError('Source below genuine1080 requirement: '+sid)
        result['sources'][sid]={'sha256':actual,'probe':meta}
    body_frames=0
    seen=set()
    for beat in plan['beats']:
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*',beat['id']) or beat['id'] in seen:raise ValueError('Unique safe beat IDs required')
        seen.add(beat['id']);frames=beat['frames'];source=plan['sources'][beat['source']]
        if type(frames)!=int or frames<=0:raise ValueError('Positive whole output frames required')
        if beat.get('speed',1)!=1 or beat.get('loop',False) or beat.get('freeze',False):raise ValueError('Native motion only: no loop, slowdown or freeze padding')
        if not beat.get('observedAction') or not beat.get('narrationConnection'):raise ValueError('Cut must explain a directly reviewed action')
        duration=frames/FPS;meta=result['sources'][beat['source']]['probe'];v=video_stream(meta)
        source_duration=min(float(meta['format']['duration']),float(v.get('duration',meta['format']['duration'])))
        if beat['sourceInSeconds']<0 or beat['sourceInSeconds']+duration>source_duration+1/FPS:raise ValueError('Cut runs past source; no tail cloning allowed')
        if beat.get('sourceAudio') and 'sourceAudioGainDb' not in beat:raise ValueError('Record chosen source audio gain')
        overlay_ass(work/(beat['id']+'.ass'),beat,source['kind'],duration)
        result['cuts'].append({'id':beat['id'],'startFrame':120+body_frames,'frames':frames,'source':beat['source'],'sourceInSeconds':beat['sourceInSeconds']})
        body_frames+=frames
    if not body_frames:raise ValueError('No cuts selected')
    narration=resolve(plan['narration']['wav']);voice_meta=probe(narration,plan)
    if digest(narration)!=plan['narration']['sha256']:raise ValueError('Narration file changed')
    voice_streams=[s for s in voice_meta['streams'] if s['codec_type']=='audio']
    if len(voice_streams)!=1 or not voice_streams[0]['codec_name'].startswith('pcm_'):raise ValueError('One approved PCM narration stream is required')
    if not plan['narration'].get('timingReviewed'):raise ValueError('Measured narration timing not recorded')
    if float(voice_meta['format']['duration'])>body_frames/FPS+1/FPS:raise ValueError('Narration would be truncated by visual timeline')
    for name,length in [('branding',2),('membership',10)]:
        p=resolve(plan[name]['file']);meta=probe(p,plan);v=video_stream(meta)
        if digest(p)!=plan[name]['sha256']:raise ValueError('Approved bookend changed: '+name)
        plan['_file_hashes'][str(p)]=plan[name]['sha256']
        if v['width']!=W or v['height']!=H or Fraction(v['avg_frame_rate'])!=FPS or abs(float(meta['format']['duration'])-length)>1/FPS:raise ValueError('Bookend format/duration mismatch')
        if v.get('nb_frames') and int(v['nb_frames'])!=length*FPS:raise ValueError('Bookend frame count mismatch')
    ko=read_srt(resolve(plan['narration']['koSrt']));en=read_srt(resolve(plan['narration']['enSrt']))
    for lang,cues in [('ko',ko),('en',en)]:
        if cues[-1]['end']>body_frames/FPS+.01:raise ValueError(lang+' subtitle exceeds body')
    result.update(bodyFrames=body_frames,totalFrames=body_frames+720,narrationSha256=digest(narration),koCues=len(ko),enCues=len(en))
    result['captionLayout']=caption_ass(work/'captions.ko.ass',ko,2,plan.get('captionEmphasis',{}))
    write_srt(work/'captions.ko.srt',ko,2);write_srt(work/'captions.en.srt',en,2)
    save(work/'preflight.json',result)
    return result

def ff(plan,args,log,cwd=None):
    command([tool('ffmpeg',plan),'-hide_banner','-v','warning','-nostdin','-y','-filter_threads','1','-filter_complex_threads','1',*args],log,cwd)
def encoder(plan):
    if plan.get('encoder','libx264')=='h264_nvenc':return ['-c:v','h264_nvenc','-preset','p5','-cq','18','-b:v','0']
    return ['-c:v','libx264','-threads','4','-preset','veryfast','-crf','18']
def render_clip(plan,source,seconds_in,frames,stem,work,overlay=None,audio=False,gain=0,viewport_height=1080):
    duration=frames/FPS;video=work/(stem+'.mp4');wav=work/(stem+'.wav');source_meta=probe(source,plan)
    cache_path=work/(stem+'.receipt.json')
    if viewport_height not in (860,1080):raise ValueError('Only verified full-frame or caption-safe860px viewport permitted')
    fingerprint={'source':str(source),'sourceSha256':plan['_file_hashes'][str(source)],'inSeconds':seconds_in,'frames':frames,'audio':audio,'gainDb':gain,'viewportHeight':viewport_height,'overlaySha256':digest(overlay) if overlay else None,'encoder':encoder(plan),'pipelineSha256':digest(Path(__file__))}
    if cache_path.exists() and video.exists() and wav.exists():
        previous=load(cache_path)
        if previous['input']==fingerprint and previous['videoSha256']==digest(video) and previous['audioSha256']==digest(wav):return video,wav
    placement='0' if viewport_height==860 else '(oh-ih)/2'
    filt=f'setpts=PTS-STARTPTS,scale=1920:{viewport_height}:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,pad=1920:1080:(ow-iw)/2:{placement}:color=black,setsar=1,fps=60,format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709'
    if overlay:filt+=',ass='+overlay.name
    ff(plan,['-ss',f'{seconds_in:.9f}','-i',source,'-an','-vf',filt,'-frames:v',str(frames),*encoder(plan),'-video_track_timescale','90000','-map_metadata','-1','-write_tmcd','0','-movflags','+faststart',video],work/'logs'/(stem+'.video.log'),work)
    if audio and any(s['codec_type']=='audio' for s in source_meta['streams']):
        af=f'aresample=48000,asetpts=PTS-STARTPTS,volume={gain}dB,afade=t=in:d=0.12,afade=t=out:st={max(0,duration-.3):.9f}:d=0.3,apad,atrim=end_sample={frames*800}'
        ff(plan,['-ss',f'{seconds_in:.9f}','-i',source,'-vn','-af',af,'-ac','2','-ar','48000','-c:a','pcm_s16le',wav],work/'logs'/(stem+'.audio.log'))
    else:ff(plan,['-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',f'{duration:.9f}','-c:a','pcm_s16le',wav],work/'logs'/(stem+'.silence.log'))
    save(cache_path,{'input':fingerprint,'videoSha256':digest(video),'audioSha256':digest(wav),'completedAt':now()})
    return video,wav
def concat(plan,files,target,work,label,audio=False):
    if audio:
        # Decode each WAV using its own format. The concat demuxer cannot safely
        # concatenate S16 bookends with float narration: it interprets later bytes
        # using the first stream's codec, doubling duration and corrupting sound.
        inputs=[];filters=[];labels=[]
        for i,p in enumerate(files):
            inputs+=['-i',p]
            filters.append(f'[{i}:a]aresample=48000,aformat=sample_fmts=flt:channel_layouts=stereo,asetpts=PTS-STARTPTS[a{i}]')
            labels.append(f'[a{i}]')
        filters.append(''.join(labels)+f'concat=n={len(files)}:v=0:a=1[joined]')
        ff(plan,[*inputs,'-filter_complex',';'.join(filters),'-map','[joined]','-c:a','pcm_f32le','-ar','48000','-ac','2',target],work/'logs'/(label+'.log'))
        return
    manifest=work/(label+'.ffconcat')
    for p in files:
        if "'" in str(p):raise ValueError('Unsupported apostrophe in concat file path')
    manifest.write_text('ffconcat version 1.0\n'+'\n'.join("file '"+str(p).replace('\\','/')+"'" for p in files)+'\n',encoding='utf-8')
    args=['-f','concat','-safe','0','-i',manifest]
    # Float intermediates preserve transient headroom until the one final limiter.
    args+=['-vn','-c:a','pcm_f32le','-ar','48000','-ac','2'] if audio else ['-an','-c:v','copy','-video_track_timescale','90000','-map_metadata','-1','-write_tmcd','0']
    ff(plan,[*args,target],work/'logs'/(label+'.log'))
def render(plan,plan_path,work,receipt):
    final=resolve(plan['outputDirectory']);final.mkdir(parents=True,exist_ok=True)
    stem=plan.get('outputStem',PROJECT.name)
    clean=final/(stem+'.clean.mp4');captioned=final/(stem+'.captioned.mp4')
    if clean.exists() or captioned.exists():raise FileExistsError('Use a fresh output revision; do not overwrite delivered masters')
    body_v=[];body_a=[];operations=[]
    for beat in plan['beats']:
        source=resolve(plan['sources'][beat['source']]['file'])
        v,a=render_clip(plan,source,beat['sourceInSeconds'],beat['frames'],beat['id'],work,work/(beat['id']+'.ass'),beat.get('sourceAudio',False),beat.get('sourceAudioGainDb',0),beat.get('viewportHeight',1080))
        body_v.append(v);body_a.append(a);operations.append({'cut':beat['id'],'video':str(v),'sha256':digest(v)})
        save(work/'render-progress.json',{'updatedAt':now(),'completedCuts':operations,'complete':False})
    brand_v,brand_a=render_clip(plan,resolve(plan['branding']['file']),0,120,'bookend-brand',work,audio=plan['branding'].get('audio',True))
    end_v,end_a=render_clip(plan,resolve(plan['membership']['file']),0,600,'bookend-member',work,audio=plan['membership'].get('audio',True))
    concat(plan,[brand_v,*body_v,end_v],work/'visuals.mp4',work,'visuals-concat')
    concat(plan,body_a,work/'body-source.wav',work,'body-source-concat',audio=True)
    body_samples=receipt['bodyFrames']*800
    # Keep approved narration PCM unchanged; normalize neither voice nor total mix per scene.
    # The foreground voice controls source-audio ducking, never the reverse.
    audio_filter=f'[0:a]aresample=48000,apad,atrim=end_sample={body_samples},volume={plan["narration"].get("gainDb",0)}dB,asplit=2[voice][side];[1:a][side]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[bed];[voice][bed]amix=inputs=2:duration=first:normalize=0[body]'
    ff(plan,['-i',resolve(plan['narration']['wav']),'-i',work/'body-source.wav','-filter_complex',audio_filter,'-map','[body]','-ac','2','-ar','48000','-c:a','pcm_f32le',work/'body-mix.wav'],work/'logs'/'body-mix.log')
    concat(plan,[brand_a,work/'body-mix.wav',end_a],work/'complete-mix.wav',work,'complete-mix-concat',audio=True)
    # Encode one AAC stream, then packet-copy it into both video variants.
    ff(plan,['-i',work/'complete-mix.wav','-af','aresample=192000,alimiter=limit=0.794328:level=false:latency=true,aresample=48000','-c:a','aac','-b:a','192k','-ar','48000','-ac','2',work/'approved-pair-audio.m4a'],work/'logs'/'encode-single-aac.log')
    ff(plan,['-i',work/'visuals.mp4','-i',work/'approved-pair-audio.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-map_metadata','-1','-movflags','+faststart',clean],work/'logs'/'clean-master.log')
    ff(plan,['-i',clean,'-vf','ass=captions.ko.ass','-map','0:v:0','-map','0:a:0',*encoder(plan),'-pix_fmt','yuv420p','-c:a','copy','-video_track_timescale','90000','-map_metadata','-1','-movflags','+faststart',captioned],work/'logs'/'captioned-master.log',work)
    shutil.copy2(work/'captions.ko.srt',final/(stem+'.ko.srt'));shutil.copy2(work/'captions.en.srt',final/(stem+'.en.srt'))
    write_index(final,stem)
    save(work/'render-progress.json',{'updatedAt':now(),'completedCuts':operations,'complete':True,'humanReview':False,'outputDirectory':str(final),'narrationInputPreservedSha256':receipt['narrationSha256']})
    return final
def write_index(directory,stem):
    safe=html.escape(stem)
    page=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>벅샷 룰렛 재구현 검수</title><style>body{{margin:28px auto;max-width:1100px;padding:0 20px;background:#0b1212;color:#eee;font:18px/1.6 system-ui}}h1{{color:#e8cf83}}video{{width:100%}}a{{color:#9ad7c6}}li{{margin:8px 0}}</style><h1>벅샷 룰렛 분석·재구현</h1><p>로컬 검수본 · 1920×1080 / 60fps · 자체 검수와 사용자 검수 상태는 별도 기록합니다.</p><video controls preload="metadata" src="{safe}.captioned.mp4"></video><ul><li><a href="{safe}.captioned.mp4">전체 자막 영상</a></li><li><a href="{safe}.clean.mp4">자막 없는 영상</a></li><li><a href="{safe}.ko.srt">한국어 자막</a> · <a href="{safe}.en.srt">영어 자막</a></li></ul></html>'''
    (directory/'index.html').write_text(page,encoding='utf-8')
def verify(plan,receipt,work):
    directory=resolve(plan['outputDirectory']);stem=plan.get('outputStem',PROJECT.name);results={}
    for kind in ['clean','captioned']:
        p=directory/(stem+'.'+kind+'.mp4');meta=probe(p,plan,count=True);v=video_stream(meta)
        if v['width']!=W or v['height']!=H or Fraction(v['avg_frame_rate'])!=FPS:raise ValueError('Wrong final video format')
        if int(v['nb_read_frames'])!=receipt['totalFrames']:raise ValueError('Final frame count differs from exact timeline')
        audio=[s for s in meta['streams'] if s['codec_type']=='audio']
        if len(audio)!=1:raise ValueError('Exactly one final audio stream required')
        expected=receipt['totalFrames']/FPS
        for name,value in [('video',v['duration']),('audio',audio[0]['duration']),('container',meta['format']['duration'])]:
            if abs(float(value)-expected)>max(1/FPS,1024/SR):raise ValueError(f'{name} duration differs from timeline: {value} vs {expected}')
        if audio[0]['sample_rate']!='48000' or audio[0]['channels']!=2:raise ValueError('Final audio must be48kHz stereo')
        ff(plan,['-xerror','-err_detect','explode','-i',p,'-map','0:v:0','-map','0:a:0','-f','null','-'],work/'logs'/('decode-'+kind+'.log'))
        pcm=work/(kind+'.audio.sha256')
        ff(plan,['-i',p,'-map','0:a:0','-c:a','pcm_s16le','-f','hash','-hash','sha256',pcm],work/'logs'/('audio-hash-'+kind+'.log'))
        results[kind]={'file':str(p),'sha256':digest(p),'probe':meta,'decodedAudioHash':pcm.read_text().strip()}
    if results['clean']['decodedAudioHash']!=results['captioned']['decodedAudioHash']:raise ValueError('Paired audio mismatch')
    ff(plan,['-v','info','-i',directory/(stem+'.captioned.mp4'),'-af','ebur128=peak=true','-f','null','-'],work/'logs'/'final-loudness.log')
    loudness_log=(work/'logs'/'final-loudness.log').read_text(encoding='utf-8',errors='replace')
    peaks=re.findall(r'True peak:\s+Peak:\s+(-?\d+(?:\.\d+)?)',loudness_log)
    if not peaks or float(peaks[-1])>-1.5:raise ValueError('Encoded AAC true peak exceeds -1.5dBTP or was not measured')
    report={'checkedAt':now(),'technicalDecodePassed':True,'pairedAudioIdentical':True,'outputs':results,'humanViewing':False,'humanListening':False,'remaining':['Read final-loudness true peak and local narration continuity report','Actual motion/caption/cut visual QA at1080 and375px','Contextual listening/ASR and original-to-prototype claim audit','User local review before upload']}
    report.update(audioLoudnessPassed=True,encodedTruePeakDbtp=float(peaks[-1]))
    save(work/'technical-qa.json',report);return report
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('timeline',type=Path)
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--render',action='store_true')
    parser.add_argument('--verify',action='store_true')
    args=parser.parse_args();plan_path=args.timeline.resolve();plan=load(plan_path)
    work=resolve(plan.get('workDirectory','production/local/documentary-v1'));work.mkdir(parents=True,exist_ok=True)
    receipt=validate(plan,plan_path,work)
    if args.render:render(plan,plan_path,work,receipt)
    if args.verify:verify(plan,receipt,work)
    print(json.dumps({'preflight':str(work/'preflight.json'),'bodyFrames':receipt['bodyFrames'],'rendered':args.render,'verified':args.verify},ensure_ascii=False))
if __name__=='__main__':main()

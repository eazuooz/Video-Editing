"""Native portrait FOV comparison. --prepare is metadata plus one marked layout.
Only --render/--pair start finite media work, after the parent handoff.
"""
from __future__ import annotations
import argparse,hashlib,json,math,re,subprocess
from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[3]
PROJECT=Path(__file__).resolve().parents[1]
OUT=PROJECT/'production/local';SLUG=PROJECT.name
FFBIN=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin')
FFMPEG,FFPROBE=str(FFBIN/'ffmpeg.exe'),str(FFBIN/'ffprobe.exe')
W,H,FPS,FRAMES=1080,1920,60,1800
DURATION=FRAMES/FPS
VIEWPORT=[0,440,1080,608]
FONTFILE='C:/Windows/Fonts/malgun.ttf';BOLDFONT='C:/Windows/Fonts/malgunbd.ttf'
CAPTION_WIDTH,CAPTION_X,CAPTION_Y,CAPTION_SIZE=796,510,1380,60
COL=dict(bg='#080B09',white='#FFFFFF',yellow='#FFD25A',blue='#70C4FF',green='#92DF9C',muted='#B8C3BC',forest='#073C32')

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(path):return Path(path).relative_to(ROOT).as_posix()
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
def run(args,**kw):
    result=subprocess.run(args,capture_output=True,check=False,**kw)
    if result.returncode:raise RuntimeError(result.stderr.decode(errors='replace')[-12000:])
    return result
@lru_cache(maxsize=32)
def font(size,bold=False):return ImageFont.truetype(BOLDFONT if bold else FONTFILE,size)
def text(draw,at,value,size,fill='white',anchor='mm',bold=False,stroke=0):
    draw.text(at,value,font=font(size,bold),fill=COL.get(fill,fill),anchor=anchor,stroke_width=stroke,stroke_fill=COL['bg'])
def ease(v):
    v=max(0,min(1,v));return v*v*(3-2*v)
def line(draw,points,progress,color,width=8):
    if progress<=0:return
    lengths=[math.dist(a,b) for a,b in zip(points,points[1:])];left=sum(lengths)*min(1,progress);partial=[points[0]]
    for a,b,length in zip(points,points[1:],lengths):
        if left>=length:partial.append(b);left-=length
        else:
            if length:partial.append((a[0]+(b[0]-a[0])*left/length,a[1]+(b[1]-a[1])*left/length))
            break
    if len(partial)>1:draw.line(partial,fill=COL.get(color,color),width=width,joint='curve')
def double_arrow(draw,left,right,y):
    color=COL['white'];draw.line([(left,y),(right,y)],fill=color,width=6)
    draw.polygon([(left,y),(left+18,y-12),(left+18,y+12)],fill=color)
    draw.polygon([(right,y),(right-18,y-12),(right-18,y+12)],fill=color)
def wrapped(value,size=CAPTION_SIZE,maxwidth=CAPTION_WIDTH):
    value=' '.join(value.replace('\n',' ').split());f=font(size)
    if f.getlength(value)<=maxwidth:return [value]
    words=value.split();choices=[]
    for i in range(1,len(words)):
        parts=[' '.join(words[:i]),' '.join(words[i:])]
        if max(f.getlength(x) for x in parts)<=maxwidth:choices.append(parts)
    if not choices:raise ValueError('Split at an existing spoken boundary; never shrink captions: '+value)
    return min(choices,key=lambda lines:abs(f.getlength(lines[0])-f.getlength(lines[1])))
def stamp(seconds,ass=False):
    scale=100 if ass else 1000;n=round(seconds*scale);h,n=divmod(n,3600*scale);m,n=divmod(n,60*scale);s,n=divmod(n,scale)
    return f'{h}:{m:02}:{s:02}.{n:02}' if ass else f'{h:02}:{m:02}:{s:02},{n:03}'
def polygon(x,y,w,h):return f'm {x:.2f} {y:.2f} l {x+w:.2f} {y:.2f} {x+w:.2f} {y+h:.2f} {x:.2f} {y+h:.2f}'
def input_map():return read(PROJECT/'script/raw-source-map.json')
def vector3(value):
    if isinstance(value,dict):return [float(value[k]) for k in ['x','y','z']]
    assert len(value)==3;return [float(x) for x in value]

BEATS=[
    dict(start=0,end=.8,id='hook-narrow',index=0,focus='center'),
    dict(start=.8,end=1.8,id='hook-wide',index=60,focus='center'),
    dict(start=1.8,end=2.8,id='hook-same-car-overlay',index=60,focus='comparison'),
    dict(start=2.8,end=8.36,id='wide-surroundings',index=60,focus='surroundings-after5.62'),
    dict(start=8.36,end=9.36,id='center-shrinks',indexFrom=0,indexTo=60,focus='center'),
    dict(start=9.36,end=12.7,id='same-center-size-comparison',index=60,focus='comparison'),
    dict(start=12.7,end=14.1,id='narrow-view',indexFrom=60,indexTo=0,focus='center'),
    dict(start=14.1,end=18.06,id='narrow-misses-surroundings',index=0,focus='offscreen-after15.26'),
    dict(start=18.06,end=20.74,id='wide-car-small',index=60,focus='center-and-surroundings'),
    dict(start=20.74,end=23.88,id='narrow-side-car-outside',index=0,focus='offscreen'),
    dict(start=23.88,end=30,id='one-tradeoff-conclusion',index=60,focus='comparison')
]
def beat_at(t):return next((b for b in BEATS if b['start']<=t<b['end']),BEATS[-1])
def source_index(t):
    beat=beat_at(t)
    if 'index' in beat:return beat['index']
    fraction=ease((t-beat['start'])/(beat['end']-beat['start']))
    return round(beat['indexFrom']+(beat['indexTo']-beat['indexFrom'])*fraction)

def make_captions():
    spec=read(PROJECT/'script/captions.json');rows=spec['cues'];events=[];layout=[];previous=0
    for i,row in enumerate(rows,1):
        a,b=row['start'],row['end'];assert a>=previous-.001 and b>a and 2.8-.001<=a<b<=29.52+.001;previous=b
        for language in ['ko','en']:wrapped(row[language])
        lines=wrapped(row['ko']);width=max(font(60).getlength(s) for s in lines)+44;height=len(lines)*78+26
        x,y=CAPTION_X-width/2,CAPTION_Y-height/2
        assert width<=840 and x>=80 and x+width<=930 and y+height+14<1560
        when=f'{stamp(a,True)},{stamp(b,True)}'
        events.extend([f'Dialogue: 10,{when},Box,,0,0,0,,{{\\an7\\pos(0,0)\\bord0\\1c&H323C07&\\p1}}'+polygon(x+12,y+12,width,height),f'Dialogue: 11,{when},Box,,0,0,0,,{{\\an7\\pos(0,0)\\p1}}'+polygon(x,y,width,height)])
        for j,value in enumerate(lines):events.append(f'Dialogue: 12,{when},Text,,0,0,0,,{{\\an5\\pos(510,{1380+(j-(len(lines)-1)/2)*78:.2f})}}'+value.replace('{','').replace('}',''))
        layout.append(dict(cue=i,start=a,end=b,lines=lines,textWidths=[font(60).getlength(s) for s in lines],box=[x,y,width,height],center=[510,1380],font=60))
    header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Text,Malgun Gothic,60,&H00090B08,&H00090B08,&H00181B16,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Box,Malgun Gothic,60,&H00FFFFFF,&H00FFFFFF,&H00181B16,&H00000000,0,0,0,0,100,100,0,0,1,3,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'captions.ko.ass').write_text(header+'\n'.join(events)+'\n',encoding='utf8')
    for lang in ['ko','en']:
        blocks=[f'{i}\n{stamp(row["start"])} --> {stamp(row["end"])}\n'+'\n'.join(wrapped(row[lang])) for i,row in enumerate(rows,1)]
        (OUT/f'captions.{lang}.srt').write_text('\n\n'.join(blocks)+'\n',encoding='utf8')
    write(OUT/'caption-layout.json',dict(rows=layout,width=W,height=H,fps=FPS,fontFile=FONTFILE,inputSha256=sha(PROJECT/'script/captions.json'),position=[510,1380],maxLines=2,effectiveTextWidth=796,editorialSafeMargins=dict(right=150,bottom=360),platformUiPixelVerification='pending'))
    return layout

def check_design():
    spec=input_map();n=spec['narration'];assert spec['output']==dict(width=1080,height=1920,fps=60,frames=1800,seconds=30)
    assert abs(n['sourceEnd']-n['sourceStart']-26.72)<1e-7 and n['placementStart']==2.8 and n['postSilenceSeconds']==.48 and n['declickSeconds']==0
    source=read(PROJECT/'sources/source-map.json');assert n['sourceStart']==source['narration']['inPoint'] and n['sourceEnd']==source['narration']['outPoint'] and n['placementStart']==source['narration']['delaySeconds']
    assert sha(ROOT/n['wordEvidence'])==n['wordEvidenceSha256'] and sha(ROOT/n['timingEvidence'])==n['timingEvidenceSha256']
    cues=read(PROJECT/'script/captions.json')['cues']
    normalize=lambda value:re.sub(r'[^가-힣A-Za-z0-9]','',value)
    assert normalize(' '.join(x['ko'] for x in cues))==normalize((PROJECT/'script/narration.ko.txt').read_text(encoding='utf8')),'Retain every word of the five approved paragraphs.'
    words=read(ROOT/n['wordEvidence'])['words'];starts=[x['timestamp'][0] for x in words];ends=[x['timestamp'][1] for x in words]
    for row in cues:
        assert row.get('approvedTimingBoundaryOverride') or min(abs(row['sourceSceneWordStart']-x) for x in starts)<=.021
        assert min(abs(row['sourceSceneWordEnd']-x) for x in ends)<=.021
        expected=row['sourceSceneWordStart']+n['wordSceneGlobalStart']-n['sourceStart']+n['placementStart']
        assert abs(row['start']-expected)<1e-6
    layout=make_captions();assert font(74,True).getlength('앞차가 작아졌다')<890
    timeline=dict(fps=FPS,frames=FRAMES,seconds=DURATION,viewport=VIEWPORT,beats=BEATS,cuts=sorted(set([0,.8,1.8,2.8,5.62,8.36,9.36,12.7,14.1,15.26,18.06,20.74,23.88,29.52,30])),onlyChangedSceneVariable='horizontal FOV',cameraAndCarTransformsFixed=True,rendererSource='actual Unity captures',sourceIndexPerOutputFrame=[source_index(i/FPS) for i in range(FRAMES)],annotations='Actual Camera.WorldToViewportPoint projections; editorial hollow guides, never detector confidence or simulated game HUD.')
    write(OUT/'visual-timeline.json',timeline)
    report=dict(status='passed-code-and-font-layout-only',frames=FRAMES,duration=DURATION,cues=len(layout),maximumCaptionWidth=max(max(x['textWidths']) for x in layout),fixedCaptionCenter=[510,1380],allFiveOriginalParagraphsRetained=True,originalWordTimingAndApprovedOverlapJoinVerified=True,newTtsJobs=0,mediaJobsStarted=0,actualCapturePixelsReviewed=False,humanListening=False)
    write(OUT/'code-preflight.json',report);return report

def capture_inputs(require_all=True,folder_override=None):
    spec=input_map()['capture'];folder=Path(folder_override) if folder_override else ROOT/spec['frameDirectory'];proof=folder/'capture-projection.json'
    if not proof.exists():
        if require_all:raise FileNotFoundError('Unity projection receipt is not ready; do not render a placeholder as final.')
        return None,None
    document=read(proof);actual=document['frames'];indices=[x['index'] for x in actual]
    assert indices==list(range(61)) or (not require_all and indices==[0,60]),'Expected61full frames or exactly the two actual preview endpoints.'
    for row in actual:
        i=row['index']
        assert abs(row['horizontalFovDegrees']-(60+40*i/60))<1e-4 and row['cameraTransformUnchanged']
        assert vector3(row['cameraPosition'])==[0,1.5,0] and vector3(row['cameraRotationEuler'])==[0,0,0]
        assert {c['id'] for c in row['cars']}=={'center','left','right'}
        for car in row['cars']:
            baseline=next(c for c in actual[0]['cars'] if c['id']==car['id'])
            assert car['worldBounds']==baseline['worldBounds'],'Only FOV may change; no camera or car motion.'
    if require_all:
        for i in range(61):
            path=folder/f'frame-{i:03}.png';assert path.exists(),path
            with Image.open(path) as image:assert image.size==(1920,1080)
    rows=[None]*61
    for row in actual:rows[row['index']]=row
    return rows,proof

def draw_target(draw,row,car_id,color='yellow',label=None,progress=1):
    car=next(x for x in row['cars'] if x['id']==car_id)
    if not car['intersectsViewport']:return False
    b=car['pixelTopLeftBounds'];sx,sy=VIEWPORT[2]/1920,VIEWPORT[3]/1080
    x0=max(5,b['x']*sx-8);y0=max(VIEWPORT[1]+5,VIEWPORT[1]+b['y']*sy-8)
    x1=min(W-5,(b['x']+b['width'])*sx+8);y1=min(VIEWPORT[1]+VIEWPORT[3]-5,VIEWPORT[1]+(b['y']+b['height'])*sy+8)
    if x1<=x0 or y1<=y0:return False
    points=[(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)]
    line(draw,points,progress,'bg',12);line(draw,points,progress,color,7)
    if label and progress>.9:
        tw=font(35,True).getlength(label);cx=max(50+tw/2,min(925-tw/2,(x0+x1)/2));cy=max(VIEWPORT[1]+38,y0-30)
        draw.rectangle((cx-tw/2-8,cy-25,cx+tw/2+8,cy+25),fill=COL['bg']);text(draw,(cx,cy),label,35,color,bold=True)
    return True
def offscreen_cue(draw,row):
    car=next(x for x in row['cars'] if x['id']=='left')
    if car['fullyInsideViewport']:return
    label='옆차가 시야 밖' if not car['intersectsViewport'] else '옆차 일부가 시야 밖'
    x,y=26,800;line(draw,[(x+105,y-46),(x,y),(x+105,y+46)],1,'green',9)
    text(draw,(64,VIEWPORT[1]+110),label,35,'green',anchor='lm',bold=True)

@lru_cache(maxsize=61)
def capture_image(index,folder_override=None):
    folder=Path(folder_override) if folder_override else ROOT/input_map()['capture']['frameDirectory']
    with Image.open(folder/f'frame-{index:03}.png') as image:return image.convert('RGB').resize((1080,608),Image.Resampling.LANCZOS)
def frame(t,rows=None,placeholder=False,folder_override=None):
    canvas=Image.new('RGB',(W,H),COL['bg']);d=ImageDraw.Draw(canvas);idx=source_index(t);state=beat_at(t)
    text(d,(64,88),'얌얌코딩',32,'muted',anchor='lm',bold=True)
    text(d,(64,185),'FOV를 넓혔더니',66,anchor='lm',bold=True)
    text(d,(64,274),'앞차가 작아졌다',74,'yellow',anchor='lm',bold=True)
    text(d,(64,347),'시야각(Field of View, FOV) = 카메라가 담는 각도',30,'muted',anchor='lm')
    hfov=60+40*idx/60;text(d,(64,399),f'가로 시야각(hFOV) {hfov:.0f}°',41,'blue' if idx>30 else 'yellow',anchor='lm',bold=True)
    if rows is not None and not placeholder:
        canvas.paste(capture_image(idx,folder_override),(0,VIEWPORT[1]));d=ImageDraw.Draw(canvas)
        focus=state['focus'];row=rows[idx]
        if focus in ['center','comparison','center-and-surroundings']:
            draw_target(d,row,'center','blue' if idx>30 else 'yellow','같은 앞차',ease((t-state['start'])/.22))
        if focus=='comparison':
            draw_target(d,rows[0],'center','yellow',None)
        if focus=='center-and-surroundings' or (focus=='surroundings-after5.62' and t>=5.62):
            draw_target(d,row,'left','green','주변 차량',ease((t-max(5.62,state['start']))/.45))
        if focus=='offscreen' or (focus=='offscreen-after15.26' and t>=15.26):offscreen_cue(d,row)
    else:
        d.rectangle((0,VIEWPORT[1],1079,VIEWPORT[1]+607),outline=COL['line'] if 'line' in COL else COL['muted'],width=2)
        text(d,(510,720),'레이아웃 검토용 · Unity 실제 캡처 대기',39,'muted',bold=True)
    text(d,(64,1084),'Unity 직접 시연 · 같은 위치 · 같은 거리',30,'muted',anchor='lm')
    if t<2.8:
        text(d,(510,1151),'시야각 하나만 바꿨습니다',46,bold=True)
        if t>=1.8:
            text(d,(280,1220),'노랑: 60° 때 크기',34,'yellow',bold=True)
            text(d,(740,1220),'파랑: 100° 때 크기',34,'blue',bold=True)
    elif t<8.36:
        text(d,(510,1160),'넓게 담으면, 주변이 더 보입니다',43,'green',bold=True)
    elif t<12.7:
        text(d,(510,1132),'원근 카메라: 가까운 것은 크게, 먼 것은 작게',35,bold=True)
        text(d,(510,1210),'이번엔 거리 고정, 시야각만 변경',39,'yellow',bold=True)
    elif t<18.06:
        text(d,(510,1144),'앞차는 커지고',44,'yellow',bold=True)
        text(d,(510,1213),'주변에서 보이는 범위는 줄어듭니다',39,'green',bold=True)
    elif t<23.88:
        text(d,(510,1160),'주변 범위와 앞차 크기를 함께 확인',42,bold=True)
    else:
        text(d,(260,1140),'주변 범위',46,'green',bold=True);double_arrow(d,423,574,1140)
        text(d,(760,1140),'중앙 대상 크기',43,'yellow',bold=True)
        text(d,(510,1220),'넓게 보면, 같은 앞차는 작아집니다',41,bold=True)
    return canvas

def sample_layout(folder=None):
    """Few stills from the actual two Unity endpoint captures; never a video render."""
    check_design();folder=Path(folder).resolve() if folder else ROOT/input_map()['capture']['frameDirectory']
    assert folder.is_relative_to(OUT.resolve()),'Preview captures must belong to this selected project local directory.'
    rows,proof=capture_inputs(require_all=False,folder_override=folder);assert rows is not None
    result=[];captions=read(PROJECT/'script/captions.json')['cues'];target=OUT/'capture-layout-samples';target.mkdir(parents=True,exist_ok=True)
    for t in [.4,1.2,2.2,6.2,10.2,16.0,25.0]:
        image=frame(t,rows,folder_override=str(folder));d=ImageDraw.Draw(image)
        cue=next((c for c in captions if c['start']<=t<c['end']),None)
        if cue:
            lines=wrapped(cue['ko']);width=max(font(60).getlength(x) for x in lines)+44;height=len(lines)*78+26;x,y=510-width/2,1380-height/2
            d.rectangle((x+12,y+12,x+width+12,y+height+12),fill=COL['forest']);d.rectangle((x,y,x+width,y+height),fill='white',outline='#161B18',width=3)
            for j,value in enumerate(lines):text(d,(510,1380+(j-(len(lines)-1)/2)*78),value,60,fill='#080B09')
        native=target/f'sample-{t:04.1f}.png';mobile=target/f'sample-{t:04.1f}-375.jpg';image.save(native);image.resize((375,667),Image.Resampling.LANCZOS).save(mobile,quality=94)
        result.append(dict(seconds=t,sourceIndex=source_index(t),native=rel(native),mobile=rel(mobile)))
    receipt=dict(actualUnityEndpoints=True,projection=rel(proof),projectionSha256=sha(proof),samples=result,captionMethod='Pillow layout sample only; exact ASS encoded pixels still pending',pixelReview='pending',videoRenderJobsStarted=0)
    write(target/'samples.json',receipt);return receipt

def check_render_authorization():
    c=read(ROOT/'shared/publishing/video-production-control.json')
    assert SLUG in [c.get('selectedVideo'),c.get('selectedDelivery',{}).get('slug'),c.get('shortsRecurringAuthorization',{}).get('selectedShort')],'Parent selection is required before a media job.'
    source=read(PROJECT/'sources/source-map.json');assert source['visual']['commercialGameplayIncluded'] is False and source['visual']['onlyChangedVariable']=='horizontal camera FOV'
    return source

def render_visual():
    check_render_authorization();check_design();rows,proof=capture_inputs();spec=input_map()['capture'];folder=ROOT/spec['frameDirectory']
    inputs=[dict(index=i,path=rel(folder/f'frame-{i:03}.png'),sha256=sha(folder/f'frame-{i:03}.png')) for i in range(61)]
    signature=dict(code=sha(__file__),captions=sha(PROJECT/'script/captions.json'),projection=sha(proof),captureFrames=inputs,frames=FRAMES,viewport=VIEWPORT,fonts=[sha(FONTFILE),sha(BOLDFONT)])
    target=OUT/'portrait-visual.mp4';receipt=OUT/'visual-build.json'
    if receipt.exists() and target.exists():
        old=read(receipt)
        if old.get('signature')==signature and old.get('sha256')==sha(target):return target
        raise RuntimeError('Preserve the earlier revision before rebuilding changed visual inputs.')
    args=[FFMPEG,'-hide_banner','-loglevel','warning','-n','-f','rawvideo','-pix_fmt','rgb24','-video_size','1080x1920','-framerate','60','-i','pipe:0','-an','-frames:v',str(FRAMES),'-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-fps_mode','cfr','-video_track_timescale','15360','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-movflags','+faststart',str(target)]
    log=OUT/'visual-render.log'
    with log.open('wb') as stderr:
        process=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=stderr)
        try:
            for i in range(FRAMES):process.stdin.write(frame(i/FPS,rows).tobytes())
            process.stdin.close();code=process.wait()
        except BaseException:
            if process.stdin and not process.stdin.closed:process.stdin.close()
            process.terminate();process.wait();raise
    if code:raise RuntimeError(log.read_text(errors='replace')[-8000:])
    report=dict(signature=signature,path=rel(target),sha256=sha(target),frames=FRAMES,sourceAudio=False,commercialGameplayIncluded=False,unityActualProjectionReceipt=rel(proof),onlyChangedSceneVariable='horizontal FOV',cameraAndCarsFixed=True,editorialMarkers='Hollow editorial guides based on actual projected MeshRenderer bounds; not CV detections.',pixelReview='pending')
    write(receipt,report);return target
def mux_pair():
    check_render_authorization();visual=OUT/'portrait-visual.mp4';audio=OUT/'final-mix.m4a';assert visual.exists() and audio.exists()
    signature=dict(visual=sha(visual),audio=sha(audio),ass=sha(OUT/'captions.ko.ass'),code=sha(__file__));receipt=OUT/'pair-build.json'
    if receipt.exists():
        old=read(receipt)
        if old.get('signature')==signature and all((ROOT/x['path']).exists() and sha(ROOT/x['path'])==x['sha256'] for x in old['files']):return old
        raise RuntimeError('Preserve the earlier encoded pair before a changed revision.')
    files=[]
    for kind in ['clean','captioned']:
        target=OUT/f'{SLUG}.{kind}.mp4';args=[FFMPEG,'-v','warning','-n','-i',str(visual),'-i',str(audio),'-map','0:v:0','-map','1:a:0']
        if kind=='clean':args+=['-c:v','copy']
        else:args+=['-vf',f"ass=filename='{rel(OUT/'captions.ko.ass')}'",'-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-fps_mode','cfr']
        args+=['-c:a','copy','-t','30','-movflags','+faststart','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv',str(target)]
        run(args,cwd=ROOT);files.append(dict(path=rel(target),sha256=sha(target),bytes=target.stat().st_size))
    report=dict(signature=signature,files=files,finalIntegrity='pending',actualCaptionPixels='pending',humanFinalReview='pending');write(receipt,report);return report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--check',action='store_true');parser.add_argument('--sample',action='store_true');parser.add_argument('--preview-dir');parser.add_argument('--render',action='store_true');parser.add_argument('--pair',action='store_true');args=parser.parse_args()
    if not any(vars(args).values()):parser.error('Explicit --prepare/--render/--pair required; importing starts no work.')
    if args.prepare or args.check:
        report=check_design();sample=frame(10,placeholder=True);sample.save(OUT/'layout-preflight.png');report['layoutSample']='placeholder-only-not-capture-approval';print(json.dumps(report))
    if args.sample:print(json.dumps(sample_layout(args.preview_dir)))
    if args.render:print(render_visual())
    if args.pair:print(json.dumps(mux_pair()))
if __name__=='__main__':main()

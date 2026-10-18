"""Finite native portrait edit. --check/--prepare never render video or audio.

The parent task owns the handoff for --render. It must finish the current
source/rights inventory before this code is allowed to consume a media source.
Only this project directory receives generated files.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re, subprocess, sys
from pathlib import Path
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
OUT = PROJECT / 'production/local'
SLUG = PROJECT.name
FFBIN = Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin')
FFMPEG, FFPROBE = str(FFBIN/'ffmpeg.exe'), str(FFBIN/'ffprobe.exe')
W, H, FPS, FRAMES = 1080, 1920, 60, 1812
DURATION, VIDEO_END, VOICE_END = FRAMES/FPS, 13.5, 30.1
COL = dict(bg='#080B09', white='#FFFFFF', yellow='#FFD25A', blue='#70C4FF', muted='#B8C3BC', line='#68746A', forest='#073C32')
FONTFILE = 'C:/Windows/Fonts/malgun.ttf'
BOLDFONT = 'C:/Windows/Fonts/malgunbd.ttf'
CAPTION_WIDTH, CAPTION_X, CAPTION_Y, CAPTION_SIZE = 796, 510, 1380, 60

def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path, data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
def rel(path): return Path(path).relative_to(ROOT).as_posix()
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def run(args, **kw):
    result=subprocess.run(args, capture_output=True, check=False, **kw)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors='replace')[-12000:])
    return result
@lru_cache(maxsize=32)
def font(size, bold=False):return ImageFont.truetype(BOLDFONT if bold else FONTFILE,size)
def text(draw, at, value, size, fill='white', anchor='mm', bold=False, stroke=0):
    draw.text(at,value,font=font(size,bold),fill=COL.get(fill,fill),anchor=anchor,stroke_width=stroke,stroke_fill=COL['bg'])
def ease(value):
    x=max(0,min(1,value));return x*x*(3-2*x)
def line(draw, points, progress, color, width=10):
    """Trace a real editorial relationship, not a fabricated detector result."""
    if progress<=0:return
    lengths=[math.dist(a,b) for a,b in zip(points,points[1:])]
    left=sum(lengths)*min(1,progress);partial=[points[0]]
    for a,b,length in zip(points,points[1:],lengths):
        if left>=length:partial.append(b);left-=length
        else:
            if length:partial.append((a[0]+(b[0]-a[0])*left/length,a[1]+(b[1]-a[1])*left/length))
            break
    if len(partial)>1:draw.line(partial,fill=COL.get(color,color),width=width,joint='curve')
def arrow(draw, start, end, progress, color='yellow', width=10):
    p=max(0,min(1,progress));tip=(start[0]+(end[0]-start[0])*p,start[1]+(end[1]-start[1])*p)
    line(draw,[start,end],p,color,width)
    if p>.05:
        ang=math.atan2(end[1]-start[1],end[0]-start[0]);length=22
        pts=[tip,(tip[0]-length*math.cos(ang-.48),tip[1]-length*math.sin(ang-.48)),(tip[0]-length*math.cos(ang+.48),tip[1]-length*math.sin(ang+.48))]
        draw.polygon(pts,fill=COL[color])
def bag(draw, cx, cy, size=150, color='yellow'):
    """Recognizable authored backpack: handle, two straps, flap and front pocket."""
    c=COL[color];s=size/150
    def box(coords):return tuple(v*s+(cx if i%2==0 else cy) for i,v in enumerate(coords))
    draw.arc(box((-39,-115,39,-37)),180,360,fill=c,width=max(4,round(10*s)))
    for side in [-1,1]:
        draw.rounded_rectangle(box((side*76-12,-62,side*76+12,90)),radius=10*s,outline=c,width=max(3,round(7*s)))
    draw.rounded_rectangle(box((-72,-84,72,102)),radius=24*s,outline=c,width=max(4,round(9*s)))
    draw.line([tuple((cx-66*s,cy-25*s)),tuple((cx+66*s,cy-25*s))],fill=c,width=max(3,round(6*s)))
    draw.rounded_rectangle(box((-46,16,46,76)),radius=10*s,outline=c,width=max(3,round(6*s)))
    draw.line([(cx,cy-37*s),(cx,cy-8*s)],fill=c,width=max(3,round(7*s)))
def coin(draw,cx,cy,radius=34,color='yellow'):
    c=COL[color];draw.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),outline=c,width=6)
    text(draw,(cx,cy),'G',radius+5,fill=color,bold=True)
def wrapped(value,size=CAPTION_SIZE,maxwidth=CAPTION_WIDTH):
    value=' '.join(value.replace('\n',' ').split());f=font(size)
    if f.getlength(value)<=maxwidth:return [value]
    words=value.split();choices=[]
    for i in range(1,len(words)):
        parts=[' '.join(words[:i]),' '.join(words[i:])]
        if max(f.getlength(x) for x in parts)<=maxwidth:choices.append(parts)
    if not choices:raise ValueError('Split this cue at an existing ASR word boundary; do not shrink font: '+value)
    return min(choices,key=lambda ls:abs(f.getlength(ls[0])-f.getlength(ls[1])))
def timestamp(seconds,ass=False):
    scale=100 if ass else 1000;n=round(seconds*scale);h,n=divmod(n,3600*scale);m,n=divmod(n,60*scale);s,frac=divmod(n,scale)
    return f'{h}:{m:02}:{s:02}.{frac:02}' if ass else f'{h:02}:{m:02}:{s:02},{frac:03}'
def polygon(x,y,w,h):return f'm {x:.2f} {y:.2f} l {x+w:.2f} {y:.2f} {x+w:.2f} {y+h:.2f} {x:.2f} {y+h:.2f}'

def make_captions():
    spec=read(PROJECT/'script/captions.json');rows=spec['cues'];events=[];layout=[]
    assert spec['timingSource']=='existing-approved-source-asr-word-boundaries'
    previous=0
    for i,row in enumerate(rows,1):
        a,b=row['start'],row['end'];assert a>=previous-.001 and b>a and b<=29.98+.001;previous=b
        for lang in ['ko','en']:wrapped(row[lang])
        lines=wrapped(row['ko']);width=max(font(60).getlength(s) for s in lines)+44;h=len(lines)*78+26
        x,y=CAPTION_X-width/2,CAPTION_Y-h/2
        assert width<=840 and x>=80 and x+width<=930 and y+h+14<1560
        when=f'{timestamp(a,True)},{timestamp(b,True)}'
        events.extend([
            f'Dialogue: 10,{when},Box,,0,0,0,,{{\\an7\\pos(0,0)\\bord0\\1c&H323C07&\\p1}}'+polygon(x+12,y+12,width,h),
            f'Dialogue: 11,{when},Box,,0,0,0,,{{\\an7\\pos(0,0)\\p1}}'+polygon(x,y,width,h),
        ])
        for j,value in enumerate(lines):
            events.append(f'Dialogue: 12,{when},Text,,0,0,0,,{{\\an5\\pos({CAPTION_X},{CAPTION_Y+(j-(len(lines)-1)/2)*78:.2f})}}'+value.replace('{','').replace('}',''))
        layout.append(dict(cue=i,start=a,end=b,lines=lines,textWidths=[font(60).getlength(s) for s in lines],box=[x,y,width,h],center=[CAPTION_X,CAPTION_Y],font=60))
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
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'captions.ko.ass').write_text(header+'\n'.join(events)+'\n',encoding='utf8')
    for lang in ['ko','en']:
        blocks=[f'{i}\n{timestamp(row["start"])} --> {timestamp(row["end"])}\n'+ '\n'.join(wrapped(row[lang])) for i,row in enumerate(rows,1)]
        (OUT/f'captions.{lang}.srt').write_text('\n\n'.join(blocks)+'\n',encoding='utf8')
    write(OUT/'caption-layout.json',dict(rows=layout,width=W,height=H,fps=FPS,fontFile=FONTFILE,requestedTextWidth=850,effectiveTextWidth=CAPTION_WIDTH,position=[CAPTION_X,CAPTION_Y],maxLines=2,editorialSafeMargins=dict(right=150,bottom=360),platformUiPixelVerification='pending',inputSha256=sha(PROJECT/'script/captions.json')))
    return layout

def check_design():
    m=read(PROJECT/'project.json');assert m['format']==dict(type='youtube-shorts',width=W,height=H,fps=FPS,frames=FRAMES,seconds=DURATION)
    source=read(PROJECT/'sources/source-map.json');assert source['videoUse']['out']==VIDEO_END and source['videoUse']['audio'] is False
    assert source['narration']['out']==VOICE_END and source['narration']['postSilenceSeconds']==.1
    assert font(62,True).getlength('딱 300골드가 부족하다면?')<=890
    assert font(62,True).getlength('2,000 − 1,700 = 300')<=900
    assert FRAMES==round(DURATION*FPS) and VOICE_END<DURATION
    source_words=read(ROOT/source['narration']['wordEvidence'])
    assert 'words' in source_words and sha(ROOT/source['narration']['wordEvidence'])==source['narration']['wordEvidenceSha256']
    cues=read(PROJECT/'script/captions.json')['cues']
    def normalized(value):
        for written,spoken in [('2,000','이천'),('1,700','천칠백'),('300','삼백')]:value=value.replace(written,spoken)
        return re.sub(r'[^가-힣A-Za-z0-9]','',value)
    assert normalized(' '.join(x['ko'] for x in cues))==normalized((PROJECT/'script/narration.ko.txt').read_text(encoding='utf8')),'Portrait cues must retain all four approved paragraphs.'
    starts=[float(x['timestamp'][0]) for x in source_words['words'] if x.get('timestamp') and x['timestamp'][0] is not None]
    ends=[float(x['timestamp'][1]) for x in source_words['words'] if x.get('timestamp') and x['timestamp'][1] is not None]
    for cue in cues:
        assert min(abs(cue['start']-x) for x in starts)<=.021,('Caption start lacks original word evidence',cue['id'])
        assert min(abs(cue['end']-x) for x in ends)<=.021,('Caption end lacks original word evidence',cue['id'])
    layout=make_captions()
    report=dict(status='passed-code-and-font-layout-only',frames=FRAMES,duration=DURATION,cues=len(layout),maximumCaptionWidth=max(max(x['textWidths']) for x in layout),fixedCaptionCenter=[CAPTION_X,CAPTION_Y],meaningfulContentBottom=1510,allFourOriginalParagraphsRetained=True,existingWordBoundaryTimingVerified=True,mediaJobsStarted=0,actualPixelApproval=False,humanListening=False)
    write(OUT/'code-preflight.json',report);return report

def frame(t):
    image=Image.new('RGB',(W,H),COL['bg']);d=ImageDraw.Draw(image)
    text(d,(64,92),'얌얌코딩',34,fill='muted',anchor='lm',bold=True)
    text(d,(64,203),'게임을 끄려는데',62,anchor='lm',bold=True)
    text(d,(64,289),'딱 300골드가 부족하다면?',62,fill='yellow',anchor='lm',bold=True)
    # The top field is overwritten only by the allowed actual video interval.
    if t<VIDEO_END:
        text(d,(64,365),'상황 예시',32,fill='muted',anchor='lm')
        text(d,(64,945),'Stardew Valley · SwenAL',30,fill='muted',anchor='lm')
        text(d,(64,1003),'설명용 가정 · 실제 HUD 값 아님',32,fill='muted',anchor='lm')
        if t>=1.74:
            bag(d,156,1178,70)
            text(d,(300,1138),'다음 가방까지',44,anchor='lm',bold=True)
            text(d,(300,1220),'300골드',70,fill='yellow',anchor='lm',bold=True)
            if t>=7.6:
                arrow(d,(740,1238),(740,1136),ease((t-7.6)/.65),width=8)
                text(d,(825,1188),'조금만 더',32,fill='yellow')
        return image
    # Self-authored numeric illustration; never overlaid onto or passed as HUD.
    text(d,(64,438),'설명용 가정 · 실제 HUD 값 아님',32,fill='muted',anchor='lm')
    bag(d,780,653,111)
    text(d,(780,803),'첫 가방 확장',40,bold=True)
    text(d,(780,862),'2,000골드',56,fill='yellow',bold=True)
    if t>=16.34:
        coin(d,265,590,42,'blue')
        text(d,(265,684),'현재',38,fill='blue',bold=True)
        text(d,(265,750),'1,700골드',56,fill='blue',bold=True)
        arrow(d,(430,680),(585,680),ease((t-16.34)/.65),'white',9)
    if t>=18.44:
        text(d,(510,962),'2,000 − 1,700 = 300',62,fill='yellow',bold=True)
    # One continuous current -> remainder -> goal relationship, not a UI mock.
    left,right,y=100,900,1124
    if t<16.34:
        text(d,(510,1124),'목표를 먼저 확인합니다',47,bold=True)
    else:
        d.line([(left,y),(right,y)],fill=COL['line'],width=14)
        current_x=left+(right-left)*.85
        d.line([(left,y),(current_x,y)],fill=COL['blue'],width=14)
        for x,color in [(left,'blue'),(current_x,'blue'),(right,'yellow')]:
            d.ellipse((x-10,y-10,x+10,y+10),fill=COL[color])
        text(d,(left,y+55),'현재1,700',34,fill='blue',anchor='lm',bold=True)
        text(d,(right,y+55),'목표2,000',34,fill='yellow',anchor='rm',bold=True)
        if t>=18.44:
            line(d,[(current_x,y-22),(current_x,y-52),(right,y-52),(right,y-22)],ease((t-18.44)/.6),'yellow',8)
        if 20.06<=t<25.88:text(d,(510,1240),'남은 300골드',62,fill='yellow',bold=True)
    if t>=22.4:
        # The final statement inherits exactly the same reward and distance.
        text(d,(510,350),'보상의 크기보다',36,fill='muted',bold=True)
        if t>=25.88:
            text(d,(510,1240),'목표와 남은 거리가 보인다',46,fill='yellow',bold=True)
    return image

def check_render_authorization():
    control=read(ROOT/'shared/publishing/video-production-control.json')
    selected=[control.get('selectedVideo'),control.get('selectedDelivery',{}).get('slug'),control.get('shortsProduction',{}).get('selectedVideo'),control.get('shortsRecurringAuthorization',{}).get('selectedShort')]
    assert SLUG in selected,'Parent must record selected short in the existing control before a costly job.'
    proof=read(PROJECT/'sources/current-source-review.json')
    assert proof.get('first13_5SecondsDirectlyViewed') and proof.get('nativeFhdSourceVerified') and proof.get('noLowResolutionPurchaseCutIncluded')
    src=ROOT/read(PROJECT/'sources/source-map.json')['sourceMaster']
    assert proof['masterSha256']==sha(src),'Source proof is stale.'
    return src,proof

def render_visual():
    source,proof=check_render_authorization();check_design()
    target=OUT/'portrait-visual.mp4';signature=dict(code=sha(__file__),captions=sha(PROJECT/'script/captions.json'),source=proof['masterSha256'],frames=FRAMES,videoEnd=VIDEO_END,fonts=[sha(FONTFILE),sha(BOLDFONT)])
    receipt=OUT/'visual-build.json'
    if receipt.exists() and target.exists():
        old=read(receipt)
        if old.get('signature')==signature and old.get('sha256')==sha(target):return target
        raise RuntimeError('Existing visual revision differs; preserve it under a distinct revision before rendering.')
    graph=f'[1:v]trim=start=0:end={VIDEO_END},setpts=PTS-STARTPTS,crop=1920:888:0:95,scale=1080:500:force_original_aspect_ratio=decrease:force_divisible_by=2,pad=1080:500:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=60[game];[0:v][game]overlay=0:400:enable=\'lt(t,{VIDEO_END})\':eof_action=pass:shortest=0,format=yuv420p[v]'
    args=[FFMPEG,'-hide_banner','-loglevel','warning','-n','-f','rawvideo','-pix_fmt','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','pipe:0','-t',str(VIDEO_END),'-i',str(source),'-filter_complex',graph,'-map','[v]','-an','-frames:v',str(FRAMES),'-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-fps_mode','cfr','-video_track_timescale','15360','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-movflags','+faststart',str(target)]
    log=OUT/'visual-render.log'
    with log.open('wb') as stderr:
        process=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=stderr)
        try:
            for index in range(FRAMES):process.stdin.write(frame(index/FPS).tobytes())
            process.stdin.close();code=process.wait()
        except BaseException:
            if process.stdin and not process.stdin.closed:process.stdin.close()
            process.terminate();process.wait();raise
    if code:raise RuntimeError(log.read_text(errors='replace')[-8000:])
    write(receipt,dict(signature=signature,path=rel(target),sha256=sha(target),sourceAllowedSeconds=[0,VIDEO_END],sourceAudio=False,frames=FRAMES,pixelReview='pending'))
    return target

def mux_pair():
    check_render_authorization();visual=OUT/'portrait-visual.mp4';audio=OUT/'final-mix.m4a'
    assert visual.exists() and audio.exists(),'Render visual and build the finite audio before muxing.'
    receipt=OUT/'pair-build.json';signature=dict(visual=sha(visual),audio=sha(audio),ass=sha(OUT/'captions.ko.ass'),code=sha(__file__))
    if receipt.exists():
        old=read(receipt)
        if old.get('signature')==signature and all((ROOT/x['path']).exists() and sha(ROOT/x['path'])==x['sha256'] for x in old['files']):return old
        raise RuntimeError('Existing encoded pair differs; preserve the revision before rebuilding.')
    files=[]
    for kind in ['clean','captioned']:
        target=OUT/f'{SLUG}.{kind}.mp4';args=[FFMPEG,'-v','warning','-n','-i',str(visual),'-i',str(audio),'-map','0:v:0','-map','1:a:0']
        if kind=='clean':args+=['-c:v','copy']
        else:
            # Relative filter path avoids Windows drive-colon escaping.
            ass=rel(OUT/'captions.ko.ass');args+=['-vf',f"ass=filename='{ass}'",'-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-fps_mode','cfr']
        args+=['-c:a','copy','-t',str(DURATION),'-movflags','+faststart','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv',str(target)]
        run(args,cwd=ROOT);files.append(dict(path=rel(target),sha256=sha(target),bytes=target.stat().st_size))
    report=dict(signature=signature,files=files,finalIntegrity='pending',actualCaptionPixels='pending',humanFinalReview='pending');write(receipt,report);return report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--prepare',action='store_true');parser.add_argument('--render',action='store_true');parser.add_argument('--pair',action='store_true');args=parser.parse_args()
    if not any(vars(args).values()):parser.error('Choose --check/--prepare, --render or --pair explicitly; nothing runs on import.')
    if args.check or args.prepare:print(json.dumps(check_design(),ensure_ascii=False))
    if args.render:print(render_visual())
    if args.pair:print(json.dumps(mux_pair(),ensure_ascii=False))
if __name__=='__main__':main()

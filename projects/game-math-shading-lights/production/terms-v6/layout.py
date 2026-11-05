"""Generate lossless, speech-timed title and formula layers in the 1920 × 1080 edit space."""
import functools
import re
from pathlib import Path
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import mathtext
from matplotlib.font_manager import FontProperties
from PIL import Image, ImageDraw, ImageFont
from notation import PAIRS, TITLES
from voice import PROJECT, WORK, read

GOLD='#ffd173';WHITE='#f6f4ee';MUTED='#c1cac8';CYAN='#8ae5ed';GREEN='#a6e7bc'
HERO={1,2,3,4,7,8,9,10,11,16,17,20,51,55}
CUES={int(p.stem):read(p) for p in (WORK.parent/'render-v2/cues').glob('???.json')}
TITLES={s:TITLES.get(s,(c['termEnglish'],c['termKorean'])) for s,c in CUES.items()}
FONT=Path('C:/Windows/Fonts')
@functools.lru_cache(None)
def font(size,bold=False,mono=False):
    return ImageFont.truetype(str(FONT/('consola.ttf' if mono else 'malgunbd.ttf' if bold else 'malgun.ttf')),size)
def fit(text,width,preferred,minsize,bold=False,mono=False):
    for size in range(preferred,minsize-1,-1):
        face=font(size,bold,mono)
        if face.getlength(text)<=width:return face
    raise ValueError(f'Text too wide at {minsize}px: {text}')
@functools.lru_cache(None)
def equation(s):
    # Rasterize the mathematical glyphs and fraction bars with the same vector font on every machine.
    # Use the glyph coverage directly so the mathematical typesetting has a transparent background.
    parser=mathtext.MathTextParser('agg')
    with mpl.rc_context({'mathtext.fontset':'stix','mathtext.default':'it'}):
        parsed=parser.parse('$'+s+'$',dpi=130,prop=FontProperties(size=65))
    import numpy as np
    alpha=Image.fromarray(np.asarray(parsed.image).astype('uint8'),'L');bounds=alpha.getbbox()
    if not bounds: raise ValueError(s)
    alpha=alpha.crop(bounds); ratio=min(1.,822/alpha.width,128/alpha.height)
    alpha=alpha.resize((max(1,round(alpha.width*ratio)),max(1,round(alpha.height*ratio))),Image.Resampling.LANCZOS)
    out=Image.new('RGBA',alpha.size,WHITE);out.putalpha(alpha);return out
def code_line(d,xy,line):
    face=fit(line,842,44,34,mono=True);x,y=xy
    for token in re.findall(r'\s+|[A-Za-z_]\w*|\d+(?:\.\d+)?|.',line):
        color=CYAN if token in {'pow','dot','max','length','saturate','normalize','reflect','shade','gobo','falloff'} else GOLD if token[:1].isdigit() or token=='PI' else WHITE
        d.text((x,y),token,font=face,fill=color,anchor='lm');x+=face.getlength(token)
def note_text(d,xy,note,color):
    face=fit(note,842,40,29);x,y=xy
    for token in re.split(r'([−⊙⊥ᵢₒₛ⅓¼Φρπωθ])',note):
        if not token:continue
        substitute=ImageFont.truetype(str(FONT/'segoeui.ttf'),face.size) if token in {'−','ᵢ','ₒ','ₛ'} else face
        d.text((x,y),token,font=substitute,fill=color,anchor='ls');x+=substitute.getlength(token)
def head(d,s,ink):
    en,ko=TITLES[s];w=1225
    a=fit(en+'  ('+ko+')',w,58,33,True)
    start=93;d.text((start,84),en,font=a,fill=GOLD,anchor='lm')
    ko_face=font(max(34,a.size-4))
    d.text((start+a.getlength(en+'  '),84),'('+ko+')',font=ko_face,fill=WHITE,anchor='lm')
    if s in HERO:
        # The simple Korean question / purpose remains next to the canonical name.
        meaning=CUES[s].get('plainMeaning','')
        d.text((95,143),meaning,font=fit(meaning,1180,32,28),fill=MUTED,anchor='lm')
def selected_steps(s,c):
    pair=PAIRS[s]; cue=CUES[s]; original=[t for t in cue.get('stepTimes',[]) if c['sourceIn']<=t<c['sourceIn']+c['frames']/60]
    special={9:[0,5.1,9.1,12.55],10:[0,4.3,6.7,9.2,12.6],11:[0,3.2,6.6],16:[0,5,15],17:[0,6.2,13],20:[0,4.8,6.95,16.5],55:[0,5.4,12.4,17.0],56:[0,6.1,12.7]}
    if s in special:marks=special[s]
    elif len(original)>=len(pair.notes):
        marks=original[:len(pair.notes)]
    else:
        from delivery import AL
        speech=[a['start']-c['globalStartFrame']/60+c['sourceIn'] for a in AL['ko'] if int(a['scene'])==s and c['globalStartFrame']/60<=a['start']< (c['globalStartFrame']+c['frames'])/60]
        marks=[speech[round(i*(len(speech)-1)/max(1,len(pair.notes)-1))] for i in range(len(pair.notes))] if speech else [c['sourceIn']]
    return [max(0,round((t-c['sourceIn'])*60)) for t in marks]
def overlays(c):
    sid=int(c['scene']);pair=PAIRS.get(sid);end=c['frames'];first=c['sourceIn'];steps=selected_steps(sid,c) if pair else []
    eq=max(0,round(((max(pair.onset,7.58) if sid==54 else pair.onset)-first)*60)) if pair else 0
    code=min(end-1,eq+60)
    keys=sorted({k for k in [0,eq,code,*steps] if 0<=k<end});states=[]
    for n,k in enumerate(keys):
        canvas=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(canvas)
        ink='#080b0e' if sid in HERO or sid==78 else '#000000'
        # Keep the source-kind chip and the source image outside the old title's bounds.
        d.rectangle((0,0,1340,169),fill=ink);head(d,sid,ink)
        if pair:
            # Left geometry/animated rays and the fixed caption band have no overlap with this region.
            d.rectangle((980,222,1919,901),fill=ink)
            if k<eq:
                if sid==54:
                    d.text((1020,260),'Radiant Flux (복사속)',font=font(45,True),fill=GOLD)
                    flux=equation(r'\Phi=\frac{\mathrm{d}Q}{\mathrm{d}t}')
                    canvas.alpha_composite(flux,(1020,378))
                    d.text((1020,594),'단위 시간에 방출하는 에너지 · W',font=font(40),fill=WHITE)
                else:d.text((1020,280),CUES[sid]['plainMeaning'],font=fit(CUES[sid]['plainMeaning'],838,43,28,True),fill=WHITE)
            else:
                d.text((1155 if sid==55 else 1096 if sid in HERO else 1020,244),'수학식',font=font(34,True),fill=GOLD)
                math_image=equation(pair.equation);canvas.alpha_composite(math_image,(1020,330+(130-math_image.height)//2))
                if k>=code:
                    d.line((1022,488,1860,488),fill='#34403f',width=2)
                    d.text((1020,510),'코드 · 의사 코드',font=font(31,True),fill=CYAN)
                    for j,line in enumerate(pair.code):code_line(d,(1020,594+j*49),line)
                prefix=sum(t<=k for t in steps)
                lines=pair.notes[max(0,prefix-2):prefix]
                for j,note in enumerate(lines):
                    note_text(d,(1020,746+59*j),note,WHITE if j==len(lines)-1 else MUTED)
            if sid==55:d.rectangle((980,222,1139,334),fill=(0,0,0,0))
            elif sid in HERO:d.rectangle((980,222,1068,295),fill=(0,0,0,0))
        if sid==37:
            d.rectangle((120,661,1810,853),fill=ink)
            for x,en,ko,stage in [(555,'Flat','플랫','면에서 계산'),(940,'Gouraud','구로','정점에서 계산'),(1325,'Phong','퐁','픽셀에서 계산')]:
                line=en+' ('+ko+')';d.text((x,716),line,font=font(42,True),fill=WHITE,anchor='mm')
                d.text((x,776),stage,font=font(36),fill=MUTED,anchor='mm')
        subheads={1:'Studio Lighting (스튜디오 조명)',3:'Light Path (빛의 경로)',4:'Light Source (광원)',7:'View Direction (시선 방향)',8:'Surface Vectors (표면 벡터)',51:'Parallel Rays (평행 광선)',19:'Incidence Angle (입사각)',47:'Light Path (빛의 경로)',60:'Light Volume (광원 영향 영역)',63:'Light Space (광원 좌표 공간)',67:'Light Space (광원 좌표 공간)',68:'Light Volume (광원 영향 영역)',24:'Indirect Light (간접광)',35:'Fresnel / Retroreflection (프레넬 / 재귀반사)',36:'Anisotropy (비등방성)',73:'SH Basis (구면 조화 기저)',77:'Environment Filtering (환경 필터링)',70:'Lightmap UV (라이트맵 UV)',71:'Vertex Lighting (정점 조명)'}
        if sid in subheads:
            x,y,w,h=(1180,284,716,62) if sid in HERO else (1030,282,845,76) if sid in {24,35,36,73,77} else (1032,298,844,84)
            d.rectangle((x,y,x+w,y+h),fill=ink)
            label=subheads[sid];d.text((x+6,y+6),label,font=fit(label,w-12,42,29,True),fill=GOLD)
        if sid==2:
            d.rectangle((1180,229,1919,351),fill=ink)
            d.text((1189,254),'Bidirectional Reflectance',font=font(42,True),fill=GOLD)
            d.text((1189,307),'Distribution Function',font=font(42,True),fill=GOLD)
        folder=WORK/'layers'/c['scene'];folder.mkdir(parents=True,exist_ok=True)
        dest=folder/f'{k:06}.png';canvas.save(dest,compress_level=2);states.append((k,dest))
    return states

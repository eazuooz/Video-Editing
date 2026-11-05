"""Compose editorial overlays over the existing shader/camera scenes without covering fixed captions."""
import math,re
from threading import Lock
from PIL import Image,ImageDraw
from common import WORK,BASE,VOICE,read,v6
from layout import font,fit,equation,code_line,note_text
from teaching import BOARDS,EXTRA
from samples import DEMOS

GOLD='#ffd173';MINT='#9ee5cf';WHITE='#f6f4ee';MUTED='#c1cac8';DARK='#080b0e'
MATH_RENDER_LOCK=Lock()
def line(d,xy,s,size=41,w=848,color=WHITE,bold=False):
    f=fit(s,w,size,min(size,29),bold);x,y=xy
    for run in re.split(r'([−ᵢⱼₑₛₒₐₗᵦ⊥])',s):
        if not run:continue
        from PIL import ImageFont
        real=ImageFont.truetype('C:/Windows/Fonts/cambria.ttc',f.size) if len(run)==1 and run in '−ᵢⱼₑₛₒₐₗᵦ⊥' else f
        d.text((x,y+f.size*.82),run,font=real,fill=color,anchor='ls');x+=real.getlength(run)
def maths(canvas,eq,x,y,maxw=825,maxh=101):
    # Matplotlib shares a mutable MathText parser between threads.
    with MATH_RENDER_LOCK:image=equation(eq)
    scale=min(maxw/image.width,maxh/image.height,1)
    if scale<1:image=image.resize((max(1,round(image.width*scale)),max(1,round(image.height*scale))),Image.Resampling.LANCZOS)
    canvas.alpha_composite(image,(x,y+(maxh-image.height)//2))
def cover(canvas,box,color=DARK):
    ImageDraw.Draw(canvas).rectangle(box,fill=color)
def board(canvas,sid,phase):
    b=BOARDS[sid];d=ImageDraw.Draw(canvas);bg=DARK if sid in {6,9,10,11,12,16,17,20,21,30,39,42,55,58} else '#000000'
    cover(canvas,(967,174,1919,922),bg)
    line(d,(1160 if sid==55 else 1018,189),b.purpose,47,720 if sid==55 else 856,GOLD,True)
    maths(canvas,b.formula,1018,282,836,114)
    # Show the names alongside the expression from its very first frame.
    if sid==42:
        line(d,(1018,408),b.definitions[0],36)
        line(d,(1018,452),'R 반사 방향 · V 카메라 쪽 · n 광택 지수',35)
        line(d,(1018,496),b.definitions[1],35)
    else:
        line(d,(1018,423),b.definitions[0],39)
        line(d,(1018,481),b.definitions[1],39)
    if sid==42:
        if phase>=1:
            line(d,(1018,557),'왼쪽 · 정점에서 구한 밝기를 섞기',33,850,MINT)
            maths(canvas,r'C_v(P)=\sum_i\lambda_i f(\mathbf{N}_i)',1018,605,826,70)
            line(d,(1018,683),'오른쪽 · 법선을 섞고 픽셀에서 밝기 구하기',33,850,MINT)
            maths(canvas,r'C_p(P)=f\!\left(\operatorname{normalize}\!\left(\sum_i\lambda_i\mathbf{N}_i\right)\right)',1018,735,826,69)
        if phase==2:code_line(d,(1018,863),'pixel: shade(normalize(blend(N)))')
    else:
        if phase>=1:
            d.line((1020,552,1862,552),fill='#354441',width=2)
            line(d,(1018,579),b.meaning,38,846,MINT)
        if phase==2:
            line(d,(1018,677),'셰이더 코드 · 의사 코드',29,846,MUTED)
            for j,c in enumerate(b.code):code_line(d,(1018,761+j*53),c)
    # Preserve camera and light glyphs from the existing sphere study.
    if sid in {9,10,11,16,17}:
        d.rectangle((967,233,1065,294),fill=(0,0,0,0))
    if sid==55:d.rectangle((967,174,1139,334),fill=(0,0,0,0))
    if sid==65:d.rectangle((1515,788,1864,879),fill=(0,0,0,0))
def demo_base(canvas,sid):
    d=ImageDraw.Draw(canvas);cover(canvas,(0,174,965,917))
    cover(canvas,(1325,25,1919,149));line(d,(1370,49),'자체 셰이더 · 실제 렌더',33,510,MUTED)
    items=([('N 법선','#99e29f'),('L 광원 쪽','#ffd076'),('V 카메라 쪽','#77d7ee'),('R 반사','#ff958b')] if sid in (12,42) else
           [('N 표면 법선','#99e29f'),('L 광원 쪽','#ffd076'),('θ 사이각','#f5efc7')] if sid in (20,21,30) else [])
    x=80
    for word,color in items:
        line(d,(x,178),word,30,205,color,True);x+=font(30,True).getlength(word)+38
    if sid in (30,42):
        left,right=('정점 밝기 보간','픽셀에서 조명') if sid==42 else ('램버트','하프 램버트')
        for x,title in [(112,left),(530,right)]:line(d,(x,220),title,42,380,WHITE,True)
    else:line(d,(102,222),'표면점과 꼭짓점 색' if sid==39 else '같은 재질 구',38,820,MUTED)
    key,lo,hi,_,_=DEMOS[sid]
    line(d,(84,789),key,40,826,GOLD,True)
    line(d,(84,849),lo,32,378,MUTED)
    face=font(32);line(d,(900-face.getlength(hi),849),hi,32,388,MUTED)
def custom_left(canvas,sid):
    # Static symbolic diagrams are preferable where a continuous material change adds no information.
    d=ImageDraw.Draw(canvas);cover(canvas,(0,175,963,920))
    if sid==44:
        line(d,(80,238),'동일한 픽셀 P',48,795,WHITE,True)
        line(d,(80,345),'광원 A',37,350,MINT);line(d,(440,345),'광원 B',37,350,MINT)
        for x,clr in [(180,'#ebae70'),(560,'#93d9f1')]:
            d.ellipse((x-25,430,x+25,480),fill=clr);d.line((x,492,376,620),fill=clr,width=6)
        d.ellipse((338,598,414,674),fill='#83a69a');line(d,(450,611),'같은 재질색 k',39,455,WHITE)
        line(d,(80,764),'A와 B를 합친 뒤 공통 재질을 적용',35,825,MUTED)
    elif sid==61:
        import numpy as np
        y,x=np.mgrid[-1:1:100j,-1:1:180j]
        g=np.clip((1-np.sqrt(x*x+y*y))/.32,0,1);falloff=np.clip(1-(x+1)*.5,0,1)
        line(d,(80,240),'한 표면점의 광원 기여',48,835,WHITE,True)
        for j,(sample,label) in enumerate([(g,'고보 G'),(falloff,'깊이 감쇠 F'),(g*falloff,'남은 빛')]):
            image=Image.fromarray((255*sample).astype('uint8'),'L').convert('RGBA').resize((205,135))
            ox=80+291*j;canvas.alpha_composite(image,(ox,463));line(d,(ox,630),label,37,228,WHITE)
        line(d,(313,505),'×',46,60,GOLD);line(d,(603,505),'=',46,60,GOLD)
    elif sid==64:
        line(d,(84,241),'같은 위치를 두 좌표로 읽기',46,835,WHITE,True)
        for y,title in [(411,'상자 중심 기준 x'),(620,'텍스처 가로 위치 u')]:
            line(d,(100,y-78),title,38,827,MUTED)
            d.line((130,y,831,y),fill='#86c7ba',width=7)
            for x in (130,480,831):d.ellipse((x-7,y-7,x+7,y+7),fill=WHITE)
        d.line((480,426,480,607),fill=GOLD,width=4)
        line(d,(387,723),'중심 ↔ 그림 가운데',35,520,GOLD)
def support(canvas,sid,phase):
    d=ImageDraw.Draw(canvas)
    if sid==15:
        for row,y in enumerate((398,611,822)):
            d.rectangle((190,y,1610,y+52),fill='black')
            for x,text in [(350,'약한 반사'),(727,'중간'),(1090,'강한 반사')]:
                line(d,(x,y+6),text,27,330,MUTED)
        line(d,(68,206),'위 · 좁음',29,285,GOLD);line(d,(68,695),'아래 · 넓음',29,285,GOLD)
        return
    a,b,c=EXTRA[sid]
    if sid==40:
        cover(canvas,(120,661,1860,884),'black');line(d,(193,706),b,40,725,MUTED);line(d,(965,706),c,38,858,MINT);return
    if sid==70:
        cover(canvas,(1456,401,1919,654),'black');line(d,(1480,437),'표면의 UV',34,415,GOLD)
        line(d,(1480,507),'표시한 한 칸을',32,415,WHITE);line(d,(1480,564),'따라 읽어요.',32,415,WHITE);return
    if sid==63:
        cover(canvas,(1008,712,1919,914),'black')
        line(d,(1030,745),b,35,840,WHITE);line(d,(1030,813),c,34,840,MUTED);return
    if sid in (73,77):
        cover(canvas,(1000,225,1919,357),'black')
        line(d,(1032,241),'SH Basis (구면 조화 기저)' if sid==73 else 'Environment Filtering (환경 필터링)',33,830,GOLD,True)
        for x,txt in zip((1035,1440),('원래 방향 분포','계수 × 기저') if sid==73 else ('환경 L(ω)','난반사 E/π')):
            line(d,(x,315),txt,28,365,WHITE)
        cover(canvas,(1008,738,1919,914),'black');line(d,(1032,763),b,34,825,WHITE);line(d,(1032,832),c,33,825,MUTED)
        if sid==77:
            for x,txt in [(1033,'좁은 반사'),(1432,'넓은 반사')]:
                cover(canvas,(x,515,x+380,563),'black');line(d,(x,520),txt,31,355,WHITE)
        return
    if sid in (35,36,19,52):
        if sid in (35,36):
            cover(canvas,(997,236,1919,914),'black')
            line(d,(1025,297),a,42,841,GOLD,True)
        else:cover(canvas,(997,574,1919,914),'black')
        if sid==35 and phase==2:
            b,c='재귀반사 · 광원 쪽이 기준','법선을 따라 반사하는 거울 방향과 달라요.'
        line(d,(1025,642),b,37,841,WHITE);line(d,(1025,726),c,34,841,MUTED);return
    bg=DARK if sid in (1,7) else '#000000'
    cover(canvas,(991,235,1919,914),bg);line(d,(1032,293),a,44,833,GOLD,True)
    line(d,(1032,468),b,39,833,WHITE);line(d,(1032,568),c,35,833,MUTED)
def generate(r):
    s=r['sid'];n=r['frames']
    if r['newSpeech']:
        a=read(VOICE/f'{s:03}-alignment.json')
        first=round((a['clauses'][1]+.06)*60);last=round((a['clauses'][min(3,len(a['clauses'])-1)]+.06)*60)
    else:
        # Attach progressively revealed details to the existing spoken cues.
        starts=[round((row['start']+2-r['oldStart']/60)*60) for row in v6.KO if int(row['scene'])==s and r['oldStart']/60<=row['start']+2<(r['oldStart']+r['oldFrames'])/60]
        first=starts[min(1,len(starts)-1)] if starts else n//4
        last=starts[min(3,len(starts)-1)] if len(starts)>2 else n//2
    keys=sorted({0,max(1,min(n-2,first)),max(2,min(n-1,max(first+1,last)))})
    folder=WORK/'plates'/f'{s:03}';folder.mkdir(parents=True,exist_ok=True);states=[]
    for phase,k in enumerate(keys):
        im=Image.new('RGBA',(1920,1080))
        if s in BOARDS:board(im,s,phase)
        if s in DEMOS:demo_base(im,s)
        if s in (44,61,64):custom_left(im,s)
        if s in EXTRA or s==15:support(im,s,phase)
        from symbol_pages import decorate
        decorate(im,r,phase)
        path=folder/f'{k:06}.png';im.save(path,compress_level=2);states.append((k,path))
    return states

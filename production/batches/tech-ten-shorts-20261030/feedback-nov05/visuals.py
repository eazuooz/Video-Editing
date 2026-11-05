"""Editable cutaway and process diagrams. Coordinates are in the 1080x840 teaching window."""
import csv, math, subprocess as sp
from functools import lru_cache
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageFont
from math import sin,cos,pi,exp
BG='#0a1416'; PANEL='#152629'; WHITE='#f0f7f4'; MUTE='#b3c9c6'; TEAL='#62e2be'; GOLD='#ffd366'; BLUE='#67c9ff'; RED='#ff917c'
@lru_cache(None)
def font(sz):return ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',sz)
@lru_cache(1200)
def glyph(st,sz,col):
    f=font(sz);b=f.getbbox(st,anchor='lt');im=Image.new('RGBA',(math.ceil(f.getlength(st))+6,b[3]+6));ImageDraw.Draw(im).text((2,2),st,font=f,fill=col,anchor='lt');return im
def label(im,x,y,st,sz=36,col=WHITE,center=False):
    g=glyph(st,sz,col);im.paste(g,(int(x-g.width/2 if center else x),int(y)),g)
def line(d,ps,color,w=6):d.line(ps,fill=color,width=w,joint='curve')
def arrow(d,p,q,color,w=8):
    line(d,[p,q],color,w);a=math.atan2(q[1]-p[1],q[0]-p[0]);z=w*2.7
    d.polygon([q,(q[0]-z*cos(a-.48),q[1]-z*sin(a-.48)),(q[0]-z*cos(a+.48),q[1]-z*sin(a+.48))],fill=color)
def clamp(x):return min(1,max(x,0))
def smooth(x):x=clamp(x);return x*x*(3-2*x)
def frame(k,topic,tag):
    im=Image.new('RGB',(1080,840),BG);d=ImageDraw.Draw(im)
    d.rectangle((35,41,47,82),fill=GOLD);label(im,67,39,topic,43,WHITE);label(im,46,109,tag,29,MUTE)
    line(d,[(44,744),(1036,744)],'#385051',3);return im,d
def foot(im,d,st):label(im,540,765,st,34,GOLD,True)
def liquid(t,end):
    wrong=t<17.78
    im,d=frame(1,'병의 축과 중력의 방향','옆에서 본 단면   /   반쯤 찬 병')
    angle=(-.72*smooth((t-11.5)/3)) if wrong else (-.75+.15*sin(t*.86))
    c=(517,452)
    def rot(x,y):return (round(c[0]+x*cos(angle)-y*sin(angle)),round(c[1]+x*sin(angle)+y*cos(angle)))
    shape=[(-128,-160),(-88,-190),(-49,-206),(-49,-254),(49,-254),(49,-206),(88,-190),(128,-160),(128,202),(110,221),(-109,221),(-128,202)]
    pts=[rot(*p) for p in shape]
    mask=Image.new('L',im.size);md=ImageDraw.Draw(mask);md.polygon(pts,fill=255)
    water=Image.new('L',im.size);wd=ImageDraw.Draw(water)
    if wrong:wd.polygon([rot(-420,0),rot(420,0),rot(420,600),rot(-420,600)],fill=255)
    else:wd.rectangle((0,c[1],1080,840),fill=255)
    blue=Image.new('RGB',im.size,'#17658b');bd=ImageDraw.Draw(blue)
    for i in range(-6,7):line(bd,[(0,c[1]+40*i),(1080,c[1]+40*i)],'#29759a',2)
    im.paste(blue,mask=ImageChops.multiply(mask,water));line(d,pts+[pts[0]],WHITE,8)
    if wrong:line(d,[rot(-128,0),rot(128,0)],RED,10);label(im,60,234,'병에 붙인 선',35,RED);arrow(d,(258,276),rot(-76,0),RED,5)
    else:
        arrow(d,(188,270),(188,540),GOLD,11);label(im,95,201,'중력',41,GOLD)
        for x in range(207,920,33):line(d,[(x,c[1]),(x+19,c[1])],TEAL,4)
        line(d,[(188,480),(216,480),(216,452)],WHITE,5)
        line(d,[(c[0]-135,c[1]),(c[0]+135,c[1])],TEAL,10)
        label(im,777,390,'수평선',39,TEAL);label(im,774,490,'아래만 물',32,BLUE)
    foot(im,d,'병에 고정한 선은 병과 함께 기울어요' if wrong else '중력은 아래로  ↓     수면은 중력과 직각');return im
def footprint(im,x,y,scale,col):
    d=ImageDraw.Draw(im)
    for dx,dy,rx,ry in [(0,-13,21,31),(-4,28,16,13)]:
        d.ellipse((x+(dx-rx)*scale,y+(dy-ry)*scale,x+(dx+rx)*scale,y+(dy+ry)*scale),fill=col)
def height(u,v):
    # One smooth sole-and-heel imprint. Both the inset and every displaced vertex
    # sample this field in the same UV coordinates; white means deeper.
    sole=((u-.32)/.105)**2+((v-.44)/.174)**2
    heel=((u-.35)/.079)**2+((v-.225)/.075)**2
    return max(smooth((1.36-sole)/.85),smooth((1.36-heel)/.85))
@lru_cache(1)
def height_tile():
    im=Image.new('RGB',(147,143));pix=im.load()
    for y in range(143):
        for x in range(147):
            k=round(11+229*height(.08+.55*x/146,.05+.68*(1-y/142)));pix[x,y]=(k,k,k)
    return im
def snow(t,insert,extra):
    capture=t<32.63
    if capture:
        im,d=frame(2,'발이 닿은 곳만 찍기','단면에서 카메라 방향을 먼저 보세요')
        label(im,63,211,'옆에서 본 눈밭',35);label(im,723,211,'카메라 출력',34)
        d.rectangle((60,424,626,477),fill='#aacbd4');d.rectangle((60,356,626,424),fill='#27474d')
        for x in range(63,622,34):line(d,[(x,355),(x+20,355)],GOLD,4)
        label(im,74,300,'발목 높이까지만',29,GOLD)
        k=clamp((t-6.5)/2);dy=int(50*(1-k))
        d.polygon([(315,237-dy),(370,237-dy),(370,375-dy),(418,395-dy),(420,420-dy),(311,420-dy),(304,392-dy)],fill='#9aaeb4',outline=WHITE,width=4)
        d.rectangle((285,595,407,664),fill='#355e62',outline=TEAL,width=5);d.polygon([(305,594),(323,565),(367,565),(387,594)],fill=TEAL)
        for x in (279,344,405):arrow(d,(x,542),(x,461),TEAL,6)
        label(im,451,578,'아래 → 위',32,TEAL)
        d.rounded_rectangle((682,280,1011,637),radius=14,fill='#040a0b',outline='#6e8687',width=4)
        for i in range(min(3,1+int(max(0,t-21.5)/.9))):
            if t>=28.1 and t<30.78 and i<2:continue
            x=(846 if t<=21.5 else 776+i*63);y=(460 if t<=21.5 else 518-i*61)
            footprint(im,x,y,1.35,'#e6f1ed' if i==2 or t<=21.5 else '#a9c5bd')
        arrow(d,(624,454),(671,454),WHITE,6)
        foot(im,d,'검정 = 접촉 없음    흰색 = 발이 닿은 곳' if t<21.53 else '이전 자국을 남기고 다음 발자국을 더해요')
        return im
    console=t<36.43
    p=clamp((t-insert)/max(extra,.1))
    stage=0 if console or (t>=insert and p<.45) else 1 if (t<insert or p<.69) else 2
    title='콘솔판  /  릴리프 매핑' if console else ['① 꼭짓점 세 개뿐이라면','② 삼각형을 나누면 점이 생겨요','③ 높이맵을 읽고 점을 내려요'][stage]
    im,d=frame(2,title,'콘솔: 깊어 보이게 표시' if console else 'PC · DirectX 11   /   테셀레이션과 변위')
    def proj(u,v):return (int(110+637*u+175*v),int(600-34*u-260*v))
    m=(1 if stage==0 else 15)
    def pt(i,j):
        u=i/m;v=j/m;x,y=proj(u,v);depth=0 if stage<2 else smooth((p-.69)/.20)*68*height(u,v)
        return x,round(y+depth)
    if console:
        d.polygon([proj(0,0),proj(1,0),proj(0,1)],fill='#abc2c8');footprint(im,395,494,1.65,'#435b64');label(im,731,416,'표면의',37);label(im,731,474,'깊이 착시',37,TEAL)
    else:
        for j in range(m-1,-1,-1):
            for i in range(m-j):
                for tri in [[(i,j),(i+1,j),(i,j+1)]]+([[(i+1,j),(i+1,j+1),(i,j+1)]] if i+j+1<m else []):
                    vs=[pt(*a) for a in tri];shade='#526e79' if stage==2 and height((i+.3)/m,(j+.3)/m)>.25 else '#a9c1c7'
                    d.polygon(vs,fill=shade);line(d,vs+[vs[0]],'#385a62',4)
        for j in range(m+1):
            for i in range(m-j+1):
                x,y=pt(i,j);r=8 if m==1 else 4;d.ellipse((x-r,y-r,x+r,y+r),fill=GOLD)
        if stage==0:
            footprint(im,400,494,1.1,'#547079');label(im,696,313,'중앙엔',34);label(im,696,362,'움직일 점이 없음',32,RED);arrow(d,(688,407),(445,479),RED,5)
        elif stage==1:label(im,731,315,'새 꼭짓점',34,GOLD);arrow(d,(754,381),pt(4,3),GOLD,6)
        else:
            label(im,733,256,'높이맵',32,WHITE);d.rectangle((762,307,914,454),fill='#03090b',outline=MUTE,width=3);im.paste(height_tile(),(765,310))
            x,y=pt(5,6);arrow(d,(x,y-111),(x,y-10),GOLD,10)
    foot(im,d,('화면에서 깊이를 표현해요' if console else ['가운데를 눌러도 옮길 꼭짓점이 없어요','면을 잘게 나누는 단계 = 테셀레이션','새 꼭짓점의 높이를 바꾸는 단계 = 변위'][stage]));return im
def ship(t):
    on=t>=13;flood=t>=27.21
    im,d=frame(3,'보이지 않는 선체 안쪽을 열어 보면','배의 단면   /   노란 선은 설명을 위해 보이게 한 메시')
    hull=[(174,310),(250,523),(372,637),(690,637),(824,520),(909,310)]
    inner=[(201,322),(272,512),(386,610),(676,610),(804,508),(880,322)]
    d.polygon(hull,fill='#28383b')
    surf=[(x,int(425+14*sin(t*2.4+x/88))) for x in range(0,1081,6)]
    water=Image.new('L',im.size);wd=ImageDraw.Draw(water);wd.polygon(surf+[(1080,699),(0,699)],fill=255)
    within=Image.new('L',im.size);ImageDraw.Draw(within).polygon(inner,fill=255)
    active=t>=17.3
    if active:water=ImageChops.subtract(water,within)
    sea=Image.new('RGB',im.size,'#17557a');sd=ImageDraw.Draw(sea);line(sd,surf,BLUE,12)
    im.paste(sea,mask=water)
    line(d,hull,'#dcb999',16)
    if on:
        h=int(86*(1-smooth((t-13)/2.7)));pts=[(x,y-h) for x,y in inner]
        line(d,pts+[pts[0]],GOLD,7)
        for i,j in [(0,2),(0,3),(1,3),(2,4),(3,5),(0,5)]:line(d,[pts[i],pts[j]],'#c39849',3)
        label(im,74,186,'마스킹 메시',37,GOLD);arrow(d,(305,234),(pts[0][0]+34,pts[0][1]+13),GOLD,6)
    if flood:
        fy=int(595-100*smooth((t-29.4)/3.8));fm=Image.new('L',im.size);ImageDraw.Draw(fm).rectangle((0,fy,1080,698),fill=255)
        im.paste('#388399',mask=ImageChops.multiply(fm,within)); label(im,530,523,'침수',35,WHITE,True)
    elif active:label(im,543,456,'바다 픽셀 제외',36,WHITE,True)
    else:label(im,540,467,'배 안에도 바다',37,WHITE,True)
    label(im,845,188,'작동' if active else '준비' if on else '꺼짐',32,TEAL if active else RED)
    foot(im,d,'선실 물은 별도 수면으로 차올라요' if flood else '바깥 파도는 남고, 틀 안의 바다만 사라져요' if active else '바다 표면은 선체 경계를 모릅니다');return im
def economy(t,progress):
    im,d=frame(6,'일꾼 정체가 전투까지 바꾸는 이유','한 가지 상황   /   광물이 돌아오지 않을 때')
    for x,st in [(168,'광물'),(528,'기지'),(873,'병력 생산')]:label(im,x,296,st,39,WHITE,True)
    for i in range(3):
        x=98+i*51;d.polygon([(x,488),(x-10,405),(x+18,354),(x+39,420),(x+25,476)],fill='#3389a1',outline=BLUE,width=5)
    d.polygon([(448,480),(459,398),(515,353),(589,402),(607,480)],fill='#325453',outline=TEAL,width=6)
    for j in range(3):
        x=769+j*74;d.rounded_rectangle((x,386,x+58,466),radius=9,outline=MUTE,width=4)
    arrow(d,(257,430),(428,430),GOLD,6);arrow(d,(630,430),(738,430),MUTE,6)
    x=287+int(44*min(1,progress*5));d.ellipse((x-16,410,x+16,444),fill=GOLD)
    line(d,[(365,401),(398,455)],RED,8);line(d,[(399,401),(365,455)],RED,8)
    label(im,540,563,'입금 중단  →  다음 유닛은 대기',43,GOLD,True)
    foot(im,d,'길을 풀러 귀환하면 전투 지휘가 끊겨요' if progress>.43 else '돈줄이 멈추면 생산 선택도 사라져요');return im
def eud(t,p):
    im,d=frame(8,'옛 맵을 살리고 위험한 접근을 막기','같은 요청: “플레이어 이름을 읽어 줘”')
    for x,st in [(167,'옛 유즈맵'),(536,'통역기'),(888,'새 게임')]:
        d.rounded_rectangle((x-121,342,x+121,469),radius=18,fill=PANEL,outline=TEAL if x==536 else MUTE,width=4);label(im,x,384,st,35,WHITE,True)
    arrow(d,(295,404),(405,404),TEAL,8);arrow(d,(666,404),(758,404),TEAL,8)
    lab='주소 직접 접근은 차단' if p<.43 else '지원하는 요청만 해석해 전달'
    line(d,[(164,331),(164,252),(894,252),(894,331)],'#805c54',5);line(d,[(520,233),(555,270)],RED,9);line(d,[(555,233),(520,270)],RED,9)
    x=int(175+708*smooth((p-.40)/.43));d.ellipse((x-10,491,x+10,511),fill=GOLD)
    label(im,540,568,lab,43,GOLD,True);foot(im,d,'옛 놀이 규칙은 살리고, 위험한 메모리 접근은 막아요');return im
def replay(t,root):
    if t<15.68:mode='record';lt=6.46*clamp((t-7.65)/7.6);phase='명령 기록'
    elif t<19.9:mode='record';lt=clamp((t-15.79)/4.13)*4.7;phase='명령 기록'
    elif t<23.4:mode='replay';lt=clamp((t-19.9)/3.4)*6.46;phase='명령 재실행'
    elif t<31.68:mode='compare';lt=clamp((t-23.4)/6.5)*6.46;phase='같은 시각 · 같은 결과'
    else:mode='patch';lt=clamp((t-31.68)/6.55)*6.46;phase='한 변수 비교 · 이동 속도'
    idx=min(194,int(lt*30+.001));im,d=frame(10,phase,'얌얌코딩 Unity 재현   /   전차·지프·헬기 6기')
    def get(k):return Image.open(root/'unity-rts-layout2'/k/f'{idx:04}.jpg')
    if mode in ['compare','patch']:
        for i,k in enumerate(['record','replay' if mode=='compare' else 'patch']):
            x=20+i*530;pic=get(k).resize((518,263),Image.Resampling.LANCZOS);im.paste(pic,(x,267));d.rectangle((x,267,x+518,530),outline=(TEAL if i==0 or mode=='compare' else GOLD),width=4)
            name=['기록 당시','재실행' if mode=='compare' else '속도를 낮춘 규칙'][i];label(im,x+259,208,name,31,WHITE,True)
            hp=trace(root,k)[idx][1];label(im,x+259,542,'포탑 체력  '+hp,33,WHITE,True)
    else:
        pic=get(mode).resize((814,414),Image.Resampling.LANCZOS);im.paste(pic,(133,183));d.rectangle((133,183,947,597),outline='#46615f',width=4)
    for x,ts,cmd in [(182,0,'시작'),(533,2,'이동'),(880,4,'공격')]:
        color=GOLD if lt>=ts else MUTE
        d.ellipse((x-9,634,x+9,652),fill=color);label(im,x,667,f'{ts}초  {cmd}',32,color,True)
    line(d,[(187,643),(874,643)],'#57706d',3);x=182+698*min(1,lt/4);d.ellipse((x-9,634,x+9,652),fill=GOLD)
    foot(im,d,'같은 맵 · 같은 규칙 · 같은 시드' if mode=='compare' else '같은 명령도 규칙이 달라지면 결과가 달라져요' if mode=='patch' else '저장하는 것: 명령을 내린 시점과 내용');return im
@lru_cache(None)
def trace(root,k):return list(csv.reader((root/'unity-rts-layout2'/k/'state.csv').read_text().splitlines()))
def make(n,path,a,b,cut,extra,work):
    # Sealed after a successful encoder exit, so an interrupted attempt is never reused.
    seal=path.with_suffix('.frames');key=str((n,a,b,cut,extra,Path(__file__).stat().st_mtime_ns))
    if path.exists() and seal.exists() and seal.read_text()==key:return
    cmd=['ffmpeg','-v','error','-nostdin','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1080x840','-framerate','30','-i','pipe:0','-an','-c:v','libx264','-threads','4','-preset','ultrafast','-crf','14','-pix_fmt','yuv420p',str(path)]
    with sp.Popen(cmd,stdin=sp.PIPE) as p:
        for j in range((b-a+1)//2):
            t=(a+2*j)/60;q=clamp((t-cut/60)/max(extra/60,.01))
            im=liquid(t,b/60) if n==1 else snow(t,cut/60,extra/60) if n==2 else ship(t) if n==3 else economy(t,q) if n==6 else eud(t,q) if n==8 else replay(t,work)
            p.stdin.write(im.tobytes())
        p.stdin.close();ret=p.wait()
    if ret:raise RuntimeError(('diagram render',n,ret))
    seal.write_text(key)

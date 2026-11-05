"""Draw labels on measured poses from the Unity cutaway and RTS simulations."""
import csv
import math
import subprocess
import wave
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw
from visuals import frame, foot, label, arrow, line, clamp, smooth, WHITE, MUTE, TEAL, GOLD, RED
import build as editor

WORK=editor.MEDIA/'general-review'
NATIVE=WORK/'native-final'
OLD=editor.MEDIA/'feedback-nov05'/'unity-rts-layout2'
@lru_cache(48)
def data(path):
    with path.open(encoding='utf8',newline='') as source:return list(csv.DictReader(source))
@lru_cache(144)
def picture(folder,number,size):
    with Image.open(folder/f'{number:04}.jpg') as source:
        return source.convert('RGB').resize(size,Image.Resampling.LANCZOS)
def progress(now,start,end):
    return clamp((now-start)/max(.01,end-start))
def speech_spans(scratch):
    pins=editor.read(scratch/'voice-files.json')
    cursor=.12
    result=[]
    for voice in pins.values():
        with wave.open(voice['path']) as src:seconds=src.getnframes()/src.getframerate()
        result.append((cursor,cursor+seconds));cursor+=seconds+.25
    return result
def phase(now,spans):
    index=next((i for i,(_,end) in enumerate(spans) if now<end+.25),len(spans)-1)
    return index, progress(now,*spans[index])
def stamp(im,d,x,y,text,color=WHITE,size=31):
    from visuals import glyph
    w=glyph(text,size,color).width
    d.rounded_rectangle((x-8,y-7,x+w+8,y+size+9),radius=7,fill='#0d1d20')
    label(im,x,y,text,size,color)
def rope_picture(im,d,mode,pose):
    folder=NATIVE/mode;pose=round(90*clamp(pose));size=(984,499);left,top=48,166
    im.paste(picture(folder,pose,size),(left,top))
    row=data(folder/'poses.csv')[pose];scale=size[0]/1080
    def point(key):return left+float(row[key+'X'])*scale,top+float(row[key+'Y'])*scale
    for key in ['anchor','end']:
        x,y=point(key);d.ellipse((x-10,y-10,x+10,y+10),outline=WHITE,width=4)
    if mode=='side':
        stamp(im,d,72,183,'옆에서 본 줄',WHITE,30)
        if pose>75:stamp(im,d,397,257,'처짐이 펴짐',TEAL)
    elif mode=='direct' and row['hit']=='1':
        x1,y1=point('anchor');x2,y2=point('end')
        ratio=(540-162.6)/(891.55-162.6)
        target=(x1+(x2-x1)*ratio,y1+(y2-y1)*ratio)
        stamp(im,d,65,184,'두 점 모두 밖',WHITE);stamp(im,d,696,192,'기둥 안쪽',RED)
        arrow(d,(735,244),target,RED,6)
    elif mode=='wrapped' and row['wrapped']=='1':
        xy=point('corner');stamp(im,d,709,190,'닿는 모서리',TEAL)
        arrow(d,(748,248),xy,TEAL,6)
    label(im,540,683,'고정점과 지프는 같은 위치에서 비교',29,MUTE,True)
def rope_pair(im,d,pose):
    for i,mode in enumerate(('direct','wrapped')):
        left=25+524*i;size=(508,258);im.paste(picture(NATIVE/mode,pose,size),(left,304))
        color=RED if i==0 else TEAL
        d.rectangle((left,304,left+508,562),outline=color,width=4)
        label(im,left+254,233,'직선으로 이으면' if i==0 else '모서리를 거치면',34,color,True)
    label(im,540,613,'두 화면의 고정점과 지프 위치가 같아요',35,WHITE,True)
def rope(now,cut,spans,extra):
    local=now-cut
    if now<cut:
        if now<21.267:
            mode='direct';u=progress(now,15.78,19.75);title='점은 밖에 있는데 줄은 안으로';caption='빨강은 기둥 속을 지나는 부분'
        else:
            mode='wrapped';u=progress(now,21.267,26.4);title='팽팽한 경로는 어디로 갈까?';caption='기둥에 닿으면 모서리에서 꺾여요'
    elif local<extra:
        index,u=phase(local,spans)
        if index==0:
            mode='side';u=progress(u,.12,.89);title='같은 길이의 줄을 당기기';caption='남는 길이가 있으면 처지고, 당기면 펴져요'
        elif index==1:
            mode='direct';u=.56+.44*progress(u,.15,.72);title='두 점 사이에서 생긴 관통';caption='점과 점 사이의 선분까지 살펴보세요'
        else:
            mode='wrapped'
            u=1 if u<.48 else 1-smooth((u-.48)/.47)*.85
            title='같은 위치에서 모서리를 돌아가기';caption='줄이 모서리에 걸렸다가 다시 풀려요'
    else:
        im,d=frame(5,'지프 위치를 그대로 맞춰 보면','Unity 원리 시연  /  같은 기둥을 위에서 본 모습')
        u=progress(local-extra,0,4.3);rope_pair(im,d,round(90*(.55+.45*u)))
        foot(im,d,'같은 양 끝, 서로 다른 경로');return im
    im,d=frame(5,title,'Unity 원리 시연  /  지프의 견인줄')
    rope_picture(im,d,mode,u);foot(im,d,caption);return im

@lru_cache(None)
def seed_rows(seed):
    return [{k:int(v) for k,v in r.items()} for r in data(NATIVE/f'seed-{seed}'/'ticks.csv')]
@lru_cache(None)
def shot_gaps(seed):
    rows=seed_rows(seed)
    return [(i,r['nextShot']-i) for i,r in enumerate(rows) if i>0 and r['nextShot']!=rows[i-1]['nextShot']]
@lru_cache(None)
def patch_hp():
    with (OLD/'patch/state.csv').open() as stream:return [int(row[1]) for row in csv.reader(stream)]
def shot_panel(im,d,seed,tick,x,title,color):
    size=(504,256);y=281
    im.paste(picture(NATIVE/f'seed-{seed}',tick//2,size),(x,y))
    d.rectangle((x,y,x+504,y+256),outline=color,width=4)
    label(im,x+252,205,title,32,color,True)
    label(im,x+252,552,f"포탑 체력  {seed_rows(seed)[tick]['hp']}",35,WHITE,True)
def version_card(im,d,available,u):
    entries=['당시 실행 파일','당시 게임 데이터','원래 맵']
    for i,st in enumerate(entries):
        y=208+i*105;col=TEAL if available or i!=1 else RED
        d.rounded_rectangle((65,y,546,y+80),radius=10,fill='#192d2f',outline=col,width=3)
        label(im,92,y+20,st,34);label(im,455,y+22,'있음' if col==TEAL else '없음',29,col)
    arrow(d,(569,352),(670,352),TEAL if available else RED,8)
    label(im,842,305,'옛 규칙으로' if available else '필요 자료',36,WHITE,True)
    label(im,842,365,'다시 실행' if available else '확보 필요',37,TEAL if available else RED,True)
    label(im,540,613,'리플레이에 적힌 버전으로 맞추기',36,GOLD,True)
def replay(now,cut,spans):
    index,u=phase(now-cut,spans)
    titles=['한 전차의 다음 발사','시드가 같으면 숫자도 다시 같아요','시드만 바꾸면 어디서 갈라질까?','속도가 달라진 버전으로 돌려 보면','패치 뒤에도 옛 경기를 보려면','옛 리플레이에 필요한 것']
    im,d=frame(10,titles[index],'얌얌코딩 Unity 실험' if index<4 else '스타크래프트 II  /  리플레이 재생 조건')
    if index==0:
        tick=round(222+112*u);im.paste(picture(NATIVE/'seed-42',tick//2,(864,438)),(108,189))
        waited=shot_gaps(42)[0][1]/60
        stamp(im,d,128,207,f'경기 시각  {tick/60:.2f}초',WHITE,30)
        label(im,540,664,'첫 전차의 다음 발사까지  %.2f초'%waited,37,GOLD,True)
        footer='우리 시연은 발사 사이의 대기 시간을 뽑아요'
    elif index in (1,2):
        other=42 if index==1 else 7;tick=round(239+150*min(1,u*1.32))
        shot_panel(im,d,42,tick,26,'처음 경기 · 시드 42',TEAL)
        shot_panel(im,d,other,tick,550,f'재실행 · 시드 {other}',TEAL if other==42 else GOLD)
        for x,s in [(278,42),(802,other)]:
            gaps=shot_gaps(s)
            vals=['%.2f초'%(gap/60) if tick>=start else '…' for start,gap in gaps[:2]]
            label(im,x,637,'  →  '.join(vals),32,GOLD,True)
        footer='같은 전차가 차례로 뽑은 발사 간격'
    elif index==3:
        tick=round(190+198*min(1,u*1.25));idx=tick//2
        for col,(stage,rate) in enumerate([('record','당시 속도'),('patch','느려진 속도')]):
            x=26+524*col
            im.paste(picture(OLD/stage,idx,(504,256)),(x,280));color=TEAL if col==0 else GOLD
            d.rectangle((x,280,x+504,536),outline=color,width=4)
            label(im,x+252,210,rate,36,color,True)
            hp=seed_rows(42)[idx*2]['hp'] if col==0 else patch_hp()[idx]
            label(im,x+252,565,f'포탑 체력  {hp}',37,WHITE,True)
        label(im,540,658,'4초 공격 명령은 두 쪽이 같아요',35,GOLD,True)
        footer='이동 속도만 다른 자체 비교 실험'
    else:
        version_card(im,d,index==4,u)
        footer='당시 자료를 갖추면 패치 뒤에도 볼 수 있어요' if index==4 else '명령을 실행할 당시 버전과 맵이 필요해요'
    foot(im,d,footer);return im
def render_window(n,path,start,end,insert,extra,scratch):
    spans=speech_spans(scratch)
    program=['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-f','rawvideo','-pixel_format','rgb24',
             '-video_size','1080x840','-framerate','30','-i','pipe:0','-an','-c:v','libx264','-threads','3',
             '-preset','ultrafast','-crf','15','-pix_fmt','yuv420p',str(path)]
    with subprocess.Popen(program,stdin=subprocess.PIPE) as encoder:
        for f in range(start,end,2):
            image=rope(f/60,insert/60,spans,extra/60) if n==5 else replay(f/60,insert/60,spans)
            encoder.stdin.write(image.tobytes())
        encoder.stdin.close()
        if encoder.wait():raise RuntimeError('The explanatory window failed to encode.')

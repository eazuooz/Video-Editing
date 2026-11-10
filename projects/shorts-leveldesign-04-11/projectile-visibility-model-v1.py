from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from xml.sax.saxutils import escape
from PIL import Image, ImageDraw, ImageFont

project=Path('projects/shorts-leveldesign-04-11')
out=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-04-11')
out.mkdir(parents=True,exist_ok=True)
def pin(path):
    return {'path':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()}
def save(path,raw):
    if path.exists():
        assert path.read_bytes()==raw,path
    else:
        with path.open('xb') as fp:
            fp.write(raw)
draft=project/'preproduction-v2.json'
assert pin(draft)['sha256']=='9c739daa9d6b3d43a048b26ea6e2ab061a45784d21a8df4b024f3fceb3da2c64'
scene=json.loads(draft.read_bytes())['sceneBeats'][3]
assert (scene['sceneId'],scene['oneChangedVariable'])==('04-11-P04','카메라 전방 오프셋')


# World positions use integer centimetres. Compare orthographic windows of the
# same width along one trajectory at 60 samples per second.
TICK_RATE = 60
START_X = 1300
STEP = 10
PROJECTILE_RADIUS = 12
PLAYER_EDGE = 45
VIEW_WIDTH = 1000

def front_edge(tick):
    return START_X - STEP * tick - PROJECTILE_RADIUS

contact = next(tick for tick in range(START_X // STEP + 1) if front_edge(tick) <= PLAYER_EDGE)

def compare(right_edge):
    entry = next(tick for tick in range(contact) if front_edge(tick) <= right_edge)
    assert front_edge(entry - 1) > right_edge
    return {'leftEdgeCm': right_edge - VIEW_WIDTH, 'rightEdgeCm': right_edge,
            'firstVisibleTick': entry, 'contactTick': contact,
            'visibleUntilContactTicks': contact - entry}

short = compare(500)
long = compare(800)
assert (short['firstVisibleTick'], long['firstVisibleTick'], contact) == (79, 49, 125)
assert (short['visibleUntilContactTicks'], long['visibleUntilContactTicks']) == (46, 76)

bg='#11161B'; card='#1E262E'; white='#FFFFFF'; light='#D5DFE6'; yellow='#FFE194'; teal='#9AEBD0'; coral='#FFAC9A'; path_color='#8396A3'
ops=[]
def rect(x,y,w,h,c,s='none',sw=0,r=0):
    ops.append(('r',x,y,w,h,c,s,sw,r))
def ln(points,c,w):
    ops.append(('l',points,c,w))
def lbl(x,y,text,c,fs,b=False):
    ops.append(('t',x,y,text,c,fs,b))
def cir(x,y,r,c,s,w):
    ops.append(('c',x,y,r,c,s,w))

def world_x(cm):
    return round(343 + cm * .465)

rect(0,0,1080,1920,bg)
lbl(65,83,'화면에 보인 뒤 충돌까지',yellow,60,True)
lbl(68,183,'탄환은 같은 경로 · 카메라 위치만 변경',light,36)
def panel(y, title, result):
    rect(62,y,956,488,card,'#526575',2,16)
    lbl(95,y+34,title,white,48,True)
    left=world_x(result['leftEdgeCm'])
    right=world_x(result['rightEdgeCm'])
    track=y+257
    hit=world_x(PLAYER_EDGE)
    launch=world_x(START_X)
    rect(left,y+139,right-left,197,'#27383D',path_color,4,2)
    ln([(left,track),(launch,track)],path_color,4)
    ln([(hit,track),(right,track)],teal,12)
    ln([(right+72,track),(right+18,track)],coral,7)
    ln([(right+32,track-12),(right+18,track),(right+32,track+12)],coral,7)
    cir(hit,track,15,card,yellow,5)
    cir(right,track,14,card,teal,5)
    lbl(left+15,y+157,'카메라 화면',light,31,True)
    lbl(hit-48,y+291,'충돌',yellow,31,True)
    lbl(right-59,y+291,'첫 노출',teal,31,True)
    lbl(99,y+391,f"첫 노출부터 충돌까지 {result['visibleUntilContactTicks']}프레임",white,37,True)

panel(300,'화면 끝이 몸에 가까울 때',short)
panel(829,'화면이 앞쪽을 더 담을 때',long)
lbl(71,1390,'두 화면에서 탄환이 몸에 닿는 순간은 같다',yellow,39,True)
lbl(74,1474,'60fps 자체 모형 · 회피 입력 없음',light,34)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">']
for k,*a in ops:
    if k=='r':
        x,y,w,h,c,s,b,r=a
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{c}" stroke="{s}" stroke-width="{b}"/>')
    elif k=='l':
        points,c,w=a
        pts=' '.join(f'{x},{y}' for x,y in points)
        svg.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
    elif k=='c':
        x,y,r,c,s,w=a
        svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" stroke="{s}" stroke-width="{w}"/>')
    else:
        x,y,t,c,fs,b=a
        svg.append(f'<text x="{x}" y="{y+fs}" fill="{c}" font-family="Malgun Gothic, sans-serif" font-size="{fs}" font-weight="{700 if b else 400}">{escape(t)}</text>')
svg.append('</svg>')
editable=project/'projectile-visibility-timeline-v1.svg'
save(editable,('\n'.join(svg)+'\n').encode())
previews=[]
for width in (1080,375):
    q=width/1080
    def S(v):return round(v*q)
    pic=Image.new('RGB',(width,S(1920)),bg)
    d=ImageDraw.Draw(pic)
    for k,*a in ops:
        if k=='r':
            x,y,w,h,c,s,b,r=a
            d.rounded_rectangle((S(x),S(y),S(x+w)-1,S(y+h)-1),radius=S(r),fill=c,
                                outline=None if s=='none' else s,width=max(1,S(b)))
        elif k=='l':
            pts,c,w=a
            d.line([(S(x),S(y)) for x,y in pts],fill=c,width=max(1,S(w)),joint='curve')
        elif k=='c':
            x,y,r,c,s,w=a
            d.ellipse((S(x-r),S(y-r),S(x+r),S(y+r)),fill=c,outline=s,width=max(1,S(w)))
        else:
            x,y,t,c,fs,b=a
            font=ImageFont.truetype('C:/Windows/Fonts/malgun'+('bd.ttf' if b else '.ttf'),S(fs))
            bounds=d.textbbox((S(x),S(y)),t,font=font,anchor='lt')
            assert bounds[2]<width-S(30),(t,width,bounds)
            d.text((S(x),S(y)),t,fill=c,font=font,anchor='lt')
    p=out/f'04-11-projectile-visibility-{width}px-v1.png'
    buf=BytesIO()
    pic.save(buf,format='PNG')
    save(p,buf.getvalue())
    previews.append(pin(p))

proof=out/'04-11-projectile-visibility-proof-v1.json'
data={'sceneId':scene['sceneId'],'preproduction':pin(draft),'implementation':pin(Path(__file__)),
      'editableDiagram':pin(editable),'previews':previews,'tickRate':TICK_RATE,
      'oneChangedVariable':'Horizontal camera-window offset',
      'heldConditions':{'viewWidthCm':VIEW_WIDTH,'projectileStartCm':START_X,
                        'projectileRadiusCm':PROJECTILE_RADIUS,'projectileStepCm':STEP,
                        'playerHitEdgeCm':PLAYER_EDGE,'input':'none','priorTelegraph':'none'},
      'nearWindow':short,'aheadWindow':long,'visibleLeadGainTicks':30,
      'scope':'Authored one-dimensional tick model using projectile edge overlap. No actual game measurement, input latency, human threshold, Unity capture or final captions.'}
save(proof,(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'proof':pin(proof),**data},ensure_ascii=False))

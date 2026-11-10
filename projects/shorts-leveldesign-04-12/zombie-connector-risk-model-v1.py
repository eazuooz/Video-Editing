
from collections import deque
from hashlib import sha256
from io import BytesIO
from math import hypot
import json
from pathlib import Path
from xml.sax.saxutils import escape
from PIL import Image, ImageDraw, ImageFont

project=Path('projects/shorts-leveldesign-04-12')
out=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-04-12')
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
assert pin(draft)['sha256']=='3f84c1b2d1b2189cb5474c704ab6421678ecedd90f3390300d04771c503298fb'
scene=json.loads(draft.read_bytes())['sceneBeats'][4]
assert (scene['sceneId'],scene['oneChangedVariable'])==('04-12-P05','좀비 위치')


# Coordinates are in model units. The rectangles below are an authored map.
# Search nodes sit every 0.5 units in a wall-clearance center domain.
PLAYER_RADIUS = .35
ZOMBIE_BODY_RADIUS = .50
ZOMBIE_ATTACK_REACH = 2.05
COLLISION = PLAYER_RADIUS + ZOMBIE_BODY_RADIUS
RISK = PLAYER_RADIUS + ZOMBIE_ATTACK_REACH
START, EXIT = (2., 7.), (18., 7.)
ROOM_SIDE, CONNECTOR = (5., 11.), (10., 7.)
STEP = .5

def can_stand(point):
    x, y = point
    if not (PLAYER_RADIUS <= x <= 20 - PLAYER_RADIUS and PLAYER_RADIUS <= y <= 14 - PLAYER_RADIUS):
        return False
    return x <= 8 - PLAYER_RADIUS or x >= 12 + PLAYER_RADIUS or 5 + PLAYER_RADIUS <= y <= 9 - PLAYER_RADIUS

def segment_distance(point, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    px, py = point[0] - a[0], point[1] - a[1]
    fraction = max(0, min(1, (px * dx + py * dy) / (dx * dx + dy * dy)))
    return hypot(px - fraction * dx, py - fraction * dy)

def route(zombie, clearance):
    pending = deque([START])
    parents = {START: None}
    while pending:
        cell = pending.popleft()
        if cell == EXIT:
            path = []
            while cell is not None:
                path.append(cell)
                cell = parents[cell]
            return list(reversed(path))
        x, y = cell
        for target in ((x+STEP, y), (x, y-STEP), (x, y+STEP), (x-STEP, y)):
            if target in parents or not can_stand(target):
                continue
            if segment_distance(zombie, cell, target) <= clearance:
                continue
            parents[target] = cell
            pending.append(target)
    return None

wide_safe = route(ROOM_SIDE, RISK)
choke_body_clear = route(CONNECTOR, COLLISION)
choke_safe = route(CONNECTOR, RISK)
assert wide_safe is not None and choke_body_clear is not None and choke_safe is None
assert max(abs(y - CONNECTOR[1]) for y in (5 + PLAYER_RADIUS, 9 - PLAYER_RADIUS)) < RISK

bg='#11161B'; card='#1E262E'; white='#FFFFFF'; light='#D5DFE6'; yellow='#FFE194'; teal='#9AEBD0'; coral='#FFAC9A'; path_color='#718796'
ops=[]
def rect(x,y,w,h,c,s='none',sw=0,r=0):
    ops.append(('r',x,y,w,h,c,s,sw,r))
def ln(points,c,w):
    ops.append(('l',points,c,w))
def lbl(x,y,text,c,fs,b=False):
    ops.append(('t',x,y,text,c,fs,b))
def cir(x,y,r,c,s,w):
    ops.append(('c',x,y,r,c,s,w))

rect(0,0,1080,1920,bg)
lbl(65,78,'좀비가 만드는 위험한 통로',yellow,59,True)
lbl(69,172,'같은 지도와 공격 범위 · 좀비 위치만 변경',light,36)
def plot(y, heading, zombie, path, safe):
    rect(61,y,958,592,card,'#526575',2,18)
    lbl(94,y+33,heading,white,46,True)
    scale=27
    ox, oy=267,y+117
    def at(point):
        return (round(ox+point[0]*scale),round(oy+point[1]*scale))
    floor='#354b58'
    rect(ox,oy,8*scale,14*scale,floor)
    rect(ox+8*scale,oy+5*scale,4*scale,4*scale,floor)
    rect(ox+12*scale,oy,8*scale,14*scale,floor)
    outline=[(0,0),(8,0),(8,5),(12,5),(12,0),(20,0),(20,14),(12,14),(12,9),(8,9),(8,14),(0,14),(0,0)]
    ln([at(p) for p in outline],path_color,4)
    zx, zy=at(zombie)
    cir(zx,zy,round(RISK*scale),card,coral,4)
    cir(zx,zy,round(COLLISION*scale),coral,coral,3)
    if safe:
        ln([at(p) for p in path],teal,8)
    else:
        for a,b in zip(path[::2],path[1::2]):
            ln([at(a),at(b)],yellow,6)
    for endpoint in (START, EXIT):
        x, sy=at(endpoint)
        cir(x,sy,12,card,white,4)
    lbl(112,y+287,'출발',light,35,True)
    lbl(831,y+287,'도착',light,35,True)
    label='공격 범위 밖에서 건너갈 수 있다' if safe else '몸을 피할 길은 있어도 공격 범위는 지난다'
    lbl(94,y+515,label,teal if safe else yellow,38,True)

plot(275,'넓은 방 한쪽에 있을 때',ROOM_SIDE,wide_safe,True)
plot(895,'좁은 연결부에 있을 때',CONNECTOR,choke_body_clear,False)
lbl(69,1542,'빨간 원  공격이 닿는 범위',coral,35,True)
lbl(69,1603,'노란 점선  몸은 피할 수 있는 경로',yellow,35,True)
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
editable=project/'zombie-connector-risk-v1.svg'
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
    p=out/f'04-12-zombie-connector-risk-{width}px-v1.png'
    buf=BytesIO()
    pic.save(buf,format='PNG')
    save(p,buf.getvalue())
    previews.append(pin(p))

proof=out/'04-12-zombie-connector-risk-proof-v1.json'
data={'sceneId':scene['sceneId'],'preproduction':pin(draft),'implementation':pin(Path(__file__)),
      'editableDiagram':pin(editable),'previews':previews,
      'oneChangedVariable':'Zombie position',
      'heldConditions':{'playerRadius':PLAYER_RADIUS,'zombieBodyRadius':ZOMBIE_BODY_RADIUS,
                        'zombieAttackReach':ZOMBIE_ATTACK_REACH,'graphStep':STEP,
                        'start':START,'exit':EXIT},
      'roomSide':{'zombie':ROOM_SIDE,'attackClearRoute':wide_safe},
      'connector':{'zombie':CONNECTOR,'bodyClearRoute':choke_body_clear,'attackClearRoute':choke_safe,
                   'playerCenterCrossSectionAtX10':[5+PLAYER_RADIUS,9-PLAYER_RADIUS],
                   'attackPlusPlayerRadius':RISK},
      'scope':'Analytic authored map. Routes are collision-free line segments under the labeled condition. The choke cross-section is covered by the attack radius at x=10. No measurement of Resident Evil, actual attack timing, AI, Unity runtime or human choices.'}
save(proof,(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'proof':pin(proof),**data},ensure_ascii=False))

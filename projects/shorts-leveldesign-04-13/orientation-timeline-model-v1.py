from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from xml.sax.saxutils import escape
from PIL import Image, ImageDraw, ImageFont

project=Path('projects/shorts-leveldesign-04-13')
out=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-04-13')
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
assert pin(draft)['sha256']=='5d899ec9133ff612b483efa7c2d053397ece8a70f57587602c384f95b1618020'
scene=json.loads(draft.read_bytes())['sceneBeats'][4]
assert (scene['sceneId'],scene['action'])==('04-13-P05','기본 안내 시점만 입장 전후 이동')


# The phase identifiers establish order only. No durations or results are measured.
timed_window=('entry','timerEnd')
puzzle='same device and puzzle'
instructions='same orientation'
scenarios=(
    {'orientationPhase':'timed','puzzlePhase':'timed','order':('entry','orientation','puzzle','timerEnd')},
    {'orientationPhase':'beforeEntry','puzzlePhase':'timed','order':('orientation','entry','puzzle','timerEnd')},
)
for scenario in scenarios:
    assert scenario['order'].index('orientation') < scenario['order'].index('puzzle')
    assert scenario['order'].index('entry') < scenario['order'].index('puzzle') < scenario['order'].index('timerEnd')
    assert tuple(event for event in scenario['order'] if event != 'orientation') == ('entry','puzzle','timerEnd')

bg='#11161B'; card='#1E262E'; white='#FFFFFF'; light='#D5DFE6'; yellow='#FFE194'; teal='#9AEBD0'; slate='#607888'
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
lbl(66,81,'기본 안내는 언제 할까?',yellow,62,True)
lbl(69,179,'같은 퍼즐과 제한 시간 · 안내 시점만 이동',light,35)

def panel(y,title,before):
    rect(61,y,958,474,card,'#526575',2,18)
    lbl(94,y+35,title,white,49,True)
    divider, ending = 381, 971
    lbl(104,y+142,'입장 전',light,35,True)
    lbl(divider+19,y+142,'같은 제한 시간',light,35,True)
    ln([(divider,y+217),(ending,y+217)],light,5)
    ln([(divider,y+199),(divider,y+236)],light,5)
    ln([(ending,y+199),(ending,y+236)],light,5)
    rect(divider,y+247,ending-divider,117,'#2a3d44',slate,2,10)
    ln([(divider,y+240),(divider,y+372)],white,5)
    orientation_x=112 if before else 403
    puzzle_x=403 if before else 660
    rect(orientation_x,y+262,215,85,yellow,'none',0,8)
    lbl(orientation_x+21,y+283,'기본 안내',bg,34,True)
    rect(puzzle_x,y+262,236,85,teal,'none',0,8)
    lbl(puzzle_x+24,y+283,'퍼즐 풀이',bg,34,True)
    lbl(divider-34,y+395,'입장',white,35,True)
    lbl(ending-91,y+395,'종료',light,35,True)

panel(284,'입장한 뒤 안내',False)
panel(805,'입장하기 전에 안내',True)
lbl(70,1353,'제한 시간 안에 놓이는 단계가 달라진다',yellow,40,True)
lbl(72,1433,'순서 도식 · 두 퍼즐과 기본 안내 내용은 동일',light,33)
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
editable=project/'escape-room-orientation-timeline-v1.svg'
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
    p=out/f'04-13-orientation-timeline-{width}px-v1.png'
    buf=BytesIO()
    pic.save(buf,format='PNG')
    save(p,buf.getvalue())
    previews.append(pin(p))

proof=out/'04-13-orientation-timeline-proof-v1.json'
data={'sceneId':scene['sceneId'],'preproduction':pin(draft),'implementation':pin(Path(__file__)),
      'editableDiagram':pin(editable),'previews':previews,
      'timedWindow':timed_window,'sameConditions':{'puzzle':puzzle,'orientation':instructions},
      'scenarios':scenarios,'measuredParticipantTime':None,'measuredSuccessRate':None,
      'scope':'Ordinal layout for the Motion Canvas comparison. Diagram lengths are not durations. A physical escape room and the digital comparison retain separate evidentiary scopes.'}
save(proof,(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'proof':pin(proof),**data},ensure_ascii=False))

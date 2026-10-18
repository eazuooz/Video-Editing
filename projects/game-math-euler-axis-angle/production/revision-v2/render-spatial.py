"""Compose current M04 Unity phase clips and narration-aligned math/axis UI.

Explicit invocation only. CPU x264; no TTS, source download, upload or next-video
side effect. The parent coordinates this after the exclusive voice jobs finish.
"""
from pathlib import Path
import argparse,hashlib,json,math,re,shutil,subprocess
from PIL import ImageFont

ROOT=Path(__file__).resolve().parents[4]
P=ROOT/'projects/game-math-euler-axis-angle'
LOCAL=P/'production/local/revision-v2'
OUT=LOCAL/'spatial'
LESSON=P/'production/revision-v2/lesson.json'
FONT=Path('C:/Windows/Fonts/malgun.ttf')
BOLD=Path('C:/Windows/Fonts/malgunbd.ttf')
COLORS={'x':'4234D5','y':'4C8515','z':'C36422'}
AXIS_LABEL_SIZE=40
AXIS_LABEL_PADDING=3  # Reserved on each side for glyph bearing/outline clearance.
AXIS_LABEL_FONT=ImageFont.truetype(str(BOLD if BOLD.exists() else FONT),AXIS_LABEL_SIZE)

# Each row is a relevant worked relation next to that exact narration line.
# These are authored calculations, not values measured from commercial gameplay.
FORMULAS={
 '03':[
  '월드 좌표계 (World frame)\n몸체 좌표계 (Body frame)',
  '같은 앞쪽 방향\n+ 다른 비틀림 = 다른 자세',
  '오일러 각 (Euler angles)\n세 각도 + 회전축 + 순서',
  '오른손 규칙 (Right-hand rule)\n엄지: 양의 축 / 손가락: 양의 회전',
  '헤딩 (Heading): y\n피치 (Pitch): 움직인 x\n뱅크 (Bank): 움직인 z',
  'v_body = (0,0,1)ᵀ\n+z 방향으로 한 단위',
  'v_world = R v_body\nR = Ry(h) Rx(p) Rz(b)'],
 '04':[
  'h: 0° → 45°\n몸체의 세 축도 함께 이동',
  'p: 0° → 30°\n돌아간 몸체 x축을 사용',
  'b: 0° → 35°\n두 회전을 거친 몸체 z축',
  '내재적 회전 (Intrinsic rotation)\nR = Ry(45°) Rx(30°) Rz(35°)',
  '우리 +pitch: +z → −y\n이름보다 축·부호를 확인',
  'heading·pitch: 앞쪽 방향\nbank: 그 앞쪽 주위 비틀림'],
 '06':[
  '외재적 회전 (Extrinsic rotation): 축은 월드에 고정',
  '몸체 Y–X–Z = 고정 Z–X–Y',
  'R = Ry(h) Rx(p) Rz(b)',
  'v 옆의 Rz → Rx → Ry 순으로 작용',
  'yaw·pitch·roll: 먼저 작동 축 확인',
  'Rx(90°) Ry(α) ≠ Ry(α) Rx(90°)',
  '축 기준과 순서를 함께 바꿔 얻는 같은 행렬',
  '같은 고정축에서는 Ry Rx ≠ Rx Ry'],
 '07':[
  '시작: v = (0,0,1)ᵀ',
  'Rx(90°) v = (0,−1,0)ᵀ',
  'Ry(90°) Rx(90°) v = (0,−1,0)ᵀ',
  '같은 시작에서 Ry(90°) v = (1,0,0)ᵀ',
  'Rx(90°) Ry(90°) v = (1,0,0)ᵀ',
  'Ry Rx ≠ Rx Ry  ·  회전 합성은 일반적으로 비가환'],
 '09':[
  '유한한 세 각도 → 하나의 자세',
  'heading 0° ≡ 360°  ·  같은 끝 자세',
  'A: (h,p,b) = (0°,135°,0°)',
  'B: (180°,45°,180°)  ·  R_A = R_B',
  'h,b ∈ (−180°,180°]  /  p ∈ [−90°,90°]',
  'p = ±90°에서는 b = 0으로 한 표현 선택'],
 '10':[
  'p: 45° → 80° → 90°',
  'p = +90°: world y축 ∥ body z축',
  'world +y와 body +z: 반대 방향, 같은 직선',
  '(h+5°) − (b+5°) = h−b',
  '자유도: 독립적으로 조절할 수 있는 변화의 수',
  '짐벌락 (Gimbal lock): 표현의 특이점\n물체의 물리적 회전은 가능'],
 '12':[
  'p = +90° → 자세는 h−b에 의존',
  '30° − 10° = 20°',
  'R(30°,90°,10°) = R(20°,90°,0°)',
  'p = −90°: 30°+10°=40°  ·  R(30°,−90°,10°)=R(40°,−90°,0°)',
  '가까운 자세 변화 ≠ 각도 성분의 작은 변화',
  '표현 하나를 선택해도 경계의 불연속은 남음'],
 '16':[
  '한 축의 짧은 각도 차이 ≠ 가장 짧은 3D 회전',
  '(0°,135°,0°) ≡ (180°,45°,180°)',
  't=0.5: (0°,67.5°,0°) ≠ (90°,22.5°,90°)',
  '각 숫자의 일정한 속도 ≠ 물체의 일정한 각속도',
  '끝 자세 저장과 그곳까지의 경로 선택을 구분',
  '같은 끝 자세여도 중간의 몸체 축은 다름'],
 '18':[
  '두 자세 사이의 변화\n중심을 고정한 한 축 회전',
  '축·각 표현 (Axis–angle)\n단위축 ||n||=1 + 각도 θ',
  'n=(0,1,0), θ=90°\n+z → +x',
  '축 방향 자유도 2 + 각도 1 = 3\n저장 성분은 4',
  '같은 축에서 90° ÷ 2 = 45°',
  'e = θ n\n축과 각도를 한 벡터로 묶기'],
 '19':[
  '회전벡터 (Rotation vector)\ne=θn, θ≥0, θ=||e||',
  '지수 사상 (Exponential map)\n회전벡터 → 회전 행렬',
  'e = (0,π/2,0) [rad]',
  '||e|| = √(0²+(π/2)²+0²)\n= π/2 rad = 90°',
  '정규화 (Normalization)\nn=e/||e||=(0,1,0)',
  'e=0: 항등 자세\n축을 구하려고 0으로 나누지 않기',
  '(−θ)(−n)=θn\n같은 벡터 / 다른 중복은 남음'],
 '21':[
  '+90°와 −270°: 경로는 달라도 같은 끝 자세',
  'e₁=90° n  /  e₂=270°(−n)',
  '두 길이 모두 <360°  ·  표현은 여전히 중복',
  '0≤θ≤180°  ·  180°에서 축의 부호 선택',
  'θ=0: 축은 임의  /  e=0',
  '표현 하나를 골라도 벡터 덧셈으로 합성할 수는 없음'],
 '22':[
  'Rx(90°) 후 Ry(90°): 앞쪽 (0,−1,0)ᵀ',
  'e_sum=(π/2,π/2,0)  ·  x와 y 사이의 축',
  '||e_sum||=π/√2 rad≈2.22144 rad≈127.28°',
  '벡터 합은 교환  /  회전 합성은 비가환',
  '정확한 합성: 순서를 정한 회전 행렬의 곱',
  '작은 각도에서의 1차 근사와 유한 회전을 구분']
}

NOTES={
 '03':['월드: 주변에 고정\n몸체/로컬 (Local frame): 물체와 함께','앞쪽 화살표만으로 전체 자세를 정할 수 없습니다.',
       '숫자의 의미는 좌표계와 적용 순서가 정합니다.','화면의 시계·반시계만으로 부호를 추측하지 않습니다.',
       '마지막 두 회전의 축도 앞 단계와 함께 움직입니다.','ᵀ는 가로로 쓴 성분을 세로 열로 읽는 표기입니다.',
       '이번 강의: 오른손·열벡터·로컬→월드'],
 '04':['고정 월드 축과 몸체 축을 나눠 보세요.','이미 돌아간 축 주위로 다음 회전이 작용합니다.',
       '앞쪽 방향은 유지하면서 그 주위를 비틉니다.','내재적 회전 (Intrinsic rotation)',
       '양의 회전은 정한 오른손 규칙으로 판단합니다.','같은 앞쪽이어도 뱅크가 다르면 다른 자세입니다.'],
 '06':['A: 몸체 축 / B: 고정 월드 축','같은 각도를 축 기준과 함께 반대 순서로 적용합니다.',
       '표기 순서와 벡터에 실제로 적용되는 순서를 구분합니다.','오른쪽의 연산부터 결과를 넘겨줍니다.',
       'roll은 bank에 대응합니다. yaw는 축 기준을 확인합니다.',
       'A: 몸체 y yaw는 앞쪽을 바꿈 / B: 월드 y heading은 계속 아래를 향함',
       '몸체 Y–X–Z와 고정 Z–X–Y가 같은 최종 자세를 만듭니다.','다음에는 같은 고정축 두 개의 순서만 바꿉니다.'],
 '07':['A·B 모두 같은 처음 자세, 같은 두 각도입니다.','앞쪽 +z가 −y로 이동합니다.','y축 위에 놓인 방향은 y회전으로 달라지지 않습니다.',
       '다른 순서는 +z를 +x로 먼저 보냅니다.','x축 위의 방향은 x회전으로 그대로입니다.','끝 방향도, 몸체의 전체 자세도 다릅니다.'],
 '09':['편집하기 쉬운 세 숫자입니다.','한 바퀴 더 돌아도 끝 자세는 같습니다.','첫 번째 각도 묶음을 실제로 적용합니다.',
       '세 성분을 따로 비교하는 대신 전체 자세를 비교합니다.','괄호 ( 는 제외, 대괄호 ] 는 포함입니다.',
       '특수한 자세에서 추가 규칙이 필요한 이유를 살펴봅니다.'],
 '10':['두 축이 점점 같은 직선에 가까워집니다.','방향이 같다는 뜻이 아니라 같은 축선이라는 뜻입니다.',
       '축의 양의 화살표가 서로 반대를 향합니다.','두 숫자를 같이 늘려도 자세가 그대로입니다.',
       '매개변수 변화가 만드는 독립적인 순간 회전 방향이 줄어듭니다.','좌표 표현과 물체 자체의 움직임을 구분합니다.'],
 '12':['우리 Y–X–Z 순서와 오른손 규약의 결과입니다.','헤딩에서 뱅크를 뺀 값이 같습니다.',
       '세 몸체 축 전체가 같은 방향을 향합니다.','음의90°에서는 차이가 아닌 합입니다.',
       '자세를 나타내는 숫자는 경계에서 크게 튈 수 있습니다.','정리 규칙은 보간 문제까지 해결하지 않습니다.'],
 '16':['각도 감싸기는 한 축의 긴 길을 줄이는 도구입니다.','먼저 같은 두 끝 자세를 확인합니다.',
       '항등 자세에서 두 숫자 묶음으로 각각 절반까지 이동합니다.','같은 숫자 변화가 같은 물리적 움직임은 아닙니다.',
       '편집용 표현과 계산에 쓸 경로를 따로 생각합니다.','다음에는 한 축과 각도로 변화 자체를 표현합니다.'],
 '18':['이동은 빼고 회전만 비교합니다.','길이를1로 맞춘 방향 화살표가 단위벡터입니다.',
       '앞쪽 하나가 아니라 몸체의 세 축이 함께 돕니다.','축에는 길이1이라는 제약이 있습니다.',
       '고정한 같은 축에서 각도에 배수를 곱합니다.','다음의 벡터 길이는 이동거리가 아닙니다.'],
 '19':['벡터의 방향은 축, 길이는 선택한 회전각입니다.','벡터와 그 벡터를 회전으로 보내는 연산은 다릅니다.',
       '라디안 단위를 확인하세요.','각 성분의 제곱을 더하고 제곱근을 구합니다.',
       '길이가0보다 클 때만 이 나눗셈을 사용합니다.','회전이 없으면 임의의 축을 고를 필요가 없습니다.',
       '회전 이력과 최종 자세의 중복은 다른 문제입니다.'],
 '21':['실제로 지난 경로까지 같다는 뜻은 아닙니다.','길이를 양수로 쓰면서 축 방향을 뒤집었습니다.',
       '한 바퀴 미만이라는 조건만으로는 부족합니다.','반대 축의180°도 같은 회전입니다.',
       '항등과 경계 조건을 함께 처리해야 합니다.','일반 벡터의 덧셈 규칙을 그대로 적용하지 않습니다.'],
 '22':['A는 순서가 있는 두 회전의 곱입니다.','B는 두 성분을 더한 하나의 회전벡터입니다.',
       'n=(1,1,0)/√2, 한 번의 대각선 축 회전입니다.','두 연산을 일반적으로 같은 공식으로 쓸 수 없습니다.',
       '다음 편의 쿼터니언 곱도 적용 순서가 중요합니다.','회전량 [rad]과 회전 변화율 [rad/s]도 구분합니다.']
}

PAIRS={'06','07','09','12','16','21','22'}
TERM_TITLES={
 '03':'오일러 각\n(Euler angles)',
 '04':'내재적 회전\n(Intrinsic rotation)',
 '06':'외재적 회전 (Extrinsic rotation)',
 '10':'짐벌락\n(Gimbal lock)',
 '18':'축·각 표현\n(Axis–angle)',
 '19':'회전벡터\n(Rotation vector)'
}
ROLES={
 '06':('A: 몸체 축에서 Y–X–Z','B: 고정 축에서 Z–X–Y'),
 '07':('A: 고정 x → 고정 y','B: 고정 y → 고정 x'),
 '09':('A: (0°,135°,0°)','B: (180°,45°,180°)'),
 '12':('A: h=30°, b=10°','B: 같은 자세의 b=0 표현'),
 '16':('A: (0°,135°,0°)로 보간','B: (180°,45°,180°)로 보간'),
 '21':('A: +90°, 축 +y','B: +270°, 축 −y'),
 '22':('A: x90° 후 y90°','B: eₓ+eᵧ로 한 번 회전')
}

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def clock(frames):
    hundredths=round(frames*100/60);h,rest=divmod(hundredths,360000);m,rest=divmod(rest,6000);s,cs=divmod(rest,100)
    return f'{h}:{m:02d}:{s:02d}.{cs:02d}'
def clean(text):return str(text).replace('{','(').replace('}',')').replace('\\','/').replace('\n','\\N')

def wrap(text,width,size,bold=False,max_lines=3):
    font=ImageFont.truetype(str(BOLD if bold and BOLD.exists() else FONT),size)
    result=[]
    for paragraph in text.split('\n'):
        line=''
        for char in paragraph:
            if line and font.getlength(line+char)>width:result.append(line.rstrip());line=char.lstrip()
            else:line+=char
        if line:result.append(line.rstrip())
    if len(result)>max_lines:raise ValueError(f'Text exceeds planned{max_lines}lines at{size}px: {text}')
    return '\n'.join(result)

class Overlay:
    def __init__(self):self.lines=[]
    def text(self,start,end,text,x,y,size=44,color='101810',bold=False,align=7,layer=5,move=None):
        position=f'\\pos({round(x)},{round(y)})' if move is None else f'\\move({round(x)},{round(y)},{round(move[0])},{round(move[1])})'
        self.lines.append(f'Dialogue: {layer},{clock(start)},{clock(end)},Text,,0,0,0,,{{\\an{align}{position}\\fs{size}\\c&H{color}&\\b{int(bold)}\\bord0}}'+clean(text))
    def leader(self,start,end,a,b,color='707070',force=False):
        if math.dist(a,b)<30 and not force:return
        self.lines.append(f'Dialogue: 3,{clock(start)},{clock(end)},Text,,0,0,0,,{{\\an7\\pos(0,0)\\p1\\c&H{color}&\\bord1\\1a&HFF&}}m {round(a[0])} {round(a[1])} l {round(b[0])} {round(b[1])}{{\\p0}}')
    def save(self,path):
        header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Text,Malgun Gothic,44,&H00101810,&H00101810,&H00707070,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
        path.write_text(header+'\n'.join(self.lines)+'\n',encoding='utf8')

def mathematical_direction(endpoint,origin):
    """Actual world-space math direction; screen proximity cannot establish it."""
    end=endpoint.get('mathWorld') if endpoint else None
    start=origin.get('mathWorld') if origin else None
    if end is None or start is None:return None
    vector=tuple(float(end[k])-float(start[k]) for k in ('x','y','z'))
    length=math.sqrt(sum(v*v for v in vector))
    if not math.isfinite(length) or length<1e-10:return None
    return tuple(v/length for v in vector)

def positively_collinear(a,b):
    if a is None or b is None:return False
    # A negative parallel axis points in the opposite direction and must keep
    # its own label. Only numerically identical positive unit directions merge.
    return sum(x*y for x,y in zip(a,b))>=1.0-1e-6

def measured_axis_label_width(text):
    box=AXIS_LABEL_FONT.getbbox(text)
    return max(AXIS_LABEL_FONT.getlength(text),box[2]-box[0])+2*AXIS_LABEL_PADDING

def label_candidates(state,pair):
    data={a['name']:a for a in state['anchors']}
    result=[]
    for prefix in (['a','b'] if pair else ['a']):
        center=data.get(prefix+'.center',{}).get('pixelTopLeft')
        if center is None:continue
        for axis in 'xyz':
            for kind,key in [('body',prefix+'.body'+axis.upper()),('world',('worldA' if prefix=='a' else 'worldB')+'.'+axis if pair else 'world.'+axis)]:
                a=data.get(key)
                if not a or not a.get('inFrame'):continue
                origin_key=prefix+'.center' if kind=='body' else (('worldA' if prefix=='a' else 'worldB')+'.origin' if pair else 'world.origin')
                direction=mathematical_direction(a,data.get(origin_key))
                v=a['pixelTopLeft'];dx=v['x']-center['x'];dy=v['y']-center['y'];length=max(1,math.hypot(dx,dy))
                x=v['x']+dx/length*32;y=v['y']+dy/length*32
                if pair and y>710:
                    x+=90 if x<1730 else -90
                result.append(dict(group=prefix,axis=axis,kind=kind,text=f'{kind} {axis}',
                    x=max(95,min(1825,x)),y=max(245 if pair else 100,min(710 if pair else 835,y)),
                    target=(v['x'],v['y']),color=COLORS[axis],directionMath=direction))
    # Screen-coincident arrows may have distinct3Ddirections. Merge only when
    # the actual positive math directions also coincide, never from pixels alone.
    collapsed=[]
    for candidate in result:
        merged=False
        for old in collapsed:
            if old['group']==candidate['group'] and old['axis']==candidate['axis'] and math.hypot(old['x']-candidate['x'],old['y']-candidate['y'])<65 and positively_collinear(old['directionMath'],candidate['directionMath']):
                old['text']='world/body '+candidate['axis'];merged=True;break
        if not merged:collapsed.append(candidate)
    # Keep at most two labels within a collision neighborhood. Additional
    # unhelpful labels are omitted; the axis legend remains explicit.
    accepted=[]
    for candidate in collapsed:
        if not pair:
            # Axis labels use centered alignment. Clamp the actual bold40px
            # text box, including spare outline/bearing room, to the geometry
            # pane; a long merged name must not enter notes beginning at1050.
            width=measured_axis_label_width(candidate['text'])
            before=candidate['x']
            candidate['x']=max(60+width*.5,min(1015-width*.5,candidate['x']))
            candidate['clampedToGeometryPane']=abs(candidate['x']-before)>.01
            candidate['measuredWidth']=width
        nearby=[old for old in accepted if math.hypot(old['x']-candidate['x'],old['y']-candidate['y'])<85]
        if len(nearby)>=2:continue
        if nearby:
            lower,upper=(245,710) if pair else (100,835)
            down=candidate['y']+52
            up=candidate['y']-52
            candidate['y']=down if down<=upper else (up if up>=lower else candidate['y'])
        accepted.append(candidate)
    return accepted

def add_anchors(overlay,slot,states,pair):
    budget=slot['endFrame']-slot['startFrame'];capture=len(states)
    # 3frame(50ms) interpolation intervals give smooth60fps label motion while
    # avoiding a whole-lecture per-frame ASS event explosion.
    for index in range(0,capture,3):
        next_index=min(capture-1,index+3)
        start=slot['startFrame']+index
        end=slot['startFrame']+min(capture,index+3)
        if end<=start:continue
        now=label_candidates(states[index],pair);later=label_candidates(states[next_index],pair)
        lookup={(l['group'],l['axis'],l['text']):l for l in later}
        for label in now:
            dest=lookup.get((label['group'],label['axis'],label['text']),label)
            overlay.text(start,end,label['text'],label['x'],label['y'],AXIS_LABEL_SIZE,label['color'],True,5,6,(dest['x'],dest['y']))
            overlay.leader(start,end,label['target'],(label['x'],label['y']),force=label.get('clampedToGeometryPane',False))
    hold_start=slot['startFrame']+capture
    if hold_start<slot['endFrame']:
        for label in label_candidates(states[-1],pair):
            overlay.text(hold_start,slot['endFrame'],label['text'],label['x'],label['y'],AXIS_LABEL_SIZE,label['color'],True,5,6)
            overlay.leader(hold_start,slot['endFrame'],label['target'],(label['x'],label['y']),force=label.get('clampedToGeometryPane',False))

def build_overlay(scene,lesson_scene,slots,out):
    sid=str(scene['id']).zfill(2);pair=sid in PAIRS;overlay=Overlay();frames=int(scene['frames'])
    title=TERM_TITLES.get(sid,lesson_scene['title'])
    if pair:
        overlay.text(0,frames,wrap(title,1660,54,True,2),120,42,54,bold=True)
        roles=ROLES[sid]
        if sid=='06':
            split=next((s['startFrame'] for s in slots if s.get('lineIndex')==5),frames)
            join=next((s['endFrame'] for s in slots if s.get('lineIndex')==5),frames)
            overlay.text(0,split,roles[0],160,162,38,bold=True);overlay.text(0,split,roles[1],1080,162,38,bold=True)
            overlay.text(split,join,'A: 최종 몸체 y축의 yaw',160,162,38,bold=True)
            overlay.text(split,join,'B: 고정 월드 y축의 heading',1080,162,38,bold=True)
            if join<frames:
                overlay.text(join,frames,roles[0],160,162,38,bold=True);overlay.text(join,frames,roles[1],1080,162,38,bold=True)
        else:
            overlay.text(0,frames,roles[0],160,162,38,bold=True);overlay.text(0,frames,roles[1],1080,162,38,bold=True)
    else:
        overlay.text(0,frames,wrap(title,750,54,True,2),1050,60,54,bold=True)
    for slot in slots:
        if 'lineIndex' not in slot:continue
        index=slot['lineIndex'];start=slot['startFrame'];end=slot['endFrame']
        formula=FORMULAS[sid][index];note=NOTES[sid][index]
        if pair:
            overlay.text(start,end,wrap(formula.replace('\n',' / '),1680,48,True,1),120,759,48,bold=True)
            overlay.text(start,end,wrap(note,1680,39,False,1),120,824,39)
        else:
            beat=lesson_scene['beats'][index]
            overlay.text(start,end,wrap(beat,730,43,True,2),1050,245,43,bold=True)
            overlay.text(start,end,wrap(formula,730,49,True,3),1050,385,49,bold=True)
            overlay.text(start,end,wrap(note,730,41,False,3),1050,610,41)
        states=[json.loads(line) for line in Path(slot['anchors']).read_text(encoding='utf8').splitlines() if line.strip()]
        if len(states)!=slot['captureFrames']:raise ValueError(f'{sid} line{index}: anchor count differs from clipframes.')
        add_anchors(overlay,slot,states,pair)
    # The words distinguish fixed and moving axes independently of color.
    legend='world: 고정 축   /   body: 물체와 함께 도는 축'
    overlay.text(0,frames,legend,1050 if not pair else 120,800 if not pair else 110,34 if not pair else 32)
    path=out/f'{sid}-overlay.ass';overlay.save(path);return path,len(overlay.lines)

def inspect(path,ffprobe):
    data=json.loads(subprocess.check_output([ffprobe,'-v','error','-select_streams','v:0','-show_entries',
        'stream=width,height,r_frame_rate,nb_frames,duration','-of','json',str(path)],text=True))['streams'][0]
    if (data['width'],data['height'],data['r_frame_rate'])!=(1920,1080,'60/1'):raise ValueError(data)
    return data

def render(scene,lesson_scene,placements,args):
    sid=str(scene['id']).zfill(2);slots=[s for s in placements if s['sceneId']==sid and 'lineIndex' in s]
    slots.sort(key=lambda s:s['startFrame'])
    if len(slots)!=len(lesson_scene['ko']):raise ValueError(f'{sid}: placement does not cover current narration lines.')
    OUT.mkdir(parents=True,exist_ok=True);target=OUT/f'{sid}.mp4';report_path=OUT/f'{sid}.json'
    clip_hashes={s['source']:sha(s['source']) for s in slots}
    anchor_hashes={s['anchors']:sha(s['anchors']) for s in slots}
    signature=hashlib.sha256(json.dumps(dict(scene=scene,lesson=lesson_scene,slots=slots,clips=clip_hashes,anchors=anchor_hashes,
        compositor=sha(__file__)),ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    if target.exists() and report_path.exists() and read(report_path).get('signature')==signature and not args.force:
        previous=read(report_path)
        if sha(target)==previous['outputSha256']:
            print(json.dumps(dict(scene=sid,status='cached',frames=previous['frames'])),flush=True);return previous
    overlay,event_count=build_overlay(scene,lesson_scene,slots,OUT)
    ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe');command=[ffmpeg,'-hide_banner','-loglevel','warning','-y','-reinit_filter','0']
    filters=[];tags=[];input_index=0;covered=0
    if slots[0]['startFrame']>0:
        hold=slots[0]['startFrame'];command+=['-i',slots[0]['source']]
        filters.append(f'[{input_index}:v]trim=end_frame=1,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop={hold-1},trim=end_frame={hold},setsar=1[seg{input_index}]')
        tags.append(f'[seg{input_index}]');input_index+=1;covered+=hold
    for slot in slots:
        if slot['startFrame']!=covered:raise ValueError(f'{sid}: gap or overlap atframe{covered}.')
        command+=['-i',slot['source']];budget=slot['endFrame']-slot['startFrame'];cap=slot['captureFrames'];hold=budget-cap
        if hold<0:raise ValueError('Capture exceeds slot.')
        filters.append(f'[{input_index}:v]trim=end_frame={cap},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop={hold},trim=end_frame={budget},setsar=1[seg{input_index}]')
        tags.append(f'[seg{input_index}]');input_index+=1;covered+=budget
    if covered!=scene['frames']:raise ValueError(f'{sid}: composed framecount{covered}!={scene["frames"]}.')
    filters.append(''.join(tags)+f'concat=n={len(tags)}:v=1:a=0[joined]')
    filters.append(f'[joined]ass={overlay.name},settb=expr=1/60,setpts=N[out]')
    command+=['-filter_complex',';'.join(filters),'-map','[out]','-an','-frames:v',str(scene['frames']),
        '-c:v','libx264','-threads','4','-preset','fast','-crf','17','-pix_fmt','yuv420p','-r','60','-fps_mode','cfr',
        '-enc_time_base','1:60','-color_range','tv','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',
        '-video_track_timescale','60000','-movflags','+faststart',str(target)]
    (OUT/f'{sid}-command.json').write_text(json.dumps(command,indent=2)+'\n',encoding='utf8')
    with (OUT/f'{sid}-render.log').open('w',encoding='utf8') as log:
        result=subprocess.run(command,cwd=OUT,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:raise RuntimeError(f'{sid}: spatial render failed. See{sid}-render.log')
    data=inspect(target,ffprobe)
    if int(data['nb_frames'])!=scene['frames']:raise ValueError(f'{sid}: encoded frames do not match exact timeline.')
    report=dict(schemaVersion=1,scene=sid,signature=signature,frames=scene['frames'],seconds=scene['frames']/60,
        stream=data,output=str(target),outputSha256=sha(target),sourceClipHashes=clip_hashes,anchorHashes=anchor_hashes,
        overlay=str(overlay),overlaySha256=sha(overlay),assEvents=event_count,renderer='Unity built-in isolated camera + authored ASS math/labels',
        canonicalSourceEditorPipeline='URP17.6; source materials adapted separately, capture is built-in',
        captureLayout=dict(single=[580,470],pairs=[[560,470],[1320,470]]),
        narrationTiming='Current measured lineStarts; finite motion followed by explicit held diagram state',
        mathematicalClaims='Current independently authored lesson; exact source matrices/anchors, no measured game values',
        captionReserve='No overlay belowy880; finalfixed captions960,970/48px/max2lines composed by parent',
        visualReview='pending current moving output atFHDand375px',fullDecode='pending parentcurrent-outputQA')
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(scene=sid,status='rendered',frames=scene['frames'],output=str(target))),flush=True)
    return report

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--timeline',default=str(P/'production/revision-v2/timeline.json'))
    ap.add_argument('--placement',default=str(LOCAL/'unity-spatial-placement.json'));ap.add_argument('--scene',action='append')
    ap.add_argument('--force',action='store_true');ap.add_argument('--validate-text-only',action='store_true');args=ap.parse_args()
    lesson=read(LESSON);lookup={str(s['id']).zfill(2):s for s in lesson['scenes']}
    for sid,rows in FORMULAS.items():
        if len(rows)!=len(lookup[sid]['ko']) or len(NOTES[sid])!=len(rows):raise ValueError(f'{sid}: current narration line mapping mismatch.')
        for line,note in zip(rows,NOTES[sid]):
            wrap(line.replace('\n',' / ') if sid in PAIRS else line,1680 if sid in PAIRS else 730,48 if sid in PAIRS else 49,True,1 if sid in PAIRS else 3)
            wrap(note,1680 if sid in PAIRS else 730,39 if sid in PAIRS else 41,False,1 if sid in PAIRS else 3)
        if sid not in PAIRS:
            wrap(TERM_TITLES.get(sid,lookup[sid]['title']),750,54,True,2)
            for beat in lookup[sid]['beats']:wrap(beat,730,43,True,2)
    if args.validate_text_only:
        print(json.dumps(dict(status='text-layout-validated',scenes=len(FORMULAS),lines=sum(map(len,FORMULAS.values())),mediaJobsStarted=False)));return
    control=read(ROOT/'shared/publishing/video-production-control.json')
    if control.get('selectedVideo')!='game-math-euler-axis-angle':raise RuntimeError('M04 is not selected.')
    # Explicitly respect exclusive GPU/voice work even though this compositor is CPU.
    if (ROOT/'shared/output/GPU_HANDOFF.json').exists():raise RuntimeError('An exclusive voice/render lease is active; no media job started.')
    timeline=read(args.timeline);placement=read(args.placement)['placements'];reports=[]
    for scene in timeline['scenes']:
        sid=str(scene['id']).zfill(2)
        if sid in FORMULAS and (not args.scene or sid in args.scene):reports.append(render(scene,lookup[sid],placement,args))
    (OUT/'spatial-render-report.json').write_text(json.dumps(dict(schemaVersion=1,reports=reports),ensure_ascii=False,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()

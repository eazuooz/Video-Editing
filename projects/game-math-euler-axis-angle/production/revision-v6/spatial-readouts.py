"""Authored spatial conditions, validated against actual native capture states.

Default prepares CPU plans only. --emit reads existing capture PNG/NDJSON and
writes clip-relative ASS plus composed endpoint PNGs; it never starts media,
Unity, TTS or an ASR model. Planned values are never called capture evidence.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import runpy
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
P = ROOT / 'projects/game-math-euler-axis-angle'
H = Path(__file__).parent
O = P / 'production/local/revision-v6'
CATALOG = ROOT / 'unity/VideoEditing/Assets/VideoScenes/game-math-euler-axis-angle/revision-v6/spatial-shots.json'
FONT_PATH = Path('C:/Windows/Fonts/malgun.ttf')
BOLD_PATH = Path('C:/Windows/Fonts/malgunbd.ttf')
BG, WHITE, GOLD, VALUE, MUTED = '#10171c', '#f5f5f5', '#e8cf83', '#73c7c2', '#b8b8b8'
MATH = runpy.run_path(str(H / 'spatial-check.py'), run_name='readout_math_without_main')
TITLES = {
 'v6-01.B01': ('오른쪽 → 아래로', '아래로 → 오른쪽'),
 'v6-02.B01': ('위치와 자세를 따로 바꾸기', '처음 자세를 비교 기준으로'),
 'v6-02.B02': ('비행기에 붙은 물체 축',),
 'v6-02.B03': ('물체 축과 직립 축을 일치시키기',),
 'v6-03.B02': ('왼손 양의 회전: +Z → +X',),
 'v6-04.B01': ('첫 번째 회전 · 헤딩',),
 'v6-04.B02': ('+Y 쪽에서 원점을 내려다보기',),
 'v6-05.B01': ('돌아간 물체 X로 피치하기',),
 'v6-05.B02': ('돌아간 물체 X 사용', '고정된 직립 X 사용'),
 'v6-06.B01': ('현재 물체 Z로 뱅크하기',),
 'v6-06.B02': ('헤딩 → 피치 → 뱅크 순서',),
 'v6-07.B01': ('뒤에서 +Z 쪽을 보는 관찰자',),
 'v6-07.B02': ('자세는 고정 · 관찰 위치만 이동',),
 'v6-08.B01': ('헤딩·피치로 기수 방향 고정', '기수 방향 유지 · 뱅크만 변화'),
 'v6-10.B01': ('내재적 회전 · 움직이는 물체 축',),
 'v6-10.B02': ('물체 축: Y → X → Z', '직립 축: Z → X → Y'),
 'v6-11.B01': ('물체 Y → 돌아간 물체 X', '아직 회전하지 않은 비교 대상'),
 'v6-11.B02': ('헤딩·피치를 마친 자세', '직립 X → 직립 Y'),
 'v6-11.B03': ('고정 X90° → 고정 Y90°', '고정 Y90° → 고정 X90°'),
 'v6-12.B01': ('기수가 수직 아래를 향하게',),
 'v6-12.B02': ('현재 물체 Y로 요 회전', '처음의 수직 Y로 헤딩 회전'),
 'v6-13.B01': ('오일러 입력 피치를 바꾸기', '완성된 물체 X로 더 회전'),
 'v6-13.B02': ('고유 오일러 각 · Y → X → Y',),
 'v6-15.B01': ('편집 예: 헤딩·피치를 한 번씩',),
 'v6-18.B01': ('누적 각도와 마지막 자세 구별',),
 'v6-18.B02': ('첫 번째 오일러 입력', '다른 숫자로 같은 끝 자세'),
 'v6-20.B01': ('피치 45° → 80° → 90°',),
 'v6-20.B02': ('p=+90°: h−b를 비교', 'p=+90°: 다른 입력과 비교'),
 'v6-20.B03': ('p=−90°: h+b를 비교', 'p=−90°: 같은 합을 유지'),
 'v6-27.B01': ('짐벌 경계: 조절 효과가 겹침',),
 'v6-27.B02': ('첫 끝 표현으로 선형 보간', '다른 끝 표현으로 선형 보간'),
 'v6-27.B03': ('각 성분 일정 속도 ≠ 일정 각속도',),
 'v6-30.B01': ('정해진 세 축으로 순차 회전', '한 단위축·한 각도로 회전'),
 'v6-30.B02': ('원점을 지나는 비스듬한 단위축',),
 'v6-31.B02': ('축 n=(0,1,0) · 단위벡터',),
 'v6-32.B02': ('같은 축 · 회전량 두 배',),
 'v6-34.B01': ('같은 축의 회전량을 배로',),
 'v6-34.B02': ('음수 배율 · 반대 방향 회전',),
 'v6-36.B02': ('위쪽 축 · 양의 각도', '아래쪽 축 · 음의 각도'),
 'v6-37.B01': ('같은 축 · 목표 +90°', '같은 축 · 목표 −270°'),
 'v6-37.B02': ('720°/s · 1초에 두 바퀴', '1080°/s · 1초에 세 바퀴'),
 'v6-38.B01': ('n · 목표 90° (2π 미만)', '−n · 목표 270° (2π 미만)'),
 'v6-38.B02': ('긴 회전 · 목표 270°', '짧은 대표 · 목표 90°'),
 'v6-38.B03': ('180° 경계 목표 · +n', '180° 경계 목표 · −n'),
 'v6-39.B02': ('고정 X90° 후 고정 Y90°', '두 회전벡터의 합으로 한 번'),
 'v6-39.B03': ('고정 X → 고정 Y', '고정 Y → 고정 X'),
 'v6-40.B01': ('고정 X2° 후 고정 Y2°', '작은 회전벡터 합 · 근사'),
 'v6-40.B03': ('각속도를 같은 좌표계로 변환',),
 'v6-41.answer-y90': ('답 확인: 같은 비행기 +Z → +X',),
}


def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p): return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def vec(v): return [float(v.get(k, 0)) for k in ['x', 'y', 'z']]
@lru_cache(maxsize=128)
def getfont(path, size): return ImageFont.truetype(str(path),size)
def render_text(text):
    # The actual Malgun font cmap has no U+2212/U+2016 glyph. Keep mathematical
    # minus/norm meaning in the same supported notation in Pillow and ASS.
    return text.replace('\u2212','-').replace('\u2016','||').replace('p\u224890\u00b0','p=90\u00b0 부근').replace('\u2248','약 ')
def norm(v): return math.sqrt(sum(x*x for x in v))
def matrix(p, t): return MATH['program'](p, t)
def flat(m): return [v for row in m for v in row]
def fmt(v, places=1):
    if abs(v) < 10**(-places)/2: v = 0.
    if abs(v-round(v)) < 1e-5: return str(int(round(v))).replace('-', '−')
    return f'{v:.{places}f}'.rstrip('0').rstrip('.').replace('-', '−')
def tup(v, places=1): return '(' + ', '.join(fmt(x, places) for x in v) + ')'
def axis(v):
    names = ['X', 'Y', 'Z']
    for i, name in enumerate(names):
        if abs(abs(v[i])-1) < 1e-5 and all(abs(v[j]) < 1e-5 for j in range(3) if j != i):
            return ('+' if v[i] > 0 else '−') + name
    return tup(v, 3)


def values(program, t):
    keys = program.get('keys', [])
    if not keys: return [0., 0., 0.], [0., 0., 0.]
    left = right = keys[0]
    for right in keys[1:]:
        if t <= right['t']: break
        left = right
    f = MATH['u'](t, left['t'], right['t'], program.get('linear', False))
    def mix(k):
        a, b = vec(left[k]), vec(right[k])
        return [x+(y-x)*f for x,y in zip(a,b)]
    return mix('value'), mix('position')


def angle_difference(a, b):
    # Geodesic comparison of actual orientation matrices, never input distance.
    # Remove only f32 basis-length drift before acos; otherwise even two equal
    # recorded frames can acquire a spurious small angle from trace roundoff.
    def orthogonal(m):
        x=[v/norm(m[0]) for v in m[0]]
        projection=sum(a*b for a,b in zip(m[1],x))
        y=[a-projection*b for a,b in zip(m[1],x)];length=norm(y);y=[v/length for v in y]
        z=[x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0]]
        return [x,y,z]
    a,b=orthogonal(a),orthogonal(b)
    delta = MATH['mm'](a, MATH['tr'](b))
    return math.degrees(math.acos(max(-1., min(1., (sum(delta[i][i] for i in range(3))-1)/2))))


def evaluated(shot, t, actual=None):
    out = {'t': t, 'sides': []}
    for i, side in enumerate(['a', 'b']):
        p = shot.get(side)
        if not p: continue
        value, position = values(p, t)
        r = matrix(p, t)
        if actual:
            key = side.upper()
            observed = actual['rowMatrix'+key]
            assert len(observed) == 9
            error = max(abs(a-b) for a,b in zip(flat(r), observed))
            assert error < 3e-5, (shot['id'], actual['frame'], side, 'matrix', error)
            r = [observed[i:i+3] for i in range(0,9,3)]
            if p['kind'] in ['euler', 'rotvec']:
                field = ('eulerDegrees' if p['kind']=='euler' else 'rotationVectorRadians') + key
                flag = ('hasEulerParameters' if p['kind']=='euler' else 'hasRotationVector') + key
                assert actual[flag], (shot['id'], field)
                recorded = vec(actual[field])
                assert max(abs(a-b) for a,b in zip(value,recorded)) < 8e-4
                value = recorded
        steps = [dict(axis=axis(vec(s['axis'])), space=s['space'], degrees=s['degrees']*MATH['u'](t,s['start'],s['end'],p.get('linear',False))) for s in p.get('steps',[])]
        n = vec(p.get('axis', {'x':0,'y':1,'z':0}))
        if norm(n): n = [x/norm(n) for x in n]
        signed_angle = math.degrees(sum(a*b for a,b in zip(value,n))) if p['kind']=='rotvec' else None
        out['sides'].append({'kind':p['kind'],'value':value,'position':position,'steps':steps,'matrix':r,
                             'axis':n,'signedDegrees':signed_angle,'lengthRadians':norm(value),'nose':r[2]})
    out['differenceDegrees'] = angle_difference(out['sides'][0]['matrix'],out['sides'][1]['matrix']) if len(out['sides'])==2 else None
    out['maximumPairMatrixElementDifference'] = MATH['diff'](out['sides'][0]['matrix'],out['sides'][1]['matrix']) if len(out['sides'])==2 else None
    return out


def rows(shot, state, i):
    s = state['sides'][i];p = shot['a' if i==0 else 'b'];key=shot['id'];t=state['t'];pair=shot['pair']
    prefix = ('A · ' if i==0 else 'B · ') if pair else ''
    title = prefix + TITLES[key][i]
    if s['kind']=='euler':
        main = '현재 입력 (h,p,b) = ' + tup(s['value']) + '°'
        detail = '물체 → 직립 · 물체축 순서 Y → X → Z'
    elif s['kind']=='sequence':
        main = '현재 적용각: ' + ' → '.join(fmt(x['degrees'])+'°' for x in s['steps'])
        detail = ' → '.join(('물체 ' if x['space']=='body' else '직립 ')+x['axis'].lstrip('+') for x in s['steps'])
        initial = vec(p.get('initialEuler',{}))
        if any(abs(x)>1e-6 for x in initial): detail += ' · 시작 (h,p,b)=' + tup(initial) + '°'
    else:
        main = 'n='+axis(s['axis'])+' · 현재 각도 '+fmt(s['signedDegrees'])+'°'
        detail = 'e = '+tup(s['value'],3)+' rad'
    if key=='v6-02.B01':
        detail = '위치 변화 '+tup(s['position'])+' · b='+fmt(s['value'][2])+'°'
    elif key=='v6-02.B03': detail = '도착: h=p=b=0° · 물체 축=직립 축' if t>1-1e-6 else '처음 자세를 향해 세 입력 되돌리기'
    elif key=='v6-04.B02': detail = '+Y에서 원점 보기 · 양의 헤딩은 시계 방향'
    elif key=='v6-06.B01': detail = '기수 방향 유지 · 물체 X와 Y만 함께 회전'
    elif key=='v6-07.B01': detail = '원점 쪽에서 +Z 보기 · 양의 뱅크는 반시계'
    elif key=='v6-07.B02': detail = '회전 입력 고정 · 보이는 시계 방향만 바뀜'
    elif key=='v6-13.B02': detail = '세차 → 장동 → 자전 · 처음/끝에 Y축 재사용'
    elif key=='v6-15.B01': detail = '편집 입력 예 · h 먼저, p 다음 (b=0 유지)'
    elif key=='v6-18.B01': detail = '누적 h='+fmt(s['value'][0])+'° · 한 바퀴는 360°'
    elif key=='v6-20.B01': detail = '두 회전 직선이 겹침 · p=+90° 경계'
    elif key=='v6-20.B02': detail = '남는 값 h−b = '+fmt(s['value'][0]-s['value'][2])+'°'
    elif key=='v6-20.B03': detail = '남는 값 h+b = '+fmt(s['value'][0]+s['value'][2])+'°'
    elif key=='v6-27.B01': detail = 'h와 b 조절 효과 겹침 · p≈90°에 주의'
    elif key=='v6-27.B02':
        detail = '보간 진행 t='+fmt(t,2)+' · 끝 표현에 따라 경로가 다름'
        if abs(t-.5)<.015: detail = '절반: '+tup(s['value'])+'° (각 성분 선형 보간)'
    elif key=='v6-27.B03': detail = 't='+fmt(t,2)+' · 세 입력의 일정 변화율'
    elif key=='v6-30.B02': detail = '‖n‖=1 · 원점을 지나는 같은 축 주위 회전'
    elif key=='v6-31.B02': detail = '+Z 기수 → +X · X와 Z 함께 회전, Y 유지'
    elif key=='v6-32.B02': detail += ' · 길이 θ='+fmt(s['lengthRadians'],3)+' rad'
    elif key=='v6-34.B01':
        main = '같은 축 n=+Y · θ='+fmt(s['value'][0])+'°'
        detail = '90°×⅓=30° · 90°×2.65=238.5°'
    elif key=='v6-34.B02': detail += ' · 길이 ‖e‖='+fmt(s['lengthRadians'],3)+' rad ≥ 0'
    elif key=='v6-37.B02':
        main = '예제 시간 '+fmt(t,2)+' s · 누적 '+fmt(s['signedDegrees'])+'°'
        detail = '시간은 0→1초 예제를 천천히 관찰 · '+('720' if i==0 else '1080')+'°/s'
    elif key=='v6-38.B01': detail += ' · ‖e‖='+fmt(s['lengthRadians'],3)+' < 2π'
    elif key=='v6-38.B02': detail += ' · 대표각 θ≤π' if i==1 else ' · θ>π인 긴 입력'
    elif key=='v6-39.B02' and i==1: detail += ' · θ='+fmt(s['lengthRadians'],3)+' rad'
    elif key=='v6-40.B03':
        main = '물체 ω = (0,0,1) rad/s'
        detail = '세계 기준 ω = '+tup(s['nose'],2)+' rad/s'
    elif key=='v6-41.answer-y90':
        main = 'h='+fmt(s['value'][0])+'° · p=b=0°'
        detail = '목표 답: n=(0,1,0), θ=90° · e=(0,π/2,0)'
    if pair and t>1-1e-6:
        difference = state['differenceDegrees']
        if key=='v6-40.B01': detail = '끝 자세 차이 ≈ '+fmt(difference,3)+'° · 근사'
        elif state['maximumPairMatrixElementDifference']<5e-5: detail += ' · 끝 자세 일치'
        else: detail += ' · 끝 자세 다름'
    if not pair:
        heading = '입력과 결과를 구별해서 보기'
        extra = '기수 방향 = '+tup(s['nose'],2)+' (직립 기준)'
        if shot['model']=='top':
            extra='자전축 +Y 방향 = '+tup(s['matrix'][1],2)+' (직립 기준)'
        if key=='v6-40.B03':
            heading='해설용 속도 벡터의 좌표 변환'
            extra='이 예에서는 세계 기준 방향=직립 방향'
        if key=='v6-41.answer-y90': extra='현재 기수 = '+tup(s['nose'],2)+' · 처음 +Z'
        return [(title,38,GOLD,True),(main,44,VALUE,True),(detail,34,WHITE,False),(heading,30,MUTED,False),(extra,34,WHITE,False)]
    return [(title,30,GOLD,True),(main,38,VALUE,True),(detail,28,WHITE,False)]


def layout(shot, state):
    entries = []
    for i in range(2 if shot['pair'] else 1):
        if shot['pair']:
            box=(120+900*i,730,900+900*i,868)
            positions=[(box[0]+18,738),(box[0]+18,776),(box[0]+18,823)]
        else:
            box=(1100,288,1824,760)
            positions=[(1120,309),(1120,385),(1120,477),(1120,590),(1120,642)]
        text_rows=[]
        for (text,size,color,bold),pos in zip(rows(shot,state,i),positions):
            text=render_text(text)
            maxwidth=box[2]-pos[0]-18
            fontfile=BOLD_PATH if bold else FONT_PATH
            font=getfont(fontfile,size)
            minimum=27 if shot['pair'] else 30
            while font.getlength(text)>maxwidth and size>minimum:
                size-=1;font=getfont(fontfile,size)
            if font.getlength(text)>maxwidth:
                # Meaning is retained, never clipped/ellipsized. Long single
                # notes wrap into their reserved two-line slot.
                assert not shot['pair'],(shot['id'],text,float(font.getlength(text)),maxwidth)
                words=text.split(' ');lines=[];line=''
                for word in words:
                    candidate=(line+' '+word).strip()
                    if line and font.getlength(candidate)>maxwidth:lines.append(line);line=word
                    else:line=candidate
                if line:lines.append(line)
                assert len(lines)<=2,(shot['id'],text,lines)
            else:lines=[text]
            for j,line in enumerate(lines):
                y=pos[1]+j*(size+9)
                ink=font.getbbox(line)
                assert pos[0]+font.getlength(line)<box[2]-8 and y+size+12<880
                actual_ink=[pos[0]+ink[0],y+ink[1],pos[0]+ink[2],y+ink[3]]
                assert actual_ink[0]>=box[0] and actual_ink[2]<=box[2] and actual_ink[1]>=box[1] and actual_ink[3]<=box[3],(shot['id'],line,actual_ink,box)
                for prior in text_rows:
                    a=prior['pixelInkBox'];b=actual_ink
                    assert min(a[2],b[2])<=max(a[0],b[0]) or min(a[3],b[3])<=max(a[1],b[1]),(shot['id'],'text ink collision',prior['text'],line)
                text_rows.append(dict(text=line,x=pos[0],y=y,size=size,color=color,bold=bold,measuredWidth=float(font.getlength(line)),inkBox=list(ink),pixelInkBox=actual_ink))
        entries.append(dict(box=list(box),rows=text_rows))
    return entries


def prepare():
    control=read(ROOT/'shared/publishing/video-production-control.json')
    assert control['selectedVideo']==P.name and control['newProductionAuthorization']['fullProductionAuthorized']
    source=read(P/'script/revision-v6-article-flow/narration.ko.json')
    byscene={s['id']:s for s in source['scenes']}
    catalog=read(CATALOG);primary=read(H/'spatial-plan.json')
    assert len(catalog['shots'])==49 and len(TITLES)==49
    assert sum(b['durationFrames'] for s in primary['scenes'] for b in s['beats'] if b['renderer']=='Unity')==19020
    assert sum(b['durationFrames'] for b in primary['auxiliaryClips'])==180
    rows_out=[];count=0
    for shot in catalog['shots']:
        assert shot['id'] in TITLES
        samples=[]
        for f in range(61):
            t=f/60;state=evaluated(shot,t);display=layout(shot,state);count+=1
            if f in [0,15,30,45,60]:samples.append(dict(t=t,rows=display))
        scene=byscene[shot['sceneId']]
        rows_out.append(dict(id=shot['id'],scene=shot['sceneId'],auxiliary=shot['id']=='v6-41.answer-y90',pair=shot['pair'],titles=TITLES[shot['id']],
            explanationLines=scene['lines'],sampleDisplays=samples,
            inputSemantics='Euler values are authored HPB inputs, sequence values are ordered increments in their named frame, signed axis-angle input is distinct from nonnegative rotation-vector length; orientation result comes from actual row matrix, never Euler input subtraction.',
            actualCaptureValidation='pending actual frame states; all frame matrices and native input fields will be checked before any ASS/PNG is emitted'))
    plan=dict(schemaVersion=1,slug=P.name,revision='article-flow-v6',status='CPU readout plan ready; actual captures and encoded display review pending',
        inputs=dict(scriptSha256=sha(P/'script/revision-v6-article-flow/narration.ko.json'),catalogSha256=sha(CATALOG),spatialPlanSha256=sha(H/'spatial-plan.json'),helperSha256=sha(Path(__file__)),mathHelperSha256=sha(H/'spatial-check.py'),fontSha256=sha(FONT_PATH),boldFontSha256=sha(BOLD_PATH)),
        primaryCount=primary['spatialShotCount'],auxiliaryCount=len(primary.get('auxiliaryClips',[])),primaryFrames=19020,auxiliaryFrames=180,
        layout=dict(single=[1100,288,1824,760],pairs=[[120,730,900,868],[1020,730,1800,868]],captionReserve=880,termCardProtected=True,colors=dict(background=BG,body=WHITE,heading=GOLD,input=VALUE,secondary=MUTED)),
        CPUValidation=dict(plannedFrameStates=count,mathematicalOrientationAndTextBoundsPassed=True,noGpuOrMediaStarted=True,notActualCaptureEvidence=True),outputs=rows_out)
    save(H/'spatial-readout-plan.json',plan)
    print('Readout CPU plan ready:',len(rows_out),'clips;',count,'sample states; no capture/media job')
    return plan,{s['id']:s for s in catalog['shots']}


def clock(frame):
    cs=(frame*100)//60;h,cs=divmod(cs,360000);m,cs=divmod(cs,6000);s,cs=divmod(cs,100)
    return f'{h}:{m:02d}:{s:02d}.{cs:02d}'
def ass_color(color):
    c=color.lstrip('#');return '&H00'+c[4:6]+c[2:4]+c[0:2]+'&'
HEADER='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Readout,Malgun Gothic,38,&H00F5F5F5,&H00F5F5F5,&H001C1710,&H001C1710,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def ass_frame(frame,entries):
    result=''
    def event(layer,text):return f'Dialogue: {layer},{clock(frame)},{clock(frame+1)},Readout,,0,0,0,,{text}\n'
    for entry in entries:
        l,t,r,b=entry['box'];result+=event(1,r'{\an7\pos(0,0)\p1\bord0\shad0\c'+ass_color(BG)+'}'+f'm {l} {t} l {r} {t} {r} {b} {l} {b}'+r'{\p0}')
        for row in entry['rows']:
            text=row['text'].replace('{','').replace('}','')
            result+=event(2,rf'{{\an7\pos({row["x"]},{row["y"]})\fs{row["size"]}\b{1 if row["bold"] else 0}\c'+ass_color(row['color'])+r'\bord0\shad0}'+text)
    return result


def still(source,dest,entries):
    image=Image.open(source).convert('RGB');assert image.size==(1920,1080)
    draw=ImageDraw.Draw(image)
    for entry in entries:
        draw.rectangle(entry['box'],fill=BG)
        for row in entry['rows']:
            font=getfont(BOLD_PATH if row['bold'] else FONT_PATH,row['size'])
            # Match the normal top-of-line spacing used by libass/Windows font.
            draw.text((row['x'],row['y']),row['text'],font=font,fill=row['color'])
    image.save(dest);image.resize((375,211),Image.Resampling.LANCZOS).save(dest.with_name(dest.stem+'.375.png'))


def emit(plan,shots,args):
    capture=Path(args.capture_dir).resolve();receipt=read(capture/'spatial-capture-receipt.json')
    actual={r['id']:r for r in receipt['outputs']}
    selected=[s for s in shots.values() if (not args.id or s['id'] in args.id) and s['id'] in actual]
    if not args.id and not receipt['sampleOnly']:assert len(selected)==49
    out=capture/'readouts';out.mkdir(parents=True,exist_ok=True);outputs=[];maximum=0.;frames_checked=0
    for shot in selected:
        key=shot['id'];record=actual[key];count=record['frames']
        files={name:Path(v['path']) for name,v in record['files'].items()}
        for name,path in files.items():assert path.exists() and sha(path)==record['files'][name]['sha256']
        states=[json.loads(line) for line in files['anchors'].read_text(encoding='utf8').splitlines()]
        assert len(states)==count
        ass=HEADER;first=last=None
        for frame,source in enumerate(states):
            assert source['frame']==frame and source['shotId']==key
            t=source['normalizedTime'];assert abs(t-frame/(count-1))<1e-6
            state=evaluated(shot,t,source);display=layout(shot,state)
            for i,side in enumerate(['a','b']):
                if not shot.get(side):continue
                maximum=max(maximum,max(abs(a-b) for a,b in zip(flat(matrix(shot[side],t)),source['rowMatrix'+side.upper()])))
            ass+=ass_frame(frame,display);frames_checked+=1
            if frame==0:first=display
            if frame==count-1:last=display
        assfile=out/(key+'.ass');assfile.write_text(ass,encoding='utf-8-sig')
        firstpng=out/(key+'.first.png');lastpng=out/(key+'.last.png')
        still(files['firstFrame'],firstpng,first);still(files['lastFrame'],lastpng,last)
        outputs.append(dict(id=key,auxiliary=key=='v6-41.answer-y90',durationFrames=count,assFile=rel(assfile),firstDisplay=rel(firstpng),lastDisplay=rel(lastpng),
            inputs=dict(anchorsSha256=sha(files['anchors']),firstFrameSha256=sha(files['firstFrame']),lastFrameSha256=sha(files['lastFrame']),clipSha256=sha(files['clip'])),
            files=[dict(path=rel(f),sha256=sha(f)) for f in [assfile,firstpng,lastpng]],actualFrameStatesValidated=count,native375AndEncodedAssReview='pending direct inspection'))
    result=dict(schemaVersion=1,sampleOnly=receipt['sampleOnly'],inputs=dict(planSha256=sha(H/'spatial-readout-plan.json'),captureReceiptSha256=sha(capture/'spatial-capture-receipt.json')),
        outputs=outputs,checks=dict(actualFrameStatesValidated=frames_checked,maximumCPUVersusCaptureMatrixElementError=maximum,allTextBBoxesWithinReservedPanels=True,captionY880Protected=True,newMediaJobsStarted=0),
        scope='Actual authored captured math states, not measured commercial-game internals; endpoint comparisons use orientation matrices; runtime geometry unchanged')
    save(out/'outputs.json',result);print('Readouts emitted:',len(outputs),'clips;',frames_checked,'actual capture frames validated')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--emit',action='store_true');parser.add_argument('--capture-dir',default=str(O/'spatial-clips'));parser.add_argument('--id',action='append');arguments=parser.parse_args()
    prepared,catalog=prepare()
    if arguments.emit:emit(prepared,catalog,arguments)

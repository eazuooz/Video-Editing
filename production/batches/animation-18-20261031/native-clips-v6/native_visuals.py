"""Source-frame comparisons. This compositor never constructs a humanoid pose."""
from functools import lru_cache
from pathlib import Path
import math
import sys

from PIL import Image, ImageDraw, ImageFont
import numpy as np

from prepare import BATCH, HERE, ROOT, WORK, read

sys.path.insert(0, str(BATCH / 'contrast-v5/renderer'))
import sources
import compose

BG = '#080c0a'
WHITE = '#f3f5ef'
YELLOW = '#f2d787'
TEAL = '#81cfc5'
RED = '#f18b81'
GREEN = '#a4d987'
MUTED = '#abb9af'

REPAIR = {'A04': {'jab'}, 'A05': {'size', 'plane', 'top', 'twist'},
          'A07': {'gesture'}, 'A08': {'flow', 'edge', 'stance', 'overview', 'warrior'},
          'A10': {'recoil', 'turn'}, 'A11': {'upper'},
          'A12': {'expression', 'eyes', 'mouth', 'distance'},
          'A14': {'guard', 'slope'}, 'A15': {'grip', 'scale', 'count'},
          'A17': {'fkik', 'hint'}, 'A18': {'head', 'tilt', 'curves', 'gaze', 'wrist'}}

TITLES = {
 ('A04','jab'): '기존 펀치 동작의 준비와 타격',
 ('A05','size'): '준비 자세와 몸 전체가 뻗은 자세',
 ('A05','plane'): '어깨와 손끝이 향하는 방향',
 ('A05','top'): '위에서 확인하는 공격 경로',
 ('A05','twist'): '공격하는 팔과 균형을 잡는 팔',
 ('A07','gesture'): '작은 시작 몸짓과 큰 반응',
 ('A08','flow'): '몸의 흐름이 보이는 두 자세',
 ('A08','edge'): '팔과 몸 사이에 남는 빈 공간',
 ('A08','stance'): '몸을 받치는 발의 위치',
 ('A08','overview'): '완성된 동작에서 자세 읽기',
 ('A08','warrior'): '전사 자세의 몸통과 디딤발',
    ('A10','recoil'): '반응 시작 → 몸이 밀림 → 넘어짐',
 ('A10','turn'): '같은 피격 동작을 다른 시점에서',
 ('A11','upper'): '같은 펀치, 다른 시간 배분',
 ('A15','grip'): '완성된 잡기 동작의 손가락',
 ('A15','scale'): '같은 손동작, 다른 화면 크기',
 ('A15','count'): '화면에 보이는 손과 처리할 대상',
}


@lru_cache(None)
def font(size):
    return ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', size)


def text(draw, xy, value, size=40, color=WHITE, width=1780):
    while draw.textlength(value, font=font(size)) > width and size > 28:
        size -= 1
    draw.text(xy, value, font=font(size), fill=color, anchor='lt')


@lru_cache(48)
def native_image(key, frame):
    build,files=native_input(key)
    frame = min(build['frames'] - 1, max(0, round(frame)))
    with Image.open(files[frame]) as im:
        return im.convert('RGB')


@lru_cache(None)
def native_input(key):
    build=read(WORK/(key+'-build.json'));receipt=read(WORK/(key+'-capture.json'))
    assert receipt['builderSha256']==build['builderSha256'], 'Native capture definition changed; recapture before adoption.'
    files=tuple(sorted((WORK/'frames'/key).glob('*.png')))
    assert len(files)==build['frames']
    return build,files


def native_crop(key, frame, side=1):
    im = native_image(key, frame)
    # Use one fixed crop for the entire performance, never a per-frame size normalization.
    if key == 'anim_GrabValve_R':
        assert len(native_input(key)[0]['yaws'])==1, 'The rejected floor-intersecting hand audition must not enter production.'
        box = (550, 260, 1370, 940)
    elif key=='anim_OpeningValve_R':
        assert len(native_input(key)[0]['yaws'])==1
        box=(550,260,1370,940)
    elif key=='A_Guard_idle':
        box=(780,200,1250,1020)
    elif key == 'am_Ready_Fight_01_Knockdown_A':
        box = (20 + 960 * side, 180, 940 + 960 * side, 925)
    else:
        box = (60 + 960 * side, 220, 915 + 960 * side, 930)
    return im.crop(box)


def legacy_crop(ep, key, frame, side=1):
    source = sources.source(ep, key)
    frame = min(source['definition']['frames'] - 1, max(0, round(frame)))
    im = sources.image(ep, key, frame)
    x0, y0, x1, y1 = sources.bounds(ep, key)
    shift = sources.panel_offset(ep, key, side)
    return im.crop((x0 + shift, y0, x1 + shift, y1))


def picture(ep, key, n, side=1):
    if ep in ('A04', 'A11'):
        return native_crop('AS_ComboHands', n, side)
    if ep == 'A10':
        if key == 'recoil':
            return legacy_crop('A10', 'recoil', n, 1)
        return native_crop('am_Ready_Fight_01_Knockdown_A', min(n, 50), side)
    if ep == 'A15':
        return native_crop('anim_GrabValve_R', n, side)
    if ep == 'A05':
        return legacy_crop(ep, 'top' if key == 'top' else 'impact' if key == 'size' else key, n, 1)
    if ep == 'A07':
        return legacy_crop(ep, 'gesture', n, 1)
    return special_picture(ep, key, n, side)


def paste(canvas, picture, box, factor=1):
    x, y, w, h = box
    scale = min(w / picture.width, h / picture.height) * factor
    dim = (max(1, round(picture.width * scale)), max(1, round(picture.height * scale)))
    im = picture.resize(dim, Image.Resampling.LANCZOS)
    at = (round(x + (w - dim[0]) / 2), round(y + (h - dim[1]) / 2))
    canvas.paste(im, at)
    return (*at, *dim)


def layout(ep, key, mode, counter=None):
    im = Image.new('RGB', (1920, 1080), BG)
    d = ImageDraw.Draw(im)
    title = TITLES[(ep, key)] if (ep, key) in TITLES else ('전사 자세의 흐름' if key == 'warrior' else compose.contract(ep, key)['heading'])
    text(d, (64, 42), title, 62, YELLOW, 1570)
    text(d, (64, 119), '언리얼 · 애니메이션 시연', 30, MUTED)
    label = '단계 비교' if mode == 'stages' else '기본 속도' if mode == 'native' else '느린 분석'
    text(d, (1590, 62), label, 32, WHITE, 290)
    if counter:
        text(d, (1510, 871), f'기본 속도 {counter}/3', 30, MUTED, 340)
    return im


def clock(ep, key, n):
    if ep == 'A04':
        return min(131, max(0, n))
    if ep == 'A11':
        return min(131, max(0, n))
    if ep == 'A10':
        return min(197, max(0, round(n * 197 / 179)))
    if ep == 'A15':
        return min(109, max(0, round(n * 109 / 179)))
    return max(0, n)


def labels(ep, key):
    if (ep, key) == ('A05', 'twist'):
        return ['전체 자세', '공격팔과 지지팔에 주목']
    if (ep, key) == ('A10', 'turn'):
        return ['옆에서 본 같은 동작', '비스듬히 본 같은 동작']
    if ep == 'A07':
        return ['반응이 시작되는 순간', '큰 몸짓이 드러나는 순간']
    if ep == 'A10':
        return ['반응 초기의 기준 자세', '이어서 나타나는 피격 반응']
    if ep == 'A11':
        return ['고르게 재생 위치 이동', '준비 후 빠르게 뻗기']
    if ep == 'A15':
        return ['펴진 손', '쥐어 가는 손'] if key == 'grip' else ['가까이서 관찰', '플레이 화면 크기']
    return ['준비 자세', '타격 자세']


def draw(ep, key, n, mode='compare', counter=None):
    if ep in ('A08', 'A12', 'A14', 'A17', 'A18'):
        return special_draw(ep, key, n, mode, counter)
    im = layout(ep, key, mode, counter)
    d = ImageDraw.Draw(im)
    if mode == 'native':
        at = n if ep=='A15' else clock(ep,key,n)
        pane = legacy_crop('A10', 'recoil', min(179,n),1) if (ep,key)==('A10','turn') else picture(ep,key,at)
        paste(im, pane, (205, 190, 1510, 640))
        text(ImageDraw.Draw(im), (80, 837), '동작 전체를 먼저 이어서 봅니다.', 39)
        return im
    if mode == 'stages':
        samples = ([8, 24, 46, 60] if ep in ('A04','A11') else [0, 60, 120, 179])
        names = (['준비', '주먹이 나감', '팔이 뻗음', '팔을 거둠'] if ep in ('A04','A11') else
                 ['반응 시작', '몸이 밀림', '넘어지는 몸', '넘어진 뒤'] if ep == 'A10' else
                 ['시작', '변화 시작', '주요 자세', '다음 자세'])
        for j, (f, name) in enumerate(zip(samples, names)):
            x = 55 + j * 465
            text(d, (x, 174), name, 42, (TEAL, YELLOW, RED, GREEN)[j], 435)
            pane=legacy_crop('A10','recoil',f,1) if (ep,key)==('A10','turn') else picture(ep,key,clock(ep,key,f))
            paste(im,pane,(x,236,425,520))
            d.line((x, 791, x + 425, 791), fill=(TEAL, YELLOW, RED, GREEN)[j], width=7)
        return im
    at = clock(ep, key, n)
    for side, x in enumerate((55, 985)):
        lab=labels(ep,key)[side]
        if (ep,key)==('A15','count'): lab=['한 캐릭터의 손','캐릭터가 많은 경우'][side]
        text(d, (x, 172), lab, 42, TEAL if not side else RED, 875)
        use_side = side if (ep, key) == ('A10', 'turn') else 1
        frame = at
        if ep == 'A11':
            u = np.clip((n - 14) / 51, 0, 1)
            frame = round(8 + 38 * (u if side == 0 else np.clip((u - .65) / .35, 0, 1)))
        elif ep == 'A05' and key == 'twist':
            frame = at
        elif (ep, key) != ('A10','turn') and not side:
            frame = min(at, 12 if ep != 'A07' else 24)
        scale = .36 if ep == 'A15' and key in ('scale','count') and side else 1
        if (ep,key)==('A15','count') and side:
            for j in range(12):
                paste(im,picture(ep,key,frame,use_side),(x+(j%4)*215,235+(j//4)*176,205,166))
            continue
        box = paste(im, picture(ep, key, frame, use_side), (x, 235, 875, 535), scale)
        if ep=='A05' and key in ('plane','top'):
            bx,by,bw,bh=box
            source=sources.source(ep,key);definition=source['definition']
            crop=sources.bounds(ep,key);shift=sources.panel_offset(ep,key,1)
            def plotted(local):
                p=sources.projected(definition,local,1)
                return (bx+(p[0]-crop[0]-shift)*bw/(crop[2]-crop[0]),
                        by+(p[1]-crop[1])*bh/(crop[3]-crop[1]))
            reference=sources.points(ep,key,81,1)['hand_r']
            current=sources.points(ep,key,min(179,frame),1)['hand_r']
            plane=[plotted([reference[0],yy,zz]) for yy,zz in
                   ((reference[1]-65,0),(reference[1]+65,0),(reference[1]+65,185),(reference[1]-65,185),(reference[1]-65,0))]
            pen=ImageDraw.Draw(im)
            # Clip editorial guides to the actual image panel.
            plane=[(min(bx+bw,max(bx,px)),min(by+bh,max(by,py))) for px,py in plane]
            pen.line(plane,fill='#75a7ed',width=6,joint='curve')
            px,py=plotted(current)
            color=GREEN if abs(current[0]-reference[0])<8 else RED
            if bx<=px<=bx+bw and by<=py<=by+bh:
                pen.ellipse((px-18,py-18,px+18,py+18),outline=color,width=6)
        if ep == 'A05' and key == 'twist' and side:
            bx, by, bw, bh = box
            pen = ImageDraw.Draw(im)
            source=sources.source(ep,key)
            crop=sources.bounds(ep,key);shift=sources.panel_offset(ep,key,1)
            points=sources.points(ep,key,frame,1)
            for suffix,color in (('r',RED),('l',TEAL)):
                chain=[]
                for bone in ('upperarm','lowerarm','hand'):
                    p=sources.projected(source['definition'],points[bone+'_'+suffix],1)
                    chain.append((bx+(p[0]-crop[0]-shift)*bw/(crop[2]-crop[0]),
                                  by+(p[1]-crop[1])*bh/(crop[3]-crop[1])))
                pen.line(chain,fill=color,width=7,joint='curve')
                hand=chain[-1]
                pen.ellipse((hand[0]-19,hand[1]-19,hand[0]+19,hand[1]+19),outline=color,width=6)
    note = ('파랑: 기준 평면 · 원: 현재 손의 위치' if ep=='A05' and key in ('plane','top') else
            '같은 동작 · 재생 시간 배분만 변경' if ep == 'A11' else
            '같은 동작 · 보는 방향만 변경' if (ep,key)==('A10','turn') else
            '준비와 타격에서 어깨·몸통·다리의 역할을 보세요.' if ep=='A05' else
            '시작의 작은 신호와 이어지는 큰 몸짓을 비교하세요.' if ep=='A07' else
            '반응이 시작되는 자세와 넘어지는 자세를 비교하세요.' if ep=='A10' else
            '손가락이 굽는 방향과 화면에서 차지하는 크기를 보세요.' if ep=='A15' else
            '주먹이 나가기 전의 준비와 타격 자세를 비교하세요.')
    text(ImageDraw.Draw(im), (80, 832), note, 38)
    return im


def special_picture(ep, key, n, side):
    from native_specials import source_picture
    return source_picture(ep, key, n, side)


def special_draw(ep, key, n, mode, counter):
    from native_specials import draw_special
    return draw_special(ep, key, n, mode, counter)

"""Editorial plates for the first design-specifics episode."""

from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
UNREAL = ROOT / 'production/batches/animation-18-20261031/local/real-clips-v2/study-frames/A03-attack'
BG, PANEL, LINE = '#0a110d', '#121d17', '#304239'
GOLD, WHITE, MUTED = '#f2d786', '#f5f4ec', '#b7c9bf'
TEAL, CORAL = '#79d2ca', '#f08a75'


@lru_cache(maxsize=24)
def font(size):
    return ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', size)


def label(draw, text, x, y, size=40, color=WHITE, anchor='lt'):
    draw.text((x, y), text, fill=color, font=font(size), anchor=anchor)


def board(title, source):
    image = Image.new('RGB', (1920, 1080), BG)
    draw = ImageDraw.Draw(image)
    label(draw, title, 80, 63, 62, GOLD)
    label(draw, source, 1830, 67, 34, MUTED, 'rt')
    draw.line((80, 153, 1840, 153), fill=LINE, width=2)
    return image, draw


@lru_cache(maxsize=85)
def attack_plate(frame):
    with Image.open(UNREAL / f'{frame:06d}.png') as image:
        crop = image.crop((505, 130, 1420, 1050)).convert('RGB')
        return crop.resize((550, 553), Image.Resampling.LANCZOS)


def hit_comparison(seconds, total):
    image, draw = board('Hit Stop (히트 스톱)', '언리얼 클립 · 자체 시연')
    slow = seconds >= 2.1
    replay_speed = 88 / (60 * max(total - 2.8, 1))
    time = (seconds - 2.1) * replay_speed if slow else seconds
    clock = min(88, round(time * 60))
    for side, title in enumerate(('접촉 직후 진행', '접촉 자세에서 정지')):
        x = 80 + side * 910
        color = CORAL if side else TEAL
        hold = 14 if side else 0
        frame = min(clock, 35) + max(0, clock - 35 - hold)
        label(draw, title, x, 192, 45, color)
        draw.rectangle((x, 262, x + 835, 815), fill=PANEL)
        image.paste(attack_plate(frame), (x + 142, 262))
        if 34 <= frame <= 38:
            draw.ellipse((x + 484, 506, x + 570, 592), outline='#a13f34', width=9)
        end = x + 830
        draw.line((x, 844, end, 844), fill=LINE, width=11)
        if hold:
            draw.line((x + 330, 844, x + 462, 844), fill=CORAL, width=11)
        cursor = x + round(830 * clock / 88)
        draw.line((cursor, 822, cursor, 866), fill=WHITE, width=5)
    label(draw, '기본 속도' if not slow else '느리게 관찰', 1820, 880, 30, MUTED, 'rt')
    return image


def impact_reading(seconds, total):
    image, draw = board('피격 위치를 남기는 정지', '원리 도식')
    x0, x1 = 175, 1745
    y0, y1 = 245, 704
    draw.rectangle((x0, y0, x1, y1), fill=PANEL, outline=LINE, width=3)
    contact_x, contact_y = 950, 440
    stage_time = min(1, seconds / max(total - .4, .1))
    marker = min(1, stage_time / .42)
    terrain = [(x0, 665), (320, 642), (490, 662), (590, 601), (705, 664), (850, 651),
               (1015, 672), (1140, 607), (1280, 668), (1500, 656), (x1, 670)]
    draw.line(terrain, fill=TEAL, width=5, joint='curve')
    if stage_time < .42:
        bullet = round(375 + 575 * marker)
        draw.ellipse((bullet - 13, 427, bullet + 13, 453), fill=CORAL)
        draw.polygon([(954, 440), (1020, 401), (1008, 441), (1020, 480)], fill=TEAL)
        label(draw, '탄이 닿기 직전', 220, 285, 42)
    else:
        radius = round(27 + 110 * min(1, (stage_time - .42) / .34))
        draw.ellipse((contact_x - radius, contact_y - radius, contact_x + radius, contact_y + radius),
                     outline=GOLD, width=6)
        draw.ellipse((contact_x - 12, contact_y - 12, contact_x + 12, contact_y + 12), fill=CORAL)
        label(draw, '기체가 사라진 자리', 220, 285, 42, GOLD)
        draw.line((708, 333, contact_x - 20, contact_y - 23), fill=GOLD, width=5)
        if stage_time >= .84:
            ship_x = round(340 + 600 * (stage_time - .84))
            draw.polygon([(ship_x + 53, 475), (ship_x, 438), (ship_x + 10, 475), (ship_x, 512)], fill=TEAL)
    for x, word, progress in [(295, '접근', 0), (750, '피격 위치', .42), (1240, '다음 기체', .84)]:
        label(draw, word, x, 790, 42, GOLD if stage_time >= progress else MUTED)
    return image


def effects_timeline(seconds, total):
    image, draw = board('같은 충돌, 다른 화면', '원리 도식')
    progress = min(1, seconds / max(total - .4, .1))
    start, impact, end = 502, 920, 1740
    rows = [('충돌 판정', '접촉 한 번', GOLD), ('게임 진행', '정지 뒤 재개', TEAL),
            ('표시 위치', '짧게 흔들림', CORAL), ('시간 속도', '느리게 진행', TEAL)]
    draw.line((impact, 218, impact, 795), fill=GOLD, width=4)
    label(draw, '접촉 순간', impact, 190, 40, GOLD, 'mt')
    for index, (title, result, color) in enumerate(rows):
        y = 320 + 144 * index
        label(draw, title, 95, y - 22, 45, WHITE)
        draw.line((start, y, end, y), fill=LINE, width=11)
        phase = max(0, min(1, (progress - index * .19) / .24))
        if phase:
            last = impact + round((85 if index == 0 else 440) * phase)
            draw.line((impact, y, last, y), fill=color, width=11)
            label(draw, result, 1460, y - 62, 36, color)
    label(draw, '판정이 끝난 뒤 화면 효과를 적용', 95, 837, 39, WHITE)
    return image


@lru_cache(maxsize=3)
def opening_still(index):
    folder = Path('C:/Users/1/Videos/YamyamProduction/design-specifics-18-20261111/DS01-assembly')
    with Image.open(folder / f'finish-still-{index}.png') as source:
        return source.convert('RGB').resize((544, 306), Image.Resampling.LANCZOS)


def finish_result(seconds, total):
    image, draw = board('공격에서 경기 종료까지', '실제 게임 화면 · 정지 분석')
    active = min(2, int(seconds / max(total, .1) * 3))
    for i, title in enumerate(('접촉 직전', '피니시 줌', '경기 종료')):
        x = 82 + 603 * i
        color = GOLD if i == active else MUTED
        label(draw, title, x, 267, 46, color)
        image.paste(opening_still(i), (x, 346))
        draw.line((x, 679, x + 544, 679), fill=color, width=8)
    label(draw, '가까워진 화면에서 마지막 공격을 읽을 수 있습니다', 82, 781, 43)
    return image


RENDERERS = {'01': finish_result, '03': hit_comparison, '06': impact_reading, '08': effects_timeline}

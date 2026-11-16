"""Meaning-matched editorial markers for the two-Stalfos example."""
from PIL import ImageDraw, ImageFont

FONT = 'C:/Windows/Fonts/malgunbd.ttf'
INK = '#f5f5f5'
ACTIVE = '#ffbe65'
WAITING = '#77ded6'


def panel(d, text, xy, color, size=35):
    f = ImageFont.truetype(FONT, size)
    box = d.textbbox(xy, text, font=f, anchor='mm')
    d.rounded_rectangle((box[0]-16, box[1]-10, box[2]+16, box[3]+10), 12,
                        fill='#071316', outline=color, width=4)
    d.text(xy, text, font=f, fill=color, anchor='mm')


def annotate(im, beat, source_seconds=None):
    d = ImageDraw.Draw(im)
    if beat.get('mode') == 'turn-taking-intents':
        panel(d, '공격 차례는 한 명씩', (492, 470), ACTIVE, 39)
        panel(d, '다른 적은 차례 대기', (492, 1322), WAITING, 39)
    if beat.get('annotation') == 'two-stalfos-waiting':
        panel(d, '주목한 상대와 전투', (245, 512), ACTIVE)
        panel(d, '다른 적은 차례 대기', (740, 512), WAITING)
        # Editorial guides apply only while both fighters are actually visible.
        if source_seconds is not None and 203 <= source_seconds <= 204.0:
            t = (source_seconds-203)/2.65
            left = (275+115*t, 396+215+270)
            right = (715+20*t, 396+215+255)
            for point, x, color in [(left,245,ACTIVE),(right,740,WAITING)]:
                px, py = point
                d.line((x,546,px,py-54), fill=color, width=7)
                d.polygon([(px,py-42),(px-13,py-65),(px+13,py-65)], fill=color)
                d.ellipse((px-45,py-65,px+45,py+65), outline=color, width=7)
    elif beat.get('annotation') == 'next-stalfos-target':
        panel(d, '한 적을 쓰러뜨린 뒤 다음 상대', (492, 512), WAITING, 38)
    return im

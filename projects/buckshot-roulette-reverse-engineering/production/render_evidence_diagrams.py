"""Independent evidence diagrams for the Buckshot documentary, not game footage.

Preparation is the default. Rendering requires explicit --render and measured
paragraph durations. Cue offsets can come from checked speech alignment; omitted
offsets are visibly recorded as proportional-text estimates awaiting moving QA.
No extracted source code is read or displayed by this renderer.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import re
import sys

from PIL import ImageFont
from assemble_documentary import (
    PROJECT, ROLE_COLORS, ass_header, bgr, command, digest, event, load, now,
    probe, save, tool, video_stream,
)

FPS = 60
FONT = Path('C:/Windows/Fonts/malgun.ttf')
BOLD = Path('C:/Windows/Fonts/malgunbd.ttf')
MONO = Path('C:/Windows/Fonts/consola.ttf')
LOCAL = PROJECT / 'production/local/evidence-diagrams'
WHITE, YELLOW, TEAL, RED, GREEN, GRAY = (
    ROLE_COLORS[k] for k in ['text', 'heading', 'focus', 'problem', 'result', 'secondary']
)

# Each anchor is an exact phrase in the independently written approved narration.
# Values are never presented as measurements of these illustrative queue states.
SPECS = {
    '02-p01': ('패키지 안에서 확인한 자료', [
        ('package', '우선 게임이 어떤 자료로'), ('reader', '패키지 구조를 분석하는 도구'),
        ('files', '내부 파일이'), ('scripts', '그중에는 게임의 동작을')]),
    '02-p02': ('함수가 바꾸는 값을 따라가기', [
        ('text', '이번에 확인한 파일은'), ('follow', '그래서 기계어를'),
        ('shoot', '사격을 처리하는 부분'), ('turn', '차례를 넘기는 부분'),
        ('items', '아이템을 사용하는 부분'), ('connect', '연결하면서 규칙을')]),
    '03-p01': ('탄환은 언제 정해질까?', [
        ('question', '먼저 궁금했던 것은'), ('random', '방아쇠를 당길 때마다'),
        ('ordered', '확인한 코드에서는'), ('front', '앞에서부터 한 발씩')]),
    '03-p02': ('앞칸에 서로 다른 세 가지 동작', [
        ('queue', '줄을 서 있는 표라고'), ('blank', '맨 앞이 공포탄이면'),
        ('consume', '한 발을 쓰고 나면'), ('next', '두 번째 칸이'),
        ('peek', '돋보기는 바로'), ('preserve', '확인해도 탄환을'),
        ('eject', '맥주는 앞칸의'), ('advance', '그러면 피해 없이')]),
    '03-p03': ('사용한 탄환과 다음 판단의 연결', [
        ('compare', '결과를 새로 뽑는 방식과'), ('different', '화면에서는 비슷해 보여도'),
        ('history', '앞에서 어떤 탄환이'), ('remaining', '다음 판단과 연결되는')]),
    '04-p01': ('같은 공포탄, 다른 다음 차례', [
        ('state', '탄환의 순서만 만들면'), ('turn', '아직 누구의 차례가'),
        ('self', '자신에게 공포탄을'), ('opponent', '상대에게 공포탄을'),
        ('compare', '공포탄이라는 결과는')]),
    '04-p02': ('차례와 함께 확인할 상태', [
        ('cuffs', '여기에 수갑이 들어오면'), ('reload', '다만 마지막 탄환을'),
        ('death', '체력이 다했을 때도'), ('together', '이렇게 탄환 수')]),
    '04-p03': ('톱은 탄환 종류가 아니라 피해를 변경', [
        ('saw', '톱은 또 다른 값을'), ('one', '실탄의 기본 피해가 하나라면'),
        ('two', '톱을 사용했을 때는'), ('blank', '그렇다고 공포탄까지'),
        ('roles', '아이템이 탄환의 종류를')]),
    '05-p01': ('딜러가 알고 있는 정보부터', [
        ('state', '이제 같은 상태를'), ('branches', '여기서 딜러의 판단은'),
        ('known', '현재 탄환을 알고 있으면'), ('live', '실탄은 플레이어에게'),
        ('blank', '공포탄은 자신에게')]),
    '05-p02': ('모드에 따라 달라지는 정보 사용', [
        ('unknown', '확실한 정보가 없을 때의'), ('story', '일반 모드에서는'),
        ('endless', '무한 모드에서는'), ('tie', '수가 같으면'),
        ('items', '아이템을 고르는 조건도'), ('peek', '돋보기로 정보를 얻은 뒤'),
        ('saw', '확인한 실탄에 톱을'), ('structure', '판단을 한 덩어리로')]),
    '06-p01': ('입력 → 행동 → 기대한 결과', [
        ('independent', '이 구조를 바탕으로'), ('fixture', '예를 들어 공포탄이'),
        ('shoot', '자신을 선택했을 때'), ('queue', '탄환은 줄어들고'),
        ('hp', '체력은 그대로이며'), ('turn', '차례는 유지되는지'),
        ('check', '같은 입력에서 기대한')]),
    '06-p02': ('규칙 검사와 화면 연결 검사', [
        ('rules', '독립적으로 작성한 규칙 코드에서는'), ('screen', '하지만 화면을 연결하자'),
        ('guard', '도구를 사용하는 동작이 끝나기 전에'),
        ('wording', '수갑 때문에 차례가'), ('integration', '이 부분을 고친 뒤'),
        ('meaning', '숫자만 보는 대신')]),
    '08-p01': ('관찰한 핵심 규칙을 새롭게 구현', [
        ('observe', '처음에 본 자기 공포탄과'), ('rules', '탄환의 순서와 차례 처리라는'),
        ('prototype', '우리는 그중 핵심 동작을'), ('scope', '삼백일흔네 개의 검사는'),
        ('result', '이번 결과물은')]),
    '08-p02': ('읽은 자료와 보이는 결과를 연결', [
        ('tools', '인공지능과 도구를 함께 쓰면'), ('evidence', '그래도 결과를 믿으려면'),
        ('read', '무엇을 읽었고'), ('input', '어떤 입력을 시험했으며'),
        ('change', '화면에 어떤 변화가'), ('connect', '이번에 만든 작은 게임은')]),
}


def ftime(value):
    return round(float(value) * FPS) / FPS


def relative(path):
    return str(Path(path).relative_to(PROJECT)).replace('\\', '/')


class Board:
    def __init__(self, key, duration, title, values):
        self.key, self.duration, self.title = key, duration, title
        self.values = values
        self.lines = ass_header('Malgun Gothic', 48)
        self.layout = []

    def text(self, a, z, x, y, text, size=48, color=WHITE, bold=False,
             width=1760, move=None, fade=False):
        if size < 48:
            raise ValueError('Main text may not be smaller than 48px')
        if any(c in text for c in '{}\\'):
            raise ValueError('Only literal text accepted')
        font = ImageFont.truetype(str(BOLD if bold else FONT), size)
        parts = text.split('\n')
        # Include font ascender/descender and 1.25 line pitch; no caption overlap.
        text_width = max(font.getlength(line) for line in parts)
        text_height = len(parts) * math.ceil(size * 1.25)
        positions = [(x, y)] if move is None else [(x, y), move]
        for px, py in positions:
            if px < 40 or py < 26 or px + text_width > 1880 or py + text_height > 876:
                raise ValueError(f'Out of safe area {self.key}: {text} at {px},{py}; {text_width}x{text_height}')
        if text_width > width:
            raise ValueError(f'Text exceeds allocated width in {self.key}: {text} ({text_width}>{width})')
        ms = min(620, round((z-a)*350))
        pos = f'\\pos({x},{y})' if move is None else f'\\move({x},{y},{move[0]},{move[1]},0,{ms})'
        tags = f'\\an7{pos}\\fs{size}\\b{int(bold)}\\1c&H{bgr(color)}&\\bord0\\shad0'
        if fade and z-a > .3:
            tags += '\\fad(100,0)'
        event(self.lines, a, z, '{'+tags+'}'+text.replace('\n', '\\N'), 4)
        self.layout.append({'text': text, 'fontPx': size, 'bounds': [x,y,x+text_width,y+text_height],
                            'startSeconds': a, 'endSeconds': z, 'roleColor': color})

    def path(self, a, z, path, color=TEAL, stroke=5, fill=False, move=None):
        pos = '\\pos(0,0)' if move is None else f'\\move(0,0,{move[0]},{move[1]},0,620)'
        tags = f'\\an7{pos}\\p1\\1c&H{bgr(color)}&\\3c&H{bgr(color)}&\\bord{stroke}\\shad0'
        if not fill:
            tags += '\\1a&HFF&'
        event(self.lines, a, z, '{'+tags+'}'+path+'{\\p0}', 1)

    def rect(self, a, z, x, y, w, h, color=GRAY, fill=False, move=None):
        if x < 40 or y < 26 or x+w > 1880 or y+h > 876:
            raise ValueError(f'Unsafe diagram geometry in {self.key}')
        self.path(a,z,f'm {x} {y} l {x+w} {y} {x+w} {y+h} {x} {y+h} {x} {y}',color,4,fill,move)

    def arrow(self, a, z, x1, y1, x2, y2, color=TEAL, reveal=True):
        if min(x1,x2)<40 or max(x1,x2)>1880 or min(y1,y2)<26 or max(y1,y2)>870:
            raise ValueError('Arrow outside safe content area')
        steps=12 if reveal and z-a>.6 else 1
        for step in range(steps):
            start=a + min(.45,(z-a)*.2)*step/steps
            stop=a + min(.45,(z-a)*.2)*(step+1)/steps if step<steps-1 else z
            f=(step+1)/steps
            tx,ty=x1+(x2-x1)*f,y1+(y2-y1)*f
            angle=math.atan2(y2-y1,x2-x1)
            bx,by=tx-19*math.cos(angle),ty-19*math.sin(angle)
            px,py=12*math.sin(angle),-12*math.cos(angle)
            self.path(start,stop,f'm {x1} {y1} l {tx:.2f} {ty:.2f} m {bx+px:.2f} {by+py:.2f} l {tx:.2f} {ty:.2f} {bx-px:.2f} {by-py:.2f}',color,4)

    def header(self):
        self.text(0,self.duration,80,52,self.title,60,YELLOW,True,width=1370,fade=False)
        self.text(0,self.duration,1450,65,'분석 원리도',48,GRAY,width=430,fade=False)

    def caption(self, a,z,text,color=GRAY):
        self.text(a,z,80,788,text,48,color,width=1760)

    def code(self,a,z,x,y,line,emphasized=False):
        """Syntax-coloured exact excerpts of our authored code, never recovered code."""
        size=56
        font=ImageFont.truetype(str(MONO),size)
        width=font.getlength(line)
        if x<40 or x+width>1880 or y<26 or y+70>876:
            raise ValueError(f'Code outside readable area: {line}')
        tokens=re.findall(r'[A-Za-z_]\w*|\d+|[^\w\s]|\s+',line)
        keywords={'var','bool','and','not','await','true','false'}
        body=''
        cursor=0
        for token in tokens:
            tail=line[cursor+len(token):]
            color='C9A3EA' if token in keywords else YELLOW if token.isdigit() else TEAL if re.match(r'^\s*\(',tail) and token.strip() and (token[0].isalpha() or token[0]=='_') else 'F0F2ED'
            body+='{\\1c&H'+bgr(color)+'&}'+token
            cursor+=len(token)
        event(self.lines,a,z,f'{{\\an7\\pos({x},{y})\\fnConsolas\\fs{size}\\bord0\\shad0}}'+body,4)
        if emphasized:
            self.rect(a,z,x-25,y+7,7,57,YELLOW,True)
        self.layout.append({'text':line,'fontPx':size,'font':'Consolas','bounds':[x,y,x+width,y+70],
                            'startSeconds':a,'endSeconds':z,'semanticSyntaxColors':True,
                            'lineMarkerMeaning':'currently discussed excerpt, not execution trace'})

    def queue(self,a,z,items,x=360,y=344,selected=False,slide=False):
        gap=276
        for i,item in enumerate(items):
            xx=x+i*gap
            col=RED if item=='실탄' else TEAL
            old=xx+gap if slide else xx
            offset=(-gap,0) if slide else None
            self.rect(a,z,old,y,224,126,col,move=offset)
            self.text(a,z,old+22,y+26,item,60,col,True,width=184,
                      move=(xx+22,y+26) if slide else None)
        if items:
            self.text(a,z,x+40,y+152,'맨 앞',48,YELLOW,True,width=225)
            self.arrow(a,z,x+112,y+140,x+112,y+130,YELLOW,False)
        if selected and items:
            self.rect(a,z,x-12,y-12,248,150,YELLOW)


def evidence_values():
    paths = [
        PROJECT/'planning/package-inventory.json', PROJECT/'planning/mechanics-findings.json',
        PROJECT/'production/local/test-evidence/rules-test-report.json',
        PROJECT/'production/local/test-evidence/integration-test-report.json',
        PROJECT/'production/local/test-evidence/main-integration-audit.json',
        PROJECT/'prototype/tests/test_rules.gd', PROJECT/'prototype/tests/test_integration.gd',
        PROJECT/'prototype/scripts/rules.gd', PROJECT/'prototype/scripts/main.gd',
    ]
    inventory,rules,integration=load(paths[0]),load(paths[2]),load(paths[3])
    if not rules['passed'] or not integration['passed'] or rules['failures'] or integration['failures']:
        raise ValueError('A source report does not pass; do not display success')
    if not inventory['scriptInventory']['contentEncodingVerified']:
        raise ValueError('Plain-text script verification is not available')
    values={'files':inventory['fileCount'],'scripts':inventory['scriptInventory']['gdCount'],
            'ruleChecks':rules['checks'],'integrationChecks':integration['check_count']}
    if values != {'files':3572,'scripts':195,'ruleChecks':374,'integrationChecks':32}:
        raise ValueError('Evidence changed; revise narration and storyboard before rendering')
    own_rules=paths[-2].read_text(encoding='utf-8')
    own_main=paths[-1].read_text(encoding='utf-8')
    for line in ['var live: bool = queue[0]','_consume_shell()',
                 'var self_blank := target == actor and not live']:
        if line not in own_rules:
            raise ValueError('Displayed own-code excerpt is stale: '+line)
    for line in ['busy = true','await stage.animate_item(ITEMS[index])','busy = false']:
        if line not in own_main:
            raise ValueError('Displayed own-code excerpt is stale: '+line)
    return values,[{'path':relative(p),'sha256':digest(p)} for p in paths]


def build_state(b,a,z,index,cue):
    """Each state inherits the preceding graphic, then changes one narrated fact."""
    key=b.key
    if key=='02-p01':
        b.rect(a,z,80,235,490,420,GRAY)
        b.text(a,z,134,285,'게임 실행 파일',54,WHITE,True,width=395)
        b.text(a,z,152,390,'내장 PCK',60,YELLOW,True,width=380)
        b.text(a,z,134,535,'리소스 패키지',48,GRAY,width=410)
        if index>=1:
            b.arrow(a,z,600,450,785,450,reveal=index==1)
            b.text(a,z,625,355,'REA',54,TEAL,True,width=200)
        if index>=2:
            b.text(a,z,860,245,f'{b.values["files"]:,}',104,WHITE,True,width=900)
            b.text(a,z,1195,277,'내부 파일',54,WHITE,width=580)
            b.text(a,z,860,400,'텍스처 · 소리 · 장면 · 스크립트',48,GRAY,width=990)
        if index>=3:
            b.rect(a,z,845,490,930,170,TEAL)
            b.text(a,z,890,530,'GDScript',60,TEAL,True,width=530)
            b.text(a,z,1410,530,str(b.values['scripts'])+'개',60,YELLOW,True,width=320)
        b.caption(a,z,'실제 패키지 목록을 읽어 확인한 수치')
    elif key=='02-p02':
        b.text(a,z,80,215,'읽을 수 있는 텍스트 형태',64,TEAL,True,width=1700)
        b.text(a,z,80,320,'상태를 공유하는 연결 관계',54,WHITE,width=1700)
        labels=[('사격','탄환 · 체력'),('차례','다음 행동자'),('아이템','정보 · 피해 · 차례')]
        for i,(label,sub) in enumerate(labels):
            x=80+i*610
            enabled=index>=i+2
            col=TEAL if enabled else GRAY
            b.rect(a,z,x,468,510,235,col)
            b.text(a,z,x+30,500,label,60,col,True,width=440)
            b.text(a,z,x+30,604,sub,48,col,width=450)
            if i<2 and index>=i+3:
                b.path(a,z,f'm {x+510} 580 l {x+610} 580',TEAL,5)
        b.caption(a,z,'사격·차례·아이템 함수가 어떤 상태를 바꾸는지 분석')
    elif key=='03-p01':
        if index<2:
            b.text(a,z,80,245,'방아쇠를 당길 때마다',68,WHITE,True,width=1700)
            b.text(a,z,80,360,'실탄 / 공포탄을 새로 뽑을까?',68,YELLOW,True,width=1740)
            if index==1:
                b.text(a,z,80,585,'이번에 확인한 규칙을 따라가 보자',54,TEAL,width=1700)
        else:
            b.text(a,z,80,220,'장전할 때 순서를 구성',60,WHITE,True,width=1740)
            b.queue(a,z,['공포탄','실탄','공포탄','실탄'],x=360,selected=index>=3)
            b.text(a,z,80,620,'발사할 때는 맨 앞 한 칸을 사용',56,TEAL,True,width=1740)
        b.caption(a,z,'원리 설명용 배열 · 실제 장전 순서 공개 아님')
    elif key=='03-p02':
        seq=['공포탄','실탄','공포탄','실탄'] if index<2 else ['실탄','공포탄','실탄'] if index<6 else ['공포탄','실탄']
        b.queue(a,z,seq,x=360,selected=index in [1,4,5],slide=index in [2,6])
        top=['줄을 선 탄환','이번 결과: 공포탄','사격: 앞칸 한 개 사용','다음 칸이 새로운 맨 앞',
             '돋보기: 맨 앞칸 확인','확인만 했으므로 세 칸 유지','맥주: 앞칸 한 개 배출','피해 없이 다음 칸으로'][index]
        b.text(a,z,80,215,top,60,YELLOW,True,width=1740)
        b.text(a,z,80,625,f'남은 탄환: {len(seq)}발',56,WHITE,True,width=800)
        if index in [4,5]:
            b.text(a,z,970,625,'정보 확인 · 소모 0발',54,TEAL,True,width=840)
        if index>=6:
            b.text(a,z,970,625,'배출 1발 · 피해 0',54,TEAL,True,width=840)
        b.caption(a,z,'돋보기는 조회, 맥주는 배출 · 서로 다른 동작')
    elif key=='03-p03':
        b.text(a,z,80,235,'매번 새로 추첨',60,RED,True,width=780)
        b.text(a,z,1050,235,'정해진 순서 소비',60,TEAL,True,width=790)
        b.text(a,z,80,350,'이전 결과와 별개',50,GRAY,width=770)
        b.text(a,z,1050,350,'사용하면 잔탄 구성이 변함',50,WHITE,width=780)
        if index>=1:
            b.arrow(a,z,820,300,1000,300,YELLOW,index==1)
            b.text(a,z,600,470,'서로 다른 규칙',60,YELLOW,True,width=1000)
        if index>=2:
            b.text(a,z,80,620,'사용한 탄환',52,GRAY,True,width=510)
            b.arrow(a,z,500,660,820,660,TEAL,index==2)
            b.text(a,z,870,620,'남은 실탄 / 공포탄',52,TEAL,True,width=900)
        b.caption(a,z,'앞에서 나온 결과가 남은 탄환을 해석하는 근거가 된다')
    elif key=='04-p01':
        b.text(a,z,80,215,'공포탄 · 피해 0',60,WHITE,True,width=1740)
        b.text(a,z,80,325,'누구를 선택했는가?',54,YELLOW,width=1740)
        if index>=2:
            b.text(a,z,80,465,'자신에게',60,TEAL,True,width=600)
            b.arrow(a,z,580,510,920,510,TEAL,index==2)
            b.text(a,z,1020,465,'내 차례 유지',60,TEAL,True,width=750)
        if index>=3:
            b.text(a,z,80,635,'상대에게',60,WHITE,True,width=600)
            b.arrow(a,z,580,680,920,680,GRAY,index==3)
            b.text(a,z,1020,635,'상대 차례로',60,WHITE,True,width=750)
        b.caption(a,z,'일반 차례 비교 · 잔탄이 있고 수갑 효과가 없는 경우')
    elif key=='04-p02':
        rows=[('수갑','상대의 다음 차례 한 번 생략',TEAL),('잔탄 0','새 장전 처리',YELLOW),('체력 0','평소의 다음 행동 중단',RED)]
        for i,(left,right,col) in enumerate(rows):
            if index>=i:
                y=235+i*158
                b.text(a,z,80,y,left,58,col,True,width=520)
                b.arrow(a,z,520,y+43,780,y+43,col,index==i)
                b.text(a,z,850,y,right,54,col,True,width=960)
        if index>=3:
            b.text(a,z,80,705,'함께 확인: 탄환 수 · 체력 · 차례 · 수갑',52,WHITE,True,width=1740)
        b.caption(a,z,'효과마다 검사 조건을 분리한다 · 종료와 새 장전도 처리')
    elif key=='04-p03':
        b.text(a,z,80,220,'실탄 피해',58,WHITE,True,width=700)
        b.text(a,z,80,330,'1',112,WHITE,True,width=400)
        if index>=2:
            b.arrow(a,z,330,405,750,405,YELLOW,index==2)
            b.text(a,z,465,310,'톱',54,YELLOW,True,width=280)
            b.text(a,z,870,330,'2',112,YELLOW,True,width=400)
        if index>=3:
            b.text(a,z,80,565,'공포탄 피해',56,TEAL,True,width=720)
            b.text(a,z,870,545,'0',100,TEAL,True,width=400)
            b.text(a,z,1150,570,'그대로',56,TEAL,width=600)
        b.caption(a,z,'정보: 돋보기  |  배출: 맥주  |  피해: 톱' if index>=4 else '톱은 다음 사격의 피해 효과 · 공포탄을 실탄으로 바꾸지 않음')
    elif key=='05-p01':
        b.text(a,z,80,225,'조건문 + 난수',64,YELLOW,True,width=1740)
        if index>=2:
            b.text(a,z,80,350,'현재 탄환을 아는 경우',54,WHITE,True,width=1740)
        if index>=3:
            b.text(a,z,80,485,'실탄',60,RED,True,width=530)
            b.arrow(a,z,470,530,880,530,RED,index==3)
            b.text(a,z,990,485,'플레이어에게',60,RED,True,width=800)
        if index>=4:
            b.text(a,z,80,640,'공포탄',60,TEAL,True,width=530)
            b.arrow(a,z,470,685,880,685,TEAL,index==4)
            b.text(a,z,990,640,'자신에게',60,TEAL,True,width=800)
        b.caption(a,z,'분석한 원작의 판단 분기 · 학습 모델이 아님')
    elif key=='05-p02':
        if index<4:
            b.text(a,z,80,220,'현재 탄환을 모르는 경우',58,WHITE,True,width=1740)
            if index>=1:
                b.text(a,z,80,355,'일반 모드',60,YELLOW,True,width=640)
                b.text(a,z,80,485,'무작위로 대상 선택',54,WHITE,width=790)
            if index>=2:
                b.text(a,z,1000,355,'무한 모드',60,TEAL,True,width=810)
                b.text(a,z,1000,485,'남은 탄환의 다수 쪽',54,WHITE,width=810)
                b.text(a,z,1000,590,'실탄 다수 → 플레이어',50,RED,width=810)
                b.text(a,z,1000,665,'공포탄 다수 → 자신',50,TEAL,width=810)
            b.caption(a,z,'실탄 수 = 공포탄 수이면 무작위 선택' if index>=3 else '분석한 모드별 주요 분기 · 알려진 정보가 있으면 먼저 사용')
        else:
            labels=['돋보기','확인한 실탄','톱 조합']
            for i,label in enumerate(labels):
                x=80+i*615
                on=index>=i+4
                color=[TEAL,RED,YELLOW][i] if on else GRAY
                b.rect(a,z,x,350,510,190,color)
                b.text(a,z,x+32,402,label,58,color,True,width=440)
                if i<2 and index>=i+5:
                    b.arrow(a,z,x+525,445,x+592,445,color,index==i+5)
            b.text(a,z,80,640,'가진 정보 → 가능한 행동',58,WHITE,True,width=1740)
            b.caption(a,z,'원작의 아이템 판단 예시 · 재구현 딜러는 사격만 수행')
    elif key=='06-p01':
        b.text(a,z,80,190,'독립 작성한 rules.gd · 관련 줄 발췌',48,GRAY,width=1740)
        b.code(a,z,110,275,'var live: bool = queue[0]',index in [0,1])
        b.code(a,z,110,350,'_consume_shell()',index in [2,3])
        b.code(a,z,110,425,'var self_blank := target == actor and not live',index>=4)
        if index>=1:
            b.text(a,z,80,520,'입력: 공포탄 → 실탄 · 내 체력 3',50,WHITE,width=1740)
        if index>=2:
            b.text(a,z,80,595,'행동: 자신에게 사격',50,TEAL,True,width=1740)
        rows=[('탄환 수','2 → 1'),('내 체력','3 → 3'),('차례','나 → 나')]
        for i,(label,value) in enumerate(rows):
            if index>=i+3:
                x=80+i*615
                b.text(a,z,x,680,label,48,GRAY,width=510)
                b.text(a,z,x+245,672,value,56,TEAL,True,width=330)
        b.caption(a,z,'test_rules.gd: 자기 공포탄의 정확한 상태 검사')
    elif key=='06-p02':
        b.text(a,z,80,205,'자체 규칙 검사',54,WHITE,True,width=990)
        b.text(a,z,80,290,str(b.values['ruleChecks']),94,GREEN,True,width=500)
        b.text(a,z,430,320,'통과',54,GREEN,True,width=500)
        if index in [1,2]:
            b.code(a,z,110,450,'busy = true')
            b.code(a,z,110,535,'await stage.animate_item(ITEMS[index])',True)
            b.code(a,z,110,620,'busy = false')
            b.text(a,z,1390,450,'잠금',52,TEAL,True,width=400)
            b.text(a,z,1390,535,'완료 대기',52,YELLOW,True,width=400)
            b.text(a,z,1390,620,'입력 허용',52,TEAL,True,width=400)
            b.caption(a,z,'독립 작성한 main.gd의 관련 줄 발췌 · 동작이 끝난 뒤 잠금 해제')
        elif index==3:
            b.text(a,z,80,480,'수갑 때문에 유지된 차례',56,YELLOW,True,width=1740)
            b.text(a,z,80,590,'자기 공포탄',54,RED,width=800)
            b.arrow(a,z,770,635,1050,635,TEAL)
            b.text(a,z,1110,590,'수갑으로 유지',54,TEAL,True,width=710)
            b.caption(a,z,'재구현 화면 문구를 실제 차례 유지 이유와 일치시킴')
        elif index>=4:
            b.text(a,z,1050,205,'화면 연결 검사',54,WHITE,True,width=800)
            b.text(a,z,1050,290,str(b.values['integrationChecks']),94,GREEN,True,width=420)
            b.text(a,z,1310,320,'통과',54,GREEN,True,width=450)
            b.text(a,z,80,500,'동작 중에는 입력 잠금',58,TEAL,True,width=1740)
            b.text(a,z,80,625,'차례 유지 이유를 구분해 표시',58,TEAL,True,width=1740)
            b.caption(a,z,'자체 코드의 단언 검사 수 · 원작 전체 동작의 동일성 검증 아님')
        else:
            b.text(a,z,80,515,'탄환 · 피해 · 차례 · 정보 · 아이템',58,TEAL,True,width=1740)
            b.caption(a,z,'실제 실행된 규칙 검사 보고서의 성공 수치')
    elif key=='08-p01':
        chain=[('관찰','자기 공포탄'),('규칙','탄환 · 차례'),('구현','독립 코드'),('결과','프로토타입')]
        count=[1,2,4,4,4][index]
        for i,(label,sub) in enumerate(chain):
            x=80+i*460
            col=TEAL if i<count else GRAY
            b.text(a,z,x,300,label,60,col,True,width=390)
            b.text(a,z,x,425,sub,48,col,width=390)
            if i<count-1:
                birth=1 if i==0 else 2
                b.arrow(a,z,x+300,350,x+415,350,TEAL,index==birth)
        if index>=3:
            b.text(a,z,80,600,'374개 검사 → 자체 규칙 모델 대상',56,YELLOW,True,width=1740)
        b.caption(a,z,'확인한 핵심 규칙을 옮긴 프로토타입 · 원작 전체 재현은 아님')
    elif key=='08-p02':
        labels=[('읽은 자료','파일과 함수'),('시험한 입력','탄환 · 선택'),('보이는 변화','화면과 상태')]
        count=0 if index<2 else min(3,index-1)
        for i,(label,sub) in enumerate(labels):
            x=80+i*615
            col=TEAL if i<count else GRAY
            b.rect(a,z,x,330,510,255,col)
            b.text(a,z,x+30,370,label,58,col,True,width=450)
            b.text(a,z,x+30,475,sub,48,col,width=450)
            if i<count-1:
                b.arrow(a,z,x+525,455,x+590,455,TEAL,index==i+3)
        b.text(a,z,80,215,'도구의 결과를 근거로 연결하기',60,YELLOW,True,width=1740)
        if index>=5:
            b.text(a,z,80,665,'작은 게임으로 그 연결을 직접 확인',58,TEAL,True,width=1740)
        b.caption(a,z,'조사 → 구현 → 검사 → 실제 동작')
    else:
        raise ValueError(key)


def paragraph_texts():
    narration=load(PROJECT/'script/narration.ko.json')
    return {f'{s["id"]}-p{i+1:02}':text for s in narration['scenes'] for i,text in enumerate(s['lines'])}


def prepare_one(entry,text,values,evidence,out,synthetic=False):
    key=f'{str(entry["scene"]).zfill(2)}-p{int(entry["paragraph"]):02}'
    title,anchors=SPECS[key]
    duration=float(entry['durationSeconds'])
    if duration<=0:
        raise ValueError('Positive measured duration required')
    frames=math.ceil(duration*FPS-1e-6)
    duration=frames/FPS
    speech_a=float(entry.get('speechStartSeconds',0))
    speech_z=float(entry.get('speechEndSeconds',duration))
    if not 0<=speech_a<speech_z<=duration+.02:
        raise ValueError('Invalid speech interval')
    supplied=entry.get('cueTimes',{})
    cues=[]
    for i,(name,phrase) in enumerate(anchors):
        position=text.find(phrase)
        if position<0:
            raise ValueError(f'Anchor is absent from current narration: {key}/{name}: {phrase}')
        method=entry.get('cueEvidence',{}).get(name,{}).get('method','provided-offset') if name in supplied else 'proportional-text-estimate'
        value=float(supplied.get(name,speech_a+(speech_z-speech_a)*position/max(1,len(text))))
        if i==0:
            value=0
            method='paragraph-start'
        value=ftime(value)
        if not 0<=value<duration:
            raise ValueError(f'Cue outside paragraph: {key}/{name}')
        if cues and value<=cues[-1]['seconds']:
            raise ValueError(f'Non-increasing cue offsets: {key}/{name}')
        cues.append({'id':name,'phrase':phrase,'seconds':value,'method':method,'textOffset':position})
    board=Board(key,duration,title,values)
    board.header()
    for i,cue in enumerate(cues):
        a=cue['seconds']; z=cues[i+1]['seconds'] if i+1<len(cues) else duration
        build_state(board,a,z,i,cue['id'])
    clipdir=out/key
    clipdir.mkdir(parents=True,exist_ok=True)
    ass=clipdir/(key+'.ass')
    ass.write_text('\n'.join(board.lines)+'\n',encoding='utf-8-sig')
    receipt={
        'schemaVersion':1,'preparedAtUtc':now(),'id':key,'assetKind':'analysis-visualization',
        'sourceKindLabel':'분석 원리도','originalGameplay':False,'originalCodeDisplayed':False,
        'title':title,'durationSeconds':duration,'requestedDurationSeconds':entry['durationSeconds'],
        'frames':frames,'width':1920,'height':1080,'fps':60,
        'captionAreaReserved':[0,892,1920,1060], 'minimumFontPx':48,
        'narrationText':text,'narrationSha256':digest(PROJECT/'script/narration.ko.json'),
        'syntheticLayoutTest':synthetic,'timingVerified':bool(entry.get('timingVerified',False)) and not synthetic,
        'cueAlignmentReviewed':bool(entry.get('cueAlignmentReviewed',False)) and not synthetic,
        'cueAlignmentSource':entry.get('cueAlignmentSource'), 'cueEvidence':entry.get('cueEvidence',{}),
        'cues':cues,'estimatedCues':[c['id'] for c in cues if c['method']=='proportional-text-estimate'],
        'evidence':evidence,'values':values,'textLayout':board.layout,'assPath':relative(ass),
        'assSha256':digest(ass),'rendered':False,'motionReviewed':False,
        'limitations':[
            'Authored explanatory diagram, not captured original game or terminal.',
            'Illustrative queue/animation timing is not a game-state measurement.',
            'Provided offsets are not automatically certified as listened/reviewed.',
            'Static bounds validation is not encoded mobile or moving visual QA.',
        ],
    }
    save(clipdir/'receipt.json',receipt)
    return receipt


def render_one(receipt,out,plan):
    if receipt['syntheticLayoutTest'] or not receipt['timingVerified']:
        raise ValueError('Rendering requires actual measured paragraph timing, not self-check durations')
    clipdir=out/receipt['id']
    mp4=clipdir/(receipt['id']+'.mp4')
    if mp4.exists() and not plan.get('overwrite',False):
        raise FileExistsError(f'Preserve existing render or explicitly use --overwrite: {mp4}')
    ass=PROJECT/receipt['assPath']
    # Relative ASS basename avoids drive-colon escaping in FFmpeg filter paths.
    args=[tool('ffmpeg',plan),'-hide_banner','-v','warning','-nostdin','-y','-filter_threads','1',
          '-f','lavfi','-i','color=c=black:s=1920x1080:r=60',
          '-vf','ass='+ass.name,'-frames:v',str(receipt['frames']),'-an']
    if plan.get('encoder')=='h264_nvenc':
        args+=['-c:v','h264_nvenc','-preset','p5','-cq','18']
    else:
        args+=['-c:v','libx264','-threads','4','-preset','veryfast','-crf','18']
    args+=['-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)]
    command(args,clipdir/'render.log',cwd=clipdir)
    metadata=probe(mp4,plan)
    stream=video_stream(metadata)
    if stream['width']!=1920 or stream['height']!=1080 or Fraction(stream['avg_frame_rate'])!=60:
        raise ValueError('Encoded output does not satisfy 1080p60')
    if int(stream.get('nb_frames',receipt['frames']))!=receipt['frames']:
        raise ValueError('Encoded frame count differs')
    save(clipdir/'ffprobe.json',metadata)
    receipt.update({'rendered':True,'renderedAtUtc':now(),'path':relative(mp4),'sha256':digest(mp4),
                    'encoder':plan.get('encoder','libx264'),'command':args,
                    'verification':'Encoded dimensions/fps/frame count checked; moving/audio QA remains pending'})
    save(clipdir/'receipt.json',receipt)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--timings',type=Path)
    ap.add_argument('--out',type=Path,default=LOCAL)
    ap.add_argument('--only',action='append',help='Paragraph id, for example 03-p02; repeatable')
    ap.add_argument('--render',action='store_true',help='Explicitly render after parent authorizes the job')
    ap.add_argument('--self-check',action='store_true',help='Synthetic timing layout check only; never renders')
    ap.add_argument('--template',type=Path,help='Write blank timing schema + cue phrases and exit')
    ap.add_argument('--encoder',choices=['libx264','h264_nvenc'],default='libx264')
    ap.add_argument('--overwrite',action='store_true')
    args=ap.parse_args()
    texts=paragraph_texts()
    if args.template:
        result={'schemaVersion':1,'kind':'measured-paragraph-diagram-timings','instructions':[
            'Supply actual measured durationSeconds and speech end for every requested paragraph.',
            'timingVerified means measured media duration, not human review.',
            'cueTimes are local seconds keyed by cue id. Omitted anchors are marked estimates.',
            'cueAlignmentReviewed must stay false until actual speech+picture review.',
            'Preparation does not render. Invoke --render only after the parent authorizes rendering.'
        ],'paragraphs':[]}
        for key,(_,anchors) in SPECS.items():
            result['paragraphs'].append({'scene':key[:2],'paragraph':int(key[-2:]),'durationSeconds':None,
                'speechStartSeconds':0,'speechEndSeconds':None,'timingVerified':False,
                'cueAlignmentReviewed':False,'cueTimes':{},'cuePhrases':dict(anchors)})
        save(args.template,result)
        print(str(args.template));return
    if args.self_check and args.render:
        ap.error('Self-check may never render')
    if args.self_check:
        entries=[{'scene':key[:2],'paragraph':int(key[-2:]),'durationSeconds':32.0} for key in SPECS]
        out=args.out/'layout-self-check'
    else:
        if not args.timings:
            ap.error('--timings is required unless writing a template or running --self-check')
        entries=load(args.timings)['paragraphs'];out=args.out
    out=out.resolve()
    if not out.is_relative_to((PROJECT/'production/local').resolve()):
        raise ValueError('Generated media and evidence must stay under this project production/local')
    values,evidence=evidence_values()
    receipts=[]
    for entry in entries:
        key=f'{str(entry["scene"]).zfill(2)}-p{int(entry["paragraph"]):02}'
        if args.only and key not in args.only:
            continue
        receipt=prepare_one(entry,texts[key],values,evidence,out,args.self_check)
        if args.render:
            render_one(receipt,out,vars(args))
        receipts.append(receipt)
        print(f'{key}: {receipt["durationSeconds"]:.3f}s, {len(receipt["cues"])} states, '
              f'{len(receipt["estimatedCues"])} estimated cue offsets; '
              +('rendered' if receipt['rendered'] else 'prepared only'))
    save(out/'index.json',{'updatedAtUtc':now(),'rendered':args.render,'syntheticLayoutTest':args.self_check,
                         'source':relative(Path(__file__)),'sourceSha256':digest(__file__),
                         'paragraphs':[{k:r[k] for k in ['id','durationSeconds','frames','assPath',
                         'rendered','estimatedCues','motionReviewed']} for r in receipts]})


if __name__=='__main__':
    main()

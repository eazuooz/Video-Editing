"""Eight narration-timed Manim inserts. All displayed numbers are teaching examples.

No TTS or source footage is produced here. Original PCM frame counts are inputs.
The output is caption-free; the unchanged final captions are composited once.
"""
import json
from pathlib import Path
import numpy as np
from manim import *
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[4]
STORY = json.loads((ROOT/'projects/game-lighting-history-01/production/animation-storyboard-v4.json').read_text(encoding='utf8'))
TIMING = json.loads((ROOT/'motion-canvas/src/projects/game-lighting-history-01/explanation-assets-v1/data.json').read_text(encoding='utf8'))
PARAS = {p['key']: p for s in STORY['scenes'] for p in s['paragraphs']}
BLOCKS = {p['paragraphKey']: p for s in TIMING['chapters'] for p in s['blocks']}
INK, GOLD, TEAL, ORANGE = '#f5f5f5', '#e8cf83', '#73c7c2', '#f39a4b'

def label(text, size=32, color=INK):
    return Text(text, font='Malgun Gothic', font_size=size, color=color)

class MathInsert(Scene):
    key = ''

    def get_time_progression(self, run_time, description, n_iterations=None, override_skip_animations=False):
        # Integer authored frames avoid np.arange's floating-stop extra frame.
        return tqdm(np.arange(round(run_time*60))/60, disable=True)

    def construct(self):
        p, b = PARAS[self.key], BLOCKS[self.key]
        self.camera.background_color = BLACK
        title = label(p['focus'], 40, GOLD).to_edge(UP, buff=.45)
        if title.width > 14.4: title.scale_to_fit_width(14.4)
        self.add(title, label('교육용 계산 · 실제 게임 측정값 아님', 23, '#b8b8b8').move_to([0, 3.05, 0]))
        state = {k: ValueTracker(v) for k, v in p['from'].items()}
        for step in b['actionSteps']:
            for k in step['to']: state.setdefault(k, ValueTracker(0))
        get = lambda k, default=0: state[k].get_value() if k in state else default
        if self.key in ('04f-p3', '04f-p4'): self.bilinear(get)
        elif self.key == '04f-p5': self.trilinear(get)
        elif self.key == '09-p3': self.depth(get)
        elif self.key in ('09-p7', '09-p8'): self.pcf(get)
        else: self.coverage(get)
        limit = label(p['limit'], 25, '#b8b8b8').move_to([0, -2.8, 0])
        if limit.width > 14.3: limit.scale_to_fit_width(14.3)
        self.add(limit)
        elapsed = 0
        for step in b['actionSteps']:
            start, count = step['actionStartFrame'], step['actionDurationFrames']
            if start > elapsed: self.wait((start-elapsed)/60)
            self.play(*[state[k].animate.set_value(v) for k,v in step['to'].items()], run_time=count/60, rate_func=linear)
            elapsed = start+count
        if elapsed < b['frames']: self.wait((b['frames']-elapsed)/60)

    def bilinear(self, g):
        colors = [TEAL, ORANGE, '#9b8ed1', GOLD]
        corners = [(-5,1.6), (-2,1.6), (-5,-1.4), (-2,-1.4)]
        for i, (x,y) in enumerate(corners):
            self.add(Square(.85, color=colors[i], fill_opacity=.65).move_to([x,y,0]), label(f'C{i}',24).move_to([x,y+.7,0]))
        self.add(Rectangle(width=3,height=3,color='#6b7280').move_to([-3.5,.1,0]))
        self.add(always_redraw(lambda: Dot([-5+3*g('u',.5),1.6-3*g('v',.5),0],color=WHITE,radius=.09)))
        weights = lambda: [(1-g('u'))*(1-g('v')),g('u')*(1-g('v')),(1-g('u'))*g('v'),g('u')*g('v')]
        for i in range(4):
            self.add(label(f'w{i} =',28,colors[i]).move_to([.4,1.4-i*.75,0]), always_redraw(lambda i=i: label(f'{weights()[i]:.3f}',32,colors[i]).move_to([2.1,1.4-i*.75,0])))
        self.add(label('결과 = w₀C₀ + w₁C₁ + w₂C₂ + w₃C₃',27).move_to([1.8,-2,0]))
        self.add(always_redraw(lambda: label(f'u = {g("u"):.2f}    v = {g("v"):.2f}    가중치 합 = {sum(weights()):.2f}',27,TEAL).move_to([2.8,2.25,0])))

    def trilinear(self,g):
        for cx,n,name in [(-4.5,4,'밉 레벨 M₀'),(0,2,'밉 레벨 M₁')]:
            for y in range(n):
                for x in range(n): self.add(Square(2/n,color='#6b7280',fill_color=(interpolate_color(ManimColor(TEAL),ManimColor(GOLD),.5) if n==2 else TEAL if (x+y)%2 else GOLD),fill_opacity=.75).move_to([cx-1+(x+.5)*2/n,1-(y+.5)*2/n,0]))
            self.add(label(name,30).move_to([cx,1.8,0]),label('각 레벨에서 바이리니어',23).move_to([cx,-1.6,0]))
        self.add(Arrow([-3.3,0,0],[-1.25,0,0],color=INK),Arrow([1.2,0,0],[3.2,0,0],color=INK))
        self.add(label('레벨 사이 보간',28,GOLD).move_to([4.7,1.2,0]))
        self.add(always_redraw(lambda: label(f't = {g("blend"):.2f}',32,TEAL).move_to([4.7,0,0])))
        self.add(label('(1 − t) B(M₀) + t B(M₁)',32).move_to([0,-2.2,0]))

    def depth(self,g):
        self.add(Arrow([-5,1.7,0],[5.5,1.7,0],color=INK),label('광원에 가까움',26).move_to([-5,2.15,0]),label('멀어짐',26).move_to([5,2.15,0]))
        for z in [0,.33,.8,.9,1]: self.add(Line([-5+10*z,1.6,0],[-5+10*z,1.8,0]),label(f'{z:.2f}',24).move_to([-5+10*z,1.15,0]))
        self.add(Dot([3,1.7,0],color=GOLD,radius=.11),label('검사점 P = 0.80',30,GOLD).move_to([3,.4,0]))
        self.add(always_redraw(lambda: Dot([-5+10*g('stored',.33),1.7,0],color=TEAL,radius=.12)))
        self.add(always_redraw(lambda: label(f'처음 기록한 깊이 D = {g("stored",.33):.2f}',32,TEAL).move_to([-1,-.6,0])))
        self.add(always_redraw(lambda: label(f'0.80 {">" if .8>g("stored",.33) else "≤"} {g("stored",.33):.2f}  →  '+('가려짐' if .8>g('stored',.33) else '가려지지 않음'),40).move_to([0,-1.7,0])))

    def pcf(self,g):
        ds=[.9,.3,.9,.3]
        for i,z in enumerate(ds):
            x=-5.4+i*3.6;lit=.8<=z
            self.add(Rectangle(width=2.8,height=1.15,color=TEAL if lit else ORANGE,fill_opacity=.15).move_to([x,.9,0]),label(f'D{i} = {z:.2f}',28).move_to([x,.95,0]),label(f'0.80 ≤ D{i}',25).move_to([x,0,0]))
            self.add(always_redraw(lambda i=i,x=x,lit=lit: label('1 · 빛' if lit else '0 · 가림',32,TEAL if lit else ORANGE).move_to([x,-.7,0]).set_opacity(min(1,max(0,g('filter',1))))))
        self.add(label('각 깊이를 비교한 뒤, 판정 결과를 평균',29,GOLD).move_to([0,2.1,0]))
        self.add(always_redraw(lambda: label('(1 + 0 + 1 + 0) / 4 = 0.50',36).move_to([0,-1.9,0]).set_opacity(max(.25,min(1,g('filter',g('pcf',.5)*2))))))

    def coverage(self,g):
        self.add(label('맵 해상도는 둘 다 2048칸',35,GOLD).move_to([0,2.0,0]))
        for x,width,title in [(-3.8,20,'좁은 범위'),(3.8,200,'넓은 범위')]:
            for i in range(9):self.add(Line([x-2+i*.5,-.8,0],[x-2+i*.5,1.2,0],color=TEAL if width==20 else ORANGE))
            self.add(Rectangle(width=4,height=2,color=INK).move_to([x,.2,0]),label(title,27).move_to([x,1.5,0]),label(f'{width} m / 2048',29).move_to([x,-1.3,0]),label(f'약 {width/2048*100:.2f} cm / 텍셀',30,TEAL if width==20 else ORANGE).move_to([x,-2,0]))
        self.add(always_redraw(lambda: SurroundingRectangle(label('',1).move_to([-3.8 if g('coverage',20)<110 else 3.8,.2,0]),buff=0,color=GOLD).stretch_to_fit_width(4.35).stretch_to_fit_height(2.35)))

for key in ('04f-p3','04f-p4','04f-p5','09-p3','09-p7','09-p8','09a-p3','09a-p4'):
    globals()['Insert_'+key.replace('-','_')] = type('Insert_'+key.replace('-','_'), (MathInsert,), {'key':key,'__module__':__name__})

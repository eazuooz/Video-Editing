"""Four finite half-width mathematical actions, reflowed from V6 logic.

Native900x660; no finished full-slide scaling or narration timing. The root
starts each native action at the measured word and holds exact endpoints while
speech continues. Transparent source stays over the same controlled3D model.
"""
import os
from manim import *

config.frame_width=9;config.frame_height=6.6
WHITE='#f5f5f5';MUTED='#b8b8b8';RULE='#6b7280';GOLD='#e8cf83';TEAL='#73c7c2'
ORANGE='#f39a4b';XCOLOR='#ef5a63';YCOLOR='#6cce8e'

def tx(text,px=64,color=WHITE,width=8.45):
    m=Text(text,font='Malgun Gothic',font_size=49,color=color)
    m.set_height(px/100)
    if m.width>width:raise ValueError(f'Actual64px text exceeds900 pane: {text} ({m.width*100:.1f}px)')
    return m

def header(text):return tx(text,54,GOLD).move_to([0,2.7,0])

def axis_line(y=-1.3,left=-3.2,right=3.2):
    return Line([left,y,0],[right,y,0],color=RULE,stroke_width=5)

def dimension(x0,x1,y,color=GOLD):
    return VGroup(Line([x0,y,0],[x1,y,0],color=color,stroke_width=5),
        Line([x0,y-.12,0],[x0,y+.12,0],color=color,stroke_width=5),
        Line([x1,y-.12,0],[x1,y+.12,0],color=color,stroke_width=5))

class RightDiagram(Scene):
    def construct(self):
        self.camera.background_opacity=0
        background=ImageMobject(os.environ['V7_RIGHT_BACKGROUND']).set(width=9,height=6.6)
        self.add(background,Rectangle(width=9,height=6.6,stroke_width=0,fill_color=BLACK,fill_opacity=.82))
        key=os.environ['V7_RIGHT_MATH']
        if key=='v7-math-storage':self.storage()
        elif key=='v7-math-half-step':self.half_step()
        elif key=='v7-math-quantize':self.quantize()
        elif key=='v7-math-stretch':self.stretch()
        else:raise ValueError(key)
        # One actual endpoint sample is retained, not an observation pause.
        self.wait(1/60)

    def storage(self):
        self.add(header('빈 저장 칸 · 성분 수 비교'))
        self.add(tx('세 각도',64,TEAL).move_to([-2.4,1.7,0]),tx('3×3 행렬',64).move_to([2.0,1.7,0]))
        left=VGroup()
        for i,label in enumerate(['h','p','b']):
            box=Rectangle(width=.92,height=.92,color=TEAL,stroke_width=4).move_to([-3.5+i*1.12,.0,0])
            left.add(VGroup(box,tx(label,64,TEAL).move_to(box.get_top()+UP*.48)))
        right=VGroup(*[Square(side_length=.76,color=WHITE,stroke_width=4)for _ in range(9)])
        right.arrange_in_grid(rows=3,cols=3,buff=.10).move_to([2.0,0,0])
        self.play(LaggedStart(*[FadeIn(v)for v in left],lag_ratio=.35),run_time=1.2)
        self.add(tx('3개',72,TEAL).move_to([-2.4,-1.9,0]))
        self.play(LaggedStart(*[Create(v)for v in right],lag_ratio=.13),run_time=1.8)
        self.add(tx('9개',72).move_to([2.0,-1.9,0]))

    def half_step(self):
        self.add(header('각도 한 성분 · 1° 간격'))
        line=axis_line(y=-.5);self.add(line)
        for x,label in [(-3.2,'0°'),(3.2,'1°')]:
            self.add(Line([x,-.68,0],[x,-.32,0],color=WHITE,stroke_width=4),tx(label,64).move_to([x,-1.3,0]))
        full=dimension(-3.2,3.2,1.1,WHITE)
        self.play(Create(full),run_time=1)
        self.add(tx('간격 1°',64).move_to([0,1.8,0]))
        self.add(DashedLine([0,-.5,0],[0,.3,0],color=MUTED,stroke_width=3))
        half=dimension(-3.2,0,.3,GOLD)
        self.play(Create(half),run_time=1)
        self.add(tx('성분 오차 ≤ 0.5°',64,GOLD).move_to([0,-2.25,0]))
        # This is a distance bound, not a20.5-to-output tie-breaking policy.

    def quantize(self):
        self.add(header('입력은 달라도 · 저장값은 같음'))
        self.add(tx('입력',64,TEAL).move_to([-2.3,1.9,0]),tx('저장',64).move_to([2.3,1.9,0]))
        a=Rectangle(width=2.8,height=1.12,color=TEAL,stroke_width=4).move_to([-2.3,.9,0])
        b=Rectangle(width=2.8,height=1.12,color=WHITE,stroke_width=4).move_to([2.3,.9,0])
        value=ValueTracker(20.0)
        before=always_redraw(lambda:tx(f'{value.get_value():.1f}°',72,TEAL).move_to(a))
        output=tx('20°',72).move_to(b)
        self.add(a,b,before,output,Arrow([-.75,.9,0],[.75,.9,0],buff=0,color=GOLD,stroke_width=5))
        self.add(tx('1° 단위 반올림',54,GOLD).move_to([0,-.2,0]))
        y=-1.5;self.add(axis_line(y))
        for x,label in [(-3.2,'20°'),(3.2,'21°')]:
            self.add(Line([x,y-.13,0],[x,y+.13,0],color=WHITE,stroke_width=4),tx(label,64).move_to([x,-2.3,0]))
        pointer=Dot([-3.2,y,0],radius=.10,color=TEAL)
        self.add(pointer)
        self.play(value.animate.set_value(20.4),pointer.animate.move_to([-3.2+6.4*.4,y,0]),run_time=2,rate_func=linear)
        # The output20° deliberately never animates or changes. All interpolated
        # inputs20.0–20.4 round to20 at1° nearest-value spacing.

    def stretch(self):
        self.add(header('행렬 한 칸 · 길이가 달라짐'))
        origin=[-3.6,-.25,0];x0=-3.6;y0=-.25
        square=Polygon([x0,y0,0],[x0+1.4,y0,0],[x0+1.4,y0+1.4,0],[x0,y0+1.4,0],color=TEAL,stroke_width=5)
        ghost=DashedVMobject(square.copy().set_color(RULE),num_dashes=24)
        target=Polygon([x0,y0,0],[x0+2.8,y0,0],[x0+2.8,y0+1.4,0],[x0,y0+1.4,0],color=TEAL,stroke_width=5)
        self.add(ghost,square,Arrow(origin,[x0+3.1,y0,0],buff=0,color=XCOLOR,stroke_width=4),Arrow(origin,[x0,y0+1.75,0],buff=0,color=YCOLOR,stroke_width=4))
        self.add(tx('X',54,XCOLOR).move_to([x0+3.2,y0-.35,0]),tx('Y',54,YCOLOR).move_to([x0-.35,y0+1.65,0]))
        grid=VGroup();coefficient=ValueTracker(1)
        for r in range(3):
            for c in range(3):
                center=[1.0+c*1.15,1.2-r*.90,0]
                box=Rectangle(width=1.10,height=.84,color=GOLD if(r,c)==(0,0)else RULE,stroke_width=3).move_to(center)
                if(r,c)==(0,0):
                    entry_center=list(center)
                    number=always_redraw(lambda:tx(f'{coefficient.get_value():.1f}'.removesuffix('.0'),64,GOLD).move_to(entry_center))
                else:number=tx('1'if r==c else'0',64,WHITE).move_to(center)
                grid.add(box,number)
        self.add(grid,tx('예: X 길이 ×2',64,GOLD).move_to([0,-1.9,0]))
        self.play(Transform(square,target),coefficient.animate.set_value(2),run_time=2.5,rate_func=smooth)
        self.add(tx('늘림이 생김 · 순수 회전 아님',54).move_to([0,-2.65,0]))

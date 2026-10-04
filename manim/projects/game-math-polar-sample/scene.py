"""Original narrated polar-coordinate lecture; Manim Community 0.20.1.

Render after production/build.py plan. All 2D/3D frames count as explanation.
Shared channel white research-paper palette; caption reserve below y=-2.9.
"""
from pathlib import Path
import json
import math
import numpy as np
from manim import *

ROOT=Path(__file__).resolve().parents[3]
PLAN=ROOT/'projects/game-math-polar-sample/production/timeline.json'
PAPER='#ffffff'; INK='#202020'; MUTED='#737373'; LINE='#cbd0d6'
BLUE='#2f5faa'; GREEN='#52704c'; RED='#c43b3b'; LIGHT='#dfeaf5'
DEFAULT={'01':22,'03':26,'05':28,'07':24.8}
def text(s,size=30,color=INK):
    return Text(s,font='Malgun Gothic',font_size=size,color=color)
def data(scene_id):
    if PLAN.exists():
        return next(s for s in json.loads(PLAN.read_text(encoding='utf8'))['scenes'] if s['id']==scene_id)
    return {'seconds':DEFAULT.get(scene_id,22),'cues':[]}
def heading(title,sub):
    a=text(title,42).to_corner(UL,buff=.65)
    b=text(sub,21,MUTED).next_to(a,DOWN,aligned_edge=LEFT,buff=.18)
    rule=Line([-6.45,2.65,0],[6.45,2.65,0],color=LINE,stroke_width=1)
    return VGroup(a,b,rule)
def card(lines,width=4.3,height=1.25,color=BLUE):
    shadow=Rectangle(width=width,height=height,stroke_width=0,fill_color=LIGHT,fill_opacity=.8).shift(.10*RIGHT+.10*DOWN)
    face=Rectangle(width=width,height=height,stroke_color=LINE,stroke_width=1.3,fill_color=WHITE,fill_opacity=1)
    words=VGroup(*[text(s,28 if i==0 else 22,color if i==0 else MUTED) for i,s in enumerate(lines)]).arrange(DOWN,buff=.13)
    if words.width>width-.4: words.scale_to_fit_width(width-.4)
    return VGroup(shadow,face,words)

class Timed:
    sid='01'
    def at(self,line):
        cues=data(self.sid)['cues']
        if line<len(cues):
            delay=cues[line]['start']-self.renderer.time
            if delay>1/60:self.wait(delay)
    def finish(self):
        remain=data(self.sid)['seconds']-self.renderer.time
        if remain>1/60:self.wait(remain)
    def init(self):
        self.camera.background_color=WHITE

class Overview(Timed,Scene):
    sid='01'
    def construct(self):
        self.init()
        self.add(heading('이 위치를 어떻게 말할까요?','게임수학 Part 2  /  01 극좌표계'))
        o=np.array([-3.5,-.25,0]); radius=1.85
        track=Circle(radius=radius,color=LINE,stroke_width=2).move_to(o)
        axis=Arrow(o,o+2.5*RIGHT,buff=0,color=MUTED,stroke_width=2)
        dot=Dot(o+radius*np.array([.8,.6,0]),color=BLUE,radius=.10)
        ray=Line(o,dot.get_center(),color=BLUE,stroke_width=5)
        tag=text('거리 + 방향',24,BLUE).move_to(o+2.2*DOWN)
        self.play(Create(track),Create(axis),FadeIn(Dot(o,color=INK)),FadeIn(dot),Create(ray),run_time=1.3)
        self.play(FadeIn(tag),run_time=.5)
        self.at(1)
        a=card(['r  ·  중심에서의 거리','θ  ·  기준 방향에서의 각도'],width=5.7,height=1.45).move_to([2.9,1.12,0])
        self.play(FadeIn(a,shift=.18*UP),run_time=.7)
        self.at(2)
        steps=VGroup(*[card([s],width=5.7,height=.72,color=GREEN) for s in ['1  실제 움직임 관찰','2  돌고 이동해서 점 찍기','3  가로·세로 좌표로 변환']]).arrange(DOWN,buff=.20).move_to([2.9,-1.12,0])
        self.play(LaggedStart(*[FadeIn(v,shift=.16*UP) for v in steps],lag_ratio=.25),run_time=1.1)
        dot.add_updater(lambda m:None)
        self.play(Rotate(VGroup(dot,ray),angle=PI/3,about_point=o),run_time=min(3,max(.5,data(self.sid)['seconds']-self.renderer.time-.1)),rate_func=smooth)
        self.finish()

def plane_objects():
    # Mathematical +x-right / +y-up convention, equal unit scale.
    axes=Axes(x_range=[-1,6,1],y_range=[-1,6,1],x_length=3.75,y_length=3.75,axis_config={'color':LINE,'stroke_width':2,'include_ticks':True,'tip_width':.12,'tip_height':.12}).move_to([-2.9,-.30,0])
    o=axes.c2p(0,0)
    labels=VGroup(text('x',22,MUTED).next_to(axes.x_axis.get_end(),RIGHT,buff=.1),text('y',22,MUTED).next_to(axes.y_axis.get_end(),UP,buff=.1),text('0',18,MUTED).next_to(o,DL,buff=.10))
    return axes,o,labels

class Locate(Timed,Scene):
    sid='03'
    def construct(self):
        self.init(); self.add(heading('한번 돌고, 앞으로 이동하기','같은 점 · 다른 표현'))
        axes,o,labs=plane_objects();p=axes.c2p(4,3);theta=math.atan2(3,4)
        origin=Dot(o,color=INK,radius=.06)
        self.add(axes,labs,origin)
        look=Arrow(o,axes.c2p(2.1,0),buff=0,color=GREEN,stroke_width=5)
        arc=Arc(radius=.65,angle=theta,color=GREEN,stroke_width=4).shift(o)
        self.play(GrowArrow(look),run_time=.7)
        self.play(Rotate(look,angle=theta,about_point=o),Create(arc),run_time=1.4)
        moving=Dot(o,color=BLUE,radius=.10)
        self.add(moving);self.play(moving.animate.move_to(p),run_time=1.6)
        ray=Line(o,p,color=BLUE,stroke_width=5)
        self.play(Create(ray),FadeOut(look),run_time=.65)
        self.at(1)
        horizontal=Line(o,axes.c2p(4,0),color=RED,stroke_width=4)
        vertical=Line(axes.c2p(4,0),p,color=GREEN,stroke_width=4)
        labels=VGroup(text('4',26,RED).next_to(horizontal,DOWN,buff=.14),text('3',26,GREEN).next_to(vertical,RIGHT,buff=.16),text('5',28,BLUE).move_to((o+p)/2+np.array([-.35,.30,0])))
        side=card(['直交座標  (4, 3)'.replace('直交座標','직교좌표'),'오른쪽 4 · 위쪽 3'],width=5.1).move_to([3.15,1.20,0])
        polar=card(['극좌표  (5, 약37°)','거리 5 · 각도 약37°'],width=5.1).move_to([3.15,-.45,0])
        self.play(Create(horizontal),Create(vertical),FadeIn(labels),FadeIn(side),FadeIn(polar),run_time=1)
        self.at(2)
        rp=text('r = 5',26,BLUE).move_to([2.2,-1.6,0]);tp=text('θ ≈ 36.87°',26,GREEN).move_to([4.4,-1.6,0])
        self.play(FadeIn(rp),FadeIn(tp),run_time=.7)
        self.at(3)
        radius=np.linalg.norm(p-o)
        ring=Circle(radius=radius,color=BLUE,stroke_width=2).move_to(o)
        self.play(FadeOut(horizontal),FadeOut(vertical),FadeOut(labels),FadeOut(arc),FadeOut(axes),FadeOut(labs),Create(ring),run_time=.6)
        new_o=np.array([-3.55,-.2,0])
        diagram=VGroup(axes,labs,origin,moving,ray,ring)
        self.play(diagram.animate.scale(.82,about_point=o).shift(new_o-o),run_time=.6)
        self.play(Rotate(VGroup(moving,ray),angle=TAU,about_point=new_o),run_time=3.3,rate_func=linear)
        self.finish()

class Convert(Timed,Scene):
    sid='05'
    def construct(self):
        self.init();self.add(heading('거리와 각도를 x, y로 바꾸기','삼각형의 비율로 이해합니다'))
        axes,o,labs=plane_objects();p=axes.c2p(4,3);q=axes.c2p(4,0)
        tri=Polygon(o,q,p,fill_color=LIGHT,fill_opacity=.45,stroke_width=0)
        h=Line(o,q,color=RED,stroke_width=5);v=Line(q,p,color=GREEN,stroke_width=5);r=Line(o,p,color=BLUE,stroke_width=5)
        corner=RightAngle(Line(q,o),Line(q,p),length=.18,color=MUTED)
        theta=Arc(radius=.63,angle=math.atan2(3,4),color=GREEN).shift(o)
        self.add(axes,labs);self.play(FadeIn(tri),Create(h),Create(v),Create(r),Create(corner),Create(theta),FadeIn(Dot(p,color=BLUE)),run_time=1)
        self.at(1)
        labels=VGroup(text('x = 4',27,RED).next_to(h,DOWN,buff=.15),text('y = 3',27,GREEN).next_to(v,RIGHT,buff=.15),text('r = 5',27,BLUE).move_to((o+p)/2+[-.45,.33,0]))
        self.play(FadeIn(labels),run_time=.7)
        self.at(2)
        eq=VGroup(text('cos θ = x / r',34,RED),text('sin θ = y / r',34,GREEN)).arrange(DOWN,buff=.48).move_to([3.4,.95,0])
        self.play(FadeIn(eq,shift=.15*UP),run_time=.8)
        self.at(3)
        solution=VGroup(text('x = r cos θ',36,RED),text('y = r sin θ',36,GREEN)).arrange(DOWN,buff=.48).move_to(eq)
        self.play(ReplacementTransform(eq,solution),run_time=.9)
        nums=card(['(5, 36.87°)  →  約(4, 3)'.replace('約','약'),'x ≈ 4    y ≈ 3'],width=5.2,height=1.2,color=BLUE).move_to([3.35,-1.05,0])
        self.play(FadeIn(nums),run_time=.7)
        self.at(4)
        units=text('도 → 라디안 : θrad = θdeg × π / 180',22,MUTED).move_to([.1,-2.35,0])
        self.play(FadeIn(units),run_time=.6)
        self.finish()

class Cylinder(Timed,ThreeDScene):
    sid='07'
    def construct(self):
        self.init()
        title=heading('평면의 원에 높이를 더하면?','3D 미리보기 · 이 그림에서는 z가 높이입니다')
        self.add_fixed_in_frame_mobjects(title)
        axes=ThreeDAxes(x_range=[-3,3,1],y_range=[-3,3,1],z_range=[0,3,1],x_length=5,y_length=5,z_length=2.5,axis_config={'color':LINE,'stroke_width':2})
        self.set_camera_orientation(phi=0*DEGREES,theta=-90*DEGREES,zoom=.80)
        radius=1.8;bottom=Circle(radius=radius,color=BLUE,stroke_width=3)
        top=bottom.copy().shift(2*OUT).set_color(GREEN)
        cylinder=Surface(lambda u,v: np.array([radius*np.cos(u),radius*np.sin(u),v]),u_range=[0,TAU],v_range=[0,2],resolution=(18,4),fill_opacity=.06,checkerboard_colors=[LIGHT,LIGHT],stroke_width=.35,stroke_color=LINE)
        a=ValueTracker(0);height=ValueTracker(0)
        dot=always_redraw(lambda:Dot3D([radius*np.cos(a.get_value()),radius*np.sin(a.get_value()),height.get_value()],radius=.13,color=BLUE,resolution=(8,8)))
        projection=always_redraw(lambda:Line([radius*np.cos(a.get_value()),radius*np.sin(a.get_value()),0],[radius*np.cos(a.get_value()),radius*np.sin(a.get_value()),height.get_value()],color=GREEN,stroke_width=3))
        radial=always_redraw(lambda:Line(ORIGIN,[radius*np.cos(a.get_value()),radius*np.sin(a.get_value()),0],color=BLUE,stroke_width=3))
        self.add(axes,bottom,dot,radial)
        self.play(a.animate.set_value(PI),run_time=2.2,rate_func=linear)
        self.at(1)
        self.add(projection)
        self.play(FadeIn(cylinder),Create(top),height.animate.set_value(2),run_time=1.1)
        self.move_camera(phi=64*DEGREES,theta=-48*DEGREES,zoom=.8,run_time=2.2)
        label=text('(r, θ, z) = 距離・角度・高さ'.replace('距離・角度・高さ','거리 · 각도 · 높이'),28,BLUE).move_to([.15,-2.28,0])
        self.add_fixed_in_frame_mobjects(label)
        self.play(a.animate.set_value(PI+TAU),run_time=2.2,rate_func=linear)
        self.at(2)
        self.remove(label)
        takeaway=text('얼마나 멀리?  어느 방향?',29,GREEN).move_to([.0,-2.35,0])
        self.add_fixed_in_frame_mobjects(takeaway)
        self.begin_ambient_camera_rotation(rate=.055)
        self.finish();self.stop_ambient_camera_rotation()

class BrandIntro(Scene):
    def construct(self):
        self.camera.background_color=WHITE
        logo=ImageMobject(str(ROOT/'shared/assets/branding/yamyamcoding-cats-original.png')).set_height(2.65)
        title=text('얌얌코딩',34,INK).next_to(logo,DOWN,buff=.3)
        self.play(FadeIn(logo,scale=.96),FadeIn(title),run_time=.5)
        self.wait(1.1);self.play(FadeOut(logo),FadeOut(title),run_time=.4)

class MemberOutro(Scene):
    def construct(self):
        self.camera.background_color=WHITE
        title=text('멤버쉽가입 감사드립니다.',40).to_corner(UL,buff=.7)
        sub=text('함께 배우고, 직접 만드는 시간을 응원합니다.',24,MUTED).next_to(title,DOWN,aligned_edge=LEFT,buff=.25)
        shot=ImageMobject(str(ROOT/'shared/assets/membership/member-list-20260929.png')).set_height(6.5).move_to([4.3,0,0])
        logo=ImageMobject(str(ROOT/'shared/assets/branding/yamyamcoding-cats-original.png')).set_height(.65).to_corner(DR,buff=.35)
        coach=text('프로그래밍 코칭 · 과외',29,BLUE).move_to([-3.5,.25,0])
        url=text('https://www.yamyamcoding.com/\n1430b1ff-a61e-8040-a542-d672d5d25328',19,MUTED).next_to(coach,DOWN,buff=.35)
        self.add(sub,shot,logo,coach,url);self.play(FadeIn(title),run_time=.5)
        self.wait(9);self.play(FadeOut(title),run_time=.5)

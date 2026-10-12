"""Projected overview/conclusion repairs. Original PCM and shared lesson unchanged."""
from pathlib import Path
import os,sys,json
import numpy as np
from manim import *
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'manim/projects/game-math-part2-full-series'))
from lesson import P,body,basis,arrow,rz,txt,fit,logical_box,INK,MUTED,RULE,RED,GREEN,BLUE,GOLD,PALE
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
TEAL='#177d86';ORANGE='#b36317'

def bicycle(origin):
    wheels=VGroup(*[Circle(radius=.36,color=INK,stroke_width=3).shift([x,0,0]) for x in [-.65,.65]])
    points=[[-.65,0,0],[-.12,.65,0],[.32,.65,0],[.65,0,0],[0,0,0]]
    edges=[(0,1),(1,4),(4,0),(1,2),(2,4),(2,3),(4,3)]
    frame=VGroup(*[Line(points[a],points[b],color=TEAL,stroke_width=4) for a,b in edges])
    saddle=logical_box([.45,.1,.2],[-.12,.73,0],ORANGE)
    handle=logical_box([.23,.1,.25],[.45,.8,0],BLUE)
    parts=VGroup(wheels,frame,saddle,handle);parts.apply_matrix(P);parts.shift(origin);return parts

class OverviewRevision(ThreeDScene):
    sid=''
    def fixed(self,*items):self.add_fixed_in_frame_mobjects(*items)
    def until(self,t):
        delta=t-self.renderer.time
        if delta>1/60:self.wait(delta,frozen_frame=True)
    def note(self,message,color=BLUE):
        if getattr(self,'active_note',None):self.remove(self.active_note)
        self.active_note=fit(txt(message,28,color),12).move_to([0,1.75,0]);self.fixed(self.active_note)
    def construct(self):
        path=os.environ.get('ORIENTATION_OVERVIEW_TIMING');assert path
        slot=next(s for s in json.loads(Path(path).read_text('utf-8-sig'))['scenes'] if s['id']==self.sid)
        self.camera.background_color=WHITE
        self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.83)
        self.fixed(fit(txt(slot['title'],40),12.7).move_to([-6.4,3.36,0],aligned_edge=LEFT),
          txt('흰 입체 개념모델 · 게임 내부 축이나 수치의 측정 아님',20,MUTED).move_to([-6.4,2.9,0],aligned_edge=LEFT),
          Line([-6.45,2.6,0],[6.45,2.6,0],color=RULE,stroke_width=1))
        if self.sid=='01b':self.examples(slot)
        elif self.sid=='01':self.opening(slot)
        else:self.conclusion(slot)
        self.until(slot['seconds']);assert self.renderer.time<=slot['seconds']+.10
    def opening(self,slot):
        left=np.array([-2.6,-2.7,-.4]);right=np.array([2.6,2.7,-.4])
        a=body(np.eye(3),left,1.65);b=body(np.eye(3),right,1.65)
        self.add(a,b)
        forward=VGroup(arrow(left,left+2.7*P[:,2],BLUE,4),arrow(right,right+2.7*P[:,2],BLUE,4));self.add(forward)
        self.comparison_label=txt('같은 앞 방향 · 서로 다른 몸의 기울기',24,BLUE).move_to([0,-2.3,0]);self.fixed(self.comparison_label)
        for i,t in enumerate(slot['lineStarts']):
            self.until(t)
            if i==0:
                self.note('방향 하나로 전체 자세를 정할 수 있을까요?')
                self.play(Rotate(b,angle=PI/3,axis=P[:,2],about_point=right),run_time=1.2)
            elif i==1:
                self.note('다음 실제 비행에서 위치와 자세를 따로 관찰')
                self.play(Indicate(a,color=GOLD),Indicate(b,color=GOLD),run_time=.65)
            elif i==2:
                self.note('몸의 세 축 → 같은 바깥 기준의 행렬 열')
                axes=basis(np.eye(3),left,2.25,with_body=False);turned=basis(rz(PI/3),right,2.25,with_body=False)
                self.play(Create(axes),Create(turned),run_time=.7)
                self.fixed(txt('x 빨강 · y 초록 · z 파랑',24,MUTED).move_to([0,-2.65,0]))
                for axis in turned:self.play(Indicate(axis,color=GOLD),run_time=.22)
            else:
                self.note('되돌리기 · 올바른 회전 검사 · 직접 검산',GREEN)
                self.play(Rotate(b,angle=-PI/3,axis=P[:,2],about_point=right),Rotate(turned,angle=-PI/3,axis=P[:,2],about_point=right),run_time=.9)
                self.remove(self.comparison_label);self.fixed(txt('몸과 세 축이 같은 자세로 되돌아온 결과',24,BLUE).move_to([0,-2.3,0]))
                self.fixed(txt('입력 공간 → 계산 → 결과 공간',28,GREEN).move_to([0,-1.9,0]))
    def examples(self,slot):
        camera_right=np.array([-np.sin(-48*DEGREES),np.cos(-48*DEGREES),0]);origins=[camera_right*x/.83+np.array([0,0,-.35]) for x in [-4.9,-1.65,1.65,4.9]]
        models=[]
        for i,o in enumerate(origins):
            floor=logical_box([1.9,.12,1.7],[0,-.5,0],PALE);floor.apply_matrix(P);floor.shift(o)
            if i in [0,2]:model=body(np.eye(3),o,.95)
            elif i==1:model=bicycle(o).scale(.95,about_point=o)
            else:
                base=logical_box([1.5,.18,1.1],[0,0,0],BLUE);part=logical_box([.55,.7,.55],[.35,.47,0],ORANGE)
                model=VGroup(base,part);model.apply_matrix(P);model.shift(o)
            models.append(model);self.add(floor,model)
        labels=['비행 / Superflight','자전거 / Descenders','조립 비행기 / Trailmakers','부품 배치 / Space Engineers']
        for x,label in zip([-4.9,-1.65,1.65,4.9],labels):self.fixed(fit(txt(label,24,BLUE),3.05).move_to([x,-1.65,0]))
        self.note('네 예시를 같은 질문으로 비교합니다')
        self.until(.15);self.play(Rotate(models[0],angle=PI/5,axis=P[:,2],about_point=origins[0]),run_time=.5)
        self.until(.65);self.play(Rotate(models[1],angle=PI/8,axis=P[:,2],about_point=origins[1]),run_time=.5)
        self.until(2.28);self.play(Indicate(models[2],color=GOLD),run_time=.55)
        self.until(3.5);self.play(Rotate(models[3][1],angle=PI/2,axis=P[:,1],about_point=models[3][1].get_center()),run_time=.55)
        self.until(4.58);self.note('공통 기준: 위치 · 앞 방향 · 전체 자세',GREEN)
        self.fixed(txt('이 개요의 모형은 설명이며 실제 게임 예시 시간에 포함하지 않습니다.',20,MUTED).move_to([0,-2.5,0]))
    def conclusion(self,slot):
        origin=np.array([-2.45,-2.45,-.6]);obj=basis(np.eye(3),origin,2.7);obj[0].scale(1.65,about_point=origin);self.add(obj)
        for i,t in enumerate(slot['lineStarts']):
            self.until(t)
            if i==0:
                self.note('방향 하나 ≠ 전체 자세')
                self.play(Rotate(obj,angle=PI/3,axis=P[:,2],about_point=origin),run_time=1.0)
            elif i==1:
                self.note('세 로컬 축을 같은 월드 기준으로 기록')
                for axis in obj[1]:self.play(Indicate(axis,color=GOLD),run_time=.3)
                self.fixed(txt('R = [ x_body  y_body  z_body ]',29,GOLD,font='Consolas').move_to([3.1,-.25,0]))
            elif i==2:
                self.note('입출력 공간 · 열벡터 약속 · 회전 검사',GREEN)
                self.fixed(txt('R^T R = I\ndet(R) = +1',30,GREEN,font='Consolas').move_to([3.1,-1.35,0]))
                self.play(Indicate(obj[1],color=GREEN),run_time=.65)
            else:
                self.note('다음 질문: 회전 순서는 왜 결과를 바꿀까요?',BLUE)
                self.play(Rotate(obj,angle=PI/5,axis=P[:,0],about_point=origin),run_time=.8)
                self.fixed(txt('축각 표현 · 짐벌락으로 이어집니다.',24,MUTED).move_to([0,-2.5,0]))

for sid in ['01','01b','24']:
    globals()['OverviewScene'+sid]=type('OverviewScene'+sid,(OverviewRevision,),{'sid':sid,'__module__':__name__})

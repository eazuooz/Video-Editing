"""Scoped projected teaching bridges and two target repairs; baseline untouched.

Logical math: right-handed y-up, column vectors, local -> world.
P is only the proper presentation rotation into Manim's z-up coordinates.
Use an explicitly saved revision timing; prototype timing is never final timing.
"""
from pathlib import Path
import os,sys,json
import numpy as np
from manim import *
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'manim/projects/game-math-part2-full-series'))
from lesson import P,body,basis,arrow,rx,rz,txt,fit,INK,MUTED,RULE,RED,GREEN,BLUE,GOLD
RDIR=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
TEAL='#177d86';ORANGE='#b36317'

class TeachingRevision(ThreeDScene):
    sid=''
    def fixed(self,*items):self.add_fixed_in_frame_mobjects(*items)
    def fixed_note(self,message,color=BLUE):
        if getattr(self,'note',None):
            self.play(FadeOut(self.note),run_time=.12);self.remove(self.note)
        self.note=fit(txt(message,29,color),12.3).move_to([0,1.7,0])
        self.fixed(self.note);self.play(FadeIn(self.note),run_time=.2)
    def wait_until(self,t):
        gap=t-self.renderer.time
        if gap>1/60:self.wait(gap,frozen_frame=True)
    def construct(self):
        timing_path=os.environ.get('ORIENTATION_REVISION_TIMING')
        assert timing_path,'Use the explicitly saved prototype/measured revision timing.'
        slot=next(x for x in json.loads(Path(timing_path).read_text('utf-8-sig'))['scenes'] if x['id']==self.sid)
        if self.sid in ['12','18']:
            data=json.loads((ROOT/'production/batches/game-math-part2-full-series/lessons/game-math-orientation-matrices.json').read_text('utf-8-sig'))
            row=next(x for x in data['scenes'] if x['id']==self.sid)
            title=row['title'];beats=row['beats']
        else:
            row=next(x for x in json.loads((RDIR/'script/additions.ko.json').read_text('utf8'))['scenes'] if x['id']==self.sid)
            title=row['title'];beats={
                '06a':['몸에 붙인 자 / 방에 고정한 자','같은 화살표 · 다른 기준의 숫자','행렬의 열 = 바깥에서 읽은 몸의 세 축'],
                '09a':['앞: 몸 → 바깥','이번: 바깥 → 몸','내적: 각 축 방향의 몫','순수 회전에서 R 역행렬 = R 전치'],
                '13a':['숫자로 적은 축 ≠ 모두 회전','길이·직각이 바뀌면 물체가 찌그러짐','길이 1 · 서로 직각 · 오른손','다음 식은 세 검사를 요약'],
                '16a':['평행한 조각을 빼기','남은 길이를 1로 맞추기','빼고 · 정규화하는 교정','0길이 / 평행 입력은 별도 처리'],
                '21a':['시작·목표만으로 중간의 안전성을 보장 못함','숫자 절반 혼합 → 두 축이 사라짐','같은 길이 검사로 확인']}[self.sid]
        self.camera.background_color=WHITE
        self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.83)
        self.fixed(fit(txt(title,40),12.7).move_to([-6.4,3.36,0],aligned_edge=LEFT),
            txt('게임수학 · 오른손 / 열벡터 · 개념모델 (게임 내부 측정 아님)',20,MUTED).move_to([-6.4,2.9,0],aligned_edge=LEFT),
            Line([-6.45,2.6,0],[6.45,2.6,0],color=RULE,stroke_width=1))
        if self.sid=='12':self.composition(slot,beats)
        elif self.sid=='18':self.storage(slot,beats)
        else:self.bridge(slot,beats)
        self.wait_until(slot['seconds'])
        assert self.renderer.time<=slot['seconds']+.12,(self.sid,self.renderer.time,slot['seconds'])
    def world(self,origin):
        axes=VGroup(*[DashedLine(origin-2.1*P[:,i],origin+2.2*P[:,i],color=RULE,stroke_width=1.7) for i in range(3)])
        self.add(axes)
        self.fixed(txt('x: 빨강    y: 초록    z: 파랑',23,MUTED).move_to([-3.3,-2.15,0]))
    def formula(self,text):
        if getattr(self,'mathlabel',None):self.remove(self.mathlabel)
        self.mathlabel=fit(txt(text,31,GOLD,font='Consolas'),6.05).move_to([3.0,-.4,0]);self.fixed(self.mathlabel)
    def bridge(self,slot,beats):
        o=np.array([-2.45,-2.45,-.28]);self.world(o)
        matrix=rz(PI/2) if self.sid in ['06a','09a'] else np.eye(3)
        obj=basis(matrix,o);self.add(obj)
        self.fixed(txt('몸에 붙인 세 축',23,BLUE).move_to([-3.3,-2.55,0]))
        for i,beat in enumerate(beats):
            self.wait_until(slot['lineStarts'][i]);self.fixed_note(beat,GREEN if i==len(beats)-1 else BLUE)
            if self.sid=='06a':
                if i==0:self.play(Indicate(obj[1],color=GOLD),run_time=.6)
                if i==1:
                    self.formula('local (1,0,0)\nworld (0,1,0)')
                    self.play(Indicate(obj[1][0],color=RED),run_time=.6)
                if i==2:
                    self.formula('R = [ x_body  y_body  z_body ]\ncolumns read in world')
                    for axis in obj[1]:self.play(Indicate(axis,color=GOLD),run_time=.24)
            elif self.sid=='09a':
                if i==0:self.formula('v_world = R v_local')
                if i==1:
                    v=np.array([-1,2,0.]);self.external=arrow(o,o+.75*P@v,ORANGE,5);self.add(self.external)
                    self.formula('world (-1,2,0)')
                if i==2:
                    first=o+.75*P@np.array([0,2,0.]);end=o+.75*P@np.array([-1,2,0.])
                    self.play(Create(arrow(o,first,RED,5)),Create(arrow(first,end,GREEN,5)),run_time=.65)
                    self.formula('dot(x_body,v) = 2\ndot(y_body,v) = 1')
                if i==3:self.formula('R^T v_world = (2,1,0)\nR^T R = I')
            elif self.sid=='13a':
                if i==0:self.formula('axes: three columns')
                if i==1:
                    bad=np.array([[1.5,.5,0],[0,1,0],[0,0,1.]])
                    self.play(Transform(obj,basis(bad,o)),run_time=.9);self.formula('length != 1\ndot(x,y) != 0')
                if i==2:
                    self.play(Transform(obj,basis(np.eye(3),o)),run_time=.9);self.formula('length = 1\nright angles\nright-handed')
                if i==3:self.formula('R^T R = I\ndet(R) = +1')
            elif self.sid=='16a':
                if i==0:
                    skew=np.array([[1,.6,0],[0,.8,0],[0,0,1.]])
                    self.play(Transform(obj,basis(skew,o)),run_time=.7)
                    parallel=arrow(o,o+2.05*P@np.array([.6,0,0]),ORANGE,5);self.add(parallel)
                    self.formula("y' = y - dot(x,y) x")
                    corrected=np.diag([1,.8,1.]);self.play(Transform(obj,basis(corrected,o)),FadeOut(parallel),run_time=.9)
                if i==1:
                    self.play(Transform(obj,basis(np.eye(3),o)),run_time=.9);self.formula("y_new = y' / length(y')")
                if i==2:self.formula('remove parallel part\nthen normalize')
                if i==3:self.formula("length(y') > epsilon\notherwise: fallback")
            elif self.sid=='21a':
                if i==0:self.formula('start = I\ntarget = Rz(180 deg)')
                if i==1:
                    self.play(Transform(obj,basis(np.diag([0.,0.,1.]),o)),run_time=1.2)
                    self.formula('0.5 I + 0.5 Rz(180)\n= diag(0,0,1)')
                if i==2:self.formula('length(x) = 0\nlength(y) = 0\nnot a rotation')
    def composition(self,slot,beats):
        o=np.array([-2.45,-2.45,-.28]);self.world(o)
        A=rx(PI/2);B=rz(PI/2);offset=np.array([1.,0,0])
        parent=body(np.eye(3),o,1.55);self.add(parent)
        child=body(B,o+P@offset,.48);child.set_color(ORANGE);self.add(child)
        child_axes=basis(B,o+P@offset,.75,with_body=False);self.add(child_axes)
        self.fixed(txt('큰 몸체: 부모    주황 부품: 자식',23,MUTED).move_to([-3.2,-2.55,0]))
        for i,beat in enumerate(beats):
            self.wait_until(slot['lineStarts'][i]);self.fixed_note(beat,GREEN if i==5 else BLUE)
            if i==0:
                self.formula('B = Rz(90 deg)\nchild x -> parent y');self.play(Indicate(child_axes[0],color=GOLD),run_time=.6)
            if i==1:
                target_parent=body(A,o,1.55);target_child=body(A@B,o+P@A@offset,.48);target_child.set_color(ORANGE)
                self.play(Transform(parent,target_parent),Transform(child,target_child),Transform(child_axes,basis(A@B,o+P@A@offset,.75,with_body=False)),run_time=1.1)
                self.formula('A = Rx(90 deg)\nparent y -> world z')
            if i==2:self.formula('child (1,0,0)\nB -> parent (0,1,0)\nA -> world (0,0,1)')
            if i==3:self.formula('A B v = A(Bv)\nrightmost acts first')
            if i==4:self.play(Indicate(child,color=GOLD),Indicate(parent,color=TEAL),run_time=.65)
            if i==5:self.formula('A B (1,0,0) = (0,0,1)\nB A (1,0,0) = (0,1,0)')
    def storage(self,slot,beats):
        # Explicit oblique projection of 3D cube front/top/right faces. Fixed
        # camera-space layout separates every label from geometry and captions.
        def cell(x,y,color):
            a=np.array([x-.235,y-.235,0]); b=np.array([x+.235,y-.235,0])
            c=np.array([x+.235,y+.235,0]); d=np.array([x-.235,y+.235,0])
            depth=np.array([.16,.12,0])
            top=Polygon(d,c,c+depth,d+depth,fill_color=interpolate_color(ManimColor(color),WHITE,.25),fill_opacity=1,stroke_color=WHITE,stroke_width=1)
            side=Polygon(b,c,c+depth,b+depth,fill_color=interpolate_color(ManimColor(color),BLACK,.22),fill_opacity=1,stroke_color=WHITE,stroke_width=1)
            front=Polygon(a,b,c,d,fill_color=color,fill_opacity=1,stroke_color=WHITE,stroke_width=1)
            return VGroup(side,top,front)
        arrays=[]
        for n,cols,x,color in [(9,3,-4.1,BLUE),(3,3,0,GREEN),(4,2,4.1,GOLD)]:
            grid=VGroup(*[cell(x+((j%cols)-(cols-1)/2)*.72,-.5+((j//cols)-(n//cols-1)/2)*.72,color) for j in range(n)])
            self.fixed(grid);arrays.append(grid)
        self.fixed(txt('Matrix / 36 B',30,BLUE).move_to([-4.1,1.05,0]),
                   txt('Euler / 12 B',30,GREEN).move_to([0,1.05,0]),
                   txt('Quaternion / 16 B',30,GOLD).move_to([4.1,1.05,0]),
                   txt('한 칸 = float32 성분 4 B',24,MUTED).move_to([0,-2.15,0]),
                   txt('성분 수와 회전 자유도를 구분',24,MUTED).move_to([0,-2.55,0]))
        for i,beat in enumerate(beats):
            self.wait_until(slot['lineStarts'][i]);self.fixed_note(beat,GREEN if i==5 else BLUE)
            if i==0:self.play(Indicate(arrays[0],color=GOLD,scale_factor=1.12),run_time=.6)
            if i==1:self.fixed(txt('회전 자유도 = 3',26,ORANGE).move_to([0,-1.72,0]))
            if i==2:self.play(Indicate(arrays[0],color=BLUE,scale_factor=1.12),Indicate(arrays[1],color=GREEN,scale_factor=1.12),run_time=.7)
            if i==3:self.play(Indicate(arrays[2],color=GOLD,scale_factor=1.12),run_time=.7)

for sid in ['06a','09a','13a','16a','21a','12','18']:
    globals()['RevisionScene'+sid]=type('RevisionScene'+sid,(TeachingRevision,),{'sid':sid,'__module__':__name__})

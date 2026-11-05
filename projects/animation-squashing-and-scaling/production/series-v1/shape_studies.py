"""Continuous 2-D projections of original matched geometry, authored in Manim."""
from manim import *
import numpy as np

FLOOR=-1.52
PEACH='#F1B680'
MINT='#77D1B7'
WHITE='#EFF1E9'

def profile(xangle):
    return np.array([np.cos(xangle),np.sin(xangle),0.])

def contour(x,y,shape):
    theta=np.linspace(0,TAU,49)
    points=[np.array([x,y,0])+shape(t) for t in theta]
    path=VMobject().set_points_smoothly(points)
    path.close_path()
    return path

def squish(point,tall,wide,bulge):
    x,y,_=point
    # A blend shape changes vertex positions while preserving the four extrema.
    return np.array([wide*x*(1+bulge*(1-x*x)),tall*y,0])

def glove(x,y,scale,color):
    points=np.array([[-.88,-.24],[-.81,.24],[-.58,.31],[-.47,.46],[-.29,.49],
                     [-.19,.45],[-.07,.54],[.11,.54],[.19,.45],[.31,.49],[.48,.45],
                     [.51,.34],[.64,.31],[.70,.13],[.65,-.04],[.56,-.13],
                     [.52,-.27],[.34,-.37],[-.05,-.43],[-.47,-.35],[-.88,-.24]])
    palm=VMobject().set_points_smoothly([[x+scale*a,y+scale*b,0] for a,b in points])
    palm.close_path()
    palm.set_fill(color,1).set_stroke(WHITE,3)
    detail=VGroup()
    for px,py in ((-.2,.45),(.18,.46),(.49,.34)):
        detail.add(ArcBetweenPoints([x+px*scale,y+py*scale,0],
                   [x+(px-.06)*scale,y+(py-.22)*scale,0],angle=.28,color='#544042',stroke_width=3))
    thumb=ArcBetweenPoints([x-.34*scale,y-.13*scale,0],[x+.48*scale,y-.08*scale,0],angle=-.42,color='#544042',stroke_width=4)
    cuff=Line([x-.69*scale,y+.19*scale,0],[x-.72*scale,y-.24*scale,0],color=WHITE,stroke_width=5)
    return VGroup(palm,detail,thumb,cuff)

class Study(Scene):
    kind=''
    def construct(self):
        self.camera.background_color='#101A18'
        grid=NumberPlane(x_range=[-8,8,.5],y_range=[-5,5,.5],
            background_line_style={'stroke_color':'#304039','stroke_width':1,'stroke_opacity':.65},
            axis_config={'stroke_opacity':0})
        self.add(grid,Line([-7,FLOOR,0],[7,FLOOR,0],color='#A5B9A9',stroke_width=2))
        tracker=ValueTracker(0)
        def pair():
            t=tracker.get_value()
            group=VGroup()
            approach=np.clip((t-7)/20,0,1)
            settle=np.clip((t-33)/28,0,1)
            blend=approach*(1-settle)
            for side in range(2):
                cx=(-3.25,3.25)[side]; tint=(PEACH,MINT)[side]
                if self.kind=='fist':
                    armend=cx-.45+1.05*blend
                    arm=Line([cx-1.65,-.12,0],[armend,-.12,0],stroke_width=21,color=tint)
                    group.add(arm,glove(armend,-.12,1+side*.72*blend,tint))
                    continue
                if self.kind=='bounce':
                    # The lowest point and contact time of the two objects are identical.
                    z=max(0,(t-27)/33) if t>=27 else max(0,(27-t)/27)
                    travel=2.05*min(1,z)**1.25
                    squash=max(0,1-abs(t-27)/9)
                    stretch=max(0,1-abs(t-40)/9)
                    tall=1+side*(-.45*squash+.28*stretch)
                    wide=tall**(-.5) if side else 1
                    bulge=0
                elif self.kind=='volume':
                    travel=0;tall=1-.5*blend
                    wide=1/tall if side else 1; bulge=0
                else:
                    travel=0;tall=1-.48*blend;wide=1+.51*blend
                    bulge=.53*side*blend
                cy=FLOOR+tall+travel
                fn=lambda theta:squish(profile(theta),tall,wide,bulge)
                surface=contour(cx,cy,fn).set_fill(tint,.92).set_stroke(WHITE,3)
                group.add(surface)
                for amount in (-.55,0,.55):
                    pts=[]
                    for y in np.linspace(-.99,.99,21):
                        x=amount*np.sqrt(1-y*y)
                        pts.append(np.array([cx,cy,0])+squish([x,y,0],tall,wide,bulge))
                    group.add(VMobject().set_points_smoothly(pts).set_stroke('#376658',2))
                if self.kind=='morph':
                    for theta in np.linspace(0,TAU,16,endpoint=False):
                        group.add(Dot(np.array([cx,cy,0])+fn(theta),radius=.036,color=WHITE))
                if self.kind=='volume':
                    group.add(Line([cx-wide,cy,0],[cx+wide,cy,0],color='#344F42',stroke_width=4))
                    group.add(Line([cx,FLOOR,0],[cx,FLOOR+2*tall,0],color='#344F42',stroke_width=4))
            return group
        dynamic=always_redraw(pair);self.add(dynamic)
        self.play(tracker.animate.set_value(120),run_time=2,rate_func=linear)

class Bounce(Study):kind='bounce'
class Volume(Study):kind='volume'
class Morph(Study):kind='morph'
class Fist(Study):kind='fist'

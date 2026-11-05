"""Offscreen, deterministic 1920x1080 drawing primitives for the door lesson."""
from functools import lru_cache
from math import cos, sin, pi
from pathlib import Path
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QImage, QPainter, QPainterPath, QPen, QPolygonF

BG='#000000'; INK='#f5f5f5'; MUTED='#b8b8b8'; GOLD='#e8cf83'
TEAL='#73c7c2'; GREEN='#a4c6a0'; RED='#ef8585'; ORANGE='#f39a4b'
PANEL='#12181c'; FIELD='#0a1012'; LINE='#344448'; DIM='#799095'
WIDTH,HEIGHT=1920,1080
ASSETS=Path(__file__).resolve().parents[1]/'research/local/evidence'
TUTORIAL=Path('C:/Program Files/Epic Games/UE_5.8/Engine/Content/Tutorial/BlueprintTutorials/TutorialAssets')

def clamp(x): return max(0.,min(1.,x))
def ease(x):
    x=clamp(x)
    return x*x*(3-2*x)
@lru_cache(None)
def font(size,bold,mono):
    f=QFont('Consolas' if mono else 'Malgun Gothic')
    f.setPixelSize(round(size));f.setWeight(QFont.Weight.Bold if bold else QFont.Weight.Normal)
    return f
@lru_cache(None)
def asset(name):
    path=(TUTORIAL/name if name in {'DoorOpenShut.png','ClassBlueprint.png','BP_Overview.png'} else ASSETS/name)
    image=QImage(str(path))
    if image.isNull():raise FileNotFoundError(path)
    return image

class Stage:
    def __init__(self,p):self.p=p
    def rect(self,x,y,w,h,fill,stroke=None,sw=2,r=0):
        self.p.setBrush(QColor(fill) if fill else Qt.BrushStyle.NoBrush)
        self.p.setPen(QPen(QColor(stroke),sw) if stroke else Qt.PenStyle.NoPen)
        self.p.drawRoundedRect(QRectF(x,y,w,h),r,r)
    def line(self,pts,col=LINE,sw=3):
        self.p.setBrush(Qt.BrushStyle.NoBrush)
        self.p.setPen(QPen(QColor(col),sw,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap,Qt.PenJoinStyle.RoundJoin))
        self.p.drawPolyline(QPolygonF([QPointF(*pt) for pt in pts]))
    def poly(self,pts,fill,stroke=None,sw=2):
        self.p.setBrush(QColor(fill));self.p.setPen(QPen(QColor(stroke),sw) if stroke else Qt.PenStyle.NoPen)
        self.p.drawPolygon(QPolygonF([QPointF(*pt) for pt in pts]))
    def circle(self,x,y,r,fill,stroke=None,sw=2):
        self.p.setBrush(QColor(fill) if fill else Qt.BrushStyle.NoBrush)
        self.p.setPen(QPen(QColor(stroke),sw) if stroke else Qt.PenStyle.NoPen)
        self.p.drawEllipse(QPointF(x,y),r,r)
    def text(self,x,y,msg,size=42,color=INK,bold=False,mono=False,align='left',maxw=0):
        f=font(size,bold,mono);fm=QFontMetricsF(f);w=fm.horizontalAdvance(msg)
        if maxw and w>maxw:
            f=font(max(18,int(size*maxw/w)),bold,mono);fm=QFontMetricsF(f);w=fm.horizontalAdvance(msg)
        self.p.setFont(f);self.p.setPen(QColor(color))
        left=x-(w if align=='right' else w/2 if align=='center' else 0)
        self.p.drawText(QPointF(left,y+fm.ascent()),msg)
        return w
    def picture(self,name,x,y,w,h):
        im=asset(name);scale=min(w/im.width(),h/im.height())
        rw,rh=im.width()*scale,im.height()*scale
        self.p.drawImage(QRectF(x+(w-rw)/2,y+(h-rh)/2,rw,rh),im)
    def arrow(self,x1,y1,x2,y2,col=TEAL,progress=1,sw=5):
        p=clamp(progress);xe=x1+(x2-x1)*p;ye=y1+(y2-y1)*p
        self.line([(x1,y1),(xe,ye)],col,sw)
        if p<.01:return
        length=max(.01,((x2-x1)**2+(y2-y1)**2)**.5)
        ux,uy=(x2-x1)/length,(y2-y1)/length
        size=min(16.,length*p*.55)
        self.poly([(xe,ye),(xe-ux*size+uy*size*.48,ye-uy*size-ux*size*.48),
                   (xe-ux*size-uy*size*.48,ye-uy*size+ux*size*.48)],col)
    def header(self,title,kind,section):
        self.text(95,54,'얌얌코딩',31,GOLD,True)
        self.line([(269,67),(269,95)],LINE,2)
        self.text(292,56,'UNREAL ENGINE',29,DIM,True,True)
        self.text(1824,57,kind,28,MUTED,False,False,'right',760)
        self.line([(96,118),(1824,118)],LINE,2)
        self.text(94,153,title,61,GOLD,True,maxw=1730)
    def tag(self,x,y,txt,color=TEAL):
        w=QFontMetricsF(font(30,True,False)).horizontalAdvance(txt)
        self.line([(x,y+7),(x,y+38)],color,6)
        self.text(x+16,y,txt,30,color,True)
        return w+18
    def caption(self,x,y,txt):
        self.text(x,y,txt,32,MUTED)
    def bank(self,x,y,items,focused=0,w=580,gap=108):
        for j,(head,detail) in enumerate(items):
            top=y+j*gap;active=j==focused;old=j<focused
            color=GOLD if active else TEAL if old else DIM
            self.circle(x+10,top+26,7,color)
            if j<len(items)-1:self.line([(x+10,top+43),(x+10,top+gap+7)],LINE,3)
            self.text(x+46,top,head,42,color,active,maxw=w-46)
            if detail:self.text(x+47,top+53,detail,29,INK if active else MUTED,maxw=w-48)
    def key(self,x,y,s=1,color=GOLD):
        self.p.save();self.p.translate(x,y);self.p.scale(s,s)
        self.circle(0,0,15,None,color,7);self.line([(13,0),(58,0),(58,12)],color,7)
        self.line([(45,1),(45,10)],color,6);self.p.restore()
    def switch(self,x,y,s,pressed):
        self.p.save();self.p.translate(x,y);self.p.scale(s,s)
        self.poly([(-36,5),(24,23),(40,14),(-20,-3)],'#1c2b2f')
        self.poly([(-9,0),(-9,-48),(7,-43),(7,5)],'#536268')
        self.poly([(7,-43),(15,-50),(15,-1),(7,5)],'#344448')
        self.poly([(-27,-77),(13,-65),(24,-75),(-17,-87)],'#aebcba')
        self.poly([(-27,-77),(13,-65),(13,-42),(-27,-54)],'#5f7276')
        self.poly([(13,-65),(24,-75),(24,-52),(13,-42)],'#36464b')
        self.poly([(-17,-79+pressed*5),(3,-73+pressed*5),(14,-80+pressed*5),(-6,-86+pressed*5)],GOLD if pressed>.5 else ORANGE)
        self.p.restore()
    def person(self,x,y,s,press):
        """Side view with articulated elbow and a hand that meets the switch."""
        self.p.save();self.p.translate(x,y);self.p.scale(s,s)
        self.poly([(-33,2),(25,11),(42,5),(-17,-4)],'#162226')
        self.line([(-12,-78),(-23,-42),(-19,-6)],'#5b6e75',17)
        self.line([(-18,-6),(-2,-3)],'#819195',12)
        self.line([(5,-75),(14,-41),(12,-8)],'#91a4a7',18)
        self.line([(13,-6),(31,-3)],'#cad2cc',13)
        self.poly([(-25,-126),(2,-135),(17,-119),(10,-70),(-12,-63),(-24,-85)],'#53757b',TEAL,2.3)
        self.poly([(0,-134),(14,-122),(11,-93),(1,-98),(-9,-117)],'#aad9d0')
        self.rect(-21,-88,29,8,'#2f474a')
        self.circle(-5,-154,23,'#93a5a8','#c7d3cb',2)
        self.poly([(-24,-162),(-9,-177),(10,-168),(18,-151),(-1,-148),(-22,-151)],'#b7c7c6')
        self.poly([(-2,-156),(18,-158),(21,-146),(5,-141),(-3,-146)],'#23393f')
        self.line([(4,-151),(16,-153)],TEAL,3)
        self.circle(6,-119,10,'#a1b5b4')
        elbow=(18+press*9,-91+press*5);hand=(31+press*27,-97+press*32)
        self.line([(6,-117),elbow,hand],'#769196',12);self.circle(*elbow,6,'#b9ceca');self.circle(*hand,7,'#d5d8c7')
        self.p.restore()
    def door(self,x,y,s=1,angle=0,exploded=0,hinge=False,detail=True):
        """Consistent oblique camera. Door leaf rotates about the left jamb."""
        self.p.save();self.p.translate(x,y);self.p.scale(s,s)
        def screen(X,Y,Z):return (X+.44*Z,-Y+.22*Z)
        def face(coords,col,edge=None):self.poly([screen(*v) for v in coords],col,edge,1.6)
        width,height,depth=190,290,20
        # Concrete plinth and the view into the doorway.
        face([(-54,0,-29),(236,0,-29),(236,0,86),(-54,0,86)],'#344448')
        face([(-54,0,86),(236,0,86),(236,-12,86),(-54,-12,86)],'#1c2b30')
        face([(236,0,-29),(236,0,86),(236,-12,86),(236,-12,-29)],'#263438')
        face([(0,0,-15),(width,0,-15),(width,height,-15),(0,height,-15)],'#2e4543')
        for j in range(3):
            a=18+j*66
            face([(a,0,-15),(a+3,0,-15),(a+3,height,-15),(a,height,-15)],'#44605b')
        for a,b,w,h in [(-19,-1,19,height+19),(width,-1,19,height+19),(-19,height,228,19)]:
            face([(a,b,0),(a+w,b,0),(a+w,b+h,0),(a,b+h,0)],'#91aaab')
            face([(a,b+h,0),(a+w,b+h,0),(a+w,b+h,-depth),(a,b+h,-depth)],'#d1d8ca')
            face([(a+w,b,0),(a+w,b,-depth),(a+w,b+h,-depth),(a+w,b+h,0)],'#41565b')
        sx,sz=0.,0.
        rad=angle*pi/180
        def leaf(u,v,z=0):
            return (sx+u*cos(rad)-z*sin(rad),v,sz+u*sin(rad)+z*cos(rad)+exploded)
        def panel(u1,v1,u2,v2,z,col,edge=None):
            face([leaf(u1,v1,z),leaf(u2,v1,z),leaf(u2,v2,z),leaf(u1,v2,z)],col,edge)
        face([leaf(width,4,0),leaf(width,4,9),leaf(width,height-3,9),leaf(width,height-3,0)],'#91b5ab')
        panel(1,4,width,height-3,10,'#496568','#a3c1b7')
        if detail:
            for ua,ub in [(15,86),(101,175)]:
                for va,vb in [(17,92),(112,263)]:
                    panel(ua,va,ub,vb,11,'#2e464c','#72928d')
                    panel(ua+5,va+5,ub-5,vb-5,12,'#3c565b')
            panel(144,107,158,147,15,'#273b40')
            panel(142,132,172,138,21,GOLD)
        for h in (47,234):panel(1,h,9,h+27,15,ORANGE if hinge else '#b3b197')
        if hinge:
            a=screen(*leaf(3,0,12));b=screen(*leaf(3,310,12))
            self.line([a,b],ORANGE,2.2)
            self.circle(*a,5,GOLD);self.circle(*b,5,GOLD)
        self.p.restore()
    def lab(self,opening,press=0,key=True,show_person=True,offset=0,exploded=0,hinge=False):
        self.p.save();self.p.setClipRect(QRectF(96,275,992,557))
        self.rect(96,275,992,557,FIELD)
        for xx in range(-400,1001,90):self.line([(xx,784),(xx+515,633)],'#1b292b',1.5)
        for yy in range(631,899,27):self.line([(90,yy),(1088,yy)],'#172526',1.4)
        self.door(550+offset,715,1.32,opening,exploded,hinge)
        if show_person:
            self.switch(415,729,1.2,press)
            self.person(334,730,1.4,press)
            if key:self.key(313,626,.42)
        self.p.restore()

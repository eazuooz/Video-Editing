"""Editable, original projected illustrations for the retained mixed EX windows.

Logical coordinates are x/right, y/up, z/forward for aircraft and equipment.
The bicycle uses x/forward, y/up, z/side.  Each scene applies one explicit
coordinate mapping and the original scene's illustrative rotation afterward.
No mesh purports to reconstruct a game character, engine rig or measured axis.
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageColor

INK = '#283445'
BLUE = '#4273a8'
TEAL = '#287c83'
PALE = '#e4edf2'
ORANGE = '#bd702e'
SKIN = '#d6a57f'
RED_AXIS = '#e64045'
TEAL_AXIS = '#24bfb2'
BLUE_AXIS = '#3e7ecb'
FONTS = {n: ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', n)
         for n in (24, 26, 28, 30, 34, 38, 48)}


class Mesh:
    def __init__(self):
        self.parts = []

    def face(self, points, color, outline=INK, width=1):
        points = np.asarray(points, dtype=float)
        # Separate projected faces have restrained, consistent local shading.
        normal = np.cross(points[1]-points[0], points[2]-points[0])
        length = np.linalg.norm(normal)
        shade = .82 + .18*abs(np.dot(normal/length, [.27, .86, .43])) if length else 1
        rgb = tuple(round(v*min(1, shade)) for v in ImageColor.getrgb(color))
        self.parts.append((points, rgb, outline, width, True))

    def line(self, a, b, color, width=2):
        self.parts.append((np.asarray([a, b], dtype=float), color, None, width, False))

    def profile(self, points, thickness, color, axis=1):
        pts = np.asarray(points, dtype=float)
        delta = np.eye(3)[axis]*thickness/2
        a, b = pts-delta, pts+delta
        self.face(a[::-1], color)
        for i in range(len(pts)):
            j = (i+1) % len(pts)
            self.face([a[i], a[j], b[j], b[i]], color)
        self.face(b, color)

    def tube(self, a, b, radius, color, sides=8):
        a, b = np.asarray(a, float), np.asarray(b, float)
        direction = b-a
        direction /= np.linalg.norm(direction)
        helper = [0., 1., 0.] if abs(direction[1]) < .9 else [1., 0., 0.]
        u = np.cross(direction, helper); u /= np.linalg.norm(u)
        v = np.cross(direction, u)
        ring = [math.cos(t)*u+math.sin(t)*v
                for t in np.linspace(0, 2*math.pi, sides, endpoint=False)]
        aa, bb = [a+radius*q for q in ring], [b+radius*q for q in ring]
        for i in range(sides):
            j = (i+1) % sides
            self.face([aa[i], aa[j], bb[j], bb[i]], color, color, 1)
        self.face(aa[::-1], color); self.face(bb, color)

    def ellipsoid(self, center, radii, color, rings=6, sides=10):
        center, radii = np.asarray(center, float), np.asarray(radii, float)
        points = [[center+radii*[math.sin(phi)*math.cos(t), math.cos(phi),
                                 math.sin(phi)*math.sin(t)]
                   for t in np.linspace(0, 2*math.pi, sides, endpoint=False)]
                  for phi in np.linspace(.04, math.pi-.04, rings)]
        for a, b in zip(points, points[1:]):
            for i in range(sides):
                j = (i+1) % sides
                self.face([a[i], a[j], b[j], b[i]], color, color, 1)

    def ring(self, center, radius, tube, color, sides=32):
        # Tire cross-section supplies visible thickness without a filled disk.
        center = np.asarray(center, float)
        points = [[center+[(radius+tube*math.cos(phi))*math.cos(t),
                           (radius+tube*math.cos(phi))*math.sin(t),
                           tube*math.sin(phi)]
                   for phi in np.linspace(0, 2*math.pi, 6, endpoint=False)]
                  for t in np.linspace(0, 2*math.pi, sides, endpoint=False)]
        for i in range(sides):
            for k in range(6):
                self.face([points[i][k], points[(i+1)%sides][k],
                           points[(i+1)%sides][(k+1)%6], points[i][(k+1)%6]],
                          color, color, 1)


@lru_cache(maxsize=None)
def aircraft():
    m = Mesh()
    m.profile([[-.07,0,.92],[.07,0,.92],[.15,0,.35],[.14,0,-.35],
               [.05,0,-.87],[-.05,0,-.87],[-.14,0,-.35],[-.15,0,.35]], .20, BLUE)
    m.profile([[-.15,.02,.22],[-.84,.02,-.02],[-.79,.02,-.27],[-.13,.02,-.20],
               [.13,.02,-.20],[.79,.02,-.27],[.84,.02,-.02],[.15,.02,.22]], .052, PALE)
    m.profile([[-.04,.03,-.56],[-.47,.03,-.69],[-.43,.03,-.83],
               [.43,.03,-.83],[.47,.03,-.69],[.04,.03,-.56]], .043, TEAL)
    m.profile([[0,.03,-.49],[0,.34,-.72],[0,.32,-.85],[0,.03,-.86]], .055, TEAL, axis=0)
    m.ellipsoid([0,.15,.34], [.12,.115,.27], '#233e57')
    m.line([-.11,.19,.20],[.11,.19,.20], '#b8d2e2', 2)
    m.line([0,.265,.13],[0,.265,.53], '#b8d2e2', 2)
    for side in [-1,1]:
        x = side*.47
        m.tube([x,-.10,.18],[x,-.10,-.21], .087, '#596d7a')
        # Circular inlet in the plane perpendicular to forward z.
        for i in range(16):
            a, b = i*math.tau/16, (i+1)*math.tau/16
            m.line([x+.065*math.cos(a),-.10+.065*math.sin(a),.19],
                   [x+.065*math.cos(b),-.10+.065*math.sin(b),.19], INK, 2)
        m.line([side*.24,.052,-.20],[side*.76,.052,-.24], BLUE, 2)
        m.line([side*.42,.055,.12],[side*.42,.055,-.22], INK, 1)
        m.line([side*.25,.058,-.15],[side*.69,.058,-.19], ORANGE, 3)
        m.line([side*.12,.11,.13],[side*.095,.10,-.52], '#b8d2e2', 1)
    return m


@lru_cache(maxsize=None)
def bicycle():
    m = Mesh()
    rear, front, crank = [-.8,-.4,0], [.8,-.4,0], [-.08,-.34,0]
    seat, stem = [-.29,.37,0], [.53,.32,0]
    for x in [-.8,.8]:
        m.ring([x,-.4,0], .43, .038, INK)
        for i in range(24):
            t, nt = i*math.tau/24, (i+1)*math.tau/24
            for z in [-.043,.043]:
                m.line([x+.388*math.cos(t),-.4+.388*math.sin(t),z],
                       [x+.388*math.cos(nt),-.4+.388*math.sin(nt),z], '#7896aa', 2)
        for t in np.linspace(0, math.tau, 12, endpoint=False):
            m.line([x,-.4,.047],[x+.388*math.cos(t),-.4+.388*math.sin(t),.047], '#91a4b0', 1)
        m.tube([x,-.4,-.075],[x,-.4,.075], .05, ORANGE)
    for a,b in [(rear,crank),(rear,seat),(seat,crank),(seat,stem),(stem,crank)]:
        m.tube(a,b,.035,TEAL)
    for z in [-.055,.055]:
        m.tube([.53,.32,z],[.8,-.4,z], .031, '#7896aa')
    m.tube([-.29,.27,0],[-.29,.50,0],.03,INK)
    m.profile([[-.48,.51,0],[-.17,.51,0],[-.13,.46,0],[-.46,.46,0]], .14, INK, axis=2)
    m.tube([.53,.32,0],[.56,.65,0], .025, INK)
    m.tube([.56,.65,-.16],[.56,.65,.16], .026, INK)
    m.line([.56,.57,.07],[.67,.2,.07], INK, 1)
    m.line([.67,.2,.07],[.8,-.12,.07], INK, 1)
    m.line([-.8,-.30,.09],[-.08,-.22,.09], INK, 2)
    m.line([-.8,-.50,.09],[-.08,-.46,.09], INK, 2)
    for t in np.linspace(0,math.tau,16,endpoint=False):
        m.line([-.08,-.34,.095],[-.08+.10*math.cos(t),-.34+.10*math.sin(t),.095], ORANGE, 1)
    hips, shoulders = [-.27,.67,0], [.20,1.13,0]
    m.tube(hips,shoulders,.14,BLUE)
    # Distinct sleeves, forearms, shorts, shins, gloves and shoes at bent joints.
    for z in [-.075,.075]:
        elbow, hand = [.42,.90,z], [.56,.65,z]
        knee = [.16,.29,z]
        foot = [-.02,-.40,z] if z<0 else [.03,-.18,z]
        m.tube([.18,1.06,z],elbow,.053,BLUE)
        m.tube(elbow,hand,.044,SKIN)
        m.ellipsoid(elbow,[.051,.047,.045],SKIN,4,8)
        m.ellipsoid(hand,[.064,.045,.045],INK,4,8)
        m.tube(hips,knee,.071,INK)
        m.tube(knee,foot,.05,SKIN)
        m.ellipsoid(knee,[.06,.06,.052],SKIN,4,8)
        m.tube(foot,np.asarray(foot)+[.18,0,0], .053, INK)
        m.tube([-.08,-.34,z*2],foot,.018,ORANGE)
        m.tube(np.asarray(foot)+[-.035,0,-.06],np.asarray(foot)+[.12,0,.06],.022,INK)
        for f in [-.02,0,.02]:
            m.line([.60,.655+f,z+.047],[.64,.635+f,z+.047],'#b8d2e2',1)
    m.tube(shoulders,[.31,1.27,0],.055,SKIN)
    m.ellipsoid([.36,1.36,0],[.14,.15,.105],SKIN)
    m.ellipsoid([.34,1.47,0],[.17,.075,.13],ORANGE)
    m.ellipsoid([.50,1.36,0],[.037,.037,.07],SKIN,4,8)
    m.line([.46,1.395,.098],[.48,1.395,.098],INK,3)
    m.line([.48,1.32,.081],[.51,1.32,.081],INK,1)
    m.line([.23,1.45,.109],[.38,1.24,.109],INK,2)
    m.line([-.21,.70,.143],[.15,1.08,.143], '#b8d2e2', 2)
    m.line([-.15,.79,.146],[.23,.96,.146], '#b8d2e2', 1)
    return m


@lru_cache(maxsize=None)
def landing_gear():
    m = Mesh()
    # Chamfered landing pad, actuator shaft, upper mounting plate and pivots.
    m.profile([[-.82,-.73,-.48],[.82,-.73,-.48],[.97,-.73,-.31],
               [.97,-.73,.31],[.82,-.73,.48],[-.82,-.73,.48],
               [-.97,-.73,.31],[-.97,-.73,-.31]], .21, TEAL)
    m.tube([0,-.55,0],[0,.42,0], .23, '#7896aa', 10)
    m.tube([0,.20,0],[0,1.18,0], .125, '#c7d1d7', 10)
    m.profile([[-.69,1.23,-.46],[.69,1.23,-.46],[.80,1.23,-.33],
               [.80,1.23,.33],[.69,1.23,.46],[-.69,1.23,.46],
               [-.80,1.23,.33],[-.80,1.23,-.33]], .20, BLUE)
    for x in [-.62,.62]:
        for z in [-.29,.29]:
            m.ellipsoid([x,1.34,z],[.053,.019,.053],INK,4,8)
    for x in [-.72,.72]:
        m.tube([x,-.56,-.26],[x,-.15,-.26], .07, ORANGE)
        m.tube([x,-.15,-.26],[x*.45,.30,-.26], .058, BLUE)
        m.tube([x,-.23,-.36],[x,-.23,-.17], .075, INK)
    for x in [-.60,-.30,.30,.60]:
        m.line([x,-.615,-.29],[x,-.615,.29], '#b8d2e2', 3)
    for x in [-.30,.30]:
        m.tube([x,-.25,.18],[x,.65,.18], .06, ORANGE)
        m.tube([x,.65,.18],[x,.95,.18], .034, '#c7d1d7')
    for a,b in [([.28,.90,.20],[.44,.54,.30]),([.44,.54,.30],[.37,.12,.32]),
                ([.37,.12,.32],[.23,-.16,.20])]:
        m.tube(a,b,.026,INK)
    return m


def draw_mesh(d, mesh, center, scale, rotation, projection, depth, mapping=None, offset=None):
    matrix = np.asarray(rotation) @ (np.eye(3) if mapping is None else np.asarray(mapping))
    offset = np.zeros(3) if offset is None else np.asarray(offset)
    parts = []
    for points,color,edge,width,is_face in mesh.parts:
        transformed = (points+offset) @ matrix.T
        xy = transformed @ np.asarray(projection).T*scale+np.asarray(center)
        z = float((transformed @ np.asarray(depth)).mean())
        parts.append((z,xy,color,edge,width,is_face))
    for _,xy,color,edge,width,is_face in sorted(parts,key=lambda x:x[0]):
        pts = [tuple(v) for v in xy]
        if is_face:
            d.polygon(pts,fill=color,outline=edge,width=width)
        else:
            d.line(pts,fill=color,width=width)


def text(d,xy,value,color=INK,size=30):
    b=d.textbbox(xy,value,font=FONTS[size])
    assert 0<=b[0] and b[2]<1900 and b[3]<897, (value,b)
    d.text(xy,value,font=FONTS[size],fill=color)


def arrow(d,a,b,color,width=6):
    dx,dy=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dy)
    if n<9:return
    d.line([a,b],fill=color,width=width);ux,uy=dx/n,dy/n
    d.polygon([b,(b[0]-17*ux+8*uy,b[1]-17*uy-8*ux),
                 (b[0]-17*ux-8*uy,b[1]-17*uy+8*ux)],fill=color)


def rz(angle):
    c,s=math.cos(angle),math.sin(angle)
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])


def frame_03b(frame):
    im=Image.new('RGB',(1920,1080),'#fafbf9');d=ImageDraw.Draw(im)
    late=frame>=1270;sec=frame/60
    local=max(0,sec-1270/60) if late else sec
    pitch=math.pi*min(1,max(0,(local-.25)/2.2)) if late else .25*math.sin(local*1.8)
    c,s=math.cos(pitch),math.sin(pitch)
    rotation=np.array([[c,0,s],[0,1,0],[-s,0,c]])
    # Follow the same rotation while reframing the larger rider away from notes.
    cy=600-120*(1-math.cos(pitch))/2 if late else 600
    center=(920+(70*math.sin(local*.7) if not late else 0),cy)
    scale=260;projection=[[.832,.555,0],[.30,-.45,-.84]];depth=[.46,-.69,.55]
    for gx in range(-4,5):
        d.line([(center[0]+scale*(.832*gx/2+.555*y),
                 center[1]+scale*(.30*gx/2-.45*y+.45)) for y in [-1.7,1.7]],fill='#dce4df',width=2)
    for gy in range(-3,4):
        d.line([(center[0]+scale*(.832*x+.555*gy/2),
                 center[1]+scale*(.30*x-.45*gy/2+.45)) for x in [-2,2]],fill='#dce4df',width=2)
    # Proper right-handed mapping: bike up/y -> scene up/z, side/z -> -y.
    mapping=[[1,0,0],[0,0,-1],[0,1,0]]
    draw_mesh(d,bicycle(),center,scale*.78,rotation,projection,depth,mapping,[0,.4,0])
    def proj(v):return tuple(np.asarray(center)+scale*(np.asarray(projection)@(rotation@v)))
    text(d,(90,85),'이동하는 위치와 물체의 자세',size=48)
    text(d,(90,164),'자전거에서도 위치 p와 자세 R은 다른 정보입니다',size=34)
    text(d,(90,825),'별도 설명모형 · 게임 내부 축이나 실제 회전각의 측정이 아닙니다','#64716a',26)
    arrow(d,(260,715),(620,715),BLUE_AXIS,8);text(d,(260,740),'이동 방향',BLUE_AXIS,28)
    if not late or sec>=25.14:
        arrow(d,proj([0,-.24,.25]),proj([1.35,-.24,.25]),RED_AXIS,8);text(d,(1420,470),'앞 f',RED_AXIS,38)
    if not late or sec>=25.5:
        arrow(d,proj([0,-.24,.25]),proj([0,-.24,1.40]),TEAL_AXIS,8);text(d,(1420,540),'위 u',TEAL_AXIS,38)
    if late and sec>=26.1:text(d,(1370,640),'두 방향을 함께 기록',size=28)
    return im


def frame_07b(frame):
    im=Image.new('RGB',(1920,1080),'#fafbf9');d=ImageDraw.Draw(im);sec=frame/60
    late=frame>=1891;local=sec-(1891/60 if late else 742/60)
    theta=math.pi/2*min(1,max(0,(local-.3)/1.3)) if late else .32*math.sin(local*1.15)
    rotation=rz(theta);center=(740,525) if late else (815,555);scale=240
    projection=[[.79,0,-.61],[.32,-.80,.41]];depth=[.49,.57,.66]
    for k in range(-4,5):
        for aa,bb in [([k/2,-.8,-2],[k/2,-.8,2]),([-2,-.8,k/2],[2,-.8,k/2])]:
            pts=[tuple(np.asarray(center)+scale*(np.asarray(projection)@v)) for v in [aa,bb]]
            d.line(pts,fill='#dce4df',width=2)
    draw_mesh(d,aircraft(),center,scale*1.8,rotation,projection,depth)
    def proj(v):return tuple(np.asarray(center)+scale*(np.asarray(projection)@(rotation@v)))
    red=late or sec>=13.1;blue=late or sec>=14.2;origin=[0,.43,.25]
    if red:arrow(d,proj(origin),proj([0,.43,1.9]),RED_AXIS,8)
    if blue:d.line([proj([-1.55,.43,.25]),proj([1.55,.43,.25])],fill=BLUE_AXIS,width=9)
    text(d,(85,80),'앞과 날개를 함께 읽는 자세',size=48)
    text(d,(85,155),'따로 정한 설명모형 · 실제 게임 내부 축의 측정이 아닙니다',size=30)
    if red:text(d,(1330,390),'앞 f · 붉은 방향',RED_AXIS,34)
    if blue:text(d,(1330,465),'날개 양쪽 · 파란 방향',BLUE_AXIS,34)
    if not late and sec>=15.72:text(d,(1270,570),'두 방향을 함께 비교',size=34)
    if late:
        text(d,(1130,570),'별도 수학 예: z축 +90°',size=34)
        text(d,(1160,645),'x → y,  y → -x,  z → z',size=30)
        text(d,(1150,715),'Rz = [[0,-1,0],[1,0,0],[0,0,1]]',size=28)
    text(d,(85,842),'게임의 회전각을 수치로 추정하지 않습니다. 카메라와 물체의 움직임을 구분하세요.','#64716a',26)
    return im


def frame_10b(frame):
    im=Image.new('RGB',(1920,1080),'#fafbf9');d=ImageDraw.Draw(im);sec=frame/60;late=frame>=1428
    angle=.30*math.sin(sec*1.15) if not late else math.pi/2*min(1,max(0,(sec-26.24)/1.5))
    rotation=rz(angle);centers=[(505,540),(1340,540)];scale=145
    projection=[[.79,0,-.61],[.32,-.80,.41]];depth=[.49,.57,.66]
    draw_mesh(d,aircraft(),centers[0],scale*1.9,rotation,projection,depth)
    draw_mesh(d,landing_gear(),centers[1],scale,rotation,projection,depth)
    text(d,(75,70),'비행 자세에서 배치 자세로',size=48)
    text(d,(75,145),'따로 정한 설명모형 · 실제 게임 내부 좌표축이 아닙니다',size=30)
    text(d,(350,760),'비행 중인 기체',size=34);text(d,(1210,760),'놓기 전 부품',size=34)
    if sec>=2.18:arrow(d,(795,420),(1045,420),TEAL_AXIS,8)
    if late:
        text(d,(70,225),'배치 상황은 달라도, 같은 기준으로 자세를 기록',size=34)
        if sec>=28.9:
            for center in centers:
                def proj(v):return tuple(np.asarray(center)+scale*(np.asarray(projection)@(rotation@v)))
                for v,col in [([1.5,0,0],RED_AXIS),([0,1.7,0],TEAL_AXIS),([0,0,1.6],BLUE_AXIS)]:
                    arrow(d,proj([0,0,0]),proj(v),col,6)
            text(d,(75,830),'이 모형의 x=빨강, y=청록, z=파랑 · 게임 관찰선과 구분',size=26)
    else:text(d,(75,830),'한 방향만 보지 않고 여러 방향을 함께 기록합니다',size=26)
    return im

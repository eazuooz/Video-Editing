"""Editable concept illustrations; logical right-handed y-up, z-forward.

Generic original illustrations, not game character copies or measured engine rigs.
The coordinate mapping is applied once after constructing each complete subject.
"""
import numpy as np
from manim import Polygon, VGroup, Line, Circle, Arc

P = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], dtype=float)
INK = '#283445'
TEAL = '#287c83'
BLUE = '#4273a8'
LIGHT = '#b8d2e2'
ORANGE = '#bd702e'
PALE = '#e4edf2'
SKIN = '#d6a57f'


def solid_profile(points, thickness, color, axis=1, edge=INK):
    """Extruded outline with visibly separate front, back and side faces."""
    pts = np.array(points, dtype=float)
    offset = np.eye(3)[axis] * thickness / 2
    top = pts + offset
    bottom = pts - offset
    faces = VGroup(Polygon(*bottom[::-1], fill_color=color, fill_opacity=1,
                           stroke_color=edge, stroke_width=.6))
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        faces.add(Polygon(bottom[i], bottom[j], top[j], top[i],
                          fill_color=color, fill_opacity=.83,
                          stroke_color=edge, stroke_width=.6))
    faces.add(Polygon(*top, fill_color=color, fill_opacity=1,
                      stroke_color=edge, stroke_width=.65))
    return faces


def capsule(a, b, radius, color, sides=8):
    """Faceted round limb/tube, rather than a rectangular placeholder."""
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    d = b - a
    d /= np.linalg.norm(d)
    helper = np.array([0., 1., 0.]) if abs(d[1]) < .9 else np.array([1., 0., 0.])
    u = np.cross(d, helper); u /= np.linalg.norm(u)
    v = np.cross(d, u)
    rings = []
    for center, r in [(a, radius*.73), (a+(b-a)*.15, radius),
                      (a+(b-a)*.85, radius), (b, radius*.73)]:
        rings.append([center+r*(np.cos(t)*u+np.sin(t)*v)
                      for t in np.linspace(0, 2*np.pi, sides, endpoint=False)])
    out = VGroup()
    for aa, bb in zip(rings, rings[1:]):
        for i in range(sides):
            j = (i+1) % sides
            out.add(Polygon(aa[i], aa[j], bb[j], bb[i], fill_color=color,
                            fill_opacity=1, stroke_color=color, stroke_width=.15))
    out.add(Polygon(*rings[0][::-1], fill_color=color, fill_opacity=1, stroke_width=0),
            Polygon(*rings[-1], fill_color=color, fill_opacity=1, stroke_width=0))
    return out


def ellipsoid(center, radii, color):
    center, radii = np.array(center, dtype=float), np.array(radii, dtype=float)
    rings = []
    for phi in np.linspace(.07, np.pi-.07, 6):
        rings.append([center+radii*np.array([np.sin(phi)*np.cos(t),
                      np.sin(phi)*np.sin(t), np.cos(phi)])
                      for t in np.linspace(0, 2*np.pi, 10, endpoint=False)])
    out = VGroup()
    for a, b in zip(rings, rings[1:]):
        for i in range(10):
            j=(i+1)%10
            out.add(Polygon(a[i], a[j], b[j], b[i], fill_color=color,
                            fill_opacity=1, stroke_color=color, stroke_width=.1))
    return out


def placed(obj, R, origin, scale=1):
    obj.apply_matrix(P @ np.asarray(R))
    obj.scale(scale, about_point=np.zeros(3))
    obj.shift(origin)
    return obj


def aircraft(R, origin, scale=1.2):
    # Tapered fuselage and swept airfoils retain an unmistakable nose/tail.
    hull = solid_profile([[-.07,0,.92], [.07,0,.92], [.15,0,.35],
                          [.14,0,-.35], [.05,0,-.87], [-.05,0,-.87],
                          [-.14,0,-.35], [-.15,0,.35]], .20, BLUE)
    wings = solid_profile([[-.15,.02,.22], [-.84,.02,-.02], [-.79,.02,-.27],
                           [-.13,.02,-.20], [.13,.02,-.20], [.79,.02,-.27],
                           [.84,.02,-.02], [.15,.02,.22]], .052, PALE)
    tail = solid_profile([[-.04,.03,-.56], [-.47,.03,-.69], [-.43,.03,-.83],
                          [.43,.03,-.83], [.47,.03,-.69], [.04,.03,-.56]], .043, TEAL)
    fin = solid_profile([[0,.03,-.49],[0,.34,-.72],[0,.32,-.85],[0,.03,-.86]],
                        .055, TEAL, axis=0)
    canopy = ellipsoid([0,.15,.34], [.12,.115,.27], '#233e57')
    canopy_trim = VGroup(Line([-.11,.14,.20], [.11,.14,.20], color=LIGHT, stroke_width=1.2),
                         Line([0,.245,.13], [0,.245,.53], color=LIGHT, stroke_width=1.2))
    details = VGroup()
    for side in [-1, 1]:
        x = side*.47
        engine = capsule([x,-.10,.18], [x,-.10,-.21], .087, '#596d7a')
        intake = Circle(radius=.063, color=INK, stroke_width=2).shift([x,-.10,.19])
        details.add(engine, intake,
                    Line([side*.24,.048,-.20],[side*.76,.048,-.24],color=BLUE,stroke_width=1.4),
                    Line([side*.42,.05,.12],[side*.42,.05,-.22],color=INK,stroke_width=.9),
                    Line([side*.25,.053,-.15],[side*.69,.053,-.19],color=ORANGE,stroke_width=2.2))
    obj = VGroup(hull, wings, tail, fin, canopy, canopy_trim, details)
    return placed(obj, R, origin, scale)


def wingsuit_person(R, origin, scale=1):
    """Prone person with helmet, visor, harness, bent joints, gloves and boots."""
    fabric = VGroup()
    limbs = VGroup()
    for side in [-1,1]:
        shoulder=[side*.22,0,.33]; elbow=[side*.60,-.04,.16]; wrist=[side*.88,-.03,-.10]
        hip=[side*.14,0,-.36]; knee=[side*.28,-.07,-.85]; ankle=[side*.37,-.02,-1.24]
        fabric.add(solid_profile([shoulder, wrist, [side*.20,-.01,-.38]], .024, TEAL),
                   solid_profile([hip, ankle, [0,-.015,-1.10]], .022, TEAL))
        limbs.add(capsule(shoulder,elbow,.073,BLUE), capsule(elbow,wrist,.061,BLUE),
                  ellipsoid(elbow,[.074,.065,.075],ORANGE),
                  capsule(hip,knee,.092,BLUE), capsule(knee,ankle,.076,BLUE),
                  ellipsoid(knee,[.084,.07,.08],ORANGE),
                  ellipsoid(wrist,[.11,.044,.082],INK),
                  capsule(ankle,[side*.38,-.025,-1.45],.078,INK))
        for f in [-.045,-.015,.015,.045]:
            limbs.add(Line([side*.88+f,-.072,-.08],[side*.93+f,-.072,-.18],
                           color=LIGHT,stroke_width=.65))
    torso=solid_profile([[-.20,0,.47],[.20,0,.47],[.22,0,.15],
                         [.14,0,-.43],[-.14,0,-.43],[-.22,0,.15]],.17,BLUE)
    neck=capsule([0,0,.47],[0,0,.58],.065,SKIN)
    helmet=ellipsoid([0,0,.73],[.18,.15,.22],ORANGE)
    visor=solid_profile([[-.135,-.075,.83],[.135,-.075,.83],
                         [.11,.075,.85],[-.11,.075,.85]],.055,INK,axis=2)
    reflection=Line([-.095,.03,.884],[.025,.06,.884],color=LIGHT,stroke_width=1.3)
    pack=ellipsoid([0,.15,-.02],[.16,.08,.27],PALE)
    harness=VGroup(Line([-.16,.096,.38],[.10,.096,-.30],color=INK,stroke_width=2.1),
                   Line([.16,.096,.38],[-.10,.096,-.30],color=INK,stroke_width=2.1),
                   Line([-.15,.10,-.28],[.15,.10,-.28],color=ORANGE,stroke_width=2.2))
    return placed(VGroup(fabric,torso,neck,limbs,helmet,visor,reflection,pack,harness),R,origin,scale)


def bicycle_with_rider(origin, scale=1):
    """Side-view bicycle with depth, spokes, drivetrain and a posed rider."""
    bike=VGroup(); wheels=VGroup()
    for x in [-.80,.80]:
        for z in [-.065,.065]:
            ring=Circle(radius=.46,color=INK,stroke_width=3).shift([x,-.40,z])
            rim=Circle(radius=.405,color='#7896aa',stroke_width=1.2).shift([x,-.40,z])
            wheels.add(ring,rim)
        for t in np.linspace(0,2*np.pi,12,endpoint=False):
            wheels.add(Line([x,-.40,.068],[x+.40*np.cos(t),-.40+.40*np.sin(t),.068],color='#91a4b0',stroke_width=.65))
        wheels.add(ellipsoid([x,-.40,0],[.058,.058,.08],ORANGE))
    rear=[-.80,-.40,0];front=[.80,-.40,0];crank=[-.08,-.34,0]
    seat=[-.29,.37,0];stem=[.53,.32,0]
    for a,b in [(rear,crank),(rear,seat),(seat,crank),(seat,stem),(stem,crank),(stem,front)]:
        bike.add(capsule(a,b,.037,TEAL))
    bike.add(capsule([-.29,.27,0],[-.29,.52,0],.032,INK),
             solid_profile([[-.49,.52,0],[-.18,.52,0],[-.16,.49,0],[-.48,.48,0]],.14,INK,axis=2),
             capsule([.53,.32,0],[.56,.65,0],.025,INK),
             capsule([.56,.65,-.15],[.56,.65,.15],.029,INK),
             Circle(radius=.12,color=ORANGE,stroke_width=2).shift([-.08,-.34,.10]),
             Line([-.80,-.30,.11],[-.08,-.22,.11],color=INK,stroke_width=1),
             Line([-.80,-.50,.11],[-.08,-.46,.11],color=INK,stroke_width=1),
             Line([.56,.57,.1],[.80,-.12,.1],color=INK,stroke_width=.65))
    hips=[-.27,.67,0];shoulders=[.20,1.13,0];head=[.36,1.36,0]
    rider=VGroup(capsule(hips,shoulders,.145,BLUE))
    for z in [-.075,.075]:
        elbow=[.42,.90,z];hand=[.56,.65,z]
        knee=[.16,.29,z];foot=[-.02,-.40,z] if z<0 else [.03,-.18,z]
        rider.add(capsule([.18,1.06,z],elbow,.052,BLUE),capsule(elbow,hand,.048,SKIN),
                  ellipsoid(hand,[.07,.045,.047],INK),capsule(hips,knee,.072,INK),
                  capsule(knee,foot,.054,SKIN),capsule(foot,np.array(foot)+[.18,0,0],.055,INK),
                  Line([-.08,-.34,z*2],foot,color=ORANGE,stroke_width=2.0))
    rider.add(capsule(shoulders,[.31,1.27,0],.057,SKIN),
              ellipsoid(head,[.14,.15,.105],SKIN),ellipsoid([.34,1.47,0],[.17,.075,.13],ORANGE),
              Line([.45,1.39,.094],[.47,1.39,.095],color=INK,stroke_width=2.0),
              Line([-.21,.70,.13],[.15,1.08,.13],color=LIGHT,stroke_width=2.0))
    return placed(VGroup(wheels,bike,rider),np.eye(3),origin,scale)


def machinery(origin, scale=1):
    """An editable dock and mounted device; panels, vents, bolts and connector."""
    base=solid_profile([[-.73,0,-.48],[.73,0,-.48],[.83,0,-.35],
                        [.83,0,.35],[.68,0,.48],[-.68,0,.48],[-.83,0,.35],[-.83,0,-.35]],.18,TEAL)
    mount=solid_profile([[-.32,.30,-.28],[.32,.30,-.28],[.38,.30,.23],
                         [.25,.30,.35],[-.25,.30,.35],[-.38,.30,.23]],.42,ORANGE)
    detail=VGroup()
    for x in [-.61,.61]:
        for z in [-.32,.32]:detail.add(ellipsoid([x,.105,z],[.034,.014,.034],INK))
    for x in np.linspace(-.22,.22,5):detail.add(Line([x,.522,-.17],[x,.522,.11],color=INK,stroke_width=1.4))
    detail.add(capsule([.34,.32,.04],[.55,.32,.04],.08,INK),
               capsule([-.22,.51,-.22],[-.22,.85,-.22],.02,INK),
               ellipsoid([-.22,.88,-.22],[.04,.04,.04],BLUE),
               Line([-.66,.11,0],[.66,.11,0],color=LIGHT,stroke_width=1.2))
    # Subgroup 1 remains the independently movable mounted part.
    return placed(VGroup(base,VGroup(mount,detail)),np.eye(3),origin,scale)

"""M17 existing projection lesson: readable labels, same coordinates and clock."""
from pathlib import Path
import os, sys, json
from manim import *

R = Path(__file__).resolve().parents[3]
slug = 'game-math-camera-projection'
T = json.loads((R/'projects'/slug/'production/timeline.json').read_text(encoding='utf8'))
sys.path.insert(0, str(R/'manim/projects/game-math-part2-full-series'))
import camera_projection as original

original.timing = lambda _slug, _data: T
base_edge, base_label = original.edge, original.label
base_diagram, base_panel, base_card = original.diagram, original.right_panel, original.card


def legible_edge(a, b, color=original.RULE, width=2, dashed=False):
    # The grid stays subordinate to the narrated vectors.
    return base_edge(a, b, color, max(2.5, width*1.4) if width>=2 else width, dashed)


def marked_label(p, value, color=original.INK, size=25, shift=(0,0,0)):
    obj = base_label(p, value, color, size, shift)
    obj.polish_label_value = value
    obj.polish_label_shift = np.array(shift)
    return obj


def readable_card(value, width=6, size=29, color=original.BLUE):
    return base_card(value, width, max(size, 28), color)


original.edge, original.label, original.card = legible_edge, marked_label, readable_card


def legible_diagram(mode, i, count):
    obj = base_diagram(mode, i, count)
    if mode in ['overview','summary']:
        return obj
    phase = 0 if mode!='pipeline' or i<5 else i
    scale, _ = original.LAYOUT[(mode,count,phase)]
    labels = [m for m in obj.get_family() if hasattr(m,'polish_label_value')]
    for m in labels:
        value = m.polish_label_value
        center = m.get_center().copy()
        anchor = center - m.polish_label_shift*scale
        target = .29 if value in ['x','y','z','위','오른쪽','앞쪽'] else .30
        m.scale(max(1, target/max(m.height,.01)))
        m.set_z_index(5)
        if mode=='view' and value=='앞쪽':
            m.shift([.70,-.27,0])
            obj.add(Line(anchor,m.get_left(),color=original.BLUE,stroke_width=2.5).set_z_index(4))
        elif mode=='view' and value in ['위','y']:
            m.shift([-.75,.35,0] if value=='위' else [-.55,-.42,0])
            obj.add(Line(anchor,m.get_right(),color=original.GREEN,stroke_width=2.2).set_z_index(4))
        elif mode=='view' and value.startswith('뷰 변위'):
            m.shift([.30,.50,0])
            obj.add(Line(anchor,m.get_bottom(),color=original.GREEN,stroke_width=2.2).set_z_index(4))
        elif mode=='conventions' and value=='한 점을 끝까지 추적':
            m.shift([0,.65,0])
        elif mode=='homogeneous' and value in ['나눈 위치','직교: 평행']:
            m.shift([.55,-.55,0])
            obj.add(Line(anchor,m.get_top(),color=original.GREEN,stroke_width=2.2).set_z_index(4))
    return obj


def legible_panel(scene, i):
    panel = base_panel(scene, i)
    mode = scene['mode']
    if (mode=='model' and i==3) or (mode=='projection' and i in [2,5]) or (mode=='alternate' and i==5):
        panel.scale(1.08, about_point=[3.12,-.2,0])
    return panel


original.diagram, original.right_panel = legible_diagram, legible_panel
for name, base in original.make_scenes(slug, __name__).items():
    sid = name.removeprefix('Scene')
    globals()['Polish'+sid] = type('Polish'+sid, (base,), {'__module__':__name__})

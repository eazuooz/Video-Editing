"""Original mounted camera illustration; not a measured game component."""
import numpy as np
from manim import VGroup, Circle, Line
from detailed_subjects_v1 import solid_profile, capsule, placed, ORANGE, INK, LIGHT
def camera_part(R, origin, scale=1):
    housing=solid_profile([[-.31,0,-.30],[.31,0,-.30],[.38,0,-.17],[.38,0,.21],
                           [.25,0,.31],[-.25,0,.31],[-.38,0,.21],[-.38,0,-.17]],.43,ORANGE)
    lens=capsule([0,0,.28],[0,0,.65],.18,INK)
    glass=Circle(radius=.145,color=LIGHT,fill_color='#31546e',fill_opacity=1,stroke_width=1.4).shift([0,0,.66])
    mount=capsule([0,-.25,-.03],[0,-.48,-.03],.085,INK)
    trim=VGroup(Line([-.22,.22,-.17],[.22,.22,-.17],color=INK,stroke_width=1.3),
                Line([-.25,.22,.10],[.25,.22,.10],color=LIGHT,stroke_width=1.3))
    return placed(VGroup(housing,lens,glass,mount,trim),R,origin,scale)

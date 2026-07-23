"""Real physics vs. arcade ("Mario") jump: same peak height, different feel.

Real physics uses one gravity constant for both rise and fall, so the arc
is symmetric. Arcade games (Mario, Celeste, ...) commonly use a *weaker*
gravity while rising and a *stronger* gravity while falling: the jump
floats a bit longer at the top (easier to aim mid-air) and then snaps
down quickly (feels responsive), even though both reach the same height.
"""

from pathlib import Path

import numpy as np
from manim import (
    BLUE,
    DOWN,
    RED,
    UP,
    Axes,
    Create,
    Dot,
    ImageMobject,
    Line,
    Scene,
    Text,
    ValueTracker,
    Write,
    always_redraw,
    linear,
)

SPRITE_PATH = Path(__file__).resolve().parent / "mario_sprite.png"

H = 3.0        # jump peak height (scene units)
G_REAL = 7.0   # single gravity for the symmetric, "real" jump
G_UP = 4.0     # weaker gravity while rising -> floatier ascent
G_DOWN = 11.0  # stronger gravity while falling -> snappy descent

V_REAL = np.sqrt(2 * G_REAL * H)
T_UP_REAL = V_REAL / G_REAL
T_TOTAL_REAL = 2 * T_UP_REAL

V_UP = np.sqrt(2 * G_UP * H)
T_UP_GAME = V_UP / G_UP
T_DOWN_GAME = np.sqrt(2 * H / G_DOWN)
T_TOTAL_GAME = T_UP_GAME + T_DOWN_GAME


def height_real(t: float) -> float:
    t = t % T_TOTAL_REAL
    return V_REAL * t - 0.5 * G_REAL * t**2


def height_game(t: float) -> float:
    t = t % T_TOTAL_GAME
    if t <= T_UP_GAME:
        return V_UP * t - 0.5 * G_UP * t**2
    td = t - T_UP_GAME
    return H - 0.5 * G_DOWN * td**2


class MarioJumpPhysics(Scene):
    def construct(self):
        axes = Axes(
            x_range=[0, 2.2, 0.5],
            y_range=[0, H + 0.5, 1],
            x_length=10,
            y_length=4,
            axis_config={"include_tip": False},
        ).to_edge(DOWN)

        real_graph = axes.plot(height_real, x_range=[0, T_TOTAL_REAL], color=BLUE)
        game_graph = axes.plot(height_game, x_range=[0, T_TOTAL_GAME], color=RED)

        real_label = Text("Real physics (symmetric)", color=BLUE, font_size=28)
        game_label = Text("Game physics (asymmetric)", color=RED, font_size=28)
        real_label.to_edge(UP).shift(3 * np.array([-1, 0, 0]))
        game_label.to_edge(UP).shift(3 * np.array([1, 0, 0]))

        ground_real = Line(axes.c2p(-0.15, 0), axes.c2p(-0.15, H + 0.5))
        ground_game = Line(axes.c2p(2.15, 0), axes.c2p(2.15, H + 0.5))

        self.play(Create(axes), Write(real_label), Write(game_label))
        self.play(Create(real_graph), Create(game_graph), Create(ground_real), Create(ground_game))

        t_tracker = ValueTracker(0)

        def make_sprite():
            sprite = ImageMobject(str(SPRITE_PATH))
            sprite.set(height=0.9)
            return sprite

        real_sprite = always_redraw(
            lambda: make_sprite().move_to(axes.c2p(-0.15, height_real(t_tracker.get_value())))
        )
        game_sprite = always_redraw(
            lambda: make_sprite().move_to(axes.c2p(2.15, height_game(t_tracker.get_value())))
        )
        real_cursor = always_redraw(
            lambda: Dot(
                axes.c2p(t_tracker.get_value() % T_TOTAL_REAL, height_real(t_tracker.get_value())),
                color=BLUE,
            )
        )
        game_cursor = always_redraw(
            lambda: Dot(
                axes.c2p(t_tracker.get_value() % T_TOTAL_GAME, height_game(t_tracker.get_value())),
                color=RED,
            )
        )

        self.add(real_sprite, game_sprite, real_cursor, game_cursor)
        self.play(t_tracker.animate.set_value(6), run_time=6, rate_func=linear)
        self.wait()

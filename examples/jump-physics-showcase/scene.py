"""Jump-design showcase: from the basic frame-by-frame gravity concept
through Mario, Metroid, Ghosts'n Goblins, Street Fighter II, Smash Bros,
and modern examples (Jump King, Celeste, Mega Man X).

Every character actually runs and jumps along a real spatial parabola
(not just a vertical bounce), and the position-over-time graph is drawn
live, in sync with the jump, rather than pre-drawn upfront. Characters
are the games' own reference art (background-removed, see sprites/);
"basic_concept" has no specific game, so it uses a plain ball instead.
"""

from pathlib import Path

import numpy as np
from manim import (
    BLUE,
    DOWN,
    GREEN,
    GREY_B,
    GREY_C,
    LEFT,
    ORANGE,
    PURPLE,
    RED,
    RIGHT,
    UP,
    WHITE,
    YELLOW,
    Axes,
    Circle,
    Create,
    FadeIn,
    FadeOut,
    Group,
    ImageMobject,
    Line,
    ParametricFunction,
    Rectangle,
    Scene,
    SurroundingRectangle,
    Text,
    ValueTracker,
    VGroup,
    Write,
    always_redraw,
    linear,
)

import profiles as jp
from explanations import EXPLANATIONS

FONT = "Malgun Gothic"
BG = "#0b0d13"
SPRITES_DIR = Path(__file__).resolve().parent / "sprites"
PLAYBACK_SPEED = 0.85  # demo animation plays at 85% speed (slower, easier to follow)

SPRITE_FILE = {
    "mario": "mario.png",
    "metroid": "metroid.png",
    "ghosts_n_goblins": "arthur.png",
    "sf2": "streetfighter2.png",
    "smash_squat": "smash.png",
    "smash_ultimate": "smash.png",
    "jump_king": "jumpking.png",
    "celeste": "celeste.png",
    "megaman": "megaman.png",
}

_sprite_cache = {}


def load_sprite(key, height=0.9):
    cache_key = (key, height)
    if cache_key not in _sprite_cache:
        img = ImageMobject(str(SPRITES_DIR / SPRITE_FILE[key]))
        img.set(height=height)
        _sprite_cache[cache_key] = img
    return _sprite_cache[cache_key]


def ball(color=ORANGE, radius=0.22):
    return Circle(radius=radius, color=color, fill_color=color, fill_opacity=1, stroke_width=2, stroke_color=WHITE)


ORIGIN_DOWN = np.array([0.0, -0.9, 0.0])


class BaseJumpScene(Scene):
    """Shared rendering helpers; construct() is defined by subclasses."""

    # ------------------------------------------------------------------
    # bookend screens
    # ------------------------------------------------------------------

    def show_title_screen(self):
        title = Text("점프 디자인 — 물리가 아니라 손맛", font=FONT, font_size=44, color=WHITE)
        sub = Text(
            "같은 중력 법칙 안에서, 게임마다 점프를 다르게 설계하는 이유",
            font=FONT,
            font_size=24,
            color=GREY_B,
        )
        grp = VGroup(title, sub).arrange(DOWN, buff=0.35)
        self.play(Write(title), run_time=1.2)
        self.play(FadeIn(sub), run_time=0.6)
        self.wait(1.0)
        self.play(FadeOut(grp))

    def show_end_screen(self):
        title = Text("점프 하나에도 이렇게 많은 설계가 숨어 있다", font=FONT, font_size=34, color=WHITE)
        sub = Text(
            "examples/jump-physics-showcase — profiles.py에서 직접 값을 바꿔보세요",
            font=FONT,
            font_size=20,
            color=GREY_B,
        )
        grp = VGroup(title, sub).arrange(DOWN, buff=0.3)
        self.play(Write(title), run_time=1.0)
        self.play(FadeIn(sub))
        self.wait(1.5)
        self.play(FadeOut(grp))

    # ------------------------------------------------------------------
    # shared header
    # ------------------------------------------------------------------

    def build_header(self, profile):
        title = Text(profile.title, font=FONT, font_size=32, color=WHITE)
        subtitle = Text(profile.subtitle, font=FONT, font_size=21, color=GREY_B)
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.16)
        header.to_edge(UP, buff=0.5)
        caption = None
        if profile.caption:
            caption = Text(profile.caption, font=FONT, font_size=18, color=GREY_C)
            caption.next_to(header, DOWN, buff=0.25)
        return header, caption

    # ------------------------------------------------------------------
    # why / how explanation card, shown after a demo
    # ------------------------------------------------------------------

    def _build_code_block(self, label_text, code_lines):
        label = Text(label_text, font=FONT, font_size=20, color=YELLOW)
        body_lines = []
        indents = []
        for line in code_lines:
            if not line.strip():
                body_lines.append(Rectangle(width=0.1, height=0.14, fill_opacity=0, stroke_opacity=0))
                indents.append(0)
                continue
            color = GREY_C if line.strip().startswith("//") else "#8fd3ff"
            body_lines.append(Text(line.lstrip(), font=FONT, font_size=16, color=color))
            indents.append(len(line) - len(line.lstrip()))
        body = VGroup(*body_lines).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        # Text() crops leading whitespace from its own bounding box, so
        # aligned_edge=LEFT erases indentation above; reapply it by hand.
        indent_unit = 0.1
        for line_mobj, indent in zip(body_lines, indents):
            if indent:
                line_mobj.shift(RIGHT * indent * indent_unit)
        box = SurroundingRectangle(body, color=GREY_C, buff=0.22)
        block = VGroup(label, VGroup(box, body)).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        if block.width > 11.5:
            block.scale_to_fit_width(11.5)
        return block

    def show_explanation(self, game_title, why_lines, how_lines):
        # Unity/Unreal source variants live in the README / artifact page
        # (as actual code blocks), not baked into the video — see
        # explanations.py's "unity_cs" / "unreal_cpp" and docs/build_docs.py.
        heading = Text(game_title, font=FONT, font_size=28, color=WHITE)
        heading.to_edge(UP, buff=0.45)
        self.play(Write(heading), run_time=0.7)

        why_label = Text("왜 이렇게 만들었나", font=FONT, font_size=20, color=YELLOW)
        why_body = VGroup(
            *[Text(line, font=FONT, font_size=19, color=GREY_B) for line in why_lines]
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        why_block = VGroup(why_label, why_body).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        why_block.next_to(heading, DOWN, buff=0.45)
        why_block.to_edge(LEFT, buff=1.0)
        self.play(FadeIn(why_block), run_time=0.6)
        self.wait(2.2)

        block = self._build_code_block("어떻게 동작하는가 (C++ 핵심 로직)", how_lines)
        block.next_to(why_block, DOWN, buff=0.4)
        block.to_edge(LEFT, buff=1.0)
        self.play(FadeIn(block), run_time=0.6)
        self.wait(3.4)

        self.play(FadeOut(VGroup(heading, why_block, block)))

    # ------------------------------------------------------------------
    # generic single-profile segment: character runs a real spatial arc,
    # the position graph is drawn live (grows in sync with the jump)
    # ------------------------------------------------------------------

    def run_profile(
        self,
        profile,
        color,
        sprite_key=None,
        sprite_height=0.9,
        loops=2,
        velocity_hud=False,
        no_air_control=False,
        squat_marker=None,
    ):
        header, caption = self.build_header(profile)
        self.play(Write(header), run_time=0.8)
        if caption:
            self.play(FadeIn(caption), run_time=0.4)

        total = profile.total
        sample_ts = np.linspace(0, total, 200)
        y_max = max(profile.height(t) for t in sample_ts) + 0.6
        x_max = max(profile.x(t) for t in sample_ts)
        x_max = max(x_max, 0.5)

        axes = Axes(
            x_range=[0, x_max * 1.08, max(x_max / 5, 0.3)],
            y_range=[0, y_max, 1],
            x_length=9.5,
            y_length=3.6,
            axis_config={"include_tip": False},
        ).move_to(ORIGIN_DOWN)
        ground_line = Line(axes.c2p(0, 0), axes.c2p(x_max * 1.05, 0), color=GREY_C, stroke_width=2)
        self.play(Create(axes), Create(ground_line), run_time=0.8)

        t_tracker = ValueTracker(0)

        def wrapped_t():
            return t_tracker.get_value() % total

        curve = always_redraw(
            lambda: ParametricFunction(
                lambda tp: axes.c2p(profile.x(tp), profile.height(tp)),
                t_range=[0, max(wrapped_t(), 0.001)],
                color=color,
            )
        )

        if sprite_key:
            template = load_sprite(sprite_key, sprite_height)
            character = always_redraw(
                lambda: template.copy().move_to(axes.c2p(profile.x(t_tracker.get_value()), profile.height(t_tracker.get_value())))
            )
        else:
            character = always_redraw(
                lambda: ball(color).move_to(axes.c2p(profile.x(t_tracker.get_value()), profile.height(t_tracker.get_value())))
            )

        mobjects = [curve, character]

        if velocity_hud and profile.velocity is not None:
            hud = always_redraw(
                lambda: Text(
                    f"v = {profile.velocity(t_tracker.get_value()):+.1f}",
                    font=FONT,
                    font_size=22,
                    color=YELLOW,
                ).next_to(axes.c2p(profile.x(t_tracker.get_value()), profile.height(t_tracker.get_value())), RIGHT, buff=0.3)
            )
            mobjects.append(hud)

        if no_air_control:
            note = Text("← 조작 무효 →", font=FONT, font_size=18, color=RED).next_to(axes, UP, buff=0.15)
            self.play(FadeIn(note))
            mobjects.append(note)

        if squat_marker is not None:
            squat_note = always_redraw(
                lambda: Text("준비...", font=FONT, font_size=18, color=YELLOW).next_to(axes.c2p(0, 0), UP, buff=0.15)
                if wrapped_t() < squat_marker
                else VGroup()
            )
            mobjects.append(squat_note)

        self.add(*mobjects)
        self.play(t_tracker.animate.set_value(total * loops), run_time=(total * loops) / PLAYBACK_SPEED, rate_func=linear)
        self.wait(0.2)

        to_remove = [header, axes, ground_line, *mobjects]
        if caption:
            to_remove.append(caption)
        self.play(FadeOut(Group(*to_remove)))

    # ------------------------------------------------------------------
    # PREVIEW variant: character stays anchored on the left (like the very
    # first mario-jump-physics example) and the graph plots height-vs-TIME
    # to the right, drawn live. A numeric readout shows the live height
    # value ticking as the jump plays.
    # ------------------------------------------------------------------

    def run_profile_left_anchor(self, profile, color, sprite_key=None, sprite_height=0.9, loops=2, squat_marker=None, no_air_control=False):
        header, caption = self.build_header(profile)
        self.play(Write(header), run_time=0.8)
        if caption:
            self.play(FadeIn(caption), run_time=0.4)

        total = profile.total
        sample_ts = np.linspace(0, total, 200)
        y_max = max(profile.height(t) for t in sample_ts) + 0.6

        axes = Axes(
            x_range=[0, total * 1.05, max(total / 5, 0.2)],
            y_range=[0, y_max, 1],
            x_length=9.5,
            y_length=3.6,
            axis_config={"include_tip": False},
        ).move_to(ORIGIN_DOWN)
        ground_line = Line(axes.c2p(-0.4, 0), axes.c2p(total * 1.02, 0), color=GREY_C, stroke_width=2)
        self.play(Create(axes), Create(ground_line), run_time=0.8)

        t_tracker = ValueTracker(0)
        char_x = -0.15  # fixed lane on the left, next to the y-axis

        def wrapped_t():
            return t_tracker.get_value() % total

        curve = always_redraw(
            lambda: ParametricFunction(
                lambda tp: axes.c2p(tp, profile.height(tp)),
                t_range=[0, max(wrapped_t(), 0.001)],
                color=color,
            )
        )

        if sprite_key:
            template = load_sprite(sprite_key, sprite_height)
            character = always_redraw(
                lambda: template.copy().move_to(axes.c2p(char_x, profile.height(t_tracker.get_value())))
            )
        else:
            character = always_redraw(
                lambda: ball(color).move_to(axes.c2p(char_x, profile.height(t_tracker.get_value())))
            )

        def readout_text():
            tt = wrapped_t()
            h = profile.height(t_tracker.get_value())
            base = f"t = {tt:.2f}s   height = {h:.2f}"
            if profile.velocity is not None:
                base += f"   v = {profile.velocity(t_tracker.get_value()):+.1f}"
            return base

        readout = always_redraw(
            lambda: Text(readout_text(), font=FONT, font_size=20, color=YELLOW)
            .next_to(axes, UP, buff=0.2)
            .align_to(axes, LEFT)
        )

        cursor_dot = always_redraw(
            lambda: Circle(radius=0.06, color=color, fill_color=color, fill_opacity=1, stroke_width=0).move_to(
                axes.c2p(wrapped_t(), profile.height(t_tracker.get_value()))
            )
        )

        mobjects = [curve, character, readout, cursor_dot]

        if no_air_control:
            note = Text("← 조작 무효 →", font=FONT, font_size=18, color=RED).next_to(axes, UP, buff=0.6)
            self.play(FadeIn(note))
            mobjects.append(note)

        if squat_marker is not None:
            squat_note = always_redraw(
                lambda: Text("준비...", font=FONT, font_size=18, color=YELLOW).next_to(axes.c2p(char_x, 0), UP, buff=0.15)
                if wrapped_t() < squat_marker
                else VGroup()
            )
            mobjects.append(squat_note)

        self.add(*mobjects)
        self.play(t_tracker.animate.set_value(total * loops), run_time=(total * loops) / PLAYBACK_SPEED, rate_func=linear)
        self.wait(0.2)
        to_remove = [header, axes, ground_line, *mobjects]
        if caption:
            to_remove.append(caption)
        self.play(FadeOut(Group(*to_remove)))

    # ------------------------------------------------------------------
    # Jump King: charge meter + committed ballistic launch
    # ------------------------------------------------------------------

    def run_jump_king(self, loops=1):
        profile, charge_state = jp.jump_king()
        header, caption = self.build_header(profile)
        self.play(Write(header), run_time=0.8)
        if caption:
            self.play(FadeIn(caption), run_time=0.4)

        total = profile.total
        sample_ts = np.linspace(0, total, 300)
        y_max = max(profile.height(t) for t in sample_ts) + 0.5
        char_x = -0.15  # fixed lane on the left, like every other left-anchored segment

        axes = Axes(
            x_range=[0, total * 1.05, max(total / 6, 0.3)],
            y_range=[0, y_max, 1],
            x_length=9.5,
            y_length=3.6,
            axis_config={"include_tip": False},
        ).move_to(ORIGIN_DOWN)
        ground_line = Line(axes.c2p(-0.4, 0), axes.c2p(total * 1.02, 0), color=GREY_C, stroke_width=2)
        self.play(Create(axes), Create(ground_line), run_time=0.8)

        t_tracker = ValueTracker(0)

        def wrapped_t():
            return t_tracker.get_value() % total

        curve = always_redraw(
            lambda: ParametricFunction(
                lambda tp: axes.c2p(tp, profile.height(tp)),
                t_range=[0, max(wrapped_t(), 0.001)],
                color=PURPLE,
            )
        )

        template = load_sprite("jump_king", height=0.85)
        character = always_redraw(
            lambda: template.copy().move_to(axes.c2p(char_x, profile.height(t_tracker.get_value())))
        )
        readout = always_redraw(
            lambda: Text(
                f"t = {wrapped_t():.2f}s   height = {profile.height(t_tracker.get_value()):.2f}",
                font=FONT,
                font_size=20,
                color=YELLOW,
            ).next_to(axes, UP, buff=0.2).align_to(axes, LEFT)
        )
        cursor_dot = always_redraw(
            lambda: Circle(radius=0.06, color=PURPLE, fill_color=PURPLE, fill_opacity=1, stroke_width=0).move_to(
                axes.c2p(wrapped_t(), profile.height(t_tracker.get_value()))
            )
        )
        hud = always_redraw(lambda: self._charge_hud(t_tracker.get_value(), charge_state, axes, char_x))

        self.add(curve, character, readout, cursor_dot, hud)
        self.play(t_tracker.animate.set_value(total * loops), run_time=(total * loops) / PLAYBACK_SPEED, rate_func=linear)
        self.wait(0.2)
        self.play(FadeOut(Group(header, caption, axes, ground_line, curve, character, readout, cursor_dot, hud)))

    def _charge_hud(self, t, charge_state, axes, char_x):
        charging, label = charge_state(t)
        if not label:
            return VGroup()
        text = f"차지: {label}" if charging else f"발사! ({label})"
        color = YELLOW if charging else RED
        return Text(text, font=FONT, font_size=20, color=color).next_to(axes.c2p(char_x, 0), UP, buff=1.2)

    # ------------------------------------------------------------------
    # Dual left-anchor: two characters bounce in fixed lanes on the left
    # (same visual language as every other segment), while their curves
    # grow over time to the right. `value_fn` picks what the curve plots —
    # height by default, but e.g. horizontal distance when two profiles
    # share an identical height(t) and only differ in x(t) (Mega Man X).
    # ------------------------------------------------------------------

    def run_dual_left_anchor(
        self,
        title_text,
        subtitle_text,
        profile_a,
        profile_b,
        color_a,
        color_b,
        legend_a,
        legend_b,
        sprite_key=None,
        sprite_height=0.75,
        loops=3,
        value_fn=None,
    ):
        value_fn = value_fn or (lambda p, t: p.height(t))

        title = Text(title_text, font=FONT, font_size=30, color=WHITE)
        subtitle = Text(subtitle_text, font=FONT, font_size=21, color=GREY_B)
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.16).to_edge(UP, buff=0.5)
        self.play(Write(header), run_time=0.9)

        total = profile_a.total
        sample_ts = np.linspace(0, total, 200)
        y_max = max(max(value_fn(profile_a, t), value_fn(profile_b, t)) for t in sample_ts) + 0.6

        axes = Axes(
            x_range=[0, total * 1.05, max(total / 5, 0.2)],
            y_range=[0, y_max, 1],
            x_length=9.5,
            y_length=3.6,
            axis_config={"include_tip": False},
        ).move_to(ORIGIN_DOWN)
        ground_line = Line(axes.c2p(-0.4, 0), axes.c2p(total * 1.02, 0), color=GREY_C, stroke_width=2)

        legend = VGroup(
            Text(f"● {legend_a}", font=FONT, font_size=18, color=color_a),
            Text(f"● {legend_b}", font=FONT, font_size=18, color=color_b),
        ).arrange(RIGHT, buff=0.6).next_to(axes, UP, buff=0.15)

        self.play(Create(axes), Create(ground_line), FadeIn(legend), run_time=1.0)

        t_tracker = ValueTracker(0)
        char_x = -0.15  # shared data-space anchor (same as every other segment)

        def wrapped_t():
            return t_tracker.get_value() % total

        def make_curve(profile, color):
            return always_redraw(
                lambda: ParametricFunction(
                    lambda tp: axes.c2p(tp, value_fn(profile, tp)),
                    t_range=[0, max(wrapped_t(), 0.001)],
                    color=color,
                )
            )

        curve_a = make_curve(profile_a, color_a)
        curve_b = make_curve(profile_b, color_b)

        # The two characters share one data-space anchor (char_x) but need
        # visual separation; axes.c2p scales data-x by the axes' own time
        # scale, so a data-space offset would land off-screen for short
        # `total`s. A fixed screen-space shift avoids that entirely.
        def make_character(profile, screen_offset, color):
            if sprite_key:
                template = load_sprite(sprite_key, sprite_height)
                return always_redraw(
                    lambda: template.copy().move_to(axes.c2p(char_x, profile.height(t_tracker.get_value()))).shift(RIGHT * screen_offset)
                )
            return always_redraw(
                lambda: ball(color).move_to(axes.c2p(char_x, profile.height(t_tracker.get_value()))).shift(RIGHT * screen_offset)
            )

        char_a = make_character(profile_a, -0.35, color_a)
        char_b = make_character(profile_b, 0.35, color_b)

        self.add(curve_a, curve_b, char_a, char_b)
        self.play(t_tracker.animate.set_value(total * loops), run_time=(total * loops) / PLAYBACK_SPEED, rate_func=linear)
        self.wait(0.2)
        self.play(FadeOut(Group(header, axes, ground_line, legend, curve_a, curve_b, char_a, char_b)))

    # ------------------------------------------------------------------
    # Dual SPATIAL comparison: two characters actually run+jump along
    # their real (x, height) arcs, landing at different points. Needed
    # whenever height(t) is identical between the two profiles (Mega Man
    # X walk vs dash) — a left-anchored height/time or distance/time graph
    # can't show that as a parabola, since only the arc shape does.
    # ------------------------------------------------------------------

    def run_dual_spatial(
        self,
        title_text,
        subtitle_text,
        profile_a,
        profile_b,
        color_a,
        color_b,
        legend_a,
        legend_b,
        sprite_key=None,
        sprite_height=0.65,
        loops=3,
    ):
        title = Text(title_text, font=FONT, font_size=30, color=WHITE)
        subtitle = Text(subtitle_text, font=FONT, font_size=21, color=GREY_B)
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.16).to_edge(UP, buff=0.5)
        self.play(Write(header), run_time=0.9)

        total = profile_a.total
        sample_ts = np.linspace(0, total, 200)
        x_max = max(max(profile_a.x(t), profile_b.x(t)) for t in sample_ts)
        y_max = max(profile_a.height(t) for t in sample_ts) + 0.5

        axes = Axes(
            x_range=[0, x_max * 1.08, max(x_max / 6, 0.3)],
            y_range=[0, y_max, 1],
            x_length=9.5,
            y_length=3.6,
            axis_config={"include_tip": False},
        ).move_to(ORIGIN_DOWN)
        ground_line = Line(axes.c2p(0, 0), axes.c2p(x_max * 1.05, 0), color=GREY_C, stroke_width=2)

        legend = VGroup(
            Text(f"● {legend_a}", font=FONT, font_size=18, color=color_a),
            Text(f"● {legend_b}", font=FONT, font_size=18, color=color_b),
        ).arrange(RIGHT, buff=0.6).next_to(axes, UP, buff=0.15)

        self.play(Create(axes), Create(ground_line), FadeIn(legend), run_time=1.0)

        t_tracker = ValueTracker(0)

        def wrapped_t():
            return t_tracker.get_value() % total

        def make_curve(profile, color):
            return always_redraw(
                lambda: ParametricFunction(
                    lambda tp: axes.c2p(profile.x(tp), profile.height(tp)),
                    t_range=[0, max(wrapped_t(), 0.001)],
                    color=color,
                )
            )

        curve_a = make_curve(profile_a, color_a)
        curve_b = make_curve(profile_b, color_b)

        def make_character(profile, color):
            if sprite_key:
                template = load_sprite(sprite_key, sprite_height)
                return always_redraw(
                    lambda: template.copy().move_to(axes.c2p(profile.x(t_tracker.get_value()), profile.height(t_tracker.get_value())))
                )
            return always_redraw(
                lambda: ball(color).move_to(axes.c2p(profile.x(t_tracker.get_value()), profile.height(t_tracker.get_value())))
            )

        char_a = make_character(profile_a, color_a)
        char_b = make_character(profile_b, color_b)

        self.add(curve_a, curve_b, char_a, char_b)
        self.play(t_tracker.animate.set_value(total * loops), run_time=(total * loops) / PLAYBACK_SPEED, rate_func=linear)
        self.wait(0.2)
        self.play(FadeOut(Group(header, axes, ground_line, legend, curve_a, curve_b, char_a, char_b)))


# ---------------------------------------------------------------------------
# combined long-form video (all 10 segments back to back, with bookends)
# ---------------------------------------------------------------------------


class JumpPhysicsShowcase(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG

        self.show_title_screen()

        self.run_profile_left_anchor(jp.basic_concept(), ORANGE, loops=2)
        self.run_profile_left_anchor(jp.mario(), BLUE, sprite_key="mario", loops=3)
        self.run_profile_left_anchor(jp.metroid(), GREEN, sprite_key="metroid", loops=2)
        self.run_profile_left_anchor(jp.ghosts_n_goblins(), ORANGE, sprite_key="ghosts_n_goblins", loops=5, no_air_control=True)

        vanilla, turbo = jp.sf2_screw_piledriver()
        self.run_dual_left_anchor(
            "스트리트 파이터 II — 장기에프 스크류 파일드라이버",
            "이동 경로(궤적)는 완전히 동일 — 속도 배분만 다르다",
            vanilla, turbo, BLUE, RED,
            "오리지널 (등속)", "터보 이후 (하강 가속)",
            sprite_key="sf2", sprite_height=0.55, loops=3,
        )

        self.run_profile_left_anchor(jp.smash_jump_squat(), PURPLE, sprite_key="smash_squat", loops=3, squat_marker=0.12)
        self.run_profile_left_anchor(jp.smash_ultimate_special(), PURPLE, sprite_key="smash_ultimate", loops=3)

        self.run_jump_king(loops=1)

        celeste_full, celeste_cut = jp.celeste_pair()
        self.run_profile_left_anchor(celeste_full, GREEN, sprite_key="celeste", loops=2)
        self.run_profile_left_anchor(celeste_cut, GREEN, sprite_key="celeste", loops=3)

        walk, dash = jp.megaman_x_dash_jump()
        self.run_dual_spatial(
            "현대 게임 — 록맨 X: 걷기 점프 vs 대시 점프",
            "높이는 똑같이, 수평 속도만 이어받아 이동 거리가 크게 늘어난다",
            walk, dash, BLUE, RED,
            "걷기 점프", "대시 점프",
            sprite_key="megaman", loops=3,
        )

        self.show_end_screen()


# ---------------------------------------------------------------------------
# 10 standalone videos: one demo + a "why / how" explanation card each
# ---------------------------------------------------------------------------


class Scene01Basic(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        self.run_profile_left_anchor(jp.basic_concept(), ORANGE, loops=2)
        e = EXPLANATIONS["basic"]
        self.show_explanation("점프의 기본 원리", e["why"], e["how"])


class Scene02Mario(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        self.run_profile_left_anchor(jp.mario(), BLUE, sprite_key="mario", loops=3)
        e = EXPLANATIONS["mario"]
        self.show_explanation("슈퍼 마리오브라더스", e["why"], e["how"])


class Scene03Metroid(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        self.run_profile_left_anchor(jp.metroid(), GREEN, sprite_key="metroid", loops=2)
        e = EXPLANATIONS["metroid"]
        self.show_explanation("메트로이드", e["why"], e["how"])


class Scene04GhostsNGoblins(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        self.run_profile_left_anchor(jp.ghosts_n_goblins(), ORANGE, sprite_key="ghosts_n_goblins", loops=5, no_air_control=True)
        e = EXPLANATIONS["ghosts_n_goblins"]
        self.show_explanation("마계촌", e["why"], e["how"])


class Scene05StreetFighter(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        vanilla, turbo = jp.sf2_screw_piledriver()
        self.run_dual_left_anchor(
            "스트리트 파이터 II — 장기에프 스크류 파일드라이버",
            "이동 경로(궤적)는 완전히 동일 — 속도 배분만 다르다",
            vanilla, turbo, BLUE, RED,
            "오리지널 (등속)", "터보 이후 (하강 가속)",
            sprite_key="sf2", sprite_height=0.55, loops=3,
        )
        e = EXPLANATIONS["sf2"]
        self.show_explanation("스트리트 파이터 II — 장기에프", e["why"], e["how"])


class Scene06SmashSquat(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        self.run_profile_left_anchor(jp.smash_jump_squat(), PURPLE, sprite_key="smash_squat", loops=3, squat_marker=0.12)
        e = EXPLANATIONS["smash_squat"]
        self.show_explanation("대난투 스매시브라더스 — 점프 스쿼트", e["why"], e["how"])


class Scene07SmashUltimate(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        self.run_profile_left_anchor(jp.smash_ultimate_special(), PURPLE, sprite_key="smash_ultimate", loops=3)
        e = EXPLANATIONS["smash_ultimate"]
        self.show_explanation("대난투 스매시브라더스 얼티밋", e["why"], e["how"])


class Scene08JumpKing(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        self.run_jump_king(loops=1)
        e = EXPLANATIONS["jump_king"]
        self.show_explanation("현대 게임 — 점프킹", e["why"], e["how"])


class Scene09Celeste(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        full, cut = jp.celeste_pair()
        self.run_profile_left_anchor(full, GREEN, sprite_key="celeste", loops=2)
        self.run_profile_left_anchor(cut, GREEN, sprite_key="celeste", loops=3)
        e = EXPLANATIONS["celeste"]
        self.show_explanation("현대 게임 — 셀레스트", e["why"], e["how"])


class Scene10MegaManDash(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        walk, dash = jp.megaman_x_dash_jump()
        self.run_dual_spatial(
            "현대 게임 — 록맨 X: 걷기 점프 vs 대시 점프",
            "높이는 똑같이, 수평 속도만 이어받아 이동 거리가 크게 늘어난다",
            walk, dash, BLUE, RED,
            "걷기 점프", "대시 점프",
            sprite_key="megaman", loops=3,
        )
        e = EXPLANATIONS["megaman"]
        self.show_explanation("현대 게임 — 록맨 X 대시 점프", e["why"], e["how"])


# ---------------------------------------------------------------------------
# PREVIEW: Mario redone with the character anchored on the left (like the
# original mario-jump-physics example) + a live numeric height/time readout
# ---------------------------------------------------------------------------


class ScenePreviewMario(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        self.run_profile_left_anchor(jp.mario(), BLUE, sprite_key="mario", loops=3)
        e = EXPLANATIONS["mario"]
        self.show_explanation("슈퍼 마리오브라더스 (프리뷰)", e["why"], e["how"])

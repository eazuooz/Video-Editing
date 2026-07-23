"""Long-form jump-design showcase: from the basic frame-by-frame gravity
concept through Mario, Metroid, Ghosts'n Goblins, Street Fighter II,
Smash Bros, and modern examples (Jump King, Celeste, Mega Man X).

Characters are drawn as simple capsules (rounded-rectangle "cylinders"),
standing in for a game's physics collider rather than any specific sprite.
"""

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
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    ParametricFunction,
    Rectangle,
    RoundedRectangle,
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


def capsule(color, w=0.46, h=0.85):
    return RoundedRectangle(
        corner_radius=w / 2,
        width=w,
        height=h,
        color=color,
        fill_color=color,
        fill_opacity=1,
        stroke_width=0,
    )


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

    def show_explanation(self, game_title, why_lines, how_lines):
        heading = Text(game_title, font=FONT, font_size=28, color=WHITE)
        heading.to_edge(UP, buff=0.45)
        self.play(Write(heading), run_time=0.7)

        why_label = Text("왜 이렇게 만들었나", font=FONT, font_size=20, color=YELLOW)
        why_body = VGroup(
            *[Text(line, font=FONT, font_size=19, color=GREY_B) for line in why_lines]
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        why_block = VGroup(why_label, why_body).arrange(DOWN, aligned_edge=LEFT, buff=0.16)

        how_label = Text("어떻게 동작하는가 (핵심 로직)", font=FONT, font_size=20, color=YELLOW)
        how_body_lines = []
        for line in how_lines:
            if not line.strip():
                # blank spacer: a real Text(" ") has a degenerate bounding box
                # that breaks arrange(), so use an invisible rectangle instead
                how_body_lines.append(Rectangle(width=0.1, height=0.14, fill_opacity=0, stroke_opacity=0))
                continue
            color = GREY_C if line.strip().startswith("#") else "#8fd3ff"
            how_body_lines.append(Text(line, font=FONT, font_size=17, color=color))
        how_body = VGroup(*how_body_lines).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        code_box = SurroundingRectangle(how_body, color=GREY_C, buff=0.22)
        how_block = VGroup(how_label, VGroup(code_box, how_body)).arrange(DOWN, aligned_edge=LEFT, buff=0.16)

        content = VGroup(why_block, how_block).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        if content.width > 11.5:
            content.scale_to_fit_width(11.5)
        content.next_to(heading, DOWN, buff=0.45)
        content.to_edge(LEFT, buff=1.0)

        self.play(FadeIn(why_block), run_time=0.6)
        self.wait(2.2)
        self.play(FadeIn(how_block), run_time=0.6)
        self.wait(3.2)
        self.play(FadeOut(VGroup(heading, content)))

    # ------------------------------------------------------------------
    # generic single-profile segment (in-place bounce OR spatial trajectory)
    # ------------------------------------------------------------------

    def run_profile(self, profile, color, loops=2, velocity_hud=False, no_air_control=False, squat_marker=None):
        header, caption = self.build_header(profile)
        self.play(Write(header), run_time=0.8)
        if caption:
            self.play(FadeIn(caption), run_time=0.4)

        total = profile.total
        is_traj = profile.show_trajectory
        sample_ts = np.linspace(0, total, 200)
        y_max = max(profile.height(t) for t in sample_ts) + 0.5

        if is_traj:
            x_max = max(profile.x(t) for t in sample_ts)
            axes = Axes(
                x_range=[0, x_max * 1.08, max(x_max / 5, 0.3)],
                y_range=[0, y_max, 1],
                x_length=9.5,
                y_length=3.6,
                axis_config={"include_tip": False},
            ).move_to(ORIGIN_DOWN)
            curve = ParametricFunction(
                lambda t: axes.c2p(profile.x(t), profile.height(t)),
                t_range=[0, total],
                color=color,
            )
            cap_x = lambda t: profile.x(t)
        else:
            axes = Axes(
                x_range=[0, total * 1.05, max(total / 5, 0.2)],
                y_range=[0, y_max, 1],
                x_length=9.5,
                y_length=3.6,
                axis_config={"include_tip": False},
            ).move_to(ORIGIN_DOWN)
            curve = axes.plot(profile.height, x_range=[0, total], color=color)
            cap_x = lambda t: -0.15

        ground_line = Line(
            axes.c2p(-0.4 if not is_traj else 0, 0),
            axes.c2p(x_max * 1.05 if is_traj else total * 1.02, 0),
            color=GREY_C,
            stroke_width=2,
        )

        self.play(Create(axes), Create(curve), Create(ground_line), run_time=1.0)

        t_tracker = ValueTracker(0)

        sprite = always_redraw(
            lambda: capsule(color).move_to(axes.c2p(cap_x(t_tracker.get_value()), profile.height(t_tracker.get_value())))
        )
        mobjects = [sprite]

        if velocity_hud and profile.velocity is not None:
            hud = always_redraw(
                lambda: Text(
                    f"v = {profile.velocity(t_tracker.get_value()):+.1f}",
                    font=FONT,
                    font_size=22,
                    color=YELLOW,
                ).next_to(axes.c2p(cap_x(t_tracker.get_value()), profile.height(t_tracker.get_value())), RIGHT, buff=0.3)
            )
            mobjects.append(hud)

        if no_air_control:
            note = Text("← 조작 무효 →", font=FONT, font_size=18, color=RED).next_to(axes, UP, buff=0.15)
            self.play(FadeIn(note))
            mobjects.append(note)

        if squat_marker is not None:
            squat_note = always_redraw(
                lambda: Text(
                    "준비...",
                    font=FONT,
                    font_size=18,
                    color=YELLOW,
                ).next_to(axes.c2p(cap_x(0), 0), UP, buff=0.15)
                if (t_tracker.get_value() % total) < squat_marker
                else VGroup()
            )
            mobjects.append(squat_note)

        self.add(*mobjects)
        self.play(t_tracker.animate.set_value(total * loops), run_time=total * loops, rate_func=linear)
        self.wait(0.2)

        to_remove = [header, axes, curve, ground_line, *mobjects]
        if caption:
            to_remove.append(caption)
        self.play(FadeOut(VGroup(*to_remove)))

    # ------------------------------------------------------------------
    # Street Fighter II: one static path, two cursors at different speeds
    # ------------------------------------------------------------------

    def run_sf2(self, vanilla, turbo, loops=3):
        title = Text("스트리트 파이터 II — 장기에프 스크류 파일드라이버", font=FONT, font_size=30, color=WHITE)
        subtitle = Text(
            "이동 경로(궤적)는 완전히 동일 — 속도 배분만 다르다", font=FONT, font_size=21, color=GREY_B
        )
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.16).to_edge(UP, buff=0.5)
        self.play(Write(header), run_time=0.9)

        total = vanilla.total
        y_max = max(jp.sf2_shape(s) for s in np.linspace(0, 1, 50)) + 0.5
        axes = Axes(
            x_range=[0, 1, 0.25],
            y_range=[0, y_max, 1],
            x_length=9.5,
            y_length=3.6,
            axis_config={"include_tip": False},
        ).move_to(ORIGIN_DOWN)

        path = axes.plot(lambda s: jp.sf2_shape(s), x_range=[0, 1], color=GREY_B)
        self.play(Create(axes), Create(path), run_time=1.0)

        legend = VGroup(
            Text("● 오리지널 (등속)", font=FONT, font_size=18, color=BLUE),
            Text("● 터보 이후 (하강 가속)", font=FONT, font_size=18, color=RED),
        ).arrange(RIGHT, buff=0.6).next_to(axes, UP, buff=0.15)
        self.play(FadeIn(legend))

        t_tracker = ValueTracker(0)
        dot_vanilla = always_redraw(
            lambda: Dot(axes.c2p(jp.sf2_vanilla_reparam(t_tracker.get_value() % total, total), jp.sf2_shape(jp.sf2_vanilla_reparam(t_tracker.get_value() % total, total))), color=BLUE, radius=0.13)
        )
        dot_turbo = always_redraw(
            lambda: Dot(axes.c2p(jp.sf2_turbo_reparam(t_tracker.get_value() % total, total), jp.sf2_shape(jp.sf2_turbo_reparam(t_tracker.get_value() % total, total))), color=RED, radius=0.13)
        )
        self.add(dot_vanilla, dot_turbo)
        self.play(t_tracker.animate.set_value(total * loops), run_time=total * loops, rate_func=linear)
        self.wait(0.2)
        self.play(FadeOut(VGroup(header, axes, path, legend, dot_vanilla, dot_turbo)))

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
        y_max = max(profile.height(t) for t in np.linspace(0, total, 300)) + 0.5
        axes = Axes(
            x_range=[0, total * 1.02, total / 6],
            y_range=[0, y_max, 1],
            x_length=9.5,
            y_length=3.6,
            axis_config={"include_tip": False},
        ).move_to(ORIGIN_DOWN)
        curve = axes.plot(profile.height, x_range=[0, total], color=PURPLE)
        ground_line = Line(axes.c2p(-0.3, 0), axes.c2p(total * 1.0, 0), color=GREY_C, stroke_width=2)
        self.play(Create(axes), Create(curve), Create(ground_line), run_time=1.0)

        t_tracker = ValueTracker(0)
        cap_x = -0.15
        sprite = always_redraw(
            lambda: capsule(PURPLE).move_to(axes.c2p(cap_x, profile.height(t_tracker.get_value())))
        )
        hud = always_redraw(lambda: self._charge_hud(t_tracker.get_value(), charge_state, axes, cap_x))

        self.add(sprite, hud)
        self.play(t_tracker.animate.set_value(total * loops), run_time=total * loops, rate_func=linear)
        self.wait(0.2)
        self.play(FadeOut(VGroup(header, caption, axes, curve, ground_line, sprite, hud)))

    def _charge_hud(self, t, charge_state, axes, cap_x):
        charging, label = charge_state(t)
        if not label:
            return VGroup()
        text = f"차지: {label}" if charging else f"발사! ({label})"
        color = YELLOW if charging else RED
        return Text(text, font=FONT, font_size=20, color=color).next_to(axes.c2p(cap_x, 0), UP, buff=1.2)

    # ------------------------------------------------------------------
    # Mega Man X: walk-jump vs dash-jump, side by side on one axes
    # ------------------------------------------------------------------

    def run_dual_trajectory(self, profile_a, profile_b, color_a, color_b, loops=3):
        title = Text("현대 게임 — 록맨 X: 걷기 점프 vs 대시 점프", font=FONT, font_size=30, color=WHITE)
        subtitle = Text(
            "높이는 똑같이, 수평 속도만 이어받아 이동 거리가 크게 늘어난다", font=FONT, font_size=21, color=GREY_B
        )
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.16).to_edge(UP, buff=0.5)
        self.play(Write(header), run_time=0.9)

        total = profile_a.total
        x_max = max(profile_b.x(total * 0.999), profile_a.x(total * 0.999))
        y_max = max(profile_a.height(t) for t in np.linspace(0, total, 200)) + 0.5
        axes = Axes(
            x_range=[0, x_max * 1.08, max(x_max / 6, 0.3)],
            y_range=[0, y_max, 1],
            x_length=9.5,
            y_length=3.6,
            axis_config={"include_tip": False},
        ).move_to(ORIGIN_DOWN)

        curve_a = ParametricFunction(lambda t: axes.c2p(profile_a.x(t), profile_a.height(t)), t_range=[0, total], color=color_a)
        curve_b = ParametricFunction(lambda t: axes.c2p(profile_b.x(t), profile_b.height(t)), t_range=[0, total], color=color_b)
        ground_line = Line(axes.c2p(0, 0), axes.c2p(x_max * 1.05, 0), color=GREY_C, stroke_width=2)

        legend = VGroup(
            Text("● 걷기 점프", font=FONT, font_size=18, color=color_a),
            Text("● 대시 점프", font=FONT, font_size=18, color=color_b),
        ).arrange(RIGHT, buff=0.6).next_to(axes, UP, buff=0.15)

        self.play(Create(axes), Create(curve_a), Create(curve_b), Create(ground_line), FadeIn(legend), run_time=1.0)

        t_tracker = ValueTracker(0)
        cap_a = always_redraw(
            lambda: capsule(color_a, w=0.36, h=0.65).move_to(axes.c2p(profile_a.x(t_tracker.get_value() % total), profile_a.height(t_tracker.get_value() % total)))
        )
        cap_b = always_redraw(
            lambda: capsule(color_b, w=0.36, h=0.65).move_to(axes.c2p(profile_b.x(t_tracker.get_value() % total), profile_b.height(t_tracker.get_value() % total)))
        )
        self.add(cap_a, cap_b)
        self.play(t_tracker.animate.set_value(total * loops), run_time=total * loops, rate_func=linear)
        self.wait(0.2)
        self.play(FadeOut(VGroup(header, axes, curve_a, curve_b, ground_line, legend, cap_a, cap_b)))


ORIGIN_DOWN = np.array([0.0, -0.9, 0.0])


# ---------------------------------------------------------------------------
# combined long-form video (all 10 segments back to back, with bookends)
# ---------------------------------------------------------------------------


class JumpPhysicsShowcase(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG

        self.show_title_screen()

        self.run_profile(jp.basic_concept(), BLUE, loops=2, velocity_hud=True)
        self.run_profile(jp.mario(), BLUE, loops=3)
        self.run_profile(jp.metroid(), GREEN, loops=2)
        self.run_profile(jp.ghosts_n_goblins(), ORANGE, loops=5, no_air_control=True)

        vanilla, turbo = jp.sf2_screw_piledriver()
        self.run_sf2(vanilla, turbo, loops=3)

        self.run_profile(jp.smash_jump_squat(), PURPLE, loops=3, squat_marker=0.12)
        self.run_profile(jp.smash_ultimate_special(), PURPLE, loops=3)

        self.run_jump_king(loops=1)

        celeste_full, celeste_cut = jp.celeste_pair()
        self.run_profile(celeste_full, GREEN, loops=2)
        self.run_profile(celeste_cut, GREEN, loops=3)

        walk, dash = jp.megaman_x_dash_jump()
        self.run_dual_trajectory(walk, dash, BLUE, RED, loops=3)

        self.show_end_screen()


# ---------------------------------------------------------------------------
# 10 standalone videos: one demo + a "why / how" explanation card each
# ---------------------------------------------------------------------------


class Scene01Basic(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        self.run_profile(jp.basic_concept(), BLUE, loops=2, velocity_hud=True)
        e = EXPLANATIONS["basic"]
        self.show_explanation("점프의 기본 원리", e["why"], e["how"])


class Scene02Mario(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        self.run_profile(jp.mario(), BLUE, loops=3)
        e = EXPLANATIONS["mario"]
        self.show_explanation("슈퍼 마리오브라더스", e["why"], e["how"])


class Scene03Metroid(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        self.run_profile(jp.metroid(), GREEN, loops=2)
        e = EXPLANATIONS["metroid"]
        self.show_explanation("메트로이드", e["why"], e["how"])


class Scene04GhostsNGoblins(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        self.run_profile(jp.ghosts_n_goblins(), ORANGE, loops=5, no_air_control=True)
        e = EXPLANATIONS["ghosts_n_goblins"]
        self.show_explanation("마계촌", e["why"], e["how"])


class Scene05StreetFighter(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        vanilla, turbo = jp.sf2_screw_piledriver()
        self.run_sf2(vanilla, turbo, loops=3)
        e = EXPLANATIONS["sf2"]
        self.show_explanation("스트리트 파이터 II — 장기에프", e["why"], e["how"])


class Scene06SmashSquat(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        self.run_profile(jp.smash_jump_squat(), PURPLE, loops=3, squat_marker=0.12)
        e = EXPLANATIONS["smash_squat"]
        self.show_explanation("대난투 스매시브라더스 — 점프 스쿼트", e["why"], e["how"])


class Scene07SmashUltimate(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        self.run_profile(jp.smash_ultimate_special(), PURPLE, loops=3)
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
        self.run_profile(full, GREEN, loops=2)
        self.run_profile(cut, GREEN, loops=3)
        e = EXPLANATIONS["celeste"]
        self.show_explanation("현대 게임 — 셀레스트", e["why"], e["how"])


class Scene10MegaManDash(BaseJumpScene):
    def construct(self):
        self.camera.background_color = BG
        walk, dash = jp.megaman_x_dash_jump()
        self.run_dual_trajectory(walk, dash, BLUE, RED, loops=3)
        e = EXPLANATIONS["megaman"]
        self.show_explanation("현대 게임 — 록맨 X 대시 점프", e["why"], e["how"])

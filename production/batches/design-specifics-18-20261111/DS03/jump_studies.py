"""Original symbolic motion studies for the jump-physics episode."""

import numpy as np
from manim import (Arrow, Axes, Dot, DOWN, LEFT, Line, MathTex, Rectangle,
                   RIGHT, RoundedRectangle, Scene, Text, UP, ValueTracker, VGroup,
                   always_redraw, linear)


BACKGROUND = '#0a110d'
BOARD = '#122019'
GRID = '#335246'
WHITE = '#f5f4ec'
MUTED = '#b7c9bf'
YELLOW = '#f2d786'
TEAL = '#79d2ca'
CORAL = '#f08a75'


def ko(text, size, color=WHITE):
    return Text(text, font='Malgun Gothic', font_size=size, color=color)


def header(scene, title):
    scene.camera.background_color = BACKGROUND
    scene.add(ko(title, 48, YELLOW).to_corner(UP + LEFT, buff=.46),
              ko('원리 도식', 26, MUTED).to_corner(UP + RIGHT, buff=.46),
              Line([-6.64, 2.90, 0], [6.64, 2.90, 0], color=GRID, stroke_width=2))


class VerticalJump(Scene):
    def construct(self):
        header(self, 'Jump Physics (점프 물리)')
        time = ValueTracker(0)
        floor = -1.9
        ground = np.array([-3.95, floor, 0])
        board = Rectangle(width=5.9, height=4.4, fill_color=BOARD, fill_opacity=1,
                          stroke_color=GRID, stroke_width=2).move_to([-3.59, -.1, 0])
        self.add(board, Line([-6.25, floor, 0], [-.9, floor, 0], color=MUTED, stroke_width=3))
        self.add(ko('게임 화면의 세로 위치', 31, TEAL).move_to([-3.58, 2.39, 0]))

        def height(t):
            return 3.1 * t * (2 - t)

        def foot():
            return ground + np.array([0, height(time.get_value()), 0])

        def body():
            feet = foot()
            return VGroup(RoundedRectangle(width=.43, height=.54, corner_radius=.07,
                           stroke_width=0, fill_opacity=1, fill_color=TEAL).move_to(feet + UP * .27),
                          Dot(feet + UP * .66, radius=.14, color=TEAL))

        def velocity():
            speed = 1 - time.get_value()
            start = foot() + RIGHT * .49
            if abs(speed) < .06:
                return Dot(start, radius=.07, color=TEAL)
            return Arrow(start, start + UP * (.92 * speed), buff=0, color=TEAL, stroke_width=6)

        self.add(always_redraw(body), always_redraw(velocity))
        self.add(always_redraw(lambda: Arrow(foot() + LEFT * .55, foot() + LEFT * .55 + DOWN * .58,
                                            buff=0, color=CORAL, stroke_width=5)))
        self.add(ko('속도', 25, TEAL).move_to([-2.25, -.67, 0]),
                 ko('중력 가속도', 25, CORAL).move_to([-2.25, -1.12, 0]))

        graph = Axes(x_range=[0, 2.18, 1], y_range=[-1.22, 1.22, 1], x_length=5.1, y_length=2.64,
                     tips=False, axis_config={'include_ticks': False, 'color': MUTED}).move_to([3.43, .48, 0])
        self.add(graph, ko('세로 속도', 31, TEAL).move_to([1.63, 2.15, 0]),
                 ko('시간', 24, MUTED).next_to(graph.c2p(2.14, 0), DOWN, buff=.14))
        self.add(graph.plot(lambda x: 1 - x, x_range=[0, 2], color=GRID, stroke_width=5))
        self.add(always_redraw(lambda: Line(graph.c2p(0, 1), graph.c2p(time.get_value(), 1-time.get_value()),
                                             color=TEAL, stroke_width=5)),
                 always_redraw(lambda: Dot(graph.c2p(time.get_value(), 1-time.get_value()), radius=.08, color=YELLOW)))
        equation = MathTex(r'v_y(t)', '=', r'v_{y,0}', '-', r'gt', font_size=49, color=WHITE)
        equation[0].set_color(TEAL)
        equation[4].set_color(CORAL)
        equation.move_to([3.44, -1.38, 0])
        self.add(equation, ko('현재 속도 · 처음 속도 · 중력과 시간', 27, MUTED).next_to(equation, DOWN, buff=.18))
        self.wait(.6)
        self.play(time.animate.set_value(1), run_time=4, rate_func=linear)
        apex = ko('가장 높을 때 세로 속도는 0', 25, YELLOW).move_to([3.52, -2.48, 0])
        self.add(apex)
        self.wait(.9)
        self.remove(apex)
        self.play(time.animate.set_value(2), run_time=4, rate_func=linear)
        self.wait(.5)


class HorizontalControl(Scene):
    def construct(self):
        header(self, 'Air Control (공중 조향)')
        time = ValueTracker(0)
        floor = -1.7
        self.add(ko('같은 세로 운동 · 가로 방향 조작만 바꿈', 34, WHITE).move_to([0, 2.16, 0]))
        for center, title, color, steer in [(-3.44, 'A · 방향 유지', TEAL, False),
                                            (3.44, 'B · 공중에서 방향 전환', CORAL, True)]:
            left = center - 2.82
            frame = Rectangle(width=6.3, height=3.25, fill_color=BOARD, fill_opacity=1,
                              stroke_color=GRID, stroke_width=2).move_to([center, -.29, 0])
            self.add(frame, ko(title, 32, color).move_to([center, 1.65, 0]),
                     Line([left, floor, 0], [left + 5.58, floor, 0], color=MUTED))

            def position(t, origin=left, turn=steer):
                elapsed = t - 1
                x = 2.62 * t if not turn or elapsed <= 0 else 2.62 + 2.62 * elapsed - 3.6 * elapsed**2
                return np.array([origin + x, floor + 2.15 * t * (2 - t), 0])

            self.add(Line(position(0), position(0) + UP * .28, color=WHITE, stroke_width=4))
            self.add(always_redraw(lambda point=position, pigment=color: Dot(point(time.get_value()), radius=.13, color=pigment)))

            def path(point=position, pigment=color):
                progress = time.get_value()
                points = [point(t) for t in np.linspace(0, progress, 52)]
                return VGroup(*(Line(a, b, color=pigment, stroke_width=4)
                                for a, b in zip(points, points[1:]) if np.linalg.norm(b-a) > 1e-6))

            self.add(always_redraw(path))
            target = position(2)
            self.add(Line(target, target + UP * .23, color=color, stroke_width=5))
        self.add(ko('같은 높이에서 내려와도 착지하는 곳은 달라집니다', 36, YELLOW).move_to([0, -2.42, 0]))
        self.wait(.7)
        self.play(time.animate.set_value(2), run_time=7.7, rate_func=linear)
        self.wait(1.6)


class JumpSquat(Scene):
    def construct(self):
        header(self, 'Jump Squat (점프 스쿼트)')
        time = ValueTracker(0)
        left, right = -2.4, 5.95
        press, attack = .33, .58
        px = lambda t: left + (right - left) * t
        for point, title in [(press, '스틱 위로'), (attack, '공격 입력')]:
            x = px(point)
            self.add(Line([x, -1.63, 0], [x, 1.78, 0], color=GRID, stroke_width=3),
                     ko(title, 32, YELLOW).move_to([x, 2.12, 0]))
        rows = [(1.0, '준비 구간 없음', '공중 공격', CORAL, '먼저 땅을 떠남'),
                (-.86, '짧은 준비 구간', '위 스매시', TEAL, '준비 구간에 입력이 들어옴')]
        for y, title, result, color, sub in rows:
            self.add(ko(title, 35, WHITE).move_to([-4.82, y, 0]),
                     Line([left, y, 0], [right, y, 0], color=GRID, stroke_width=10),
                     Line([px(press), y, 0], [px(attack), y, 0], color=color, stroke_width=10),
                     ko(sub, 27, MUTED).move_to([px(.46), y - .35, 0]))
            output = ko(result, 34, color).move_to([4.86, y + .3, 0])
            output.add_updater(lambda text: text.set_opacity(1 if time.get_value() >= attack else .16))
            self.add(output)
        self.add(always_redraw(lambda: Line([px(time.get_value()), -1.54, 0],
                                            [px(time.get_value()), 1.63, 0], color=WHITE, stroke_width=4)),
                 ko('스틱 위로 점프하는 설정을 예로 든 입력 판정', 35, YELLOW).move_to([0, -2.41, 0]))
        self.wait(.6)
        self.play(time.animate.set_value(1), run_time=7.6, rate_func=linear)
        self.wait(1.8)


class InitialLift(Scene):
    def construct(self):
        header(self, 'Initial Jump Velocity (점프 초기 속도)')
        time = ValueTracker(0)
        base, gravity = 2.6, 2.3
        apex = base**2 / (2 * gravity)
        early_time, blend_velocity = .37, 1.25
        blend_height = apex - blend_velocity**2 / (2 * gravity)
        initial = 2 * blend_height / early_time - blend_velocity
        early_gravity = (initial - blend_velocity) / early_time

        def height(t, fast):
            if not fast:
                return max(0, base * t - .5 * gravity * t**2)
            if t < early_time:
                return initial * t - .5 * early_gravity * t**2
            elapsed = t - early_time
            return max(0, blend_height + blend_velocity * elapsed - .5 * gravity * elapsed**2)

        floor, scale = -1.58, 2.2
        apex_y = floor + apex * scale
        self.add(Line([-5.95, apex_y, 0], [5.95, apex_y, 0], color=GRID, stroke_width=3),
                 ko('같은 최고 높이', 29, MUTED).move_to([0, apex_y + .26, 0]),
                 Line([-5.95, floor, 0], [5.95, floor, 0], color=MUTED, stroke_width=4),
                 ko('높이를 그대로 두고 지면을 더 빨리 벗어납니다', 36, YELLOW).move_to([0, -2.43, 0]))
        for x, fast, color, title in [(-3.17, False, TEAL, 'A · 일정한 중력'),
                                      (3.17, True, CORAL, 'B · 빠른 이륙과 초반 감속')]:
            self.add(ko(title, 32, color).move_to([x, 2.35, 0]),
                     Line([x, floor, 0], [x, apex_y, 0], color=GRID, stroke_width=7))
            self.add(always_redraw(lambda x=x, fast=fast, color=color: Dot(
                [x, floor + height(time.get_value(), fast) * scale, 0], radius=.17, color=color)))
        self.wait(.7)
        self.play(time.animate.set_value(2.3), run_time=8.6, rate_func=linear)
        self.wait(.7)


class PiledriverTempo(Scene):
    def construct(self):
        header(self, 'Descent Timing (하강 시간)')
        time = ValueTracker(0)
        for x, color, title, fall in [(-3.35, TEAL, 'A · 완만한 하강', 3.25),
                                       (3.35, CORAL, 'B · 짧은 하강', 1.15)]:
            ground, high = -1.74, 1.36
            self.add(ko(title, 37, color).move_to([x, 2.12, 0]),
                     Line([x-2.75, ground, 0], [x+2.75, ground, 0], color=MUTED, stroke_width=5),
                     Line([x-1.28, high, 0], [x+1.28, high, 0], color=GRID, stroke_width=3),
                     Line([x, ground, 0], [x, high, 0], color=GRID, stroke_width=5))

            def height(t, descent=fall):
                if t <= 3:
                    return 1 - (1 - t / 3) ** 2
                return max(0, 1 - ((t - 3) / descent) ** 2)

            self.add(always_redraw(lambda x=x, pigment=color, fraction=height:
                     Dot([x, ground + (high - ground) * fraction(time.get_value()), 0], radius=.17, color=pigment)))
            marker = ko('바닥에 닿음', 31, color).move_to([x, ground + .35, 0])
            marker.add_updater(lambda text, end=3+fall: text.set_opacity(1 if time.get_value() >= end else 0))
            self.add(marker)
        self.add(ko('같은 경로에서 하강에 쓰는 시간만 줄임', 37, YELLOW).move_to([0, -2.45, 0]))
        self.wait(.6)
        self.play(time.animate.set_value(6.5), run_time=8.7, rate_func=linear)
        self.wait(.7)


class CommittedJump(Scene):
    def construct(self):
        header(self, 'Committed Jump (방향 고정 점프)')
        time = ValueTracker(0)
        floor = -1.4
        self.add(Line([-5.9, floor, 0], [-.1, floor, 0], color=MUTED, stroke_width=4),
                 Line([1.65, floor, 0], [5.9, floor, 0], color=MUTED, stroke_width=4),
                 Dot([-3.35, floor, 0], radius=.11, color=YELLOW),
                 ko('착지 지점', 32, YELLOW).move_to([-3.35, floor-.43, 0]),
                 ko('뒤로 뛰면서 앞을 공격', 41, WHITE).move_to([0, 2.27, 0]))

        def pose(t):
            x = -.45 - 2.9 * t
            return np.array([x, floor + .22 + 5.75 * t * (1 - t), 0])

        def attack():
            t = time.get_value()
            if t < .24:
                return VGroup()
            start = pose(.24) + RIGHT * ((t - .24) * 7.2 + .26)
            return Arrow(start, start + RIGHT * .68, buff=0, color=CORAL, stroke_width=6)

        self.add(always_redraw(lambda: Dot(pose(time.get_value()), radius=.17, color=TEAL)), always_redraw(attack),
                 Arrow([-.58, -.71, 0], [-2.12, -.71, 0], buff=0, color=TEAL, stroke_width=5),
                 ko('점프 방향', 29, TEAL).move_to([-2.2, .56, 0]),
                 ko('공격 방향', 29, CORAL).move_to([2.52, .45, 0]),
                 ko('뛰기 전에 착지할 곳을 고릅니다', 38, YELLOW).move_to([0, -2.47, 0]))
        self.wait(.5)
        self.play(time.animate.set_value(1), run_time=7.7, rate_func=linear)
        self.wait(1.8)

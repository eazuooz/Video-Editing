from manim import Circle, Create, PINK, Scene


class Example(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
        self.play(circle.animate.set_fill(PINK, opacity=0.5))

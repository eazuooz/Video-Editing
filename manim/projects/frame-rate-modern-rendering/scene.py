from manim import DOWN, FadeIn, FadeOut, Scene, Text


class MainScene(Scene):
    def construct(self):
        title = Text("게임의 프레임 레이트는 무엇일까? 30 FPS부터 DLSS까지", font_size=56)
        subtitle = Text("What Is Frame Rate in Games? From 30 FPS to DLSS", font_size=28).next_to(title, DOWN)

        self.play(FadeIn(title), FadeIn(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

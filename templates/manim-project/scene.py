from manim import DOWN, FadeIn, FadeOut, Scene, Text


class MainScene(Scene):
    def construct(self):
        title = Text("{{TITLE_KO}}", font_size=56)
        subtitle = Text("{{TITLE_EN}}", font_size=28).next_to(title, DOWN)

        self.play(FadeIn(title), FadeIn(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

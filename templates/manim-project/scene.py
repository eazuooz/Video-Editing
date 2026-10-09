from manim import BLACK, DOWN, FadeIn, FadeOut, Scene, Text


class MainScene(Scene):
    def construct(self):
        # New productions: research-black-v1. Preserve existing copied scenes.
        self.camera.background_color = BLACK
        title = Text("{{TITLE_KO}}", font="Malgun Gothic", font_size=48, color="#e8cf83")
        subtitle = Text("{{TITLE_EN}}", font="Segoe UI", font_size=28, color="#f5f5f5").next_to(title, DOWN)

        self.play(FadeIn(title), FadeIn(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

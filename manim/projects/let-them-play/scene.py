from manim import DOWN, FadeIn, FadeOut, Scene, Text, WHITE


class MainScene(Scene):
    def construct(self):
        # docs/VIDEO_VISUAL_STYLE.md: white, neutral ink, blue data marks.
        self.camera.background_color = WHITE
        title = Text("설명은 나중에, 일단 플레이! 게임의 첫 3분을 설계하는 법", font="Malgun Gothic", font_size=48, color="#202020")
        subtitle = Text("Let Them Play: Designing the First Three Minutes", font="Segoe UI", font_size=28, color="#737373").next_to(title, DOWN)

        self.play(FadeIn(title), FadeIn(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

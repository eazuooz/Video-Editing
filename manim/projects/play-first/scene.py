from manim import DOWN, FadeIn, FadeOut, Scene, Text, WHITE


class MainScene(Scene):
    def construct(self):
        # docs/VIDEO_VISUAL_STYLE.md: white, neutral ink, blue data marks.
        self.camera.background_color = WHITE
        title = Text("스타트를 눌렀으면 놀게 해 주세요 | 첫 3분 게임 디자인", font="Malgun Gothic", font_size=48, color="#202020")
        subtitle = Text("Just Let Them Play | Designing a Game's First 3 Minutes", font="Segoe UI", font_size=28, color="#737373").next_to(title, DOWN)

        self.play(FadeIn(title), FadeIn(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

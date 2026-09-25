from manim import DOWN, FadeIn, FadeOut, Scene, Text, WHITE


class MainScene(Scene):
    def construct(self):
        # docs/VIDEO_VISUAL_STYLE.md: white, neutral ink, blue data marks.
        self.camera.background_color = WHITE
        title = Text("그래픽은 멋진데, 왜 플레이하기 불편할까? | 시야와 화면 설계", font="Malgun Gothic", font_size=48, color="#202020")
        subtitle = Text("Why Great Graphics Can Still Be Hard to Play | View and Screen Design", font="Segoe UI", font_size=28, color="#737373").next_to(title, DOWN)

        self.play(FadeIn(title), FadeIn(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

from manim import DOWN, FadeIn, FadeOut, Scene, Text, WHITE


class MainScene(Scene):
    def construct(self):
        # docs/VIDEO_VISUAL_STYLE.md: white, neutral ink, blue data marks.
        self.camera.background_color = WHITE
        title = Text("게임 기획서 정리: 계층형 아웃라인으로 생각을 묶는 법", font="Malgun Gothic", font_size=48, color="#202020")
        subtitle = Text("Organizing Game Design Ideas with Hierarchical Outlines", font="Segoe UI", font_size=28, color="#737373").next_to(title, DOWN)

        self.play(FadeIn(title), FadeIn(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

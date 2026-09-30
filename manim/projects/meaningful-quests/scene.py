from manim import DOWN, FadeIn, FadeOut, Scene, Text, WHITE


class MainScene(Scene):
    def construct(self):
        # docs/VIDEO_VISUAL_STYLE.md: white, neutral ink, blue data marks.
        self.camera.background_color = WHITE
        title = Text("심부름 퀘스트는 왜 지루할까? | 재미있는 퀘스트 디자인", font="Malgun Gothic", font_size=48, color="#202020")
        subtitle = Text("Why Are Fetch Quests Boring? | Designing Meaningful Quests", font="Segoe UI", font_size=28, color="#737373").next_to(title, DOWN)

        self.play(FadeIn(title), FadeIn(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

from manim import DOWN, FadeIn, FadeOut, Scene, Text, WHITE


class MainScene(Scene):
    def construct(self):
        # docs/VIDEO_VISUAL_STYLE.md: white, neutral ink, blue data marks.
        self.camera.background_color = WHITE
        title = Text("GPT 아스트라로 무엇을 만들었을까? | 제작 사례 8선", font="Malgun Gothic", font_size=48, color="#202020")
        subtitle = Text("What Did Creators Build with GPT Astra? | 8 Showcases", font="Segoe UI", font_size=28, color="#737373").next_to(title, DOWN)

        self.play(FadeIn(title), FadeIn(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

from manim import DOWN, FadeIn, FadeOut, Scene, Text, WHITE


class MainScene(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        title = Text("AI 시대, 컴공생은 무엇을 공부해야 할까?", font="Malgun Gothic", font_size=44, color="#202020")
        subtitle = Text("What Should CS Students Learn in the AI Era?", font="Segoe UI", font_size=28, color="#737373").next_to(title, DOWN)

        self.play(FadeIn(title), FadeIn(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

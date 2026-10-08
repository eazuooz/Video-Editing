"""Depth-episode overview using the existing projected mathematical diagrams.

Only this episode imports the overrides; delivered point-to-pixel scenes retain
their original module and rendering behavior.
"""
import camera_projection as base

original_diagram = base.raw_diagram


class DepthComparisonScene(base.CameraProjectionScene):
    """Hide the previous depth formula before changing its matching graph."""

    def construct(self):
        self.camera.background_color = base.WHITE
        data = base.json.loads((base.ROOT / f'production/batches/game-math-part2-full-series/lessons/{self.slug}.json').read_text(encoding='utf8'))
        scene = next(s for s in data['scenes'] if s['id'] == self.sid)
        slot = next(s for s in base.timing(self.slug, data)['scenes'] if s['id'] == self.sid)
        assert scene['mode'] == 'depth'
        episode = data.get('episodeSubtitle', '렌더링4편').split(' · ')[0]
        title = base.fit(base.txt(scene['title'], 39), 12.5).to_corner(base.UL, buff=.58)
        subtitle = base.fit(base.txt(f'게임수학 Part 2 / {episode} · LH 행벡터 / 앞+z / 깊이[0,1] / 화면 왼쪽 위', 20, base.MUTED), 12.5).next_to(title, base.DOWN, aligned_edge=base.LEFT, buff=.14)
        self.add(title, subtitle, base.Line([-6.5, 2.32, 0], [6.5, 2.32, 0], color=base.RULE, stroke_width=1))
        graph = base.diagram('depth', 0, len(scene['beats']))
        self.add(graph, base.fit(base.txt('그림의 비스듬한 시점은 설명용 / 실제 게임의 내부 값은 추정하지 않음', 21, base.MUTED), 12.3).move_to([0, -2.25, 0]))
        active = formula = None
        for index, beat in enumerate(scene['beats']):
            start = slot['lineStarts'][index]
            if start > self.renderer.time + 1 / 60:
                self.wait(start - self.renderer.time, frozen_frame=True)
            if active is not None:
                self.play(base.FadeOut(active), base.FadeOut(formula), run_time=.10)
                self.remove(active, formula)
                self.play(base.Transform(graph, base.diagram('depth', index, len(scene['beats']))), run_time=.65)
            else:
                self.play(base.Indicate(graph, color=base.GOLD, scale_factor=1.015), run_time=.55)
            wrapped = '\n'.join(base.textwrap.wrap(beat, width=26, break_long_words=False, break_on_hyphens=False))
            active = base.card(wrapped, width=6.15, size=25, color=base.GREEN if index == len(scene['beats']) - 1 else base.BLUE).move_to([3.12, 1.65, 0])
            formula = base.right_panel(scene, index)
            self.play(base.FadeIn(active, shift=.04 * base.UP), base.FadeIn(formula, shift=.04 * base.UP), run_time=.20)
        if slot['seconds'] > self.renderer.time:
            self.wait(slot['seconds'] - self.renderer.time, frozen_frame=True)


def depth_episode_diagram(mode, index):
    if mode == 'overview':
        if index == 0:
            return base.depth_chart(False, 4)
        if index == 1:
            return base.depth_chart(False, 6)
        if index == 2:
            return base.interpolation(4)
        return base.compact_pipeline(4)
    if mode == 'summary' and index == 3:
        return base.interpolation(4)
    return original_diagram(mode, index)


def make_scenes(slug, module):
    assert slug == 'game-math-projection-depth'
    base.raw_diagram = depth_episode_diagram
    base.LAYOUT.clear()
    scenes = base.make_scenes(slug, module)
    scenes['Scene02'] = type('Scene02', (DepthComparisonScene,), {'slug': slug, 'sid': '02', '__module__': module})
    return scenes

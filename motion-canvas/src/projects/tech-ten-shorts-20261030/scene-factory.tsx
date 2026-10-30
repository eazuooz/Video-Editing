import {Circle, Img, Line, Node, Rect, Txt, makeScene2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';
import {DARK} from '../../styles/research-dark';
import {clamp, Config, frameSource, markGeometry, markVisibleInFrame, Point, smooth, Timing, validate} from './model';
import {eudDiagram, gridDiagram, replayDiagram} from './diagrams';

const C = DARK, FONT = 'Malgun Gothic';

/** Exact native capture/actual footage compositor, with explicit 2D mechanism exceptions. */
export function createTechScene(timing: Timing, config: Config) {
  validate(timing, config);
  return makeScene2D(function* (view) {
    view.fill(C.background);
    const time = createSignal(0);
    const frame = () => Math.min(timing.frames - 1, Math.floor(time() * 60 + .0001));
    const section = () => timing.sections.find(s => frame() >= s.startFrame && frame() < s.endFrame) ?? timing.sections[timing.sections.length - 1];
    const elapsed = () => time() - section().start;
    const phase = () => clamp(elapsed() / Math.max(1 / 60, section().end - section().start));
    const event = (name: string, defaults: [number, number]) => {
      const key = timing.events?.[section().id + ':' + name] ?? timing.events?.[name];
      return key ? smooth((frame() - key.startFrame) / Math.max(1, key.endFrame - key.startFrame))
        : smooth((phase() - defaults[0]) / (defaults[1] - defaults[0]));
    };
    const native = () => section().kind === 'unity';
    const game = () => section().kind === 'game';
    const diagram = () => section().kind === 'diagram';
    const type = () => section().diagramType ?? config.diagramType;
    const firstExplanation = timing.sections.find(s => s.kind !== 'game');
    const definitionEvent = timing.events?.['term-definition'] ?? (firstExplanation ? {
      startFrame: firstExplanation.startFrame,
      endFrame: Math.min(firstExplanation.endFrame, firstExplanation.startFrame + 270),
    } : undefined);
    const definition = () => definitionEvent && frame() >= definitionEvent.startFrame && frame() < definitionEvent.endFrame ? 1 : 0;
    view.add(<Txt text={() => game() ? config.game : config.term} position={[-462, -482]} offset={[-1, 0]}
      fill={() => game() ? C.ink : C.teal} fontFamily={FONT} fontSize={29} fontWeight={700}/>);
    view.add(<Txt text={() => game() ? '실제 게임 녹화' : native() ? 'Unity 자체 구현' : '원리 도식'}
      position={[464, -482]} offset={[1, 0]} fill={C.muted} fontFamily={FONT} fontSize={25}/>);

    // Frame sources are the real inspected/native assets. Never synthesize a
    // Unity label over a canvas substitute or stretch aspect ratios to portrait.
    const panel = new Rect({size: [1000, 800], position: [0, -70], clip: true, opacity: () => diagram() ? 0 : definition() ? .22 : 1});
    view.add(panel);
    const sourceSize = (): Point => [section().width ?? (native() ? 1080 : 1920), section().height ?? 1080];
    const scale = () => section().crop ? 1000 / section().crop!.width : Math.min(1000 / sourceSize()[0], 800 / sourceSize()[1]);
    const cropCenter = (): Point => section().crop?.center ?? [sourceSize()[0] / 2, sourceSize()[1] / 2];
    const map = (p: Point): Point => [(p[0] - cropCenter()[0]) * scale(), (p[1] - cropCenter()[1]) * scale()];
    panel.add(<Img src={() => diagram() ? frameSource(timing.sections[0], 0, config.frameRoot) : frameSource(section(), frame(), config.frameRoot)}
      size={() => [sourceSize()[0] * scale(), sourceSize()[1] * scale()]}
      position={() => map([sourceSize()[0] / 2, sourceSize()[1] / 2])}/>);
    const mark = () => (timing.annotations ?? config.annotations)?.[section().id]?.find(m => markVisibleInFrame(m, elapsed(), section()));
    const geometry = () => markGeometry(mark(), elapsed());
    const markOpacity = () => mark() ? smooth((elapsed() - mark()!.start) / .16) * smooth((mark()!.end - elapsed()) / .12) : 0;
    const markColor = () => mark()?.role === 'problem' ? C.red : mark()?.role === 'result' ? C.green : C.teal;
    panel.add(<Rect position={() => map(geometry().center)} size={() => [geometry().size[0] * scale(), geometry().size[1] * scale()]}
      stroke={markColor} lineWidth={7} radius={10} opacity={() => markOpacity() * (mark()?.kind === 'ellipse' || mark()?.kind === 'arrow' ? 0 : 1)}/>);
    panel.add(<Circle position={() => map(geometry().center)} size={() => [geometry().size[0] * scale(), geometry().size[1] * scale()]}
      stroke={markColor} lineWidth={7} opacity={() => markOpacity() * (mark()?.kind === 'ellipse' ? 1 : 0)}/>);
    panel.add(<Line points={() => {const p = map(geometry().center); return [[p[0] - geometry().size[0] * scale(), p[1] - geometry().size[1] * scale()], p];}}
      stroke={markColor} lineWidth={7} endArrow arrowSize={19} opacity={() => markOpacity() * (mark()?.kind === 'arrow' ? 1 : 0)}/>);
    panel.add(<Rect position={() => {const g = geometry(); if (g.labelCenter) return map(g.labelCenter);
      const p = map(g.center); return [p[0], p[1] + g.size[1] * scale() / 2 + 35];}}
      fill={C.background} size={[420, 52]} radius={8} opacity={markOpacity}>
      <Txt text={() => mark()?.label ?? ''} fill={markColor} fontFamily={FONT} fontSize={29} fontWeight={700}/>
    </Rect>);
    for (const kind of ['grid', 'eud', 'replay'] as const) {
      const stage = new Node({position: [0, -35], opacity: () => diagram() && type() === kind ? definition() ? .22 : 1 : 0});
      view.add(stage); ({grid: gridDiagram, eud: eudDiagram, replay: replayDiagram}[kind])(stage, {section, phase, elapsed, event});
    }

    // The brief definition stays in the existing world and collapses into the
    // upper-left term label; it does not reset the lesson with a slide.
    view.add(<Rect position={[0, -70]} size={[930, 230]} radius={12} fill="#080b0a" opacity={() => definition() * .96}>
      <Txt text={config.english} position={[0, -68]} fill={C.teal} fontFamily={FONT} fontSize={31} fontWeight={700}/>
      <Txt text={config.term} position={[0, 0]} fill={C.ink} fontFamily={FONT} fontSize={36} fontWeight={700}/>
      <Txt text={config.plainMeaning ?? ''} position={[0, 68]} fill={C.title} fontFamily={FONT} fontSize={29}/>
    </Rect>);
    // Narration-linked object step list, only when authored for the current scene.
    for (let i = 0; i < 3; i++) view.add(<Txt text={() => section().steps?.[i] ?? ''}
      position={[-448, 196 + i * 38]} offset={[-1, 0]} opacity={() => section().steps?.[i] && !diagram() ? 1 : 0}
      fill={() => section().activeStep === i ? C.title : C.muted} fontFamily={FONT} fontSize={28} fontWeight={700}/>);
    const reactions = timing.reactions ?? config.catReactions ?? [];
    const reaction = () => reactions.find(r => time() >= r.start && time() < r.end);
    const catOpacity = () => {const r = reaction(); return r ? smooth((time() - r.start) / .18) * smooth((r.end - time()) / .2) : 0;};
    const cat = new Rect({size: [460, 560], position: [290, 640], clip: true, opacity: catOpacity});
    view.add(cat);
    cat.add(<Img src={() => reaction()?.kind === 'relief' ? relief : realize} size={560}
      position={() => [55 + 24 * (1 - catOpacity()), 0]}/>);
    yield view.toPromise();
    yield* time(timing.frames / 60, timing.frames / 60, linear);
  });
}

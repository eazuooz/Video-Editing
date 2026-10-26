import {Circle, Img, Line, Node, Rect, Txt, makeScene2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import puzzled from '../../../../shared/assets/branding/cat-reactions-v1/puzzled.png';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';
import {DARK as C} from '../../styles/research-dark';
import {imageUrl, requireProductionInput, type Label, type Point, type Production, type SectionId} from './production-input';

const FONT = 'Malgun Gothic';
const clamp = (value: number, low = 0, high = 1) => Math.min(high, Math.max(low, value));
const smooth = (value: number) => {const t = clamp(value); return t * t * (3 - 2 * t);};
const xy = (x: number, y: number): Point => [x - 540, y - 960];
const colors: Record<string, string> = {concept: C.teal, result: C.green, changed: C.title, problem: C.red, caution: C.red, secondary: C.muted};
const cats = {puzzled, realize, relief};
const titles: Record<SectionId, string> = {
  game: '반짝임은 어디까지 강해도 될까?',
  pbs: '빛과 재질의 반응을 계산',
  boundary: '어두운 잉크에서 색 경계가 흐려진다',
  flat: '명암을 없애면, 지형의 모양도 흐려진다',
  specular: '광택과 작은 잠수 흔적의 경쟁',
  close: '세 가지 정보가 함께 보여야 한다',
};

/**
 * 1080x1920. Finishing owns header0..440 and fixed captions1290..1470.
 * Native-aspect hero stays in y620..1183. No source lines or duplicate brand.
 * Bottom-right reaction crop stays below1478; face/hands cannot cover the hero,
 * canonical terms or fixed captions. Actual375px moving QA is still required.
 */
export default makeScene2D(function* (view) {
  const {config, timing, readback, gameEndFrame}: Production = yield requireProductionInput();
  view.fill(C.background);
  const time = createSignal(0);
  const frame = () => Math.min(timing.frames - 1, Math.floor(time() * 60 + 0.0001));
  const section = () => timing.sections.find(s => frame() >= s.startFrame && frame() < s.endFrame)!;
  const id = () => section().visualId ?? section().id;
  const actualGame = () => frame() < gameEndFrame;
  const record = () => {
    if (actualGame()) return undefined;
    const result = readback.get(frame());
    if (!result) throw new Error(`Missing actual Unity readback at frame ${frame()}`);
    return result;
  };
  const cut = () => config.game.cuts.find(c => frame() >= c.startFrame && frame() < c.endFrame);
  const picture = () => {
    const width = actualGame() ? config.game.width : config.unity.width;
    const height = actualGame() ? config.game.height : config.unity.height;
    const scale = Math.min(1000 / width, 562.5 / height);
    return {left: (1080 - width * scale) / 2, top: 620, width: width * scale, height: height * scale};
  };
  const picturePosition = (): Point => {
    const p = picture(); return xy(p.left + p.width / 2, p.top + p.height / 2);
  };
  const inCue = (first: string, last = first) => frame() >= timing.events[first].startFrame && frame() < timing.events[last].endFrame;
  // Define specular first, then collapse before p5-2 changes its strength.
  // The actual A/B transition must remain at full picture opacity.
  const definition = () => !actualGame() && (inCue('p2-4', 'p2-5') ? 'pbs' : inCue('p5-1') ? 'specular' : undefined);
  const canonical = () => frame() >= timing.events['p5-1'].startFrame ? 'specular'
    : frame() >= timing.events['p2-4'].startFrame ? 'pbs' : 'ink';
  const titleColor = () => ['boundary', 'flat'].includes(id()) ? C.red : C.title;

  view.add(<Txt text={() => actualGame() ? '스플래툰 3 · Splatoon 3'
    : canonical() === 'specular' ? '정반사 · Specular reflection'
    : canonical() === 'pbs' ? '물리 기반 셰이딩 · PBS' : '잉크의 명암과 광택'}
    position={xy(60, 468)} offset={[-1, 0]} fontFamily={FONT} fontSize={28} fontWeight={700} fill={C.teal}/>);
  view.add(<Txt text={() => actualGame() ? '실제 게임 녹화' : '우리 Unity 모형'}
    position={xy(1020, 468)} offset={[1, 0]} fontFamily={FONT} fontSize={26} fill={C.muted}/>);
  view.add(<Txt text={() => actualGame() ? '반짝이는 표면 · 캐릭터의 잠수'
    : frame() >= timing.events['p1-3'].startFrame ? '개발 사례: 스플래툰 2 · 2017' : '같은 현상을 설명하는 모형'}
    position={xy(60, 510)} offset={[-1, 0]} fontFamily={FONT} fontSize={27} fill={C.muted}/>);
  view.add(<Txt text={() => titles[id()]} position={xy(540, 565)} fontFamily={FONT}
    fontSize={36} fontWeight={700} fill={titleColor}/>);

  // One image node: hidden Unity nodes never request non-existent pre-intro
  // frames. There is no image-index clamp, loop, freeze or default stock frame.
  view.add(<Img src={() => {
    if (actualGame()) {
      const c = cut();
      if (!c) throw new Error(`Missing native gameplay cut at ${frame()}`);
      return imageUrl(c.frameDirectory, c.pattern, c.digits, c.firstFrame + frame() - c.startFrame);
    }
    return imageUrl(config.unity.frameDirectory, config.unity.pattern, config.unity.digits, frame());
  }} position={picturePosition} size={() => [picture().width, picture().height]}
    opacity={() => definition() ? 0.22 : 1}/>);

  const definitionCard = new Node({opacity: () => definition() ? 1 : 0});
  view.add(definitionCard);
  definitionCard.add(<Txt text={() => definition() === 'pbs' ? 'Physically Based Shading · PBS' : 'Specular reflection'}
    position={xy(540, 735)} fill={C.title} fontFamily={FONT} fontSize={34} fontWeight={700}/>);
  definitionCard.add(<Txt text={() => definition() === 'pbs' ? '물리 기반 셰이딩' : '정반사'}
    position={xy(540, 795)} fill={C.ink} fontFamily={FONT} fontSize={39} fontWeight={700}/>);
  definitionCard.add(<Txt text={() => definition() === 'pbs' ? '빛과 재질의 반응을 물리 원리로 근사' : '반사된 빛이 만드는 밝은 광택'}
    position={xy(540, 857)} fill={C.ink} fontFamily={FONT} fontSize={32}/>);

  const labels = () => !actualGame() && !definition() ? record()!.labelRequests.filter(label =>
    label.inFrontAndInFrame && label.targetActive && !config.hiddenLabels?.some(hidden => hidden.id === label.id &&
      frame() >= hidden.startFrame && frame() < hidden.endFrame)) : [];
  const targetPoint = (label: Label): Point => {
    const p = picture(); return xy(p.left + label.u * p.width, p.top + label.v * p.height);
  };
  const bubblePoint = (label: Label): Point => {
    const p = picture();
    const x = clamp(p.left + label.u * p.width + (label.u < 0.5 ? -80 : 80), 200, 880);
    // Actual full-capture droplets extend above the ring; keep their small
    // silhouettes clear while the leader still ends at the recorded ring.
    const offsetY = label.target === 'splash' ? -120 : label.v < 0.3 ? 65 : -65;
    const y = clamp(p.top + label.v * p.height + offsetY, 662, 1135);
    return xy(x, y);
  };
  for (let index = 0; index < 3; index++) {
    const label = () => labels()[index];
    const color = () => colors[label()?.role ?? 'concept'] ?? C.teal;
    const overlay = new Node({opacity: () => label() ? 1 : 0});
    view.add(overlay);
    overlay.add(<Line points={() => label() ? [bubblePoint(label()), targetPoint(label())] : [[0, 0], [0, 0]]}
      stroke={color} lineWidth={5} endArrow arrowSize={13}/>);
    overlay.add(<Circle position={() => label() ? targetPoint(label()) : [0, 0]} size={31}
      stroke={color} lineWidth={5}/>);
    overlay.add(<Rect position={() => label() ? bubblePoint(label()) : [0, 0]} size={[285, 54]}
      fill="#000000e8" radius={7} stroke={color} lineWidth={2}/>);
    overlay.add(<Txt text={() => label()?.textKo ?? ''} position={() => label() ? bubblePoint(label()) : [0, 0]}
      fill={C.ink} fontFamily={FONT} fontSize={29} fontWeight={700}/>);
  }

  const focus = () => {
    const keys = cut()?.focus;
    const window = cut()?.focusWindow;
    if (!window || frame() < window.startFrame || frame() >= window.endFrame) return undefined;
    if (!actualGame() || !keys?.length || frame() < keys[0].frame || frame() > keys[keys.length - 1].frame) return undefined;
    const after = keys.findIndex(key => key.frame >= frame());
    if (after <= 0) return keys[0];
    const a = keys[after - 1], b = keys[after], t = (frame() - a.frame) / (b.frame - a.frame);
    return {x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t,
      radiusX: a.radiusX + (b.radiusX - a.radiusX) * t, radiusY: a.radiusY + (b.radiusY - a.radiusY) * t};
  };
  const focusPosition = (): Point => {
    const f = focus(), p = picture(); return f ? xy(p.left + f.x / 1920 * p.width, p.top + f.y / 1080 * p.height) : [0, 0];
  };
  const focusSize = (): Point => {const f = focus(), p = picture(); return f ? [f.radiusX * 2 / 1920 * p.width, f.radiusY * 2 / 1080 * p.height] : [1, 1];};
  view.add(<Circle position={focusPosition} size={focusSize} stroke="#000000" lineWidth={11} opacity={() => focus() ? 1 : 0}/>);
  view.add(<Circle position={focusPosition} size={focusSize}
    stroke={C.green} lineWidth={6} opacity={() => focus() ? 1 : 0}/>);

  // These are read from the actual controller capture trace, never fabricated
  // Nintendo coefficients, measurements of visibility or performance numbers.
  view.add(<Txt text="우리 모형의 값" position={xy(65, 1222)} offset={[-1, 0]}
    fill={C.muted} fontFamily={FONT} fontSize={26} opacity={() => actualGame() || definition() ? 0 : 1}/>);
  view.add(<Txt text={() => {
    const r = record(); return r ? `명암 ${r.appliedState.shadingStrength.toFixed(2)}  ·  정반사 ${r.appliedState.specularStrength.toFixed(2)}` : '';
  }} position={xy(1020, 1222)} offset={[1, 0]} fill={C.title} fontFamily={FONT} fontSize={31} fontWeight={700}
    opacity={() => definition() ? 0 : 1}/>);
  view.add(<Txt text={() => actualGame() ? '빛나는 표면과 잠수 동작을 함께 보기' : '같은 바닥·벽·빛·카메라'}
    position={xy(65, 1260)} offset={[-1, 0]} fill={C.muted} fontFamily={FONT} fontSize={25}/>);

  // No node draws into the fixed caption band1290..1470.
  for (let i = 0; i < 3; i++) {
    const active = () => (id() === 'close'
      ? frame() >= timing.events['p6-5'].startFrame ? 2 : frame() >= timing.events['p6-4'].startFrame ? 1 : 0
      : record()?.activeStep) === i;
    view.add(<Txt text={() => {
      const step = record()?.steps[i]; return step ? `${i + 1}  ${step}` : '';
    }} position={xy(75, 1535 + i * 59)} offset={[-1, 0]} fontFamily={FONT} fontSize={33}
      fontWeight={700} fill={() => active() ? C.title : C.muted}/>);
    view.add(<Line points={[xy(75, 1560 + i * 59), xy(470, 1560 + i * 59)]}
      stroke={C.title} lineWidth={4} opacity={() => active() && Boolean(record()?.steps[i]) ? 1 : 0}/>);
  }

  const reactions = [
    {cue: 'p1-4-b', kind: 'puzzled' as const},
    {cue: 'p5-4', kind: 'realize' as const},
    {cue: 'p6-7', kind: 'relief' as const},
  ];
  const reaction = () => reactions.find(r => frame() >= timing.events[r.cue].startFrame &&
    frame() < Math.min(timing.events[r.cue].endFrame, timing.events[r.cue].startFrame + 138));
  const catOpacity = () => {
    const r = reaction();
    if (!r) return 0;
    const first = timing.events[r.cue].startFrame, last = Math.min(timing.events[r.cue].endFrame, first + 138);
    return smooth((frame() - first) / 9) * smooth((last - frame()) / 10);
  };
  const cat = new Rect({size: [460, 410], position: xy(830, 1695), clip: true, opacity: catOpacity});
  view.add(cat);
  cat.add(<Img src={() => cats[reaction()?.kind ?? 'realize']} size={650} position={[0, -20]}/>);

  yield view.toPromise();
  yield* time(timing.frames / 60, timing.frames / 60, linear);
});

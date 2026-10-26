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
  game: '광택이 강하면, 잠수 흔적은?',
  pbs: '빛과 재질을 함께 계산',
  boundary: '어두워진 두 팀의 색 경계',
  flat: '명암 켬 → 끔: 벽과 바닥은?',
  specular: '광택만 강하게: 물방울은 그대로',
  close: '색 경계 · 지형 · 잠수 흔적',
};

/**
 * 1080x1920. Finishing owns header0..440 and fixed captions1290..1470.
 * Native gameplay is unchanged. Unity is uniformly enlarged 1.16x; only its
 * empty black margins are clipped in y620..1220. Source camera is unchanged.
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
    if (!actualGame()) return {left: -40, top: 580, width: 1160, height: 652.5};
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
  const unityUrl = (n: number) => imageUrl(config.unity.frameDirectory, config.unity.pattern, config.unity.digits, n);
  // Reference crops use inspected, completed capture frames. Both members of
  // each pair have identical submerge phase; only the named parameter differs.
  const references = {
    shading: [timing.sections.find(s => s.id === 'flat')!.startFrame, timing.events['p4-1'].endFrame],
    specular: [timing.events['p1-4'].startFrame - 1, timing.events['p1-4-b'].endFrame],
  } as const;
  for (const [kind, pair] of Object.entries(references)) {
    const a = readback.get(pair[0])?.appliedState, b = readback.get(pair[1])?.appliedState;
    if (!a || !b || Math.abs(a.submergePhase - b.submergePhase) > 0.00001 ||
      (kind === 'shading' ? Math.abs(a.specularStrength - b.specularStrength) > 0.00001 ||
        Math.abs(a.shadingStrength - 1) > 0.00001 || Math.abs(b.shadingStrength) > 0.00001
        : Math.abs(a.shadingStrength - b.shadingStrength) > 0.00001 ||
          Math.abs(a.specularStrength - 0.3) > 0.00001 || Math.abs(b.specularStrength - 3.5) > 0.00001)) {
      throw new Error(`Clarity comparison requires the actual matched ${kind} capture pair`);
    }
  }
  const comparison = (): 'shading' | 'specular' | undefined => {
    if (actualGame() || definition()) return undefined;
    if (inCue('p1-4-b') || inCue('p5-4') || inCue('p6-5')) return 'specular';
    if (inCue('p4-2', 'p4-4') || inCue('p6-3', 'p6-4')) return 'shading';
    return undefined;
  };

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
  const hero = new Rect({size: [1000, 600], position: xy(540, 920), clip: true});
  view.add(hero);
  hero.add(<Img src={() => {
    if (actualGame()) {
      const c = cut();
      if (!c) throw new Error(`Missing native gameplay cut at ${frame()}`);
      return imageUrl(c.frameDirectory, c.pattern, c.digits, c.firstFrame + frame() - c.startFrame);
    }
    return unityUrl(frame());
  }} position={() => {
    const p = picturePosition(); return [p[0], p[1] + 40];
  }} size={() => [picture().width, picture().height]}
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
    const x = clamp(p.left + label.u * p.width + (label.u < 0.5 ? -125 : 125), 190, 890);
    // Actual full-capture droplets extend above the ring; keep their small
    // silhouettes clear while the leader still ends at the recorded ring.
    const offsetY = label.target === 'splash' ? -145 : label.v < 0.3 ? 75 : -80;
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
    overlay.add(<Rect position={() => label() ? bubblePoint(label()) : [0, 0]} size={[260, 60]}
      fill="#000000e8" radius={7} stroke={color} lineWidth={2}/>);
    overlay.add(<Txt text={() => label() ? ({boundary: '색 경계', join: '벽 ↔ 바닥', splash: '잠수 물방울'}[label().target] ?? label().textKo) : ''}
      position={() => label() ? bubblePoint(label()) : [0, 0]}
      fill={C.ink} fontFamily={FONT} fontSize={34} fontWeight={700}/>);
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
  view.add(<Txt text="같은 바닥·벽·빛·카메라" position={xy(65, 1250)} offset={[-1, 0]}
    fill={C.muted} fontFamily={FONT} fontSize={26} opacity={() => actualGame() || definition() ? 0 : 1}/>);
  view.add(<Txt text={() => {
    const r = record();
    if (!r) return '';
    const {shadingStrength: shade, specularStrength: spec} = r.appliedState;
    if (id() === 'flat') return shade < 0.005 ? '명암 끔' : shade > 0.995 ? '명암 켬' : '명암 줄이는 중';
    if (id() === 'game' || id() === 'specular') return spec < 0.305 ? '광택 약함' : spec > 3.495 ? '광택 강함' : '광택 강해지는 중';
    return id() === 'boundary' ? '어두운 경계에 주목' : id() === 'close' ? '세 가지를 함께' : '빛 + 재질';
  }} position={xy(1020, 1250)} offset={[1, 0]} fill={C.title} fontFamily={FONT} fontSize={36} fontWeight={700}
    opacity={() => definition() ? 0 : 1}/>);
  view.add(<Txt text={() => actualGame() ? '빛나는 표면과 잠수 동작을 함께 보기' : '같은 바닥·벽·빛·카메라'}
    position={xy(65, 1260)} offset={[-1, 0]} fill={C.muted} fontFamily={FONT} fontSize={25}
    opacity={() => actualGame() ? 1 : 0}/>);

  // No node draws into the fixed caption band1290..1470.
  for (let i = 0; i < 3; i++) {
    const active = () => (id() === 'close'
      ? frame() >= timing.events['p6-5'].startFrame ? 2 : frame() >= timing.events['p6-4'].startFrame ? 1 : 0
      : record()?.activeStep) === i;
    view.add(<Txt text={() => {
      const step = record()?.steps[i]; return step ? `${i + 1}  ${step}` : '';
    }} position={xy(75, 1535 + i * 59)} offset={[-1, 0]} fontFamily={FONT} fontSize={33}
      fontWeight={700} fill={() => active() ? C.title : C.muted} opacity={() => comparison() ? 0 : 1}/>);
    view.add(<Line points={[xy(75, 1560 + i * 59), xy(470, 1560 + i * 59)]}
      stroke={C.title} lineWidth={4} opacity={() => !comparison() && active() && Boolean(record()?.steps[i]) ? 1 : 0}/>);
  }

  // Exact still references, clearly separate from the live hero above. The
  // source crop and scale are identical within a pair; no painted highlight,
  // altered brightness, synthetic particles or visibility score is added.
  const compare = new Node({opacity: () => comparison() ? 1 : 0});
  view.add(compare);
  compare.add(<Txt text="같은 순간의 비교 캡처 · 확대" position={xy(540, 1510)}
    fontFamily={FONT} fontSize={28} fill={C.muted}/>);
  for (const side of [0, 1] as const) {
    const center = side === 0 ? 287 : 793;
    const role = side === 0 ? C.teal : C.title;
    compare.add(<Txt text={() => comparison() === 'shading' ? (side === 0 ? '명암 켬' : '명암 끔')
      : (side === 0 ? '광택 약함' : '광택 강함')}
      position={xy(center, 1560)} fontFamily={FONT} fontSize={38} fontWeight={700} fill={role}/>);
    const crop = new Rect({size: [460, 250], position: xy(center, 1720), clip: true,
      stroke: role, lineWidth: 4});
    compare.add(crop);
    const scale = () => 460 / (comparison() === 'shading' ? 600 : 430);
    const cropCenter = (): Point => comparison() === 'shading' ? [1168, 440] : [978, 665];
    crop.add(<Img src={() => unityUrl(references[comparison() ?? 'shading'][side])}
      size={() => [1920 * scale(), 1080 * scale()]}
      position={() => [(960 - cropCenter()[0]) * scale(), (540 - cropCenter()[1]) * scale()]}/>);
    compare.add(<Txt text={() => comparison() === 'shading'
      ? (side === 0 ? '면의 꺾임' : '납작해진 명암') : '물방울은 동일'}
      position={xy(center, 1880)} fontFamily={FONT} fontSize={30} fill={C.ink}/>);
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
    if (!r || comparison()) return 0;
    const first = timing.events[r.cue].startFrame, last = Math.min(timing.events[r.cue].endFrame, first + 138);
    return smooth((frame() - first) / 9) * smooth((last - frame()) / 10);
  };
  const cat = new Rect({size: [460, 410], position: xy(830, 1695), clip: true, opacity: catOpacity});
  view.add(cat);
  cat.add(<Img src={() => cats[reaction()?.kind ?? 'realize']} size={650} position={[0, -20]}/>);

  yield view.toPromise();
  yield* time(timing.frames / 60, timing.frames / 60, linear);
});

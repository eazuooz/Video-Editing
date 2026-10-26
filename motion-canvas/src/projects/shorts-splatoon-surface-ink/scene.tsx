import {makeScene2D, Circle, Img, Line, Node, Rect, Txt} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import puzzled from '../../../../shared/assets/branding/cat-reactions-v1/puzzled.png';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';
import {DARK as C} from '../../styles/research-dark';
import {requireProductionInput} from './production-input';
import {cueProgress, focusAt, sectionAt, smooth, visualAt, type CueId, type Point} from './model';

const FONT = 'Malgun Gothic';
const point = (x: number, y: number): Point => [x - 540, y - 960];
const cats = {puzzled, realize, relief};

/** Composites real source frames and our captured Unity scene; never simulates Nintendo internals. */
export default makeScene2D(function* (view) {
  const {timing, config} = requireProductionInput();
  view.fill(C.background);
  const time = createSignal(0);
  const frame = () => Math.min(timing.frames - 1, Math.floor(time() * 60 + 0.0001));
  const section = () => sectionAt(timing, frame()).id;
  const visual = () => visualAt(timing, config, frame());
  const isGame = () => visual().kind === 'gameplay';
  const inCue = (id: CueId) => frame() >= timing.events[id].startFrame && frame() < timing.events[id].endFrame;
  const after = (id: CueId) => frame() >= timing.events[id].startFrame;
  const anchors = config.compositing.anchors;

  const definition = () => {
    if (inCue('p2-3')) return {
      english: 'Texture', korean: '텍스처', plain: '색을 저장하는 그림', cue: 'p2-3' as CueId,
    };
    if (inCue('p4-2')) return {
      english: 'UV coordinates', korean: 'UV 좌표', plain: '그림 속 가로·세로 주소', cue: 'p4-2' as CueId,
    };
    return undefined;
  };
  const definitionOpacity = () => {
    const d = definition();
    return d ? 1 - smooth((cueProgress(timing, frame(), d.cue) - .60) / .40) : 0;
  };

  // Full captured image is kept at the user-specified 0.6 scale. Blank Unity
  // margins may lie behind header/captions; reviewed meaningful geometry may not.
  view.add(<Img src={() => visual().path}
    size={() => isGame() ? [1000, 562.5] : config.unityImagePlacement.size}
    position={() => isGame() ? point(540, 820) : point(...config.unityImagePlacement.center)}
    opacity={() => isGame() ? 1 : 1 - definitionOpacity() * .72}/>);

  view.add(<Txt text={() => after('p4-2') ? 'UV coordinates · UV 좌표'
    : after('p2-3') ? 'Texture · 텍스처' : '표면에 남는 잉크'}
    position={point(75, 475)} offset={[-1, 0]} fill={C.teal}
    fontFamily={FONT} fontSize={29} fontWeight={700}/>);
  view.add(<Txt text={() => isGame() ? '실제 게임 영상' : '우리 Unity 시연'}
    position={point(1000, 475)} offset={[1, 0]} fill={C.muted}
    fontFamily={FONT} fontSize={28}/>);
  view.add(<Txt text={() => isGame() ? '스플래툰 3' : '공개된 방식의 독립 구현'}
    position={point(1000, 512)} offset={[1, 0]} fill={C.muted}
    fontFamily={FONT} fontSize={24}/>);

  const explanation = new Node({opacity: () => isGame() ? 0 : 1});
  view.add(explanation);
  const card = new Node({opacity: definitionOpacity});
  explanation.add(card);
  card.add(<Txt text={() => definition()?.english ?? ''} position={point(540, 570)}
    fill={C.title} fontFamily={FONT} fontSize={38} fontWeight={700}/>);
  card.add(<Txt text={() => definition()?.korean ?? ''} position={point(540, 620)}
    fill={C.ink} fontFamily={FONT} fontSize={36} fontWeight={700}/>);
  card.add(<Txt text={() => definition()?.plain ?? ''} position={point(540, 674)}
    fill={C.ink} fontFamily={FONT} fontSize={31}/>);

  const labels = new Node({opacity: () => 1 - definitionOpacity()});
  explanation.add(labels);
  const showSheet = () => section() !== 'orbit';
  // Labels remain full-resolution and outside the little capture's meaningful
  // surfaces. These leader lines are editorial guides, not measured game data.
  labels.add(<Txt text={() => section() === 'patch' ? '그림 조각의 경계'
    : after('p2-3') ? '색을 저장하는 텍스처' : '표면에 연결한 색칠 그림'}
    position={point(75, 560)} offset={[-1, 0]} fill={C.title}
    fontFamily={FONT} fontSize={31} fontWeight={700}
    opacity={() => showSheet() && after('p2-1') ? 1 : 0}/>);
  labels.add(<Line points={() => [point(75, 600), point(380, 600), point(...anchors.sheet)]}
    stroke={C.title} lineWidth={4} endArrow arrowSize={12}
    end={() => section() === 'sheet' ? smooth(cueProgress(timing, frame(), 'p2-1', 'p2-2')) : 1}
    opacity={() => showSheet() && after('p2-1') ? 1 : 0}/>);
  labels.add(<Txt text="시연 표면: 벽·바닥" position={point(75, 1135)} offset={[-1, 0]}
    fill={C.ink} fontFamily={FONT} fontSize={31} fontWeight={700}
    opacity={() => showSheet() ? 1 : 0}/>);
  labels.add(<Line points={() => [point(75, 1095), point(340, 1095), point(...anchors.wall)]}
    stroke={C.line} lineWidth={3} endArrow arrowSize={11}
    opacity={() => showSheet() ? 1 : 0}/>);

  const stageIndex = () => section() === 'collision' ? 0 : section() === 'uv' ? 1
    : section() === 'stamp' ? 2 : -1;
  const steps = ['① 충돌 위치', '② UV 주소', '③ 색 기록'];
  const stepColors = [C.red, C.teal, C.green];
  for (let index = 0; index < steps.length; index++) {
    labels.add(<Txt text={steps[index]} position={point(75, 820 + index * 69)} offset={[-1, 0]}
      fill={() => stageIndex() === index ? stepColors[index] : C.muted}
      fontFamily={FONT} fontSize={32} fontWeight={() => stageIndex() === index ? 700 : 400}
      opacity={() => stageIndex() >= 0 ? (stageIndex() === index ? 1 : .58) : 0}/>);
  }
  labels.add(<Line points={() => [point(285, 820), point(350, 820), point(...anchors.impact)]}
    stroke={C.red} lineWidth={5} endArrow arrowSize={13}
    end={() => smooth(cueProgress(timing, frame(), 'p3-1'))}
    opacity={() => section() === 'collision' ? 1 : 0}/>);
  labels.add(<Line points={() => [point(285, 889), point(365, 820), point(...anchors.sheet)]}
    stroke={C.teal} lineWidth={5} endArrow arrowSize={13}
    end={() => smooth(cueProgress(timing, frame(), 'p4-1', 'p4-3'))}
    opacity={() => section() === 'uv' ? 1 : 0}/>);
  labels.add(<Line points={() => [point(285, 958), point(365, 958), point(...anchors.wall)]}
    stroke={C.green} lineWidth={5} endArrow arrowSize={13}
    end={() => smooth(cueProgress(timing, frame(), 'p5-1', 'p5-2'))}
    opacity={() => section() === 'stamp' ? 1 : 0}/>);

  const readout = config.compositing.uvReadout;
  labels.add(<Txt text={() => `U = ${readout.u!.toFixed(1)}\nV = ${readout.v!.toFixed(1)}`}
    position={point(75, 670)} offset={[-1, -1]} fill={C.teal}
    fontFamily={FONT} fontSize={38} fontWeight={700} lineHeight={52}
    opacity={() => section() === 'uv' && after('p4-4') ? 1 : 0}/>);
  labels.add(<Txt text="우리 시연의 가운데 주소" position={point(75, 782)} offset={[-1, 0]}
    fill={C.muted} fontFamily={FONT} fontSize={26}
    opacity={() => section() === 'uv' && after('p4-4') ? 1 : 0}/>);
  labels.add(<Circle position={() => point(...anchors.sheet)} size={23}
    stroke={C.teal} lineWidth={5} fill={C.background}
    opacity={() => section() === 'uv' && after('p4-3') ? 1 : 0}/>);

  labels.add(<Txt text={() => after('p6-2') ? '이웃한 표면까지 연결' : '경계에서 자국이 끊길 수 있다'}
    position={point(75, 690)} offset={[-1, 0]}
    fill={() => after('p6-2') ? C.green : C.red} fontFamily={FONT} fontSize={30} fontWeight={700}
    opacity={() => section() === 'patch' ? 1 : 0}/>);
  labels.add(<Line points={() => [point(75, 735), point(350, 735), point(...anchors.seam)]}
    stroke={() => after('p6-2') ? C.green : C.red} lineWidth={5} endArrow arrowSize={13}
    end={() => smooth(cueProgress(timing, frame(), 'p6-1'))}
    opacity={() => section() === 'patch' ? 1 : 0}/>);
  labels.add(<Txt text={'시점이 바뀌어도\n표면의 색 기록은 그대로'} position={point(75, 1190)} offset={[-1, 0]}
    fill={C.title} fontFamily={FONT} fontSize={32} fontWeight={700} lineHeight={46}
    opacity={() => section() === 'orbit' ? 1 : 0}/>);

  const gameTarget = () => {
    const current = visual();
    if (current.kind !== 'gameplay') return undefined;
    const cut = config.gameplayCuts[current.cut];
    return focusAt(cut.focus ?? [], current.sourceSeconds! - cut.sourceStartSeconds);
  };
  view.add(<Circle position={() => {
    const target = gameTarget();
    return target ? point(540 + (target.x - 960) * 1000 / 1920,
      820 + (target.y - 540) * 1000 / 1920) : [0, 0];
  }} size={() => {
    const target = gameTarget();
    return target ? [target.radiusX * 2000 / 1920, target.radiusY * 2000 / 1920] : [1, 1];
  }} stroke={C.green} lineWidth={7} opacity={() => gameTarget() ? 1 : 0}/>);

  // Exactly three semantic reactions, bound to actual clauses rather than an
  // invented example runtime. Fixed clip matches the approved large cat layout.
  const reaction = () => {
    for (const [cueId, kind] of [['p1-2', 'puzzled'], ['p4-4', 'realize'], ['p7-3', 'relief']] as const) {
      const cue = timing.events[cueId];
      const start = cue.startFrame / 60;
      const end = Math.min(cue.endFrame / 60, start + 2.3);
      if (time() >= start && time() < end) return {kind, start, end};
    }
    return undefined;
  };
  const catOpacity = () => {
    const r = reaction();
    return r ? smooth((time() - r.start) / .16) * smooth((r.end - time()) / .18) : 0;
  };
  const cat = new Rect({size: [460, 560], position: point(830, 1390), clip: true, opacity: catOpacity});
  view.add(cat);
  cat.add(<Img src={() => cats[reaction()?.kind ?? 'realize']} size={650}
    position={() => [55 + 14 * (1 - catOpacity()), 0]}/>);

  yield view.toPromise();
  yield* time(timing.frames / 60, timing.frames / 60, linear);
});

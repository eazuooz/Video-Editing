import {Circle, Line, Node, Rect, Txt} from '@motion-canvas/2d';
import {Vector2} from '@motion-canvas/core';

const C = {
  black: '#000000',
  white: '#FFFFFF',
  yellow: '#FFD25A',
  red: '#F27C70',
  green: '#92DF9C',
  muted: '#B8C3BC',
};

const FONT = 'Malgun Gothic';
const clamp01 = (value: number) =>
  Number.isFinite(value) ? Math.max(0, Math.min(1, value)) : 0;
const smooth = (value: number) => {
  const p = clamp01(value);
  return p * p * (3 - 2 * p);
};
const stagger = (progress: number, index: number, count: number) =>
  clamp01(progress * count - index);

export type PacingPhase = 'hidden' | 'baseline' | 'compare' | 'gap' | 'result';
export type SoundMigrationPhase = 'hidden' | 'before' | 'sound' | 'move' | 'result';

/**
 * Both factories return a local Node centered at (0,-30). Their content fits
 * a 900x650 region around that center. Place/scale that Node as one unit.
 *
 * The parent supplies phase() and progress() (0..1 WITHIN the current phase).
 * clock() is accepted for the common scene adapter but intentionally unused:
 * there are no assumed narration times, durations, random values, or loops.
 * Unknown phases are hidden. The parent may hide either Node independently.
 *
 * Pacing: baseline -> compare -> gap -> result.
 * Sound: before -> sound -> move -> result.
 * Hold result to retain the final state; reset phases/progress to replay.
 */
export function makePacingDiagram(
  _clock: () => number,
  phase: () => string,
  progress: () => number,
): Node {
  const order: readonly string[] = ['hidden', 'baseline', 'compare', 'gap', 'result'];
  const stage = () => Math.max(0, order.indexOf(phase()));
  const p = () => clamp01(progress());
  const root = new Node({position: [0, -30], opacity: () => stage() > 0 ? 1 : 0});
  const topReveal = (i: number) => stage() > 1 ? 1 : stagger(p(), i, 12);
  const bottomReveal = (i: number) => stage() > 2 ? 1 :
    stage() === 2 ? stagger(p(), i, 8) : 0;
  const gapReveal = () => stage() > 3 ? 1 : stage() === 3 ? p() : 0;

  root.add(<Txt text="같은 위협, 다른 간격" fontFamily={FONT} fontSize={46}
    fontWeight={700} fill={C.yellow} position={[0, -275]}/>);

  const condition = new Node({opacity: gapReveal});
  root.add(condition);
  condition.add(<Txt text="전투가 격해짐" fontFamily={FONT} fontSize={34}
    fill={C.white} position={[-220, -200]}/>);
  condition.add(<Line points={[[-55, -200], [45, -200]]} stroke={C.yellow}
    lineWidth={5} endArrow arrowSize={12} end={gapReveal}/>);
  condition.add(<Txt text="위협 유입 잠시 줄임" fontFamily={FONT} fontSize={34}
    fill={C.green} position={[245, -200]}/>);

  root.add(<Txt text="조절 없음" fontFamily={FONT} fontSize={38}
    fontWeight={700} fill={C.white} position={[-330, -82]}/>);
  root.add(<Txt text="휴식 조절" fontFamily={FONT} fontSize={38}
    fontWeight={700} fill={C.green} position={[-330, 115]}
    opacity={() => stage() >= 2 ? 1 : 0}/>);

  // Each block has exactly the same size in both rows. Only the arrival gaps
  // differ: this is a qualitative pacing comparison, not actual threat counts.
  const topX = Array.from({length: 12}, (_, i) => -185 + 51 * i);
  const bottomX = [-185, -134, -83, -32, 223, 274, 325, 376];
  root.add(<Line points={[[-210, -34], [415, -34]]} stroke={C.muted}
    lineWidth={3} opacity={0.55}/>);
  root.add(<Line points={[[-210, 163], [415, 163]]} stroke={C.muted}
    lineWidth={3} opacity={() => stage() >= 2 ? 0.55 : 0}/>);
  topX.forEach((x, i) => root.add(<Rect width={34} height={68}
    position={[x, -82]} fill={C.red} opacity={() => topReveal(i)}/>));
  bottomX.forEach((x, i) => root.add(<Rect width={34} height={68}
    position={[x, 115]} fill={C.red} opacity={() => bottomReveal(i)}/>));

  // Bracket names the deliberately empty interval. It does not represent
  // an invulnerability window or instantly remove already-present enemies.
  root.add(<Line points={[[-4, 183], [-4, 204], [194, 204], [194, 183]]}
    stroke={C.green} lineWidth={5} end={gapReveal}
    opacity={() => gapReveal() > 0 ? 1 : 0}/>);
  root.add(<Txt text="숨 돌릴 틈" fontFamily={FONT} fontSize={38}
    fontWeight={700} fill={C.green} position={[95, 244]}
    opacity={() => clamp01((gapReveal() - 0.35) / 0.65)}/>);
  root.add(<Txt text="원리 설명 · 실제 게임 수치 아님" fontFamily={FONT}
    fontSize={28} fill={C.muted} position={[0, 307]}/>);
  return root;
}

export function makeSoundMigrationDiagram(
  _clock: () => number,
  phase: () => string,
  progress: () => number,
): Node {
  const order: readonly string[] = ['hidden', 'before', 'sound', 'move', 'result'];
  const stage = () => Math.max(0, order.indexOf(phase()));
  const p = () => clamp01(progress());
  const root = new Node({position: [0, -30], opacity: () => stage() > 0 ? 1 : 0});
  const soundReveal = () => stage() > 2 ? 1 : stage() === 2 ? p() : 0;
  const move = () => stage() > 3 ? 1 : stage() === 3 ? smooth(p()) : 0;
  const soundLines = () => stage() === 2 ? 1 :
    stage() === 3 ? 1 - clamp01(p() / 0.25) : 0;
  const sound = new Vector2(265, -35);
  const starts = [new Vector2(-310, -90), new Vector2(-245, 130), new Vector2(-100, 5)];
  const ends = [new Vector2(175, -90), new Vector2(195, 100), new Vector2(310, 85)];

  root.add(<Txt text="소리를 따라, 기존 좀비가 이동" fontFamily={FONT}
    fontSize={44} fontWeight={700} fill={C.yellow} position={[0, -275]}/>);
  root.add(<Txt text="기존 좀비" fontFamily={FONT} fontSize={38}
    fontWeight={700} fill={C.red} position={[-265, -180]}/>);
  root.add(<Txt text="먼 총성" fontFamily={FONT} fontSize={38}
    fontWeight={700} fill={C.yellow} position={[265, -145]} opacity={soundReveal}/>);

  // The sound-to-node arrows explain transmission. Once movement starts,
  // separate red paths explain the opposite relationship: approach the sound.
  starts.forEach((start, i) => {
    const direction = start.sub(sound).normalized;
    root.add(<Line points={[sound.add(direction.scale(38)), start.sub(direction.scale(33))]}
      stroke={C.yellow} lineWidth={5} lineDash={[12, 10]} endArrow arrowSize={13}
      end={() => stagger(soundReveal(), i, starts.length)} opacity={soundLines}/>);
  });
  root.add(<Circle width={58} height={58} position={sound} stroke={C.yellow}
    lineWidth={7} fill={C.black} opacity={soundReveal}/>);

  // Exactly these three red nodes are created, once. Their positions change;
  // no new node appears, no starting ghost is left behind, and no spawn is shown.
  starts.forEach((start, i) => {
    const destination = ends[i];
    const at = () => start.add(destination.sub(start).scale(move()));
    root.add(<Line points={[start, destination]} stroke={C.red} lineWidth={4}
      endArrow arrowSize={12} end={move}
      opacity={() => move() > 0 ? 0.75 : 0}/>);
    root.add(<Circle width={50} height={50} position={at} stroke={C.red}
      lineWidth={7} fill={C.black}/>);
  });
  root.add(<Txt text={() => stage() === 2 ? '소리가 전달됨' :
    stage() >= 3 ? '같은 개체가 소리 쪽으로 이동' : '아직 이동하지 않은 상태'}
    fontFamily={FONT} fontSize={35} fill={() => stage() === 2 ? C.yellow : C.white}
    position={[0, 235]}/>);
  root.add(<Txt text="원리 설명 · 실제 게임 수치 아님" fontFamily={FONT}
    fontSize={28} fill={C.muted} position={[0, 307]}/>);
  return root;
}

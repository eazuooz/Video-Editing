import {Circle, Line, Node, Rect, Txt} from '@motion-canvas/2d';

/**
 * Original, code-native vector artwork. No external sprite or reference-channel
 * artwork is used. The three monsters are created once and keep their size,
 * appearance and gait; only the spacing of encounter tokens changes.
 *
 * Full-height Shorts coordinates: origin is the centre of 1080x1920. Content
 * occupies native y560..1260, leaving the existing header and the fixed native
 * caption centre (510,1380) clear. The factory deliberately supplies neither
 * branding nor captions so the parent can reuse the approved framing.
 *
 * This is an encounter-sequence illustration, not a simulation of enemies
 * freezing, despawning, changing hit points, or a measured Director state.
 */
const C = {
  black: '#000000', white: '#FFFFFF', yellow: '#FFD25A',
  red: '#F27C70', green: '#92DF9C', muted: '#B8C3BC', forest: '#073C32',
};
const FONT = 'Malgun Gothic';
const clamp01 = (n: number) => Math.max(0, Math.min(1, Number.isFinite(n) ? n : 0));
const smooth = (n: number) => {const p = clamp01(n); return p * p * (3 - 2 * p);};
const lerp = (a: number, b: number, p: number) => a + (b - a) * p;

/** Jointed leg: hip, knee, shin and recognisable shoe, with opposing steps. */
function leg(clock: () => number, side: -1 | 1, trousers: string): Node {
  const swing = () => side * 15 * Math.sin(clock() * 7);
  const hip = new Node({position: [side * 13, 20], rotation: swing});
  hip.add(<Line points={[[0, 0], [0, 31]]} stroke={trousers} lineWidth={20}
    lineCap="round"/>);
  const knee = new Node({position: [0, 31], rotation: () => -swing() * .8});
  knee.add(<Line points={[[0, 0], [-1, 32]]} stroke={C.green} lineWidth={14}
    lineCap="round"/>);
  knee.add(<Circle width={11} height={11} fill={C.green} stroke={C.muted}
    lineWidth={2}/>);
  knee.add(<Rect width={35} height={15} radius={5} position={[-9, 35]}
    fill={C.black} stroke={C.muted} lineWidth={3}/>);
  hip.add(knee);
  return hip;
}

/** Side-facing zombie: torn shirt, exposed jaw, uneven eyes and bent elbows. */
function zombie(clock: () => number): Node {
  const actor = new Node({y: () => Math.abs(Math.sin(clock() * 7)) * -2});
  actor.add(<Line points={[[-29, -48], [20, -49], [32, -6], [21, 26],
    [8, 19], [0, 29], [-13, 20], [-25, 26], [-31, -7]]} closed
    fill={C.red} stroke={C.white} lineWidth={3} lineJoin="round"/>);
  actor.add(leg(clock, 1, C.forest));
  actor.add(leg(clock, -1, C.forest));
  // Uneven collar and a torn sleeve establish a person-like monster rather
  // than an abstract block. The back arm is articulated behind the front arm.
  actor.add(<Line points={[[-8, -47], [-3, -24], [9, -45]]}
    stroke={C.black} lineWidth={5} lineJoin="round"/>);
  const rearArm = new Node({position: [22, -35], rotation: () => 6 * Math.sin(clock() * 7)});
  rearArm.add(<Line points={[[0, 0], [-28, 16], [-53, 10]]}
    stroke={C.green} lineWidth={13} lineCap="round" lineJoin="round"/>);
  rearArm.add(<Circle width={10} height={10} position={[-28, 16]}
    fill={C.green} stroke={C.muted} lineWidth={2}/>);
  actor.add(rearArm);
  actor.add(<Rect width={20} height={26} position={[-3, -57]}
    fill={C.green} stroke={C.muted} lineWidth={2}/>);
  actor.add(<Line points={[[-31, -100], [-17, -115], [11, -112], [26, -94],
    [23, -68], [7, -55], [-14, -61], [-31, -77]]} closed
    fill={C.green} stroke={C.white} lineWidth={3} lineJoin="round"/>);
  actor.add(<Line points={[[-29, -99], [-22, -115], [-11, -119],
    [-2, -111], [10, -116], [20, -104], [8, -106], [0, -99], [-9, -105]]}
    closed fill={C.black} stroke={C.white} lineWidth={2}/>);
  actor.add(<Circle width={12} height={13} position={[-20, -87]} fill={C.white}/>);
  actor.add(<Circle width={9} height={8} position={[1, -87]} fill={C.white}/>);
  actor.add(<Circle width={4} height={6} position={[-23, -87]} fill={C.black}/>);
  actor.add(<Circle width={3} height={4} position={[-2, -87]} fill={C.black}/>);
  actor.add(<Line points={[[-30, -96], [-15, -93]]} stroke={C.black} lineWidth={4}/>);
  actor.add(<Line points={[[-23, -71], [-8, -67], [2, -71]]}
    stroke={C.black} lineWidth={6} lineCap="round"/>);
  actor.add(<Rect width={5} height={7} position={[-18, -69]} fill={C.white}/>);
  actor.add(<Rect width={5} height={6} position={[-8, -67]} fill={C.white}/>);
  actor.add(<Line points={[[13, -85], [19, -78]]} stroke={C.forest} lineWidth={3}/>);
  const frontArm = new Node({position: [-26, -33], rotation: () => -5 * Math.sin(clock() * 7)});
  frontArm.add(<Line points={[[0, 0], [-21, 21], [-47, 9]]}
    stroke={C.green} lineWidth={15} lineCap="round" lineJoin="round"/>);
  frontArm.add(<Circle width={12} height={12} position={[-21, 21]}
    fill={C.green} stroke={C.white} lineWidth={2}/>);
  frontArm.add(<Line points={[[-45, 7], [-57, 5], [-58, 13]]}
    stroke={C.green} lineWidth={7} lineCap="round" lineJoin="round"/>);
  actor.add(frontArm);
  return actor;
}

function player(): Node {
  const actor = new Node({});
  actor.add(<Line points={[[-12, 18], [-17, 76]]} stroke={C.muted}
    lineWidth={18} lineCap="round"/>);
  actor.add(<Line points={[[13, 18], [24, 76]]} stroke={C.muted}
    lineWidth={18} lineCap="round"/>);
  actor.add(<Rect width={34} height={13} radius={4} position={[-10, 82]}
    fill={C.black} stroke={C.white} lineWidth={3}/>);
  actor.add(<Rect width={34} height={13} radius={4} position={[30, 82]}
    fill={C.black} stroke={C.white} lineWidth={3}/>);
  actor.add(<Line points={[[-27, -47], [22, -47], [28, 22], [-24, 22]]}
    closed fill={C.green} stroke={C.white} lineWidth={3} lineJoin="round"/>);
  actor.add(<Rect width={19} height={22} position={[0, -57]}
    fill={C.white} stroke={C.muted} lineWidth={2}/>);
  actor.add(<Rect width={53} height={58} radius={17} position={[2, -88]}
    fill={C.white} stroke={C.muted} lineWidth={3}/>);
  actor.add(<Line points={[[-25, -92], [-26, -112], [-10, -123],
    [17, -117], [29, -102], [9, -107], [-4, -98]]}
    closed fill={C.black} stroke={C.white} lineWidth={3} lineJoin="round"/>);
  actor.add(<Circle width={5} height={7} position={[19, -88]} fill={C.black}/>);
  actor.add(<Line points={[[17, -73], [27, -73]]} stroke={C.black}
    lineWidth={3} lineCap="round"/>);
  actor.add(<Line points={[[20, -34], [40, -15], [56, -28]]}
    stroke={C.white} lineWidth={13} lineCap="round" lineJoin="round"/>);
  actor.add(<Line points={[[-24, -31], [-29, -2], [-4, 3]]}
    stroke={C.white} lineWidth={13} lineCap="round" lineJoin="round"/>);
  return actor;
}

export function makeMonsterFrequencyIntro(clock: () => number, duration: number): Node {
  const total = Math.max(1, duration);
  const p = () => clamp01(clock() / total);
  const spread = () => smooth((p() - .34) / .34);
  const reveal = () => smooth(p() / .10);
  const result = () => smooth((p() - .70) / .12);
  const root = new Node({});
  root.add(<Txt text="전투가 벌어지는 간격" fontFamily={FONT} fontSize={52}
    fontWeight={700} fill={C.yellow} position={[-30, -350]}/>);
  root.add(<Txt text="같은 좀비 · 달라지는 만남의 간격" fontFamily={FONT}
    fontSize={34} fill={C.white} position={[-30, -280]}/>);
  root.add(<Txt text={() => p() < .40 ? '연달아 맞닥뜨림' : '게임이 간격을 조절'}
    fontFamily={FONT} fontSize={40} fontWeight={700}
    fill={() => p() < .40 ? C.red : C.green} position={[-30, -200]}/>);

  // Ground and a dotted encounter line make the left-to-right ordering clear.
  root.add(<Line points={[[-430, 117], [400, 117]]} stroke={C.muted}
    lineWidth={4}/>);
  root.add(<Line points={[[-255, -120], [-255, 117]]} stroke={C.white}
    lineWidth={3} lineDash={[10, 10]} opacity={.7}/>);
  root.add(<Txt text="플레이어" fontFamily={FONT} fontSize={31} fill={C.white}
    position={[-365, 162]}/>);
  root.add(<Txt text="조우" fontFamily={FONT} fontSize={28} fill={C.muted}
    position={[-255, -145]}/>);
  const human = player(); human.position([-365, 20]); human.scale(1.05);
  root.add(human);

  // Equal size and appearance across the A→B change. These are encounter
  // tokens on a timeline; their articulation supplies a recognisable walk.
  [-125, -10, 105].forEach((start, i) => {
    const endpoint = [-125, 100, 325][i];
    const actor = new Node({
      position: () => [lerp(start, endpoint, spread()), 20], scale: 1.05,
      opacity: reveal,
    });
    actor.add(zombie(() => clock() + i * .16));
    root.add(actor);
  });

  // Only the empty interval changes. The bracket arrives after the gap is
  // visible, so the viewer first sees the result and then receives its name.
  root.add(<Line points={() => [[-78, 173], [-78, 195],
    [lerp(-48, 53, spread()), 195], [lerp(-48, 53, spread()), 173]]}
    stroke={C.green} lineWidth={5} end={result} opacity={result}/>);
  root.add(<Txt text="숨 돌릴 틈" fontFamily={FONT} fontSize={38}
    fontWeight={700} fill={C.green} position={[-12, 245]} opacity={result}/>);
  root.add(<Txt text="전투 순서의 개념도 · 실제 게임 수치 아님" fontFamily={FONT}
    fontSize={27} fill={C.muted} position={[-30, 300]}/>);
  return root;
}

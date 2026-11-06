import {Circle, Line, Node, Rect, Txt, makeScene2D} from '@motion-canvas/2d';
import {Vector2, createSignal, tween, useScene} from '@motion-canvas/core';

type Segment = 'p2' | 'p6' | 'p7';
type Point = [number, number];
type PhaseFrame = {frame: number; phase: number};
const C = {
  black: '#000000', floor: '#101715', white: '#F5F5F5', muted: '#B8B8B8',
  yellow: '#E8CF83', view: '#A4C6A0', teal: '#73C7C2', problem: '#EF8585',
  wall: '#66716E', wood: '#986036', woodLight: '#C68C50', metal: '#B6BDB8',
};
const FONT = 'Noto Sans KR';
const clamp01 = (v: number) => Math.max(0, Math.min(1, v));
const ramp = (v: number, a: number, b: number) => clamp01((v - a) / (b - a));
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

/** Stable editorial IDs, normalized draft positions, not recorded speech times. */
export const DIAGRAM_CUES = [
  {id: '07.04-p2-01-partial-hint', paragraph: 2, at: 0.08, speech: '풍경이나 보물의 존재는 알리되'},
  {id: '07.04-p2-02-withhold-information', paragraph: 2, at: 0.27, speech: '전체 모습이나 도달하는 길은 남겨 두는 거죠.'},
  {id: '07.04-p2-03-name-spatial-denial', paragraph: 2, at: 0.50, speech: '스페이셜 디나이얼, 공간을 통한 보상 유보'},
  {id: '07.04-p2-04-reason-to-investigate', paragraph: 2, at: 0.82, speech: '보이는 일부가 더 살펴볼 이유가 될 수 있습니다.'},
  {id: '07.04-p6-01-same-visible-chest', paragraph: 6, at: 0.04, speech: '보물방은 조금 다릅니다.'},
  {id: '07.04-p6-02-visible-not-reachable', paragraph: 6, at: 0.16, speech: '상자 자체는 보여 주되, 거기까지 가는 길을 가릴 수도 있죠.'},
  {id: '07.04-p6-03-discover-the-bends', paragraph: 6, at: 0.36, speech: '여기서는 보상에 도달하는 방법을 남겨 둔 겁니다.'},
  {id: '07.04-p6-04-different-question', paragraph: 6, at: 0.91, speech: '플레이어가 풀어야 하는 질문은 다릅니다.'},
  {id: '07.04-p7-01-refuge-arrival', paragraph: 7, at: 0.04, speech: '쉼터는 도착했을 때의 놀라움이 중요한 경우도 있습니다.'},
  {id: '07.04-p7-02-partly-hidden-entrance', paragraph: 7, at: 0.25, speech: '갈림길 너머로 입구 일부를 보이게 하거나'},
  {id: '07.04-p7-03-approach-and-music-hint', paragraph: 7, at: 0.45, speech: '가까워질수록 들리는 음악으로 존재를 암시할 수 있습니다.'},
  {id: '07.04-p7-04-follow-reward-role', paragraph: 7, at: 0.88, speech: '보상의 역할에 맞춰 정하는 겁니다.'},
] as const;

// One shared floor plan; no sea/slit geometry, pixel visibility or Unity raycast is reproduced here.
const START: Point = [220, 700];
const CHEST: Point = [760, 410];
const VAULT_ROUTE: Point[] = [START, [350, 700], [350, 270], [880, 270], [880, 530], [760, 530]];
const REFUGE_ROUTE: Point[] = [START, [420, 610], [590, 610], [590, 490], [650, 490]];

function along(points: Point[], progress: number): Vector2 {
  const lengths = points.slice(1).map((p, i) => Math.hypot(p[0] - points[i][0], p[1] - points[i][1]));
  let remaining = lengths.reduce((a, b) => a + b, 0) * clamp01(progress);
  for (let i = 0; i < lengths.length; i++) {
    if (remaining <= lengths[i]) {
      const t = lengths[i] === 0 ? 0 : remaining / lengths[i];
      return new Vector2(lerp(points[i][0], points[i + 1][0], t), lerp(points[i][1], points[i + 1][1], t));
    }
    remaining -= lengths[i];
  }
  return new Vector2(points[points.length - 1]);
}

/** Only the future scoped renderer supplies these ASR-bound editorial keyframes. */
function authoredPhase(frame: number, map: PhaseFrame[]): number {
  for (let i = 1; i < map.length; i++) {
    if (frame <= map[i].frame) {
      const a = map[i - 1], b = map[i];
      return lerp(a.phase, b.phase, clamp01((frame - a.frame) / (b.frame - a.frame)));
    }
  }
  return map[map.length - 1].phase;
}

function txt(text: string | (() => string), x: number, y: number, size = 34, fill = C.white, weight = 500) {
  return new Txt({text, x, y, fontFamily: FONT, fontSize: size, fontWeight: weight, fill});
}

function chest(): Node {
  const node = new Node({position: CHEST});
  node.add(new Rect({width: 142, height: 78, y: 16, radius: 8, fill: C.wood, stroke: C.woodLight, lineWidth: 3}));
  node.add(new Rect({width: 146, height: 52, y: -32, radius: 20, fill: C.woodLight, stroke: C.wood, lineWidth: 4}));
  for (const x of [-46, 46]) node.add(new Rect({x, y: -2, width: 12, height: 106, fill: C.metal}));
  for (const y of [8, 29, 49]) node.add(new Line({points: [[-66, y], [66, y]], stroke: '#613E27', lineWidth: 2}));
  node.add(new Rect({width: 26, height: 31, y: 0, radius: 4, fill: C.yellow, stroke: '#4A3D1F', lineWidth: 3}));
  node.add(new Circle({size: 8, y: -4, fill: '#4A3D1F'}));
  node.add(new Line({points: [[0, -1], [0, 8]], stroke: '#4A3D1F', lineWidth: 4}));
  return node;
}

export default makeScene2D(function* (view) {
  view.fill(C.black);
  const scene = useScene();
  const selected = scene.variables.get('segment', 'all')();
  if (!['all', 'p2', 'p6', 'p7'].includes(selected)) throw new Error('Unknown 07.04 diagram segment');
  const segment = createSignal<Segment>(selected === 'all' ? 'p2' : selected as Segment);
  const phase = createSignal(0);
  const p2 = () => segment() === 'p2';
  const p6 = () => segment() === 'p6';
  const p7 = () => segment() === 'p7';
  const canonical = () => p2() ? ramp(phase(), 0.50, 0.64) : 1;
  const collapsed = () => p2() ? ramp(phase(), 0.68, 0.82) : 1;
  const walk = () => p6() ? ramp(phase(), 0.36, 0.90) : p7() ? ramp(phase(), 0.35, 0.84) : 0;
  const player = () => p7() ? along(REFUGE_ROUTE, walk()) : p6() ? along(VAULT_ROUTE, walk()) : new Vector2(START);

  // Anchor the 1080x900 content clip at the actual canvas top-left. On a full
  // portrait canvas all drawing is still restricted to global picture y<900.
  const screen = new Node({position: () => view.size().scale(-0.5)});
  view.add(screen);
  const clip = new Rect({x: 540, y: 450, width: 1080, height: 900, clip: true, fill: C.black});
  screen.add(clip);
  const stage = new Node({position: [-540, -450]});
  clip.add(stage);

  const openingQuestion = txt('보물은 보이는데, 길은 어디일까?', 520, 150, 46, C.yellow, 700);
  openingQuestion.opacity(() => p2() ? 1 - canonical() : 0);
  stage.add(openingQuestion);
  const canonicalName = txt('Spatial Denial (공간을 통한 보상 유보)', 520, 150, 44, C.yellow, 700);
  canonicalName.opacity(canonical);
  canonicalName.position(() => [lerp(520, 395, collapsed()), lerp(150, 62, collapsed())]);
  canonicalName.fontSize(() => lerp(44, 32, collapsed()));
  stage.add(canonicalName);
  const heading = txt(() => p2() ? '일부 단서가 남기는 질문' : p6() ? 'Visible Reward (보이는 보상)' : 'Refuge Hint (쉼터 단서)', 520, 150, 46, C.yellow, 700);
  heading.opacity(() => ramp(collapsed(), 0.8, 1));
  stage.add(heading);
  stage.add(txt(() => p2() ? '전체 모습을 숨기거나 가는 길을 감추기' : p6() ? '보이는 순간과 도달 방법은 다른 질문' : '입구와 음악으로 존재만 암시하기', 520, 214, 32));
  stage.add(txt('설명도', 860, 62, 27, C.muted));

  const floor = new Rect({x: 520, y: 538, width: 810, height: 554, fill: C.floor, stroke: '#46534E', lineWidth: 3});
  stage.add(floor);
  const vault = new Node({opacity: () => p7() ? 0 : 1});
  stage.add(vault);
  // An open-barred barrier permits a schematic view of the target, not passage.
  // It is not the native experiment's angled channel and makes no raycast claim.
  vault.add(new Line({points: [[540, 330], [540, 485]], stroke: C.wall, lineWidth: 24}));
  vault.add(new Line({points: [[540, 595], [540, 780]], stroke: C.wall, lineWidth: 24}));
  vault.add(new Rect({x: 540, y: 540, width: 28, height: 110, stroke: C.metal, lineWidth: 4}));
  for (const y of [505, 527, 549, 571]) vault.add(new Line({points: [[527, y], [553, y]], stroke: C.metal, lineWidth: 3}));
  vault.add(txt('직행 불가', 660, 589, 30, C.problem, 700));
  vault.add(txt('보여도 돌아가야 함', 720, 630, 28, C.muted));
  const reward = chest();
  vault.add(reward);
  // Editorial information mask, not a simulated geometric visibility mask.
  vault.add(new Rect({x: 804, y: 408, width: 84, height: 128, fill: C.floor, opacity: () => p2() ? 1 : 0}));
  vault.add(txt(() => p2() ? '보상의 일부 단서' : '상자 자체는 보임', 758, 328, 32, C.view, 700));
  const sight = new Line({points: [START, [725, 405]], stroke: C.view, lineWidth: 6, endArrow: true, arrowSize: 15,
    end: () => ramp(phase(), 0.08, 0.27), opacity: () => p2() ? 1 : p6() ? 1 - ramp(phase(), 0.27, 0.36) : 0});
  vault.add(sight);
  const route = new Line({points: VAULT_ROUTE, stroke: C.yellow, lineWidth: 9, lineDash: [18, 12], endArrow: true, arrowSize: 18, end: walk, opacity: () => p6() ? 1 : 0});
  vault.add(route);
  // Undiscovered approach is withheld as map information. The same route is
  // progressively exposed through its actual bends, with the position dot on it.
  const unknown = new Rect({x: 760, y: 285, width: 220, height: 42, fill: C.black, opacity: () => p6() ? 1 - ramp(phase(), 0.58, 0.73) : 1});
  vault.add(unknown);
  vault.add(txt(() => p6() && phase() >= 0.9 ? '도달 방법을 발견' : '가는 길은?', 750, 710, 31, C.muted));

  const refuge = new Node({opacity: () => p7() ? 1 : 0});
  stage.add(refuge);
  refuge.add(new Line({points: [START, [420, 610], [840, 710]], stroke: '#69756D', lineWidth: 7}));
  refuge.add(new Line({points: REFUGE_ROUTE, stroke: C.yellow, lineWidth: 8, lineDash: [18, 12], end: walk}));
  refuge.add(txt('갈림길', 422, 690, 32));
  const door = new Node({position: [760, 442]});
  refuge.add(door);
  door.add(new Rect({width: 122, height: 172, radius: 20, fill: C.wall}));
  door.add(new Rect({width: 86, height: 142, radius: 10, fill: C.wood, stroke: C.woodLight, lineWidth: 4}));
  for (const x of [-20, 0, 20]) door.add(new Line({points: [[x, -66], [x, 66]], stroke: C.woodLight, lineWidth: 2}));
  door.add(new Circle({x: 26, y: 10, size: 11, fill: C.yellow}));
  // Opaque foreground return covers part of the entrance; the refuge interior
  // never opens and no invisible target marker is drawn behind the wall.
  refuge.add(new Rect({x: 710, y: 445, width: 68, height: 230, fill: C.wall}));
  refuge.add(new Line({points: [[660, 330], [744, 330]], stroke: C.wall, lineWidth: 25}));
  refuge.add(txt('입구 일부', 825, 325, 32, C.view, 700));
  refuge.add(new Line({points: [[845, 351], [806, 388]], stroke: C.view, lineWidth: 5, endArrow: true, arrowSize: 13}));
  // Both approach and cue grow from the same authored position. This is an
  // illustrative relationship, never a sampled game waveform or a decibel meter.
  const far = Math.hypot(START[0] - 760, START[1] - 442);
  const near = Math.hypot(650 - 760, 490 - 442);
  const hintStrength = () => {
    const p = player();
    return clamp01((far - Math.hypot(p.x - 760, p.y - 442)) / (far - near));
  };
  for (let i = 0; i < 3; i++) refuge.add(new Circle({x: 760, y: 442, size: 190 + i * 80, startAngle: 140, endAngle: 220,
    stroke: C.yellow, lineWidth: 5, end: () => clamp01(hintStrength() * 1.5 - i * 0.22),
    opacity: () => (0.25 + 0.65 * hintStrength()) * ramp(phase(), 0.43, 0.48)}));
  const musicGlyph = new Node({opacity: () => ramp(phase(), 0.43, 0.48)});
  musicGlyph.add(new Line({points: [[855, 484], [855, 442], [882, 435], [882, 476]], stroke: C.yellow, lineWidth: 5}));
  musicGlyph.add(new Circle({x: 848, y: 484, width: 18, height: 12, rotation: -20, fill: C.yellow}));
  musicGlyph.add(new Circle({x: 875, y: 476, width: 18, height: 12, rotation: -20, fill: C.yellow}));
  refuge.add(musicGlyph);
  refuge.add(txt('음악 단서 · 개념 표시', 520, 764, 31, C.yellow));

  // A labelled abstract position is intentional: this map does not replace a
  // recognizable 3D actor with a cube or pretend to show commercial game internals.
  const marker = new Node({position: player});
  marker.add(new Circle({size: 25, fill: C.white, stroke: C.black, lineWidth: 4}));
  marker.add(new Circle({size: 40, stroke: C.teal, lineWidth: 3}));
  stage.add(marker);
  const positionLabel = txt('플레이어 위치', 0, 0, 29, C.white);
  // Introduce the marker before movement, then remove its text before upper/
  // right bends so it cannot cover the reward label or protected platform rail.
  positionLabel.opacity(() => p6() ? 1 - ramp(walk(), 0.30, 0.40)
    : p7() ? (walk() === 0 ? 1 : 0) : 1);
  positionLabel.position(() => player().add(p7() ? [-140 * walk(), lerp(47, -50, walk())]
    : p6() ? [-120 * ramp(walk(), 0.75, 1), 47 * (1 - ramp(walk(), 0.75, 1))] : [0, 47]));
  stage.add(positionLabel);
  stage.add(txt(() => p2() ? (phase() < 0.5 ? '모두 숨기기보다, 존재의 단서를 남기기' : '단서 → 더 살펴볼 질문')
    : p6() ? (phase() < 0.36 ? '보이는 보상 ≠ 알아낸 길' : '굽은 길을 따라 도달 방법을 발견')
    : phase() < 0.88 ? '내부는 감추고, 접근하며 입구·음악을 발견' : '무엇을 드러낼지는 보상의 역할에 맞게', 520, 812, 33, C.white, 600));

  const sequence: Segment[] = selected === 'all' ? ['p2', 'p6', 'p7'] : [selected as Segment];
  const actualMode = scene.variables.get('timingMode', 'draft')() === 'authored-cue-frames';
  const actualFrames = scene.variables.get('segmentFrames', 0)();
  const actualMap = scene.variables.get<PhaseFrame[]>('phaseFrameMap', [])();
  if (actualMode) {
    if (selected === 'all' || !Number.isInteger(actualFrames) || actualFrames < 2
      || actualMap.length < 2 || actualMap[0].frame !== 0
      || actualMap[actualMap.length - 1].frame !== actualFrames - 1
      || actualMap.some((p, i) => !Number.isInteger(p.frame) || !Number.isFinite(p.phase) || p.phase < 0 || p.phase > 1
        || (i > 0 && (p.frame <= actualMap[i - 1].frame || p.phase <= actualMap[i - 1].phase)))) {
      throw new Error('Exact segment frames and monotone authored phase-frame map required');
    }
  }
  for (const next of sequence) {
    segment(next);
    phase(0);
    const seconds = actualMode ? actualFrames / 60
      : scene.variables.get(`${next}Seconds`, next === 'p2' ? 20 : 24)();
    if (!Number.isFinite(seconds) || seconds <= 0) throw new Error('Draft duration must be finite and positive');
    yield* tween(seconds, value => phase(actualMode ? authoredPhase(value * actualFrames, actualMap) : value));
  }
});

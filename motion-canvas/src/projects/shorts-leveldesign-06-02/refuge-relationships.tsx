import {Circle, Line, Node, Rect, Txt, makeScene2D} from '@motion-canvas/2d';
import {Vector2, createSignal, tween, useScene} from '@motion-canvas/core';

type Segment = 'p04' | 'p25';
type Point = [number, number];
type PhaseFrame = {frame: number; phase: number};
const C = {
  black: '#000000', floor: '#101715', ink: '#F5F5F5', muted: '#B8B8B8',
  title: '#E8CF83', relation: '#73C7C2', refuge: '#A4C6A0', exposed: '#EF8585',
  refugeFill: '#16271A', exposedFill: '#301D1D', border: '#66716E',
};
const FONT = 'Noto Sans KR';
const A: Point = [185, 410], B: Point = [650, 410];
const C1: Point = [650, 650], D: Point = [185, 650];
const clamp = (v: number) => Math.max(0, Math.min(1, v));
const ramp = (v: number, a: number, b: number) => clamp((v - a) / (b - a));
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

/** Normalized authoring phases, NOT measured speech times or recorded positions. */
export const RELATIONSHIP_CUES = [
  {id: '06.02-p04-01-current-reference', paragraph: 4, at: 0.06,
    exactSpokenAnchorKo: '지금 머무는 은신처와 바로 앞의 조망 공간이 현재의 기준입니다.'},
  {id: '06.02-p04-02-secondary-refuge', paragraph: 4, at: 0.25,
    exactSpokenAnchorKo: '그 건너편에 다음 은신처가 보이면'},
  {id: '06.02-p04-03-arrival-reference', paragraph: 4, at: 0.65,
    exactSpokenAnchorKo: '그곳에 도착하면 다시 그 자리가 현재 은신처가 되고'},
  {id: '06.02-p04-04-look-beyond', paragraph: 4, at: 0.82,
    exactSpokenAnchorKo: '그 너머의 공간을 살피게 되죠.'},
  {id: '06.02-p25-01-small-space', paragraph: 25, at: 0.06,
    exactSpokenAnchorKo: '이런 대비는 작은 공간 하나에도 만들 수 있습니다.'},
  {id: '06.02-p25-02-linear', paragraph: 25, at: 0.25,
    exactSpokenAnchorKo: '은신처를 차례로 잇으면 정해진 순서의 길이 되고'},
  {id: '06.02-p25-03-branch', paragraph: 25, at: 0.51,
    exactSpokenAnchorKo: '여러 은신처를 연결하면 갈림 경로도 만들 수 있죠.'},
  {id: '06.02-p25-04-relationship', paragraph: 25, at: 0.80,
    exactSpokenAnchorKo: '어디에서 무엇을 읽고 다음 어디로 움직일 수 있는지'},
] as const;

export function validateFrameContract(segment: string, count: number, map: PhaseFrame[]) {
  if (!['p04', 'p25'].includes(segment) || !Number.isInteger(count) || count < 2
    || map.length < 2 || map[0].frame !== 0 || map[0].phase !== 0
    || map[map.length - 1].frame !== count - 1 || map[map.length - 1].phase !== 1
    || map.some((p, i) => !Number.isInteger(p.frame) || !Number.isFinite(p.phase)
      || p.phase < 0 || p.phase > 1 || (i > 0
        && (p.frame <= map[i - 1].frame || p.phase <= map[i - 1].phase)))) {
    throw new Error('One segment and exact finite monotone authored frame contract required');
  }
}
export function authoredPhase(frame: number, map: PhaseFrame[]): number {
  for (let i = 1; i < map.length; i++) {
    if (frame <= map[i].frame) {
      const a = map[i - 1], b = map[i];
      return lerp(a.phase, b.phase, clamp((frame - a.frame) / (b.frame - a.frame)));
    }
  }
  return map[map.length - 1].phase;
}
function text(value: string | (() => string), x: number, y: number, size = 36,
  color = C.ink, weight = 500) {
  return new Txt({text: value, x, y, fontFamily: FONT, fontSize: size, fill: color, fontWeight: weight});
}

export default makeScene2D(function* (view) {
  const vars = useScene().variables;
  const selected = vars.get('segment', 'p04')();
  const count = vars.get('segmentFrames', 0)();
  const map = vars.get<PhaseFrame[]>('phaseFrameMap', [])();
  if (vars.get('timingMode', 'unbound-source-preparation')() !== 'authored-cue-frames') {
    throw new Error('Source preparation only: actual ASR-bound frame map is not supplied');
  }
  validateFrameContract(selected, count, map);
  const segment = selected as Segment;
  const chain = segment === 'p04';
  const phase = createSignal(0);
  const walk = () => chain ? ramp(phase(), 0.35, 0.62) : 0;
  const arrived = () => chain && phase() >= 0.65;
  const revealBeyond = () => chain ? ramp(phase(), 0.79, 0.89) : 1;
  const branching = () => chain ? 0 : ramp(phase(), 0.49, 0.69);
  const observer = () => new Vector2(lerp(A[0], B[0], walk()), A[1]);

  view.fill(C.black);
  const screen = new Node({position: () => view.size().scale(-0.5)});
  view.add(screen);
  const clip = new Rect({x: 540, y: 450, width: 1080, height: 900, clip: true, fill: C.black});
  screen.add(clip);
  const stage = new Node({position: [-540, -450]});
  clip.add(stage);
  stage.add(text('Prospect–Refuge (조망–은신처)', 488, 62, 38, C.title, 700));
  stage.add(text('설명도', 860, 112, 30, C.muted));
  stage.add(text(chain ? '보고 → 건너고 → 다시 보기' : '같은 공간, 길의 연결만 바꾸기', 488, 180, 42, C.ink, 700));
  stage.add(new Rect({x: 508, y: 505, width: 810, height: 540, radius: 24,
    fill: C.floor, stroke: C.border, lineWidth: 3}));

  // Spatial roles, not measured safety fields or human silhouettes.
  stage.add(new Rect({x: 417, y: 410, width: 270, height: 145, radius: 12,
    fill: C.exposedFill, stroke: C.exposed, lineWidth: 3}));
  const beyondBand = new Node({opacity: revealBeyond});
  beyondBand.add(new Rect({x: 650, y: 540, width: 132, height: 100, radius: 12,
    fill: C.exposedFill, stroke: C.exposed, lineWidth: 3}));
  beyondBand.add(text(chain ? '그 너머' : '다음 구간', 807, 551, 32, C.exposed));
  stage.add(beyondBand);
  const alternateBand = new Node({opacity: () => chain ? 0 : 1});
  alternateBand.add(new Rect({x: 185, y: 540, width: 132, height: 100, radius: 12,
    fill: C.exposedFill, stroke: C.exposed, lineWidth: 3}));
  alternateBand.add(new Rect({x: 417, y: 650, width: 270, height: 110, radius: 12,
    fill: C.exposedFill, stroke: C.exposed, lineWidth: 3}));
  stage.add(alternateBand);

  const edge = (points: Point[], progress: () => number, color = C.relation) => {
    const line = new Line({points, stroke: color, lineWidth: 9, end: progress,
      endArrow: true, arrowSize: 17});
    stage.add(line);
    return line;
  };
  edge([[A[0] + 80, A[1]], [B[0] - 85, B[1]]], () => chain ? ramp(phase(), 0.26, 0.34) : ramp(phase(), 0.22, 0.36));
  edge([[B[0], B[1] + 80], [C1[0], C1[1] - 65]], () => chain ? revealBeyond() : ramp(phase(), 0.33, 0.46));
  edge([[A[0], A[1] + 80], [D[0], D[1] - 65]], branching);
  edge([[D[0] + 65, D[1]], [C1[0] - 65, C1[1]]], branching);
  const refuge = (point: Point, radius: number, opacity: () => number) => {
    stage.add(new Circle({position: point, size: radius * 2, fill: C.refugeFill,
      stroke: C.refuge, lineWidth: 6, opacity}));
  };
  refuge(A, 78, () => 1);
  refuge(B, 78, () => chain ? ramp(phase(), 0.16, 0.24) : 1);
  refuge(C1, 60, revealBeyond);
  refuge(D, 60, () => chain ? 0 : 1);

  stage.add(text(() => chain ? arrived() ? '지나온 은신처' : '현재 은신처' : '출발 은신처', A[0], 298, 34, C.refuge));
  const bLabel = text(() => chain ? arrived() ? '현재 은신처' : '다음 은신처' : '다음 은신처', B[0], 298, 34, C.refuge);
  bLabel.opacity(() => chain ? ramp(phase(), 0.16, 0.24) : 1);stage.add(bLabel);
  const cLabel = text(chain ? '다음 은신처' : '도착 은신처', C1[0], 740, 34, C.refuge);
  cLabel.opacity(revealBeyond);stage.add(cLabel);
  const dLabel = text('다른 은신처', D[0], 740, 34, C.refuge);
  dLabel.opacity(() => chain ? 0 : 1);stage.add(dLabel);
  stage.add(text(() => chain && arrived() ? '지나온 조망' : '조망 공간', 417, 545, 34, C.exposed));

  // White point/eye is an explicitly labelled abstract observation position.
  const eye = new Node({position: observer});
  eye.add(new Circle({width: 58, height: 28, stroke: C.ink, lineWidth: 5}));
  eye.add(new Circle({size: 12, fill: C.ink}));
  stage.add(eye);
  const positionLabel = text('관찰점', A[0], 456, 30, C.ink);
  positionLabel.opacity(() => walk() === 0 && branching() === 0 ? 1 : 0); // Never travel into fixed labels.
  stage.add(positionLabel);
  stage.add(text(chain ? '관찰 → 건너기 → 다시 관찰' : '보호·노출·다음 목적지를 연결', 488, 840, 36, C.ink));

  // Future renderer supplies totalFrames/actual ASR anchors. No fabricated seconds.
  yield* tween(count / 60, value => phase(authoredPhase(value * count, map)));
});

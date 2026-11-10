import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {board, palette as c} from '../board';

const seconds = 8;
const headings = ['Position Offset (위치 오프셋)', 'Pivot (피벗)', '같은 각도로 돌아도 검 끝이 그리는 원은 달라짐'];
const conclusions = ['기본 궤적을 유지하고 그림만 정해 둔 순서로 어긋나게 배치합니다.',
  '피벗은 그림이 도는 기준점입니다. 물리 계산의 질량 중심과 구분할 수 있습니다.',
  '피벗에서 검 끝까지의 거리가 바뀌면 화면에서 그리는 원도 달라집니다.'];
const offsets: [number, number][] = [[0, -40], [35, -20], [35, 20], [0, 40], [-35, 20], [-35, -20]];

class Pivot extends Node {
  public constructor(private readonly clock: () => number) { super({}); }

  protected draw(ctx: CanvasRenderingContext2D) {
    const time = this.clock(), mode = Math.floor(time / seconds);
    const local = time % seconds;
    const {text, box, path, dot} = board(ctx);
    text(headings[mode], -846, -338, 54, c.gold);
    const titles = mode === 0 ? ['A · 기본 궤적 그대로', 'B · 표시 위치에 오프셋 추가']
      : mode === 1 ? ['A · 물체 중심에서 회전', 'B · 중심에서 벗어난 피벗']
      : ['A · 손잡이 쪽의 피벗', 'B · 날 중앙 쪽의 피벗'];
    for (const [i, title] of titles.entries()) {
      const x = -846 + i * 875, ink = i === 0 ? c.teal : c.coral;
      text(title, x, -244, 43, ink);
      box(x, -184, 812, 443);
      if (mode === 0) {
        const clock = Math.min(1, local / 7);
        const px = x + 91 + 609 * clock, py = 35;
        const step = Math.floor(local * 3.5) % offsets.length;
        const [dx, dy] = i === 0 ? [0, 0] : offsets[step];
        path([[x + 78, py], [x + 744, py]], c.grid, 6);
        if (i === 1) path([[px, py], [px + dx, py + dy]], c.gold, 5);
        dot(px, py, 12, c.gold);
        dot(px + dx, py + dy, 25, ink);
        text('기본 궤적', x + 78, 180, 36, c.gold);
        if (i === 1) {
          for (const [j, [a, b]] of offsets.entries()) {
            dot(x + 684 + 1.45 * a, 173 + b, j === step ? 14 : 8, j === step ? c.gold : c.muted);
          }
          text('순서대로 반복', x + 334, 180, 35, ink);
        }
      } else {
        const ox = x + 405, oy = 34, angle = local * 1.4;
        const offset = mode === 1 ? (i === 0 ? 0 : 52) : (i === 0 ? 86 : 0);
        const point = (a: number, b: number, theta = angle): [number, number] =>
          [ox + a * Math.cos(theta) - b * Math.sin(theta), oy + a * Math.sin(theta) + b * Math.cos(theta)];
        const trace = mode === 1 ? offset : 126 + offset;
        if (trace > 0) {
          ctx.setLineDash([9, 9]);
          path(Array.from({length: 49}, (_, step) => point(trace, 0, step * Math.PI / 24)), c.grid, 4);
          ctx.setLineDash([]);
        }
        if (mode === 1) {
          const [cx, cy] = point(offset, 0);
          dot(cx, cy, 73, ink);
          path([point(offset + 27, -54), point(offset + 52, -86), point(offset + 74, -85)], c.white, 12);
          dot(cx, cy, 9, c.white);
        } else {
          path([point(offset - 132, 0), point(offset + 126, 0)], ink, 26);
          path([point(offset - 76, -37), point(offset - 76, 37)], c.white, 11);
          dot(...point(offset + 126, 0), 13, c.white);
        }
        dot(ox, oy, 12, c.gold);
        text('피벗', x + 77, 185, 37, c.gold);
        text(mode === 1 ? '물체의 그림 중심' : '검 끝의 경로', x + 330, 185, 37, c.white);
      }
    }
    text(conclusions[mode], -845, 320, 38);
  }
}

export default makeScene2D(function* (view) {
  view.fill(c.bg);
  const clock = createSignal(0);
  view.add(<Txt x={-846} y={-450} offsetX={-1} text="회전축과 위치 오프셋" fontFamily="Malgun Gothic"
    fontSize={60} fontWeight={700} fill={c.gold}/>);
  view.add(<Txt x={846} y={-450} offsetX={1} text="원리 도식" fontFamily="Malgun Gothic"
    fontSize={35} fill={c.muted}/>);
  view.add(new Pivot(clock));
  const end = headings.length * seconds;
  yield* tween(end, p => clock(Math.min(end - .001, p * end)));
});

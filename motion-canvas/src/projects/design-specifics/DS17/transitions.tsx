import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {board, palette as c} from '../board';

const seconds = 8;
const headings = ['어두운 구간과 입력 제한을 나눠 보기', '같은 출발점에서 바로 옆 화면으로', '경계의 모양으로 다음 장면을 알리기'];
const conclusions = ['어디에 도착했는지 읽히는 시점과 다시 움직일 수 있는 시점을 맞춥니다.',
  '이전 장소와 새 장소가 이어져 있다는 정보가 전환 중에도 남습니다.',
  '화면을 넘기는 모양 자체로 무엇이 바뀌었는지 보여 줄 수 있습니다.'];
const clamp = (x: number) => Math.min(1, Math.max(0, x));

class Transitions extends Node {
  public constructor(private readonly clock: () => number) { super({}); }

  protected draw(ctx: CanvasRenderingContext2D) {
    const t = this.clock(), mode = Math.floor(t / seconds);
    const phase = clamp((t % seconds) / 7);
    const {text, box, path, dot} = board(ctx);
    text(headings[mode], -845, -338, 52, c.gold);
    const sides = mode === 0 ? ['A · 느린 페이드', 'B · 짧은 페이드']
      : mode === 1 ? ['A · 즉시 화면 전환', 'B · 옆으로 이어지는 스크롤']
      : ['A · 직선 와이프', 'B · 열쇠 구멍 와이프'];
    for (const [i, label] of sides.entries()) {
      const x = -845 + i * 874, ink = i === 0 ? c.teal : c.coral;
      const y = -184, width = 810, height = 289;
      text(label, x, -243, 43, ink);
      const drawRoom = (offset: number, next: boolean) => {
        const xx = x + offset;
        box(xx, y, width, height, next ? '#253830' : '#23332e');
        box(xx + (next ? 102 : 624), y + 84, 57, 149, c.grid);
        path([[xx + 30, 41], [xx + 780, 41]], c.muted, 4);
        box(xx + (next ? 651 : 93), y + 44, 102, 70, next ? c.gold : c.teal);
        dot(xx + (next ? 238 : 497), 34, 17, c.white);
        text(next ? '도착' : '출발', xx + 43, y + 37, 35);
      };
      ctx.save();
      ctx.beginPath(); ctx.rect(x, y, width, height); ctx.clip();
      if (mode === 0) {
        const half = i === 0 ? .27 : .11;
        drawRoom(0, phase >= .5);
        const opacity = clamp(1 - Math.abs(phase - .5) / half);
        ctx.globalAlpha = opacity;
        box(x, y, width, height, '#070a08');
        ctx.globalAlpha = 1;
      } else if (mode === 1 && i === 1) {
        const displacement = width * clamp((phase - .26) / .47);
        drawRoom(-displacement, false);
        drawRoom(width - displacement, true);
      } else if (mode === 2) {
        if (i === 0) {
          drawRoom(0, false);
          const reveal = clamp((phase - .21) / .53);
          ctx.beginPath();
          ctx.rect(x, y, width * reveal, height);
          ctx.clip();
          drawRoom(0, true);
        } else if (phase < .22) {
          drawRoom(0, false);
        } else if (phase < .72) {
          box(x, y, width, height, '#070a08');
          const size = 750 * (1 - clamp((phase - .22) / .46));
          const cx = x + 497, cy = 8;
          if (size > 0) {
            ctx.beginPath();
            ctx.arc(cx, cy - .18 * size, .63 * size, 0, Math.PI * 2);
            ctx.rect(cx - .32 * size, cy, .64 * size, .87 * size);
            ctx.clip();
            drawRoom(0, false);
          }
        } else {
          drawRoom(0, true);
        }
      } else {
        drawRoom(0, phase >= .5);
      }
      ctx.restore();
      const resume = mode === 0 ? (i === 0 ? .78 : .61) : .75;
      const from = mode === 0 && i === 0 ? .23 : .36;
      text('그림', x + 12, 149, 32, c.muted);
      text('입력', x + 12, 207, 32, c.muted);
      const a = x + 124, w = 631;
      path([[a, 149], [a + w, 149]], c.grid, 6);
      path([[a, 207], [a + w, 207]], c.grid, 6);
      path([[a + w * from, 149], [a + w * resume, 149]], c.gold, 9);
      path([[a, 207], [a + w * from, 207]], c.teal, 8);
      path([[a + w * resume, 207], [a + w, 207]], c.teal, 8);
      path([[a + w * phase, 130], [a + w * phase, 225]], c.white, 4);
      text(phase < from || phase >= resume ? '이동 가능' : '입력 제한', x + 16, 269, 35, ink);
    }
    text(conclusions[mode], -845, 347, 38);
  }
}

export default makeScene2D(function* (view) {
  view.fill(c.bg);
  const clock = createSignal(0);
  view.add(<Txt x={-846} y={-449} offsetX={-1} text="빠른 화면 전환" fontFamily="Malgun Gothic"
    fontSize={60} fontWeight={700} fill={c.gold}/>);
  view.add(<Txt x={846} y={-449} offsetX={1} text="전환 비교 도식" fontFamily="Malgun Gothic"
    fontSize={35} fill={c.muted}/>);
  view.add(new Transitions(clock));
  const end = headings.length * seconds;
  yield* tween(end, p => clock(Math.min(end - .001, p * end)));
});

import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {board, palette as c} from '../board';

const seconds = 8;
const headings = ['같은 끝 위치 · 다른 도달 시간', '같은 대시 · 다른 손동작', '대시를 공격 회피에 사용'];
const endings = ['짧은 입력 창 안에 경계를 통과하면 대시로 분기합니다.',
  '전용 버튼, 두 번 누르기, 빠르게 젖히기는 각각 다른 입력 약속입니다.',
  '공격 방향을 확인하고, 빈 쪽으로 빠져나가 다음 행동을 만듭니다.'];

class Flick extends Node {
  public constructor(private readonly clock: () => number) { super({}); }

  protected draw(ctx: CanvasRenderingContext2D) {
    const time = this.clock(), mode = Math.floor(time / seconds);
    const phase = Math.min(1, time % seconds / 6.8);
    const {text, box, path, dot} = board(ctx);
    text(headings[mode], -846, -342, 54, c.gold);
    const titles = mode === 0 ? ['A · 천천히 밀기', 'B · 빠르게 젖히기']
      : mode === 1 ? ['A · 방향키를 두 번 누름', 'B · 스틱을 한 번 빠르게 젖힘']
      : ['A · 공격 경로에 남음', 'B · 옆으로 대시'];
    for (const [i, title] of titles.entries()) {
      const x = -845 + i * 873, ink = i === 0 ? c.teal : c.coral;
      text(title, x, -242, 42, ink);
      box(x, -190, 807, 443);
      if (mode === 0) {
        const left = x + 287, floor = 142, width = 432;
        const response = (t: number) => Math.min(1, Math.max(0, (t - .10) / (i === 0 ? .75 : .23)));
        const pos = response(phase);
        const trigger = .73;
        const trace: [number, number][] = [];
        for (let step = 0; step <= 48; step++) {
          const t = Math.min(step / 48, phase);
          trace.push([left + width * t, floor - 225 * response(t)]);
          if (t >= phase) break;
        }
        box(left, floor - 232, width * .47, 231, '#263b30');
        path([[left, floor], [left + width, floor]], c.grid, 4);
        path([[left, floor - trigger * 225], [left + width, floor - trigger * 225]], c.gold, 4);
        text('경계', left + width - 66, floor - trigger * 225 - 23, 31, c.gold);
        text('입력 창', left + 15, floor + 35, 32, c.muted);
        text('시간', left + width - 68, floor + 35, 32, c.muted);
        path(trace, ink, 8);
        dot(x + 151, 31, 88, c.grid);
        dot(x + 151 + 59 * pos, 31, 29, ink);
        text(pos < trigger ? '기울이는 중' : i === 0 ? '걷기' : '대시', x + 70, 193, 43, ink);
      } else if (mode === 1) {
        const taps = i === 0 ? [.23, .48] : [.39];
        const active = phase >= taps.at(-1)!;
        for (const [j, tap] of taps.entries()) {
          const xx = x + 105 + j * 244;
          box(xx, -105, 183, 116, phase >= tap ? ink : c.grid);
          text(i === 0 ? '→' : '스틱 ↗', xx + 22, -46, 46, phase >= tap ? c.bg : c.white);
        }
        path([[x + 105, 88], [x + 699, 88]], c.grid, 8);
        dot(x + 105 + Math.max(0, phase - taps.at(-1)!) * 930, 88, 25, active ? ink : c.muted);
        text(active ? '대시 시작' : '입력 기다림', x + 105, 180, 38, ink);
      } else {
        const left = x + 111, hitY = 33;
        const avoid = i === 1 ? Math.min(1, Math.max(0, (phase - .53) / .26)) : 0;
        path([[left, hitY], [x + 733, hitY]], c.grid, 8);
        const missile = left + Math.min(1, phase / .86) * 606;
        dot(missile, hitY, 20, c.coral);
        const bodyX = x + 646, bodyY = hitY + 105 * avoid;
        path([[bodyX, hitY], [bodyX, bodyY]], c.teal, 8);
        const hit = i === 0 && Math.abs(missile - bodyX) < 44;
        dot(bodyX, bodyY, 30, hit ? c.gold : c.teal);
        text(i === 0 ? '공격 경로 위' : avoid > .5 ? '경로 밖에서 다음 입력' : '빈 쪽으로 조작', x + 100, 192, 38, ink);
      }
    }
    text(endings[mode], -846, 320, 39);
  }
}

export default makeScene2D(function* (view) {
  view.fill(c.bg);
  const clock = createSignal(0);
  view.add(<Txt x={-846} y={-451} offsetX={-1} text="Flick Input (플릭 입력)" fontFamily="Malgun Gothic"
    fontSize={61} fontWeight={700} fill={c.gold}/>);
  view.add(<Txt x={846} y={-451} offsetX={1} text="원리 도식" fontFamily="Malgun Gothic"
    fontSize={35} fill={c.muted}/>);
  view.add(new Flick(clock));
  const end = seconds * headings.length;
  yield* tween(end, p => clock(Math.min(end - .001, p * end)));
});

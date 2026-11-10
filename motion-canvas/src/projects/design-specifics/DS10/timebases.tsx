import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {board, palette as c} from '../board';

const seconds = 8;
const labels = ['같은 실제 시간 · 서로 다른 처리 횟수', '시계에 따라 달라지는 허기', '업데이트에서 실제로 바뀐 범위', '같은 시작 상태 · 같은 실시간'];
const conclusions = ['업데이트 횟수를 게임 시간으로 쓰면 빠른 기기에서 게임도 빨라집니다.',
  '최종 기기에서 같은 시간이 흐른 뒤 남은 양을 비교합니다.',
  '기록은 변경 범위를 보여 줍니다. 최초 난도의 원인은 따로 검증합니다.',
  '실제 시간으로 고정한 빌드는 표시가 더 부드러워져도 같은 결과에 도달합니다.'];

class Timebases extends Node {
  public constructor(private readonly clock: () => number) { super({}); }

  protected draw(ctx: CanvasRenderingContext2D) {
    const time = this.clock(), mode = Math.floor(time / seconds);
    const progress = Math.min(1, time % seconds / 7);
    const {text, box, path, dot} = board(ctx);
    text(labels[mode], -845, -337, 53, c.gold);
    const titles = mode === 2 ? ['A · 도전자 전투', 'B · 모험 모드'] : ['A · 기존 속도', 'B · 처리량 증가'];
    for (const [i, title] of titles.entries()) {
      const x = -845 + i * 873, ink = i === 0 ? c.teal : c.coral;
      text(title, x, -243, 43, ink);
      box(x, -188, 807, 442);
      if (mode === 2) {
        const active = progress >= (i === 0 ? .26 : .56);
        const base = x + 93, y = 34;
        path([[base, y], [x + 712, y]], c.grid, 8);
        dot(x + 365, y, 18, active ? ink : c.muted);
        text(i === 0 ? '도전자 난도 조정' : '아주 쉬움 난도 추가', base, -62, 46, active ? ink : c.muted);
        text(i === 0 ? '버전 1.2.0' : '버전 4.0.0', base, 134, 37, c.white);
      } else {
        const elapsed = Math.min(1, progress * (i === 0 || mode === 3 ? .78 : 1.36));
        const remaining = Math.max(0, 1 - elapsed);
        const ticks = i === 0 ? 8 : 14;
        const base = x + 76, usable = 654;
        text('같은 실제 시간', base, -123, 36, c.white);
        path([[base, -76], [base + usable, -76]], c.grid, 5);
        path([[base, -76], [base + usable * progress, -76]], c.gold, 5);
        for (let tick = 0; tick <= ticks; tick++) {
          const at = base + usable * tick / ticks;
          path([[at, -90], [at, -62]], tick <= ticks * progress ? ink : c.grid, 4);
        }
        if (mode === 0) {
          for (let column = 0; column < 5; column++) {
            for (let row = 0; row < 4; row++) {
              const fall = Math.floor(elapsed * 6) % 4;
              if (row === 3 || (column === 2 && row === fall)) {
                box(base + 55 + column * 57, -32 + row * 43, 45, 32, row === 3 ? c.grid : ink);
              }
            }
          }
        }
        const left = mode === 0 ? base + 400 : base;
        const width = mode === 0 ? 245 : usable;
        text(mode === 1 ? '허기 도달까지' : '남은 게임 시간', left, mode === 0 ? 5 : 28, 35, c.white);
        box(left, 77, width, 21, c.grid);
        box(left, 77, width * remaining, 21, ink);
        text(remaining === 0 ? '같은 시간인데 이미 끝남' : mode === 3 ? '시간 기준으로 같은 결과' : '게임의 시계는 계속 흐름',
          base, 189, 34, ink);
      }
    }
    text(conclusions[mode], -845, 320, 37);
  }
}

export default makeScene2D(function* (view) {
  view.fill(c.bg);
  const clock = createSignal(0);
  view.add(<Txt x={-845} y={-451} offsetX={-1} text="최적화 뒤에 바뀐 게임 시간" fontFamily="Malgun Gothic"
    fontSize={59} fontWeight={700} fill={c.gold}/>);
  view.add(<Txt x={845} y={-451} offsetX={1} text="시간 기준 비교 도식" fontFamily="Malgun Gothic"
    fontSize={35} fill={c.muted}/>);
  view.add(new Timebases(clock));
  const end = labels.length * seconds;
  yield* tween(end, p => clock(Math.min(end - .001, p * end)));
});

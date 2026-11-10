import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {board, palette as c} from '../board';

const seconds = 8;
const headings = ['배운 곳과 처음 쓰는 곳 사이', '표적 위치가 필요한 행동을 알려 줌', '해 보고 아는 플레이어는 계속 진행'];
const conclusions = ['설명, 행동, 결과가 가까이 있으면 배운 것을 바로 확인할 수 있습니다.',
  '바닥과 공중에 둔 표적이 서로 다른 입력을 유도합니다.',
  '실험할 공간을 주면서 이미 익숙한 사람의 흐름을 이어 줍니다.'];

class Tutorial extends Node {
  public constructor(private readonly clock: () => number) { super({}); }

  protected draw(ctx: CanvasRenderingContext2D) {
    const time = this.clock(), mode = Math.floor(time / seconds);
    const progress = Math.min(1, time % seconds / 6.7);
    const {text, box, path, dot} = board(ctx);
    text(headings[mode], -845, -336, 53, c.gold);
    if (mode === 0) {
      const lanes = [
        ['읽고 나중에 하기', [.12, .72, .86]],
        ['별도 연습장에서 하기', [.12, .37, .59]],
        ['플레이 중 바로 하기', [.12, .24, .35]],
      ] as const;
      for (const [i, [label, marks]] of lanes.entries()) {
        const y = -203 + i * 168, start = -320, width = 1070;
        text(label, -840, y, 41, i === 2 ? c.teal : c.white);
        path([[start, y], [start + width, y]], c.grid, 9);
        path([[start, y], [start + width * progress, y]], c.muted, 5);
        for (const [j, mark] of marks.entries()) {
          const x = start + width * mark;
          const ink = [c.gold, c.teal, c.coral][j];
          dot(x, y, 17, progress >= mark ? ink : c.grid);
          text(['설명', '행동', '결과'][j], x - 32, y + 48, 34, ink);
        }
      }
    } else {
      const options = mode === 1 ? ['A · 낮은 표적', 'B · 높은 표적'] : ['A · 처음 해 보는 플레이어', 'B · 이미 아는 플레이어'];
      for (const [i, label] of options.entries()) {
        const x = -845 + i * 875;
        const ink = i === 0 ? c.teal : c.coral;
        text(label, x, -245, 42, ink);
        box(x, -186, 810, 439);
        path([[x + 55, 143], [x + 749, 143]], c.grid, 9);
        const high = mode === 1 && i === 1;
        const amount = mode === 2 && i === 0 ? Math.max(0, (progress - .28) / .72) : progress;
        const actorX = x + 112 + 543 * amount;
        const lift = high ? Math.sin(Math.PI * Math.min(1, Math.max(0, (amount - .25) / .67))) * 152
          : mode === 2 ? Math.sin(Math.PI * Math.min(1, Math.max(0, (amount - .49) / .44))) * 100 : 0;
        const target = [x + 535, 102 - Number(high) * 135] as const;
        const reached = amount > .76;
        dot(actorX, 104 - lift, 26, ink);
        if (mode === 1) {
          dot(target[0], target[1], reached ? 16 : 26, reached ? c.muted : c.gold);
          if (reached) text('명중', target[0] + 39, target[1], 36, c.gold);
          text(high ? '점프 → 공중 공격' : '다가가기 → 공격', x + 60, 208, 38, ink);
        } else {
          box(x + 540, 57, 68, 85, reached ? c.teal : c.grid);
          text('다음 장소', x + 602, 36, 34, c.gold);
          if (i === 0 && amount < .76) text('점프를 직접 눌러 보기', x + 66, -92, 39, c.white);
          text(reached ? '연습 뒤 이어서 이동' : i === 0 ? '짧은 안내를 보고 시도' : '바로 지나갈 수 있음', x + 65, 209, 36, ink);
        }
      }
    }
    text(conclusions[mode], -845, 320, 39);
  }
}

export default makeScene2D(function* (view) {
  view.fill(c.bg);
  const clock = createSignal(0);
  view.add(<Txt x={-845} y={-448} offsetX={-1} text="플레이하면서 배우는 조작" fontFamily="Malgun Gothic"
    fontSize={61} fontWeight={700} fill={c.gold}/>);
  view.add(<Txt x={845} y={-448} offsetX={1} text="원리 도식" fontFamily="Malgun Gothic"
    fontSize={35} fill={c.muted}/>);
  view.add(new Tutorial(clock));
  const end = seconds * headings.length;
  yield* tween(end, p => clock(Math.min(end - .001, p * end)));
});

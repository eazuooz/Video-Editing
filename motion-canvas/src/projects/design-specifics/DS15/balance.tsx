import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {board, palette as c} from '../board';

const seconds = 8;
const headings = ['같은 사거리로 맞추기 · 대응할 틈을 만들기', '같은 도구로 겨루기 · 다른 도구로 겨루기', '전체 수치와 한 매치업을 구분하기'];
const conclusions = ['장점을 살리고 빈틈을 보여 주면, 각 캐릭터를 고를 이유가 남습니다.',
  '서로 다른 캐릭터는 위치와 타이밍에 따라 각자 유리한 상황을 만듭니다.',
  '전체 승률로 먼저 살핀 뒤, 실제 매치업에서 선택이 막히는지 확인합니다.'];

class Balance extends Node {
  public constructor(private readonly clock: () => number) { super({}); }

  protected draw(ctx: CanvasRenderingContext2D) {
    const time = this.clock(), mode = Math.floor(time / seconds);
    const phase = Math.min(1, time % seconds / 6.6);
    const {text, box, path, dot} = board(ctx);
    text(headings[mode], -845, -339, 51, c.gold);
    const choices = mode === 2 ? ['A · 당시 전체 온라인 표본', 'B · 따로 확인할 매치업']
      : mode === 1 ? ['A · 미러 매치', 'B · 사거리가 다른 매치업']
      : ['A · 사거리를 똑같이 줄임', 'B · 사거리와 대응할 틈을 남김'];
    for (const [i, title] of choices.entries()) {
      const x = -846 + i * 875, ink = i === 0 ? c.teal : c.coral;
      text(title, x, -243, 42, ink);
      box(x, -186, 812, 442);
      if (mode === 2) {
        if (i === 0) {
          const start = x + 106;
          path([[start, 48], [start + 597, 48]], c.grid, 10);
          path([[start + 95, 48], [start + 555, 48]], c.teal, 13);
          dot(start + 95, 48, 17, c.teal);
          dot(start + 555, 48, 17, c.teal);
          text('47.18%', start + 24, -3, 40, c.teal);
          text('51.43%', start + 486, -3, 40, c.teal);
          text('발표 당시 파이터 87명', start, 157, 38, c.white);
        } else {
          const rows = ['파이터 조합', '플레이어 숙련도', '게임 버전과 조건'];
          for (const [j, row] of rows.entries()) {
            const at = -108 + j * 112;
            dot(x + 105, at, 14, phase > .19 + .25 * j ? c.coral : c.grid);
            text(row, x + 147, at, 42);
          }
        }
      } else {
        const left = x + 170, origin = x + 641;
        const recovery = i === 1 && phase >= .56;
        const right = origin - (recovery ? Math.min(1, (phase - .56) / .41) * 205 : 0);
        const long = i === 1 ? 340 : 185;
        path([[x + 63, 139], [x + 747, 139]], c.grid, 8);
        path([[left, 75], [left + long, 75]], recovery ? c.grid : c.teal, 10);
        path([[right, 101], [right - 185, 101]], c.coral, 10);
        dot(left, 127, 27, c.teal);
        dot(right, 127, 27, c.coral);
        text(recovery ? '헛친 뒤 접근' : i === 0 ? '공격 범위가 같음' : '한쪽이 멀리 닿음', x + 82, -62, 44, c.white);
        text(i === 1 ? '기술이 빗나가면 다음 행동까지 여유가 생김' : '서로 같은 거리에서 같은 공격을 씀', x + 82, 200, 35, ink);
      }
    }
    text(conclusions[mode], -845, 347, 38);
  }
}

export default makeScene2D(function* (view) {
  view.fill(c.bg);
  const clock = createSignal(0);
  view.add(<Txt x={-846} y={-449} offsetX={-1} text="개성이 있는 밸런스" fontFamily="Malgun Gothic"
    fontSize={60} fontWeight={700} fill={c.gold}/>);
  view.add(<Txt x={846} y={-449} offsetX={1} text="원리 도식과 공개 범위" fontFamily="Malgun Gothic"
    fontSize={35} fill={c.muted}/>);
  view.add(new Balance(clock));
  const end = headings.length * seconds;
  yield* tween(end, p => clock(Math.min(end - .001, p * end)));
});

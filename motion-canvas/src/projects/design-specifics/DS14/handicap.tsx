import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {board, palette as c} from '../board';

const seconds = 8;
const headings = ['뒤처진 사람에게 한 번 더 선택 주기', '캐릭터의 조건과 경기 전체의 규칙', '같이 정하는 규칙과 처음부터 보이는 규칙'];
const conclusions = ['따라갈 기회를 주면 마지막까지 선택이 남습니다. 승리는 조작에 달려 있습니다.',
  '한 캐릭터의 정체성과 모두가 쓰는 경기 설정을 구분합니다.',
  '처음 만난 사람끼리도 어떤 설정으로 겨루는지 경기 전에 알 수 있어야 합니다.'];

class Handicap extends Node {
  public constructor(private readonly clock: () => number) { super({}); }

  protected draw(ctx: CanvasRenderingContext2D) {
    const time = this.clock(), mode = Math.floor(time / seconds);
    const progress = Math.min(1, (time % seconds) / 6.8);
    const {text, box, path, dot} = board(ctx);
    text(headings[mode], -846, -337, 51, c.gold);
    const sides = mode === 0 ? ['A · 실력 차이를 그대로 유지', 'B · 뒤쪽에 추격 기회 제공']
      : mode === 1 ? ['A · 캐릭터 고유 조건', 'B · 공통 경기 설정']
      : ['A · 친구와 함께 정함', 'B · 온라인에서는 먼저 표시'];
    for (const [i, title] of sides.entries()) {
      const x = -845 + i * 873, ink = i === 0 ? c.teal : c.coral;
      text(title, x, -242, 42, ink);
      box(x, -187, 809, 442);
      if (mode === 0) {
        const start = x + 92, lane = 609;
        const leader = Math.min(1, .23 + .77 * progress);
        const helper = i === 1 ? .21 * Math.max(0, (progress - .48) / .52) : 0;
        const runner = .07 + .53 * progress + helper;
        const bounds = [[start, 29], [start + lane, 29]] as [number, number][];
        path(bounds, c.grid, 7);
        path([[start, 116], [start + lane, 116]], c.grid, 7);
        path([[start + lane, -4], [start + lane, 145]], c.gold, 6);
        dot(start + lane * leader, 29, 20, c.teal);
        dot(start + lane * runner, 116, 20, c.coral);
        text('선두', start, -30, 35, c.teal);
        text('추격', start, 170, 35, c.coral);
        if (i === 1 && progress > .48) text('아이템을 쓸 타이밍 선택', start + 115, 209, 34, c.gold);
      } else if (mode === 1) {
        const options = i === 0 ? ['선택한 파이터', '그 캐릭터의 발동 조건', '고유 기술이 열림']
          : ['경기 시작 전에 선택', '아이템 · 스테이지 · 게이지', '모든 참가자에게 적용'];
        for (const [j, option] of options.entries()) {
          const y = -117 + j * 130;
          const live = progress >= .18 + .25 * j;
          dot(x + 90, y, 16, live ? ink : c.grid);
          if (j < 2) path([[x + 90, y + 21], [x + 90, y + 104]], c.grid, 5);
          text(option, x + 133, y, 41, live ? c.white : c.muted);
        }
      } else {
        const options = i === 0 ? ['같이 할 사람과 약속', '어떤 행동에 제한을 둘까?', '모두 동의하면 시작']
          : ['모드가 보여 주는 규칙', '적용 중인 항목 확인', '규칙을 알고 매치 시작'];
        for (const [j, option] of options.entries()) {
          const y = -132 + j * 119;
          const active = progress >= .15 + .26 * j;
          box(x + 74, y, 651, 83, active ? '#2b4b3b' : '#1a2a21');
          text(option, x + 104, y + 41, 40, active ? c.white : c.muted);
        }
      }
    }
    text(conclusions[mode], -845, 346, 36);
  }
}

export default makeScene2D(function* (view) {
  view.fill(c.bg);
  const clock = createSignal(0);
  view.add(<Txt x={-846} y={-449} offsetX={-1} text="Handicap System (핸디캡 시스템)" fontFamily="Malgun Gothic"
    fontSize={59} fontWeight={700} fill={c.gold}/>);
  view.add(<Txt x={846} y={-449} offsetX={1} text="원리 도식" fontFamily="Malgun Gothic"
    fontSize={35} fill={c.muted}/>);
  view.add(new Handicap(clock));
  const end = headings.length * seconds;
  yield* tween(end, p => clock(Math.min(end - .001, p * end)));
});

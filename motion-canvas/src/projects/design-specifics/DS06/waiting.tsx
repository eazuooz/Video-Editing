import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';

const colors = {bg: '#0a110d', board: '#132019', lines: '#374f42', white: '#f5f4ec',
  title: '#f2d786', action: '#86d1c3', clue: '#edc982', wait: '#c3d1c7', empty: '#f1a08a'};
const lanes = [
  {title: 'A · 다음 행동이 일찍 열림', marks: [0, .23, .42, .52, .52, 1]},
  {title: 'B · 조작이 열리기 전에 공백이 남음', marks: [0, .23, .42, .52, .77, 1]},
];
const phases = [
  {title: '조작 가능', color: colors.action}, {title: '단서 공개', color: colors.clue},
  {title: '로딩', color: colors.wait}, {title: '공백', color: colors.empty},
  {title: '조작 가능', color: colors.action},
];

class WaitingStudy extends Node {
  public constructor(private readonly cursor: () => number) { super({}); }

  protected draw(ctx: CanvasRenderingContext2D) {
    const current = this.cursor();
    const x = -842, width = 1684;
    const txt = (value: string, px: number, y: number, size: number, color: string) => {
      ctx.font = `600 ${size}px "Malgun Gothic", sans-serif`;
      ctx.textBaseline = 'middle';
      ctx.fillStyle = color;
      ctx.fillText(value, px, y);
    };
    for (const [lane, {title, marks}] of lanes.entries()) {
      const y = -265 + lane * 274;
      txt(title, x, y - 41, 44, lane === 0 ? colors.action : colors.empty);
      ctx.fillStyle = colors.board;
      ctx.fillRect(x, y, width, 169);
      for (const [i, phase] of phases.entries()) {
        const start = marks[i], end = marks[i + 1];
        if (start === end) continue;
        const at = x + start * width;
        const active = current >= start && current < end;
        ctx.fillStyle = phase.color;
        ctx.globalAlpha = active ? 1 : .63;
        ctx.fillRect(at + 2, y + 22, (end - start) * width - 4, 14);
        ctx.globalAlpha = 1;
        txt(phase.title, at + 12, y + 81, 36, active ? colors.white : phase.color);
      }
      ctx.fillStyle = colors.white;
      ctx.fillRect(x + Math.min(width - 4, current * width), y + 6, 4, 148);
      const canAct = current < marks[1] || current >= marks[4];
      txt(canAct ? '입력 가능' : '다음 입력을 기다림', x + 12, y + 139, 34, canAct ? colors.action : colors.wait);
    }
    txt('전체 길이는 같습니다. B는 로딩이 끝난 뒤에도 입력을 기다립니다.', x, 346, 40, colors.white);
  }
}

export default makeScene2D(function* (view) {
  view.fill(colors.bg);
  const clock = createSignal(0);
  view.add(<Txt x={-845} y={-449} offsetX={-1} text="플레이어가 기다리는 시간" fontFamily="Malgun Gothic"
    fontSize={61} fontWeight={700} fill={colors.title}/>);
  view.add(<Txt x={845} y={-449} offsetX={1} text="같은 길이 · 다른 선택 시점" fontFamily="Malgun Gothic"
    fontSize={35} fill={colors.wait}/>);
  view.add(new WaitingStudy(clock));
  yield* tween(10, progress => clock(Math.min(1, progress / .91)));
});

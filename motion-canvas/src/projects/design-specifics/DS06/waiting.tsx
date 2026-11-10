import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';

const colors = {bg: '#0a110d', board: '#132019', lines: '#374f42', white: '#f5f4ec',
  title: '#f2d786', action: '#86d1c3', clue: '#edc982', wait: '#c3d1c7', empty: '#f1a08a'};
const studySeconds = 10;
const studies = [
  {heading: '천천히 움직이는 동안 읽는 정보',
    takeaway: '이동 속도가 느려도 새 단서가 보이고 입력이 이어지면 판단할 수 있습니다.',
    lanes: [
      {title: 'A · 복도를 살피며 이동', marks: [0, .31, .68, .68, .68, 1], continuousInput: true},
      {title: 'B · 문을 열고 다음 조작 대기', marks: [0, .28, .59, .59, .75, 1]},
    ]},
  {heading: '로딩 완료와 입력 가능 시점',
    takeaway: '로딩이 끝난 위치와 입력이 돌아오는 위치를 따로 기록합니다.',
    lanes: [
      {title: 'A · 로딩 직후 입력 재개', marks: [0, .23, .42, .56, .56, 1]},
      {title: 'B · 로딩 뒤에도 입력 제한', marks: [0, .23, .42, .56, .79, 1]},
    ]},
  {heading: '연출이 단서를 주는 구간',
    takeaway: '단서가 나온 뒤 남은 구간에 새 정보가 더해지는지 살핍니다.',
    lanes: [
      {title: 'A · 단서 뒤에 다음 행동', marks: [0, .23, .63, .63, .63, 1]},
      {title: 'B · 단서 뒤에 정보 없는 화면', marks: [0, .23, .63, .63, .86, 1]},
    ]},
  {heading: '같은 길이 · 다른 선택 시점',
    takeaway: '같은 길이에서도 다음 선택이 일찍 열리면 시간의 밀도가 달라집니다.',
    lanes: [
      {title: 'A · 다음 행동이 일찍 열림', marks: [0, .23, .42, .54, .54, 1]},
      {title: 'B · 조작이 열리기 전에 공백이 남음', marks: [0, .23, .42, .54, .79, 1]},
    ]},
];
const phases = [
  {title: '조작 가능', color: colors.action}, {title: '단서 공개', color: colors.clue},
  {title: '로딩', color: colors.wait}, {title: '공백', color: colors.empty},
  {title: '조작 가능', color: colors.action},
];

class WaitingStudy extends Node {
  public constructor(private readonly cursor: () => number) { super({}); }

  protected draw(ctx: CanvasRenderingContext2D) {
    const time = this.cursor();
    const {heading, lanes, takeaway} = studies[Math.floor(time / studySeconds)];
    const current = Math.min(1, (time % studySeconds) / 9.1);
    const x = -842, width = 1684;
    const txt = (value: string, px: number, y: number, size: number, color: string) => {
      ctx.font = `600 ${size}px "Malgun Gothic", sans-serif`;
      ctx.textBaseline = 'middle';
      ctx.fillStyle = color;
      ctx.fillText(value, px, y);
    };
    txt(heading, -842, -367, 44, colors.white);
    for (const [lane, {title, marks, continuousInput}] of lanes.entries()) {
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
      const canAct = continuousInput || current < marks[1] || current >= marks[4];
      txt(canAct ? '입력 가능' : '다음 입력을 기다림', x + 12, y + 139, 34, canAct ? colors.action : colors.wait);
    }
    txt(takeaway, x, 346, 40, colors.white);
  }
}

export default makeScene2D(function* (view) {
  view.fill(colors.bg);
  const clock = createSignal(0);
  view.add(<Txt x={-845} y={-449} offsetX={-1} text="플레이어가 기다리는 시간" fontFamily="Malgun Gothic"
    fontSize={61} fontWeight={700} fill={colors.title}/>);
  view.add(<Txt x={845} y={-449} offsetX={1} text="원리 도식" fontFamily="Malgun Gothic"
    fontSize={35} fill={colors.wait}/>);
  view.add(new WaitingStudy(clock));
  const duration = studies.length * studySeconds;
  yield* tween(duration, progress => clock(Math.min(duration - .001, duration * progress)));
});

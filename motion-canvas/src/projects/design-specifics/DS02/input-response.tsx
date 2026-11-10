import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';

const palette = {
  background: '#0a110d', field: '#101b16', grid: '#345046', white: '#f5f4ec',
  muted: '#bbcdc4', heading: '#f2d786', left: '#81d8cc', right: '#f2a08b',
};

const press = 0.75;
const release = 2.85;
const maxSpeed = 132;
const baseline = {rise: 0.52, fall: 0.42, delay: 0};
const experiments = [
  {title: '가속 · 움직이기 시작한 뒤', change: '가속을 낮춤',
    result: '출발 시점은 같고, 오른쪽의 속도가 더 천천히 붙습니다.',
    response: {...baseline, rise: 1.75}},
  {title: '감속 · 버튼을 놓은 뒤', change: '감속을 낮춤',
    result: '놓는 시점은 같고, 오른쪽은 더 멀리 움직이고 멈춥니다.',
    response: {...baseline, fall: 1.44}},
  {title: '입력 지연 · 첫 움직임 전', change: '입력 반응을 늦춤',
    result: '오른쪽은 출발만 늦고, 출발한 뒤 속도가 붙는 모양은 같습니다.',
    response: {...baseline, delay: 0.5}},
];

function responseAt(time: number, {rise, fall, delay}: typeof baseline) {
  const running = Math.max(0, time - press - delay);
  const ramp = Math.min(rise, running);
  const cruise = Math.min(Math.max(0, running - rise), release - press - rise);
  const braking = Math.min(fall, Math.max(0, time - release - delay));
  const distance = maxSpeed * (ramp ** 2 / (2 * rise) + cruise + braking - braking ** 2 / (2 * fall));
  const speed = time >= release + delay ? maxSpeed * (1 - braking / fall) : maxSpeed * ramp / rise;
  return {distance, speed};
}

class ResponseBoard extends Node {
  public constructor(private readonly clock: () => number) {
    super({});
  }

  protected draw(ctx: CanvasRenderingContext2D) {
    const duration = 6;
    const time = this.clock();
    const experiment = experiments[Math.min(2, Math.floor(time / duration))];
    const elapsed = Math.min(4.75, time % duration);
    const label = (value: string, x: number, y: number, size: number, color: string) => {
      ctx.font = `600 ${size}px "Malgun Gothic", sans-serif`;
      ctx.textBaseline = 'middle';
      ctx.fillStyle = color;
      ctx.fillText(value, x, y);
    };
    const line = (x1: number, y1: number, x2: number, y2: number, color: string, width = 3) => {
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    };

    label(experiment.title, -848, -326, 52, palette.heading);
    const pressed = elapsed >= press && elapsed < release;
    label(pressed ? '방향 버튼 누르는 중' : elapsed >= release ? '방향 버튼 뗌' : '방향 버튼 입력 전',
      -846, -242, 37, pressed ? palette.white : palette.muted);
    for (const [index, response] of [baseline, experiment.response].entries()) {
      const x = -850 + 875 * index;
      const width = 820;
      const origin = x + 88;
      const color = index === 0 ? palette.left : palette.right;
      const state = responseAt(elapsed, response);
      label(index === 0 ? 'A · 기본' : `B · ${experiment.change}`, x, -154, 44, color);
      ctx.fillStyle = palette.field;
      ctx.fillRect(x, -112, width, 394);
      for (let mark = 0; mark <= 6; mark++) {
        const tick = origin + mark * 106;
        line(tick, -92, tick, -9, palette.grid);
      }
      line(origin, -10, x + width - 72, -10, palette.muted);
      line(origin, -50, origin + state.distance * 1.66, -50, color, 7);
      ctx.fillStyle = color;
      ctx.fillRect(origin + state.distance * 1.66 - 13, -76, 26, 53);
      label('이동 거리', origin, 24, 31, palette.muted);
      label('속력', x + 16, 90, 30, palette.white);
      const step = 127;
      const floor = 211;
      line(origin, floor, origin + step * 5, floor, palette.grid);
      for (const [point, text] of [[press, '누름'], [release, '놓음']] as const) {
        const px = origin + point * step;
        line(px, 91, px, floor, palette.grid);
        label(text, px - 22, 248, 29, palette.muted);
      }
      line(origin + elapsed * step, 86, origin + elapsed * step, floor, palette.white, 2);
      ctx.beginPath();
      ctx.moveTo(origin, floor);
      for (let t = 0; t < elapsed + 0.016; t += 0.016) {
        const point = Math.min(t, elapsed);
        ctx.lineTo(origin + point * step, floor - responseAt(point, response).speed * 0.83);
      }
      ctx.strokeStyle = color;
      ctx.lineWidth = 7;
      ctx.stroke();
    }
    label(experiment.result, -848, 347, 37, palette.white);
  }
}

export default makeScene2D(function* (view) {
  view.fill(palette.background);
  const clock = createSignal(0);
  view.add(<Txt x={-850} y={-450} offsetX={-1} text="버튼의 무게" fontFamily="Malgun Gothic"
    fontSize={60} fontWeight={700} fill={palette.heading}/>);
  view.add(<Txt x={850} y={-450} offsetX={1} text="같은 버튼 · 반응 비교" fontFamily="Malgun Gothic"
    fontSize={35} fill={palette.muted}/>);
  view.add(new ResponseBoard(clock));
  yield* tween(18, progress => clock(Math.min(17.999, progress * 18)));
});

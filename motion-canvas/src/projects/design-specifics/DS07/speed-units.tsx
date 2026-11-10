import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';

const color = {bg: '#0a110d', field: '#132219', grid: '#436256', white: '#f5f4ec',
  heading: '#f2d786', teal: '#83d9cd', coral: '#f3a08a', muted: '#b8ccbe'};
const duration = 8;

class SpeedStudy extends Node {
  public constructor(private readonly clock: () => number) { super({}); }

  protected draw(ctx: CanvasRenderingContext2D) {
    const time = this.clock();
    const world = time >= duration && time < 2 * duration;
    const view = time >= 2 * duration;
    const passed = Math.min(1, (time % duration) / 7);
    const label = (text: string, x: number, y: number, size: number, pigment: string) => {
      ctx.font = `600 ${size}px "Malgun Gothic", sans-serif`;
      ctx.textBaseline = 'middle';
      ctx.fillStyle = pigment;
      ctx.fillText(text, x, y);
    };
    const heading = view ? 'Screen Speed (화면상 속력)'
      : world ? 'World Speed (월드 속력)' : 'Pixels per Frame (프레임당 픽셀)';
    label(heading, -848, -335, 54, color.heading);
    for (let i = 0; i < 2; i++) {
      const x = -848 + i * 875;
      const pigment = i === 0 ? color.teal : color.coral;
      const width = view || world || i === 1 ? 807 : 572;
      const distance = width - 105;
      const steps = world ? (i === 0 ? 8 : 16) : 16;
      const stride = world ? (i === 0 ? 80 : 40) : 49;
      const elapsedSteps = Math.floor(steps * passed);
      const zoom = i === 0 ? .61 : 1.18;
      const displacement = view ? passed * 520 * zoom : Math.min(distance, elapsedSteps * stride);
      const head = x + 52 + displacement;
      const title = view ? (i === 0 ? 'A · 멀리서 봄' : 'B · 가까이서 봄')
        : world ? (i === 0 ? '업데이트 간격이 긴 경우' : '업데이트 간격이 짧은 경우')
        : (i === 0 ? '폭이 좁은 화면' : '폭이 넓은 화면');
      label(title, x, -237, 42, pigment);
      ctx.fillStyle = color.field;
      ctx.fillRect(x, -181, width, 378);
      ctx.strokeStyle = color.grid;
      ctx.lineWidth = 3;
      for (let tick = 0; tick < distance; tick += 49) {
        ctx.beginPath();
        ctx.moveTo(x + 52 + tick, -165);
        ctx.lineTo(x + 52 + tick, 178);
        ctx.stroke();
      }
      ctx.fillStyle = pigment;
      ctx.fillRect(x + 52, 81, Math.max(2, displacement), 7);
      ctx.beginPath();
      ctx.arc(head, 27, view ? 29 * zoom : 26, 0, Math.PI * 2);
      ctx.fill();
      const status = view ? (i === 0 ? '화면에서 적게 움직임' : '화면에서 많이 움직임')
        : world ? '같은 초당 거리' : displacement >= distance ? '반대편에 도착' : '같은 픽셀 간격으로 이동 중';
      label(status, x, 252, 36, pigment);
    }
    const takeaway = view ? '실제로 간 거리는 같습니다. 카메라만 바꿨습니다.'
      : world ? '이동 거리 = 월드 속력 × 경과 시간' : '한 번에 같은 거리만큼 움직여도, 화면 폭이 좁으면 먼저 도착합니다.';
    label(takeaway,
      -848, 320, 38, color.white);
  }
}

export default makeScene2D(function* (view) {
  view.fill(color.bg);
  const time = createSignal(0);
  view.add(<Txt x={-847} y={-449} offsetX={-1} text="속도를 어떤 단위로 말할까" fontFamily="Malgun Gothic"
    fontSize={60} fontWeight={700} fill={color.heading}/>);
  view.add(<Txt x={847} y={-449} offsetX={1} text="원리 도식" fontFamily="Malgun Gothic"
    fontSize={35} fill={color.muted}/>);
  view.add(new SpeedStudy(time));
  yield* tween(duration * 3, p => time(Math.min(duration * 3 - .001, p * duration * 3)));
});

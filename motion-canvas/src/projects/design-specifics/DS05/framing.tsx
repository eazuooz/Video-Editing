import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';

const color = {
  background: '#0a110d', field: '#14211a', lines: '#3d5d51', white: '#f5f4ec',
  mute: '#bed0c4', gold: '#f2d786', teal: '#81d8cc', coral: '#f2a08b',
};
const period = 8;

class CameraStudy extends Node {
  public constructor(private readonly clock: () => number) {
    super({});
  }

  protected draw(ctx: CanvasRenderingContext2D) {
    const time = this.clock();
    const ahead = time >= period && time < 2 * period;
    const evade = time >= 2 * period;
    const phase = Math.min(1, (time % period) / 6.5);
    const lift = 148 * Math.sin(Math.PI * phase);
    const text = (value: string, x: number, y: number, size: number, pigment: string) => {
      ctx.fillStyle = pigment;
      ctx.font = `600 ${size}px "Malgun Gothic", sans-serif`;
      ctx.textBaseline = 'middle';
      ctx.fillText(value, x, y);
    };
    const rule = (x: number, y: number, dx: number, dy: number, pigment: string, width = 4) => {
      ctx.strokeStyle = pigment;
      ctx.lineWidth = width;
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x + dx, y + dy);
      ctx.stroke();
    };
    const runner = (x: number, foot: number, pigment: string) => {
      const step = Math.sin(phase * Math.PI * 15) * (ahead || evade ? 24 : 13);
      ctx.fillStyle = pigment;
      ctx.fillRect(x - 17, foot - 93, 34, 51);
      ctx.beginPath();
      ctx.arc(x, foot - 107, 17, 0, Math.PI * 2);
      ctx.fill();
      rule(x, foot - 45, -18 + step, 42, pigment, 12);
      rule(x, foot - 45, 18 - step, 42, pigment, 12);
    };
    const mech = (x: number, foot: number, pigment: string) => {
      ctx.fillStyle = pigment;
      ctx.beginPath();
      ctx.moveTo(x - 48, foot - 104);
      ctx.lineTo(x - 33, foot - 122);
      ctx.lineTo(x + 33, foot - 122);
      ctx.lineTo(x + 49, foot - 104);
      ctx.lineTo(x + 28, foot - 62);
      ctx.lineTo(x - 28, foot - 62);
      ctx.closePath();
      ctx.fill();
      ctx.fillStyle = color.field;
      ctx.fillRect(x - 17, foot - 112, 34, 18);
      rule(x - 26, foot - 62, -15, 51, pigment, 15);
      rule(x + 26, foot - 62, 15, 51, pigment, 15);
      rule(x - 47, foot - 99, -25, 27, pigment, 13);
      rule(x + 46, foot - 101, 43, -10, pigment, 13);
    };

    text(evade ? 'Evasion Framing (회피가 읽히는 구도)'
      : ahead ? 'Look-Ahead (앞을 먼저 보여 주는 카메라)' : 'Vertical Tracking (세로 따라가기)',
      -845, -326, 50, color.gold);
    for (let i = 0; i < 2; i++) {
      const x = -850 + 880 * i;
      const pigment = i === 0 ? color.teal : color.coral;
      const dodge = evade ? 188 * Math.max(0, Math.min(1, (phase - .38) / .29)) : 0;
      const cameraY = ahead || evade ? 0 : lift * (i === 0 ? 1 : .23);
      const cameraX = evade ? dodge * (i === 0 ? 1 : .2) : ahead && i === 1 ? 140 : 0;
      const floor = 105 + cameraY;
      const center = x + 410;
      const heading = evade ? (i === 0 ? '기체가 계속 화면 가운데' : '기체가 화면 안에서 비켜남')
        : ahead ? (i === 0 ? '캐릭터가 가운데' : '진행 방향을 먼저 보여 줌')
        : (i === 0 ? '세로까지 밀착해서 따라감' : '세로 움직임을 조금 남김');
      text(`${i === 0 ? 'A' : 'B'} · ${heading}`, x, -235, 41, pigment);
      ctx.fillStyle = color.field;
      ctx.fillRect(x, -190, 815, 428);
      ctx.save();
      ctx.beginPath();
      ctx.rect(x, -190, 815, 428);
      ctx.clip();
      ctx.setLineDash([12, 9]);
      rule(x, 16, 815, 0, color.lines);
      rule(center, -190, 0, 428, color.lines);
      ctx.setLineDash([]);
      rule(x, floor, 815, 0, color.mute, 7);
      for (let tile = 0; tile <= 12; tile++) {
        rule(x + tile * 93 - (ahead ? phase * 275 % 93 : 0), floor, 0, 102, color.lines, 3);
      }
      if (evade) {
        const projected = center - cameraX;
        const projectile = -160 + 365 * phase;
        ctx.setLineDash([11, 9]);
        rule(projected, -158, 0, 358, color.gold, 4);
        ctx.setLineDash([]);
        ctx.fillStyle = color.gold;
        ctx.beginPath();
        ctx.arc(projected, projectile, 13, 0, Math.PI * 2);
        ctx.fill();
        text('탄의 경로', projected - 144, -109, 33, color.gold);
        rule(projected, floor + 40, dodge, 0, pigment, 5);
      } else if (ahead) {
        const obstacle = center + 490 - phase * 275 - cameraX;
        ctx.fillStyle = color.gold;
        ctx.fillRect(obstacle, floor - 56, 70, 56);
        rule(center - cameraX + 50, floor - 52, 76, 0, pigment, 6);
      }
      if (evade) mech(center + dodge - cameraX, floor, pigment);
      else runner(center - cameraX, floor - (ahead ? 0 : lift), pigment);
      ctx.restore();
      text('화면 기준선', x + 18, -161, 29, color.mute);
      const observation = evade ? (i === 0 ? '배경과 탄의 화면 위치가 바뀜' : '기체가 탄 옆으로 이동하는 모습')
        : ahead ? (i === 0 ? '장애물이 늦게 들어옴' : '같은 장애물이 먼저 들어옴')
        : (i === 0 ? '몸의 화면 위치가 거의 그대로' : '몸이 화면의 위쪽으로 올라감');
      text(observation, x, 273, 37, pigment);
    }
    text(evade ? '같은 회피 동작입니다. 카메라가 따라가는 정도만 바꿉니다.'
      : ahead ? '화면 크기는 같고, 어디를 먼저 볼지만 바꿉니다.'
      : '두 캐릭터의 실제 점프 높이는 같습니다.', -846, 348, 39, color.white);
  }
}

export default makeScene2D(function* (view) {
  view.fill(color.background);
  const clock = createSignal(0);
  view.add(<Txt x={-850} y={-450} offsetX={-1} text="카메라 중심점" fontFamily="Malgun Gothic"
    fontSize={60} fontWeight={700} fill={color.gold}/>);
  view.add(<Txt x={850} y={-450} offsetX={1} text="같은 행동 · 다른 구도" fontFamily="Malgun Gothic"
    fontSize={35} fill={color.mute}/>);
  view.add(new CameraStudy(clock));
  yield* tween(3 * period, value => clock(Math.min(3 * period - .001, 3 * period * value)));
});

import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';

const palette = {
  background: '#0a110d', panel: '#101b16', grid: '#233c32', white: '#f5f4ec',
  muted: '#b7c9bf', heading: '#f2d786', shot: '#f08a75', ship: '#79d2ca',
};
const modes = ['기본', '정지', '정지 + 흔들림', '정지 + 흔들림 + 슬로모션'];
const panelWidth = 820;
const hitTime = 1.15;
const holdTime = .65;
const revealTime = 1.25;
const sequenceSeconds = 8;

function stateAt(t: number, mode: number) {
  const elapsed = Math.max(0, t - hitTime);
  const hold = mode > 0 ? holdTime : 0;
  const recovering = Math.max(0, elapsed - hold);
  const isSlow = mode === 3 && recovering < 1.05;
  const worldTime = Math.min(t, hitTime) + (mode === 3
    ? Math.min(recovering, 1.05) * .34 + Math.max(0, recovering - 1.05)
    : recovering);
  const shake = mode > 1 && elapsed > 0
    ? Math.sin(elapsed * 41) * 12 * Math.max(0, 1 - elapsed / .37)
    : 0;
  return {
    worldTime, shake, hit: t >= hitTime,
    stage: t < hitTime ? '접근 중' : elapsed < hold ? '충돌 지점 유지' : isSlow ? '느리게 재개' : '이동 재개',
  };
}

class ShooterComparison extends Node {
  public constructor(private readonly clock: () => number) {
    super({});
  }

  protected draw(ctx: CanvasRenderingContext2D) {
    const playTime = this.clock();
    const text = (label: string, x: number, y: number, size: number, color: string) => {
      ctx.fillStyle = color;
      ctx.font = `600 ${size}px "Malgun Gothic", sans-serif`;
      ctx.textBaseline = 'middle';
      ctx.fillText(label, x, y);
    };
    modes.forEach((mode, i) => {
      const x = -850 + 880 * (i % 2);
      const y = -306 + 315 * Math.floor(i / 2);
      const start = .55 + .5 * i;
      const t = Math.max(0, playTime - start);
      const state = stateAt(t, i);
      const travel = Math.min(1, t / hitTime);
      const impactAge = state.worldTime - hitTime;
      const contactX = x + 560;
      const contactY = y + 115;

      text(mode, x, y - 24, 40, playTime >= start ? palette.heading : palette.muted);
      ctx.fillStyle = palette.panel;
      ctx.fillRect(x, y, panelWidth, 220);
      ctx.save();
      ctx.beginPath();
      ctx.rect(x, y, panelWidth, 220);
      ctx.clip();
      ctx.translate(state.shake, 0);
      ctx.strokeStyle = palette.grid;
      ctx.lineWidth = 2;
      const drift = state.worldTime * 82 % 60;
      for (let column = 0; column <= panelWidth + 60; column += 60) {
        ctx.beginPath();
        ctx.moveTo(x + column - drift, y);
        ctx.lineTo(x + column - drift, y + 220);
        ctx.stroke();
      }
      for (const row of [55, 110, 165]) {
        ctx.beginPath();
        ctx.moveTo(x, y + row);
        ctx.lineTo(x + panelWidth, y + row);
        ctx.stroke();
      }
      if (impactAge <= 0) {
        ctx.fillStyle = palette.ship;
        ctx.beginPath();
        ctx.moveTo(contactX + 4, contactY);
        ctx.lineTo(contactX + 46, contactY - 25);
        ctx.lineTo(contactX + 37, contactY);
        ctx.lineTo(contactX + 46, contactY + 25);
        ctx.closePath();
        ctx.fill();
        ctx.fillStyle = palette.shot;
        ctx.beginPath();
        ctx.arc(x + 140 + travel * 420, contactY, 12, 0, 2 * Math.PI);
        ctx.fill();
      }
      if (state.hit && impactAge < revealTime) {
        const fade = Math.max(.12, 1 - impactAge / revealTime);
        ctx.globalAlpha = fade;
        ctx.strokeStyle = palette.heading;
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.arc(contactX, contactY, 30 + 65 * impactAge, 0, 2 * Math.PI);
        ctx.stroke();
        ctx.globalAlpha = 1;
      } else if (state.hit) {
        ctx.strokeStyle = palette.heading;
        ctx.lineWidth = 3;
        ctx.setLineDash([8, 7]);
        ctx.beginPath();
        ctx.arc(contactX, contactY, 30, 0, 2 * Math.PI);
        ctx.stroke();
        ctx.setLineDash([]);
        text('접촉 위치', contactX + 45, contactY, 28, palette.heading);
      }
      ctx.restore();
      text(playTime < start ? '같은 기체 · 같은 적탄' : state.stage, x, y + 248, 34,
        state.hit ? palette.ship : palette.white);
    });
    text('접촉 위치는 같고, 효과만 순서대로 추가', -850, 330, 39, palette.white);
  }
}

export default makeScene2D(function* (view) {
  view.fill(palette.background);
  const clock = createSignal(0);
  view.add(<Txt x={-850} y={-450} offsetX={-1} text="결정적인 순간의 정지 연출"
    fontFamily="Malgun Gothic" fontSize={60} fontWeight={700} fill={palette.heading}/>);
  view.add(<Txt x={850} y={-450} offsetX={1} text="자체 시연"
    fontFamily="Malgun Gothic" fontSize={35} fill={palette.muted}/>);
  view.add(new ShooterComparison(clock));
  yield* tween(sequenceSeconds, progress => clock(sequenceSeconds * progress));
});

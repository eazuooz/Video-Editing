import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';

const palette = {
  background: '#0a110d', board: '#142019', line: '#496557', white: '#f5f4ec',
  yellow: '#f2d786', teal: '#83d9c9', muted: '#b8cabe', coral: '#f3a08a',
};

function label(ctx: CanvasRenderingContext2D, text: string, x: number, y: number, size: number, color: string) {
  ctx.font = `600 ${size}px "Malgun Gothic", sans-serif`;
  ctx.fillStyle = color;
  ctx.textBaseline = 'middle';
  ctx.fillText(text, x, y);
}

function arrow(ctx: CanvasRenderingContext2D, x: number, y: number, endX: number, endY: number, color: string) {
  const direction = Math.atan2(endY - y, endX - x);
  const head = Math.min(18, Math.hypot(endX - x, endY - y) / 2);
  ctx.strokeStyle = color;
  ctx.lineWidth = 6;
  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.lineTo(endX, endY);
  ctx.lineTo(endX - head * Math.cos(direction - .47), endY - head * Math.sin(direction - .47));
  ctx.moveTo(endX, endY);
  ctx.lineTo(endX - head * Math.cos(direction + .47), endY - head * Math.sin(direction + .47));
  ctx.stroke();
}

class FeedbackLoop extends Node {
  public constructor(private readonly clock: () => number) {
    super({});
  }

  protected draw(ctx: CanvasRenderingContext2D) {
    const stages = [
      ['1 · 손의 입력', '방향을 누름'], ['2 · 게임 처리', '위치와 동작 결정'],
      ['3 · 화면과 소리', '이동과 착지 확인'], ['4 · 다음 입력', '손을 떼거나 점프'],
    ];
    const time = this.clock();
    const focus = Math.min(3, Math.floor(time / 1.35));
    for (const [i, [name, action]] of stages.entries()) {
      const x = -846 + i * 434;
      const active = i <= focus;
      ctx.fillStyle = palette.board;
      ctx.fillRect(x, -125, 377, 222);
      ctx.fillStyle = i === focus ? palette.yellow : active ? palette.teal : palette.line;
      ctx.fillRect(x, -125, 377, 5);
      label(ctx, name, x + 20, -67, 41, active ? palette.white : palette.muted);
      label(ctx, action, x + 20, 19, 36, active ? palette.teal : palette.muted);
      if (i > 0) arrow(ctx, x - 49, -20, x - 13, -20, active ? palette.teal : palette.line);
    }
    if (focus === 3) {
      ctx.strokeStyle = palette.yellow;
      ctx.lineWidth = 6;
      ctx.beginPath();
      ctx.moveTo(654, 126);
      ctx.lineTo(654, 215);
      ctx.lineTo(-640, 215);
      ctx.stroke();
      arrow(ctx, -640, 215, -640, 124, palette.yellow);
      label(ctx, '본 결과가 다음 조작을 바꿉니다', -310, 271, 42, palette.yellow);
    }
  }
}

class StickDeadZone extends Node {
  public constructor(private readonly clock: () => number) {
    super({});
  }

  protected draw(ctx: CanvasRenderingContext2D) {
    const time = this.clock();
    const angle = Math.sin(time * 1.8) * .26 - .35;
    const raw = time < 2.1 ? 15 + 7 * Math.sin(time * 5.4) : Math.min(238, 21 + (time - 2.1) * 55);
    const thresholds = [62, 126];
    for (const [i, deadZone] of thresholds.entries()) {
      const center = -456 + i * 880;
      const y = 8;
      const outside = raw > deadZone;
      const input = outside ? palette.teal : palette.yellow;
      label(ctx, i === 0 ? 'A · 좁은 데드존' : 'B · 넓은 데드존', center - 232, -289, 42, palette.white);
      ctx.lineWidth = 4;
      ctx.strokeStyle = palette.line;
      ctx.beginPath();
      ctx.arc(center, y, 246, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(center, y, deadZone, 0, Math.PI * 2);
      ctx.fillStyle = palette.board;
      ctx.fill();
      ctx.strokeStyle = palette.coral;
      ctx.setLineDash([10, 7]);
      ctx.stroke();
      ctx.setLineDash([]);
      const x2 = center + raw * Math.cos(angle);
      const y2 = y + raw * Math.sin(angle);
      arrow(ctx, center, y, x2, y2, input);
      ctx.fillStyle = input;
      ctx.beginPath();
      ctx.arc(x2, y2, 11, 0, Math.PI * 2);
      ctx.fill();
      label(ctx, outside ? '캐릭터 이동 시작' : '아직 움직이지 않음', center - 165, 303, 36, input);
    }
  }
}

function heading(view: Node, text: string) {
  view.add(<Txt x={-850} y={-440} offsetX={-1} text={text} fontFamily="Malgun Gothic"
    fontSize={57} fontWeight={700} fill={palette.yellow}/>);
  view.add(<Txt x={850} y={-440} offsetX={1} text="원리 도식" fontFamily="Malgun Gothic"
    fontSize={35} fill={palette.muted}/>);
}

export default makeScene2D(function* (view) {
  view.fill(palette.background);
  const time = createSignal(0);
  heading(view, 'Feedback Loop (피드백 루프)');
  view.add(new FeedbackLoop(time));
  yield* tween(7, progress => time(7 * progress));
  view.removeChildren();
  time(0);
  heading(view, 'Analog Stick Dead Zone (아날로그 스틱 데드존)');
  view.add(new StickDeadZone(time));
  yield* tween(9, progress => time(9 * progress));
});

import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';

const color = {bg: '#0a110d', panel: '#14211a', white: '#f5f4ec', gold: '#f2d786',
  muted: '#b9ccbf', edge: '#496354', hold: '#82d8ca', fall: '#f29a84'};
const actions = [
  {title: 'A · 걷기', action: '계속 걷기', result: '경계를 지나 낙하', crossing: true, speed: 117},
  {title: 'B · 제자리 공격', action: '공격 중 조금 전진', result: '발은 경계 앞에 유지', crossing: false, speed: 110},
  {title: 'C · 강한 돌진', action: '빠르게 전진', result: '허용된 구간에서 낙하', crossing: true, speed: 151},
];

class LedgeStudy extends Node {
  public constructor(private readonly clock: () => number) { super({}); }

  protected draw(ctx: CanvasRenderingContext2D) {
    const time = Math.max(0, this.clock() - .55);
    const txt = (value: string, x: number, y: number, size: number, fill: string) => {
      ctx.font = `600 ${size}px "Malgun Gothic", sans-serif`;
      ctx.fillStyle = fill;
      ctx.textBaseline = 'middle';
      ctx.fillText(value, x, y);
    };
    const stroke = (x1: number, y1: number, x2: number, y2: number, ink: string, width: number) => {
      ctx.strokeStyle = ink;
      ctx.lineWidth = width;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    };
    for (const [i, action] of actions.entries()) {
      const x = -845 + i * 570;
      const platformEdge = x + 321;
      const startingX = x + 130;
      const distance = action.speed * Math.min(3.4, time);
      const intentX = startingX + distance;
      const footX = action.crossing ? intentX : Math.min(platformEdge - 20, intentX);
      const movingPastEdge = action.crossing && footX > platformEdge;
      const fallen = movingPastEdge ? Math.min(133, 1.5 * (footX - platformEdge)) : 0;
      const floor = 49;
      const ink = movingPastEdge ? color.fall : color.hold;
      const bodyY = floor + fallen;
      txt(action.title, x, -259, 45, color.gold);
      ctx.fillStyle = color.panel;
      ctx.fillRect(x, -209, 530, 439);
      ctx.fillStyle = color.edge;
      ctx.fillRect(x + 24, floor, platformEdge - x - 24, 31);
      ctx.setLineDash([10, 10]);
      stroke(platformEdge, -139, platformEdge, 217, color.gold, 4);
      ctx.setLineDash([]);
      txt('경계', platformEdge - 30, -166, 32, color.gold);
      stroke(startingX, floor - 150, Math.min(x + 487, footX), floor - 150, ink, 6);
      const step = !movingPastEdge && intentX < platformEdge - 20 ? Math.sin(time * 14) * 13 : 0;
      const bodyX = Math.min(x + 493, footX);
      stroke(bodyX, bodyY - 92, bodyX, bodyY - 35, ink, 22);
      stroke(bodyX, bodyY - 43, bodyX - 15 + step, bodyY - 3, ink, 12);
      stroke(bodyX, bodyY - 43, bodyX + 15 - step, bodyY - 3, ink, 12);
      stroke(bodyX, bodyY - 77, bodyX + (i === 1 ? 60 : 24), bodyY - 71, ink, 12);
      ctx.fillStyle = ink;
      ctx.beginPath();
      ctx.arc(bodyX, bodyY - 109, 15, 0, Math.PI * 2);
      ctx.fill();
      const resolved = movingPastEdge || (!action.crossing && intentX >= platformEdge - 20);
      txt(resolved ? action.result : action.action, x, 267, 35, ink);
    }
    txt('같은 위치에서 행동마다 다른 경계 규칙을 적용합니다.', -844, 347, 40, color.white);
  }
}

export default makeScene2D(function* (view) {
  view.fill(color.bg);
  const time = createSignal(0);
  view.add(<Txt x={-845} y={-444} offsetX={-1} text="낭떠러지에서 행동이 바뀌는 순간" fontFamily="Malgun Gothic"
    fontSize={58} fontWeight={700} fill={color.gold}/>);
  view.add(<Txt x={845} y={-444} offsetX={1} text="원리 도식" fontFamily="Malgun Gothic"
    fontSize={35} fill={color.muted}/>);
  view.add(new LedgeStudy(time));
  yield* tween(10, p => time(Math.min(4.2, p * 4.9)));
});

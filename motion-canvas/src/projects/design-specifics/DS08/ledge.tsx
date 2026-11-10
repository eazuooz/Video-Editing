import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';

const color = {bg: '#0a110d', panel: '#14211a', white: '#f5f4ec', gold: '#f2d786',
  muted: '#b9ccbf', edge: '#496354', hold: '#82d8ca', fall: '#f29a84'};
const period = 10;
const studies = [
  {heading: '어떤 입력 때문에 경계에 닿았을까?', takeaway: '같은 위치에서 행동마다 다른 경계 규칙을 적용합니다.', actions: [
    {title: 'A · 걷기', action: '계속 걷기', result: '경계를 지나 낙하', motion: 'fall', speed: 117},
    {title: 'B · 제자리 공격', action: '공격 중 조금 전진', result: '발은 경계 앞에 유지', motion: 'stop', speed: 110},
    {title: 'C · 강한 돌진', action: '빠르게 전진', result: '허용된 구간에서 낙하', motion: 'fall', speed: 151},
  ]},
  {heading: '어느 단계에서 경계에 닿았을까?', takeaway: '동작 단계나 남은 속력으로 낙하를 구분할 수 있습니다.', actions: [
    {title: 'A · 전진 구간', action: '전진 중 경계에 닿음', result: '전진 힘을 이어 낙하', motion: 'fall', speed: 151},
    {title: 'B · 끝나는 구간', action: '회복 구간에 닿음', result: '동작 끝에서는 멈춤', motion: 'stop', speed: 109},
    {title: 'C · 속력 기준', action: '굴러가며 감속 중', result: '설정한 기준보다 느림', motion: 'stop', speed: 89},
  ]},
  {heading: '경계에 닿았을 때 선택을 어떻게 전달할까?', takeaway: '유지 입력, 경계 방향, 자동 점프는 서로 다른 선택입니다.', actions: [
    {title: 'A · 입력 유지', action: '방향을 더 누르고 있음', result: '유지한 뒤 경계 통과', motion: 'hold', speed: 123},
    {title: 'B · 경계 따라가기', action: '바깥 성분을 줄임', result: '경계와 나란히 이동', motion: 'slide', speed: 113},
    {title: 'C · 자동 점프', action: '뛰어넘을 위치에 접근', result: '맞은편 발판에 착지', motion: 'jump', speed: 125},
  ]},
];

class LedgeStudy extends Node {
  public constructor(private readonly clock: () => number) { super({}); }

  protected draw(ctx: CanvasRenderingContext2D) {
    const clock = this.clock();
    const {heading, takeaway, actions} = studies[Math.floor(clock / period)];
    const time = Math.max(0, Math.min(4.2, (clock % period) * .49) - .55);
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
    txt(heading, -845, -353, 42, color.white);
    for (const [i, action] of actions.entries()) {
      const x = -845 + i * 570;
      const platformEdge = x + 321;
      const startingX = x + 130;
      const distance = action.speed * Math.min(3.4, time);
      const intentX = startingX + distance;
      const holdEnd = (platformEdge - startingX) / action.speed + .70;
      const stopped = action.motion === 'stop' || action.motion === 'slide';
      let footX = stopped ? Math.min(platformEdge - 20, intentX) : intentX;
      if (action.motion === 'hold') {
        footX = time < holdEnd ? Math.min(platformEdge, footX) : platformEdge + (time - holdEnd) * action.speed;
      }
      const jumping = action.motion === 'jump';
      const movingPastEdge = !stopped && footX > platformEdge;
      const jump = jumping ? Math.max(0, Math.min(1, (footX - platformEdge) / 110)) : 0;
      const slide = action.motion === 'slide' ? Math.max(0, Math.min(100, intentX - platformEdge + 20)) : 0;
      const fallen = movingPastEdge && !jumping ? Math.min(133, 1.5 * (footX - platformEdge)) : 0;
      const floor = 49;
      const ink = movingPastEdge && !jumping ? color.fall : color.hold;
      const bodyY = floor + fallen - 4 * jump * (1 - jump) * 94;
      txt(action.title, x, -259, 45, color.gold);
      ctx.fillStyle = color.panel;
      ctx.fillRect(x, -209, 530, 439);
      if (action.motion === 'slide') {
        const originY = 138;
        ctx.fillStyle = color.edge;
        ctx.fillRect(x + 23, -131, platformEdge - x - 23, 331);
        stroke(platformEdge, -131, platformEdge, 200, color.gold, 4);
        txt('위에서 본 경계', x + 33, -163, 31, color.muted);
        stroke(startingX, originY, footX, originY - slide, ink, 7);
        if (slide > 0) {
          stroke(footX, originY - slide, footX, originY - slide - 45, ink, 7);
          stroke(footX, originY - slide - 45, footX - 11, originY - slide - 32, ink, 7);
        }
        ctx.fillStyle = ink;
        ctx.beginPath();
        ctx.arc(footX, originY - slide, 18, 0, Math.PI * 2);
        ctx.fill();
        txt(slide > 0 ? action.result : action.action, x, 267, 35, ink);
        continue;
      }
      ctx.fillStyle = color.edge;
      ctx.fillRect(x + 24, floor, platformEdge - x - 24, 31);
      if (jumping) ctx.fillRect(platformEdge + 110, floor, 85, 31);
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
      const resolved = jumping ? jump === 1 : movingPastEdge || (stopped && intentX >= platformEdge - 20);
      txt(resolved ? action.result : action.action, x, 267, 35, ink);
    }
    txt(takeaway, -844, 320, 40, color.white);
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
  const duration = period * studies.length;
  yield* tween(duration, p => time(Math.min(duration - .001, duration * p)));
});

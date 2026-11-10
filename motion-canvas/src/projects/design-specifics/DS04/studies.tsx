import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';

const color = {
  bg: '#0a110d', panel: '#15221b', grid: '#345044', white: '#f5f4ec', muted: '#b9cdc0',
  gold: '#f2d786', teal: '#82d6c9', coral: '#f0a08a', red: '#b74538',
};

const studies = [
  {term: 'Shake Amplitude (흔들림 크기)', sides: ['같은 크기', '맞은 쪽을 더 크게'],
    conclusion: '접점은 같습니다. 힘을 받은 쪽의 흔들림을 구분합니다.'},
  {term: 'Hurtbox (허트박스)', sides: ['그림과 판정이 함께 움직임', '판정은 제자리에 유지'],
    conclusion: '점선은 실제 판정 범위입니다. 그림만 흔들면 접점은 바뀌지 않습니다.'},
  {term: 'Shake Axis (흔들림 방향)', sides: ['지상에서도 위아래로', '지상에서는 가로로'],
    conclusion: '발이 땅에 닿아 있는 동안에는 바닥이 기준입니다.'},
  {term: 'Amplitude Decay (흔들림 감쇠)', sides: ['끝까지 같은 폭', '갈수록 폭을 줄임'],
    conclusion: '끝에서 중심으로 돌아오는 폭이 작아지면 재개가 부드럽습니다.'},
  {term: 'Hit Stop Multiplier (히트 스톱 배율)', sides: ['짧은 정지', '긴 정지'],
    conclusion: '같은 접촉 자세에서 정지 길이만 바꿔 봅니다.'},
  {term: 'Pose Interpolation (자세 보간)', sides: ['맞는 자세로 바로 전환', '사이를 짧게 이어 줌'],
    conclusion: '두 끝 자세는 같습니다. 어느 쪽이 힘의 방향을 읽기 쉬운지 봅니다.'},
  {term: 'Visual Motion (표현 동작)', sides: ['칼도 같이 멈춤', '칼끝만 느리게 지나감'],
    conclusion: '칼끝은 움직여도 적중 판정은 한 번만 일어납니다.'},
  {term: 'Screen-Space Shake (화면상 흔들림)', sides: ['가까운 카메라', '먼 카메라'],
    conclusion: '같은 월드 이동도, 멀리서 보면 화면에서 덜 움직입니다.'},
];

const secondsPerStudy = 7;
const impact = 1.16;
const initialHold = 1.40;

function state(time: number, study: number, side: number, airborne: boolean) {
  const age = Math.max(0, time - impact);
  const hold = study === 4 ? (side === 0 ? .68 : 1.83) : initialHold;
  const hit = time >= impact;
  const holding = hit && age < hold;
  const easing = study === 3 && side === 1 ? 1 - Math.min(1, age / hold) : 1;
  const wave = holding ? Math.sin(age * 29) * easing : 0;
  const attackerOffset = study === 0 && holding ? (side === 0 ? 24 : 6) * wave : 0;
  const defenderAmplitude = study === 0 ? (side === 0 ? 24 : 44) : 27;
  const defenderOffset = defenderAmplitude * wave;
  const vertical = study === 2 && side === (airborne ? 1 : 0) ? wave * 30 : 0;
  const rawLean = study === 5 && side === 1 ? Math.min(1, age / .63) : Number(hit);
  const sword = study === 6 && side === 1 ? Math.min(1, age / hold) : 0;
  return {attackerOffset, defenderOffset, defenderRange: defenderAmplitude * easing,
    vertical, lean: rawLean * 25, sword, hold, holding, hit, age};
}

class Comparison extends Node {
  public constructor(private readonly clock: () => number) {
    super({});
  }

  protected draw(ctx: CanvasRenderingContext2D) {
    const elapsed = this.clock();
    const index = Math.min(studies.length - 1, Math.floor(elapsed / secondsPerStudy));
    const local = elapsed - index * secondsPerStudy;
    const airborne = index === 2 && local >= 3.7;
    const time = airborne ? local - 3.7 : local;
    const study = studies[index];
    const text = (value: string, x: number, y: number, size: number, fill: string) => {
      ctx.font = `600 ${size}px "Malgun Gothic", sans-serif`;
      ctx.textBaseline = 'middle';
      ctx.fillStyle = fill;
      ctx.fillText(value, x, y);
    };
    const line = (a: [number, number], b: [number, number], fill: string, width: number) => {
      ctx.strokeStyle = fill;
      ctx.lineWidth = width;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(...a);
      ctx.lineTo(...b);
      ctx.stroke();
    };
    const figure = (x: number, floor: number, fill: string, lean: number, reach: number, facing: number) => {
      const shoulder: [number, number] = [x + lean, floor - 142];
      const hip: [number, number] = [x + .33 * lean, floor - 75];
      const elbow: [number, number] = [shoulder[0] + facing * 38, shoulder[1] + 28 - 10 * reach];
      const hand: [number, number] = [elbow[0] + facing * (25 + 25 * reach), elbow[1] - 18 * reach];
      const back: [number, number] = [shoulder[0] - facing * 21, shoulder[1] + 51];
      line(shoulder, hip, fill, 28);
      line(shoulder, elbow, fill, 19);
      line(elbow, hand, fill, 16);
      line(shoulder, back, fill, 16);
      for (const step of [-25, 25]) {
        const knee: [number, number] = [x + step * .77, floor - 39];
        line(hip, knee, fill, 20);
        line(knee, [x + step, floor - 5], fill, 17);
        line([x + step - 9, floor - 2], [x + step + 13, floor - 2], fill, 10);
      }
      ctx.fillStyle = fill;
      ctx.beginPath();
      ctx.arc(shoulder[0], shoulder[1] - 26, 20, 0, 2 * Math.PI);
      ctx.fill();
      return hand;
    };

    text(study.term, -846, -339, 54, color.gold);
    const sides = airborne ? ['공중에서도 가로만', '공중에서는 세로도 허용'] : study.sides;
    for (const [side, title] of sides.entries()) {
      const x = -850 + side * 880;
      const c = state(time, index, side, airborne);
      const actor = x + 336 + c.attackerOffset;
      const target = x + 496;
      const floor = 133;
      const feet = airborne ? floor - 94 : floor;
      const reach = Math.min(1, time / impact);
      const motion = c.holding ? 0 : Math.max(0, c.age - c.hold);
      const separation = Math.min(81, motion * 43);
      const cameraScale = index === 7 && side === 1 ? .55 : 1;
      const moved = target + c.defenderOffset + separation;
      const spot = x + 437;
      text(`${side === 0 ? 'A' : 'B'} · ${title}`, x, -243, 39, side === 0 ? color.teal : color.coral);
      ctx.fillStyle = color.panel;
      ctx.fillRect(x, -199, 815, 424);
      line([x + 35, floor], [x + 780, floor], color.grid, 4);
      ctx.save();
      ctx.translate(spot, floor);
      ctx.scale(cameraScale, cameraScale);
      ctx.translate(-spot, -floor);
      const hand = figure(actor, feet, color.teal, c.hit ? 13 : reach * 13, reach, 1);
      figure(moved, feet + c.vertical, color.coral, c.lean, .25, -1);
      if (index === 6) line(hand, [hand[0] + 88 - c.sword * 26, hand[1] - 28 + 66 * c.sword], color.gold, 10);
      if (index === 1) {
        ctx.strokeStyle = color.gold;
        ctx.lineWidth = 5;
        ctx.setLineDash([10, 9]);
        ctx.strokeRect((side === 0 ? moved : target) - 51, floor - 200, 104, 201);
        ctx.setLineDash([]);
      }
      if (c.holding) {
        if (index === 0 || index === 3) {
          const y = feet - 222;
          const width = c.defenderRange;
          line([target - width, y], [target + width, y], color.coral, 5);
          line([target, y - 12], [target, y + 12], color.muted, 3);
          line([target + c.defenderOffset, y - 8], [target + c.defenderOffset, y + 8], color.gold, 5);
          if (index === 0) {
            const origin = x + 336;
            const width = side === 0 ? 24 : 6;
            line([origin - width, y], [origin + width, y], color.teal, 5);
            line([origin, y - 12], [origin, y + 12], color.muted, 3);
            line([actor, y - 8], [actor, y + 8], color.gold, 5);
          }
        }
        ctx.strokeStyle = color.gold;
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.arc(spot, feet - 113, 24, 0, 2 * Math.PI);
        ctx.stroke();
      }
      ctx.restore();
      line([x + 26, 181], [x + 786, 181], color.grid, 8);
      const status = !c.hit ? '접근' : c.holding ? '정지 구간' : '이동 재개';
      const start = x + 185;
      line([start, 181], [start + c.hold * 170, 181], c.holding ? color.gold : color.muted, 8);
      const position = Math.min(x + 786, start + (time - impact) * 170);
      line([Math.max(x + 26, position), 160], [Math.max(x + 26, position), 201], color.white, 4);
      text(status, x + 17, 261, 34, c.holding ? color.gold : color.muted);
    }
    text(airborne ? '발이 떠 있을 때에는 위아래로도 반응을 줄 수 있습니다.' : study.conclusion,
      -846, 338, 38, color.white);
  }
}

export default makeScene2D(function* (view) {
  view.fill(color.bg);
  const clock = createSignal(0);
  view.add(<Txt x={-850} y={-454} offsetX={-1} text="히트 스톱 8가지" fontFamily="Malgun Gothic"
    fontSize={61} fontWeight={700} fill={color.gold}/>);
  view.add(<Txt x={850} y={-454} offsetX={1} text="조건을 바꾼 원리 도식" fontFamily="Malgun Gothic"
    fontSize={35} fill={color.muted}/>);
  view.add(new Comparison(clock));
  const total = studies.length * secondsPerStudy;
  yield* tween(total, progress => clock(Math.min(total - .001, total * progress)));
});

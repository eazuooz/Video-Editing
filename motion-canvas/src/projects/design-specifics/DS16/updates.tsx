import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {board, palette as c} from '../board';

const seconds = 8;
const headings = ['같은 문에서 만나는 서로 다른 상태', '고친 뒤에 다시 지나갈 길', '제보를 재현 가능한 순서로 만들기', '오류 수정과 기능 추가'];
const explanations = ['문 하나를 열어도 그 전에 무엇을 했는지에 따라 저장 상태가 달라집니다.',
  '수정한 문만 통과하면 끝나는지, 연관된 행동이 계속 되는지 확인합니다.',
  '같은 버전, 같은 저장 상태, 같은 직전 행동으로 현상을 재현합니다.',
  '막혔던 길을 다시 열어 주는 일과 새 행동을 추가하는 일을 나눠 봅니다.'];

class Updates extends Node {
  public constructor(private readonly clock: () => number) { super({}); }

  protected draw(ctx: CanvasRenderingContext2D) {
    const time = this.clock(), mode = Math.floor(time / seconds);
    const progress = Math.min(1, time % seconds / 6.7);
    const {text, box, path, dot} = board(ctx);
    text(headings[mode], -845, -337, 53, c.gold);
    if (mode === 0) {
      const journeys = ['처음 방문해 열쇠를 얻음', '열쇠를 버렸다 다시 줍음', '문 앞의 저장을 다시 불러옴'];
      for (const [i, title] of journeys.entries()) {
        const y = -202 + i * 165, ink = i === 0 ? c.teal : i === 1 ? c.gold : c.coral;
        text(title, -835, y, 40);
        path([[-225, y], [363, y], [604, -37]], c.grid, 9);
        const part = Math.min(1, progress * 1.22);
        const pos = part < .7 ? [-225 + 588 * part / .7, y] : [363 + 241 * (part - .7) / .3, y + (-37 - y) * (part - .7) / .3];
        dot(pos[0], pos[1], 17, ink);
      }
      box(598, -135, 162, 196, '#294333');
      dot(717, -36, 13, c.gold);
      text('같은 문', 599, 115, 40, c.gold);
    } else {
      const variants = mode === 1 ? [
        {title: '수정 지점', steps: ['문이 다시 열림', '문 바로 뒤로 이동', '다음 지역 도착']},
        {title: '함께 확인할 경로', steps: ['열쇠 퀘스트', '이전 저장 다시 열기', '다음 지역 진입 재검사']},
      ] : mode === 2 ? [
        {title: '플레이어의 제보', steps: ['어느 버전이었나', '어디에서 저장했나', '바로 전에 무엇을 했나']},
        {title: '팀의 재현', steps: ['같은 버전에서 실행', '같은 저장 상태 만들기', '같은 입력 후 결과 확인']},
      ] : [
        {title: 'A · 오류 수정', steps: ['재현 조건 확인', '문제 경로 수정', '원래 하려던 행동 가능']},
        {title: 'B · 편의 기능 추가', steps: ['불편했던 지점 확인', '선택이나 기능 추가', '플레이 흐름이 달라짐']},
      ];
      for (const [i, variant] of variants.entries()) {
        const x = -844 + 872 * i, ink = i === 0 ? c.teal : c.coral;
        text(variant.title, x, -242, 44, ink);
        box(x, -185, 810, 439);
        for (const [j, step] of variant.steps.entries()) {
          const y = -102 + 131 * j;
          const active = progress >= .12 + j * .26;
          if (j < 2) path([[x + 109, y], [x + 109, y + 113]], c.grid, 5);
          dot(x + 109, y, 16, active ? ink : c.grid);
          text(step, x + 159, y, 42, active ? c.white : c.muted);
        }
      }
    }
    text(explanations[mode], -845, 348, 38);
  }
}

export default makeScene2D(function* (view) {
  view.fill(c.bg);
  const clock = createSignal(0);
  view.add(<Txt x={-845} y={-449} offsetX={-1} text="온라인 업데이트와 회귀 테스트" fontFamily="Malgun Gothic"
    fontSize={60} fontWeight={700} fill={c.gold}/>);
  view.add(<Txt x={845} y={-449} offsetX={1} text="원리 도식" fontFamily="Malgun Gothic"
    fontSize={35} fill={c.muted}/>);
  view.add(new Updates(clock));
  const end = headings.length * seconds;
  yield* tween(end, p => clock(Math.min(end - .001, p * end)));
});

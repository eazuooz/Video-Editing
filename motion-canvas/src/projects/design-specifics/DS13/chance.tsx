import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {board, palette as c} from '../board';

const seconds = 8;
const headings = ['선택지가 달라지는 순간', '도구를 고를 때 · 결과를 받은 뒤 고를 때', '같은 시드에서 같은 순서로 뽑기'];
const conclusions = ['상황이 바뀌더라도 플레이어가 다음 수를 고를 수 있어야 합니다.',
  '무작위로 나온 메뉴에서도 어떤 기술을 쓸지는 플레이어가 정합니다.',
  '같은 시드와 같은 호출 순서로 결과를 재현할 수 있습니다.'];
const kinds = ['이동', '방어', '회복', '공격', '강화', '회피'];

function drawSequence(seed: number) {
  const result = [];
  for (let i = 0; i < 5; i++) {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
    result.push(kinds[(seed >>> 16) % kinds.length]);
  }
  return result;
}

class Chance extends Node {
  public constructor(private readonly clock: () => number) { super({}); }

  protected draw(ctx: CanvasRenderingContext2D) {
    const time = this.clock(), mode = Math.floor(time / seconds);
    const amount = Math.min(1, (time % seconds) / 6.7);
    const {text, box, path, dot} = board(ctx);
    text(headings[mode], -845, -338, 53, c.gold);
    const sides = mode === 0 ? ['A · 추첨이 결과를 결정', 'B · 추첨 뒤에 선택']
      : mode === 1 ? ['A · 피치가 도구를 먼저 선택', 'B · 용사가 나온 기술 중 선택']
      : ['A · 처음 실행', 'B · 같은 시드로 다시 실행'];
    for (const [i, title] of sides.entries()) {
      const x = -845 + i * 875, ink = i === 0 ? c.teal : c.coral;
      text(title, x, -243, 43, ink);
      box(x, -189, 810, 442);
      const data = mode === 2 ? drawSequence(722)
        : mode === 1 ? (i === 0 ? ['프라이팬', '골프채', '라켓'] : ['방어', '강화', '회복'])
        : (i === 0 ? ['이동', '공격', '회복'] : ['방어', '강화', '회피']);
      const step = Math.floor(Math.min(data.length, amount * (data.length + .55)));
      const actions = mode === 0 && i === 0 ? ['추첨', '즉시 결과'] : data;
      const cardW = actions.length === 5 ? 127 : 192;
      const gap = actions.length === 5 ? 15 : 32;
      const start = x + 53;
      path([[start, 98], [x + 753, 98]], c.grid, 7);
      for (const [j, action] of actions.entries()) {
        const at = start + j * (cardW + gap);
        const shown = i === 0 && mode === 1
          || (mode === 0 && i === 0 ? amount >= .16 + .27 * j : j < step);
        const selected = mode !== 2 && j === 1 && amount >= .72 && (i === 1 || mode === 1);
        box(at, -77, cardW, 116, selected ? ink : c.grid);
        text(shown ? action : '· · ·', at + 16, -16, mode === 1 ? 37 : 41, selected ? c.bg : shown ? c.white : c.muted);
        dot(at + cardW / 2, 98, 11, shown ? ink : c.grid);
      }
      const message = mode === 2 ? '같은 시작 상태와 같은 호출 순서'
        : mode === 1 ? (i === 0 ? '원하는 도구를 지정' : '상황에 맞는 기술 선택')
        : i === 0 ? '결과 뒤에 행동이 없음' : '결과를 보고 대응할 수 있음';
      text(message, start, 188, 37, ink);
    }
    text(conclusions[mode], -845, 320, 39);
  }
}

export default makeScene2D(function* (view) {
  view.fill(c.bg);
  const clock = createSignal(0);
  view.add(<Txt x={-845} y={-450} offsetX={-1} text="Randomness (무작위성)" fontFamily="Malgun Gothic"
    fontSize={61} fontWeight={700} fill={c.gold}/>);
  view.add(<Txt x={845} y={-450} offsetX={1} text="원리 도식" fontFamily="Malgun Gothic"
    fontSize={35} fill={c.muted}/>);
  view.add(new Chance(clock));
  const end = headings.length * seconds;
  yield* tween(end, p => clock(Math.min(end - .001, p * end)));
});

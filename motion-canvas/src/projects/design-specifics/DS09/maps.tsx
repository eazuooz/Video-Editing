import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {board, palette as c} from '../board';

const seconds = 8;
const headings = ['시선이 어디로 갈까?', '한 좌표에 겹친 서로 다른 층', '게임 화면 위에 길을 겹치기', '코너가 보이는 곳에 단서 주기'];
const conclusions = ['지금 움직이는 데 필요한 정보가 어디에 있는지 비교합니다.',
  '지도에서 같은 좌표라도 실제 월드에서는 높이가 다를 수 있습니다.',
  '지도를 펼치지 않아도 통로와 다음 갈림길을 계속 읽습니다.',
  '멀리 갈 경로는 지도에 두고, 감속 단서는 지금 볼 화면에 둡니다.'];
const maze: [number, number][] = [[0, 150], [145, 150], [145, 35], [305, 35], [305, 110], [469, 110], [469, -32], [590, -32]];

function route(progress: number): [number, number][] {
  const point = Math.min(maze.length - 1.0001, progress * (maze.length - 1));
  const i = Math.floor(point), [x, y] = maze[i], [a, b] = maze[i + 1];
  return [...maze.slice(0, i + 1), [x + (a - x) * (point - i), y + (b - y) * (point - i)]];
}

class Maps extends Node {
  public constructor(private readonly clock: () => number) { super({}); }

  protected draw(ctx: CanvasRenderingContext2D) {
    const time = this.clock(), study = Math.floor(time / seconds);
    const amount = Math.min(1, (time % seconds) / 6.7);
    const {text, box, path, dot} = board(ctx);
    text(headings[study], -846, -339, 53, c.gold);
    const sides = study === 1 ? ['A · 공간을 옆에서 봄', 'B · 지도에서 층을 선택']
      : study === 2 ? ['A · 지도를 열 때', 'B · 지도를 겹친 상태']
      : ['A · 미니맵을 먼저 봄', 'B · 플레이 화면에 단서를 둠'];
    for (const [i, title] of sides.entries()) {
      const x = -845 + i * 873;
      text(title, x, -241, 43, i === 0 ? c.teal : c.coral);
      box(x, -185, 810, 440);
      if (study === 1) {
        const upper = amount < .55;
        if (i === 0) {
          path([[x + 61, -48], [x + 747, -48]], c.teal, 9);
          path([[x + 61, 105], [x + 747, 105]], c.coral, 9);
          path([[x + 470, -82], [x + 470, 130]], c.gold, 3);
          dot(x + 470, -48, 17, c.teal);
          dot(x + 470, 105, 17, c.coral);
          text('위층', x + 90, -83, 38, c.teal);
          text('아래층', x + 90, 67, 38, c.coral);
          text('지도 좌표는 같음', x + 437, 187, 34, c.gold);
        } else {
          const ink = upper ? c.teal : c.coral;
          text(upper ? '선택 · 위층' : '선택 · 아래층', x + 79, -125, 38, ink);
          path([[x + 120, 137], [x + 470, 137], [x + 470, -10], [x + 690, -10]], c.grid, 20);
          dot(x + 470, 48, 20, ink);
          path([[x + 470, 70], [x + 470, 190]], ink, 5);
          text('현재 층의 표식', x + 343, 222, 35, ink);
        }
      } else {
        const overlay = study === 2 && i === 1;
        const mapView = study === 2 && i === 0;
        const main = i === 1 && !overlay;
        const base = (p: [number, number], small = false): [number, number] => small
          ? [x + 603 + p[0] * .28, -116 + p[1] * .33] : [x + 106 + p[0], p[1] - 20];
        path(maze.map(p => base(p)), mapView ? c.muted : c.grid, mapView ? 16 : 49);
        const progress = mapView ? Math.min(.38, amount) : amount;
        const traced = route(progress);
        const tip = traced.at(-1)!;
        if (overlay) {
          ctx.globalAlpha = .68;
          path(maze.map(p => base(p)), c.muted, 11);
          ctx.globalAlpha = 1;
        }
        if (main || overlay || mapView) path(traced.map(p => base(p)), c.teal, 9);
        dot(...base(tip), 13);
        if (!overlay && !mapView) {
          box(x + 586, -151, 199, 108, '#213a2e');
          path(maze.map(p => base(p, true)), c.muted, 3);
          dot(...base(tip, true), 7, c.gold);
        }
        if (main) {
          const [bx, by] = base(maze[2]);
          dot(bx, by, 19, c.gold);
          text(study === 3 ? '감속 지점' : '다음 방향', bx + 27, by - 31, 36, c.gold);
        }
        if (mapView) text('이동 중 게임 화면이 가려짐', x + 78, 216, 34, c.muted);
        if (overlay) text('캐릭터와 통로가 함께 보임', x + 78, 216, 34, c.teal);
      }
    }
    text(conclusions[study], -845, 320, 39);
  }
}

export default makeScene2D(function* (view) {
  view.fill(c.bg);
  const clock = createSignal(0);
  view.add(<Txt x={-847} y={-450} offsetX={-1} text="게임 화면으로서의 지도" fontFamily="Malgun Gothic"
    fontSize={60} fontWeight={700} fill={c.gold}/>);
  view.add(<Txt x={847} y={-450} offsetX={1} text="원리 도식" fontFamily="Malgun Gothic"
    fontSize={35} fill={c.muted}/>);
  view.add(new Maps(clock));
  const end = headings.length * seconds;
  yield* tween(end, p => clock(Math.min(end - .001, p * end)));
});

import {Rect, Txt, View2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../styles/research-paper';
import timeline from '../../../../projects/one-button-game-design/planning/timeline.plan.json';
import {diagramScene} from './diagram';
export function* bodyScene(view: View2D, index: number) {
  const scene=timeline.scenes[index];
  view.fill(P.background);
  // Explicit draft slate, never disguised as cleared gameplay.
  view.add(<Rect width={1660} height={750} fill={P.panel}>
    <Txt text={'자료화면 확보 중 — '+scene.title} y={-90} fontSize={48} fill={P.ink} fontFamily={P.font}/>
    <Txt text={'대본·음성 승인 전 시각 초안 / 최종 영상 아님'} y={10} fontSize={31} fill={P.muted} fontFamily={P.font}/>
  </Rect>);
  yield* waitFor(scene.plannedExampleSeconds);
  view.removeChildren();
  yield* diagramScene(view,index,scene.plannedExplanationSeconds);
}

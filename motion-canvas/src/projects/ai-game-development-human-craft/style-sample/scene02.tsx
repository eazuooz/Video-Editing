import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK} from '../../../styles/research-dark';
import {flowArrow,flowNode} from '../../../shared/animated-flow';
import {annotation,scaffold} from './common';

export default makeScene2D(function*(view){
  const {diagram,caption}=scaffold(view,'02','확인하지 않은 조건을 펼쳐 보면','같은 구현에도 서로 다른 검사 경로가 필요합니다.');
  const trunk=flowArrow(diagram,()=>[[-574,0],[-146,0]]);
  const edges=[-195,0,195].map(y=>flowArrow(diagram,()=>[[26,0],[200,0],[330,y],[444,y]]));
  const code=flowNode(diagram,'AI 구현','{ }',[-660,0],'구현됨');
  const gate=flowNode(diagram,'조건 검사','?',[-60,0],'3가지 예시');
  const checks=[flowNode(diagram,'골드 부족','G',[530,-195],'미확인'),flowNode(diagram,'가방 가득','[]',[530,0],'미확인'),flowNode(diagram,'중복 요청','×2',[530,195],'미확인')];
  // Compact vertical branches: labels sit to the right, never below another node.
  checks.forEach(n=>{n.ring.size(100);n.name.position([185,-12]);n.state.position([185,32]);n.name.fontSize(31);n.glyph.fontSize(32);});
  caption.text('그런데 골드가 부족하면 어떻게 될까요?');
  yield* code.focus('구현됨',DARK.teal);yield* trunk.trace(.65);yield* gate.focus('조건을 나누기');trunk.active.stroke(DARK.teal);
  yield* waitFor(.65);yield* edges[0].trace(.7);yield* checks[0].focus('확인할 조건');yield* waitFor(1.1);
  edges[0].active.stroke(DARK.muted);checks[0].state.fill(DARK.muted);checks[0].ring.stroke(DARK.muted);
  caption.text('인벤토리가 가득 차 있으면 어떻게 해야 할까요?');
  yield* edges[1].trace(.7);yield* checks[1].focus('확인할 조건');yield* waitFor(1.3);
  edges[1].active.stroke(DARK.muted);checks[1].state.fill(DARK.muted);checks[1].ring.stroke(DARK.muted);
  caption.text('버튼을 빠르게 여러 번 누르면 구매가 중복 처리되지는 않을까요?');
  yield* edges[2].trace(.7);yield* checks[2].focus('확인할 조건');yield* waitFor(1.75);
});

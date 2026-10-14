import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK} from '../../../styles/research-dark';
import {flowArrow,flowNode} from '../../../shared/animated-flow';
import {scaffold} from './common';

export default makeScene2D(function*(view){
  const {diagram,caption}=scaffold(view,'01','한 번 작동했다고, 완성일까요?','먼저 정상적인 구매 한 번을 확인합니다.');
  const edges=[-660,-220,220].map(x=>flowArrow(diagram,()=>[[x+86,-70],[x+354,-70]]));
  const nodes=[flowNode(diagram,'요구사항','?',[-660,-70],'상점 기능'),flowNode(diagram,'AI 구현','{ }',[-220,-70]),flowNode(diagram,'구매 실행','▶',[220,-70]),flowNode(diagram,'실행 결과','✓',[660,-70])];
  caption.text('AI에게 골드로 아이템을 구매하는 기능을 만들어 달라고 요청했습니다.');
  yield* nodes[0].focus('상점 기능'); yield* waitFor(.65);
  yield* edges[0].trace(.75); yield* nodes[1].focus('구현'); yield* edges[0].verify();nodes[0].ring.stroke(DARK.teal);nodes[0].state.fill(DARK.teal);
  yield* waitFor(.75);
  caption.text('버튼을 누르면 골드가 줄고 아이템이 들어옵니다.');
  yield* edges[1].trace(.75); yield* nodes[2].focus('100 → 70 골드'); yield* edges[1].verify();nodes[1].ring.stroke(DARK.teal);nodes[1].state.fill(DARK.teal);
  yield* waitFor(.85);
  yield* edges[2].trace(.75); yield* nodes[3].focus('한 조건 확인',DARK.teal); yield* edges[2].verify();nodes[2].ring.stroke(DARK.teal);nodes[2].state.fill(DARK.teal);
  caption.text('한 번 눌러 봤을 때는 잘 작동합니다.');
  yield* waitFor(2.7);
});

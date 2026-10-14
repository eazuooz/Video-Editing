import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK} from '../../../styles/research-dark';
import {flowArrow,flowNode} from '../../../shared/animated-flow';
import {annotation,scaffold} from './common';

export default makeScene2D(function*(view){
  const {diagram,caption}=scaffold(view,'03','검사 결과를 다음 수정으로 연결하기','예시 입력: 잔액 20골드, 가격 30골드');
  const forward=flowArrow(diagram,()=>[[-574,-70],[-86,-70]]);
  const result=flowArrow(diagram,()=>[[86,-70],[574,-70]]);
  const back=flowArrow(diagram,()=>[[0,-156],[0,-222],[-660,-222],[-660,-156]],DARK.red);
  const code=flowNode(diagram,'구현','{ }',[-660,-70],'차감만 수행');
  const test=flowNode(diagram,'부족한 골드 검사','?', [0,-70],'기대: 구매 거절');
  const done=flowNode(diagram,'재검사','✓',[660,-70],'대기');
  const feedback=annotation(diagram,'검사 실패 → 조건 추가',-330,-249,DARK.red);feedback.opacity(0);
  caption.text('AI가 요구사항을 읽고, 코드를 수정하고, 테스트를 실행하고, 실패한 부분을 다시 고치도록 구성할 수 있습니다.');
  yield* code.focus('차감만 수행');yield* forward.trace(.75);yield* test.focus('−10 골드: 문제',DARK.red);
  yield* waitFor(.8);feedback.opacity(1);yield* back.trace(1.2);yield* code.focus('잔액 검사 추가');
  yield* waitFor(.8);back.root.opacity(.3);forward.progress(0);yield* forward.trace(.75);
  yield* test.focus('구매 거절 · 20 유지',DARK.teal);yield* forward.verify();code.ring.stroke(DARK.teal);code.state.fill(DARK.teal);
  yield* result.trace(.75);yield* done.focus('이 조건 통과',DARK.teal);yield* result.verify();
  caption.text('바로 여기서 개발자의 이해가 필요합니다.');
  yield* waitFor(2.4);
});

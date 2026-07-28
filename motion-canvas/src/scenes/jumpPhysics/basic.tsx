import {makeScene2D} from '@motion-canvas/2d';
import {EXPLANATIONS} from './explanations';
import {basicConcept} from './profiles';
import {ORANGE, addBackground, runProfileLeftAnchor, showExplanation} from './shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  const profile = basicConcept();
  yield* runProfileLeftAnchor(view, profile, ORANGE, {loops: 2});
  const e = EXPLANATIONS.basic;
  yield* showExplanation(view, '점프의 기본 원리', e.why, e.how);
});

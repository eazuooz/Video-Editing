import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanation} from '../spatial-score-explanation';
import {EXPLANATION_TIMING} from '../explanation-timing';
export default makeScene2D(function* (view) {
  yield* scoreExplanation(view,'08-scoring-feedback',EXPLANATION_TIMING['08-scoring-feedback']);
});

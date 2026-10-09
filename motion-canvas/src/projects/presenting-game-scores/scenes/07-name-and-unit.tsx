import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanation} from '../spatial-score-explanation';
import {EXPLANATION_TIMING} from '../explanation-timing';
export default makeScene2D(function* (view) {
  yield* scoreExplanation(view,'07-name-and-unit',EXPLANATION_TIMING['07-name-and-unit']);
});

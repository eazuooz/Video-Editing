import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanation} from '../spatial-score-explanation';
import {EXPLANATION_TIMING} from '../explanation-timing';
export default makeScene2D(function* (view) {
  yield* scoreExplanation(view,'06-relative-gap',EXPLANATION_TIMING['06-relative-gap']);
});

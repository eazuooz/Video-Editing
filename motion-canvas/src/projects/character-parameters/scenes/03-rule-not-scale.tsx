import {makeScene2D} from '@motion-canvas/2d';
import {characterExplanation} from '../spatial-character-explanation';
import {PROTOTYPE_TIMING} from '../prototype-timing-v1';
export default makeScene2D(function* (view) {
  yield* characterExplanation(view,'03-rule-not-scale',PROTOTYPE_TIMING['03-rule-not-scale']);
});

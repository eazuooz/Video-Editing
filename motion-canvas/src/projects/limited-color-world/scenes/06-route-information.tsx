import {makeScene2D} from '@motion-canvas/2d';
import {colorExplanation} from '../spatial-color-explanation';
import {PROTOTYPE_TIMING} from '../prototype-timing-v1';
export default makeScene2D(function* (view) {
  yield* colorExplanation(view,'06-route-information',PROTOTYPE_TIMING['06-route-information']);
});

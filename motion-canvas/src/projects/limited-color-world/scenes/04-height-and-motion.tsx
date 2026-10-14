import {makeScene2D} from '@motion-canvas/2d';
import {colorExplanation} from '../spatial-color-explanation';
import {PROTOTYPE_TIMING} from '../prototype-timing-v1';
export default makeScene2D(function* (view) {
  yield* colorExplanation(view,'04-height-and-motion',PROTOTYPE_TIMING['04-height-and-motion']);
});

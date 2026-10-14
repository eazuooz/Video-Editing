import {makeScene2D} from '@motion-canvas/2d';
import {colorExplanation} from '../spatial-color-explanation';
import {PROTOTYPE_TIMING} from '../prototype-timing-v1';
export default makeScene2D(function* (view) {
  yield* colorExplanation(view,'03-pattern-and-erasing',PROTOTYPE_TIMING['03-pattern-and-erasing']);
});

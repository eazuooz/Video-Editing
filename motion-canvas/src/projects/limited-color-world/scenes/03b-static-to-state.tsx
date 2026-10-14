import {makeScene2D} from '@motion-canvas/2d';
import {causalColorBridge} from '../spatial-causal-bridges';
export default makeScene2D(function* (view) {
  // Structural prototype only. Replace12s after independent bridge PCM measurement.
  yield* causalColorBridge(view,'03b-static-to-state',12);
});

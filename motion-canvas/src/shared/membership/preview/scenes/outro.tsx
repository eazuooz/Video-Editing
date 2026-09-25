import {makeScene2D} from '@motion-canvas/2d';
import {membershipOutro} from '../../membership-outro';

export default makeScene2D(function* (view) {
  yield* membershipOutro(view);
});

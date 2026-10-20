// Channel rule: every video ends with the ~10s membership thank-you (docs/MEMBERSHIP_OUTRO.md).
import {makeScene2D} from '@motion-canvas/2d';
import {membershipOutro} from '../../../shared/membership/membership-outro';

export default makeScene2D(function* (view) {
  yield* membershipOutro(view);
});

// Narration segments 02 + 03 — gravity added every frame, then apex and fall.
// One continuous basic-jump graph covers both, since the narrator walks up the
// same curve: 5 -> 4 -> 3 -> 2, zero at the apex, then accelerating downward.

import {makeScene2D} from '@motion-canvas/2d';
import {SEGMENTS} from '../../narration';
import {basicConcept} from '../jumpPhysics/profiles';
import {ORANGE, addBackground, runProfileLeftAnchor} from '../jumpPhysics/shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  yield* runProfileLeftAnchor(view, basicConcept(), ORANGE, {
    duration: SEGMENTS.basic.duration,
  });
});

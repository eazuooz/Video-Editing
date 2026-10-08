import {makeScene2D} from '@motion-canvas/2d';
import {observationGuideExplanation} from '../observation-guide-explanation-v4';
import timing from '../observation-guide-timing-measured-v1.json';
export default makeScene2D(function*(view){yield* observationGuideExplanation(view,'10-origin-effect-target-guide',timing.rows[1]);});

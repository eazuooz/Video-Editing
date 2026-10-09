import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanationMeasuredV7} from '../measured-score-explanation-v7';
// Selected measured explanation input; silent render, all final pixel gates pending.
export default makeScene2D(function* (view) {yield* scoreExplanationMeasuredV7(view,"09-feedback-hierarchy",{"durationSeconds": 7.433333333333334, "paragraphStarts": [0, 0.15, 4.0], "measured": true});});

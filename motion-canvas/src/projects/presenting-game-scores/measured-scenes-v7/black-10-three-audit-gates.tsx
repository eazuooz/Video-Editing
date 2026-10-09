import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanationMeasuredV7} from '../measured-score-explanation-v7';
// Selected measured explanation input; silent render, all final pixel gates pending.
export default makeScene2D(function* (view) {yield* scoreExplanationMeasuredV7(view,"10-audit-and-close",{"durationSeconds": 13.216666666666667, "paragraphStarts": [0, 2.8, 7.0], "measured": true});});

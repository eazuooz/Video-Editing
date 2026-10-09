import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanationMeasuredV7} from '../measured-score-explanation-v7';
// Selected measured explanation input; silent render, all final pixel gates pending.
export default makeScene2D(function* (view) {yield* scoreExplanationMeasuredV7(view,"06-observed-2920",{"durationSeconds": 12.0, "paragraphStarts": [0, 6.24, 9.5], "measured": true});});

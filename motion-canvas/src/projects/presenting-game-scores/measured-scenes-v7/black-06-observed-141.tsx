import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanationMeasuredV7} from '../measured-score-explanation-v7';
// Selected measured explanation input; silent render, all final pixel gates pending.
export default makeScene2D(function* (view) {yield* scoreExplanationMeasuredV7(view,"06-observed-141",{"durationSeconds": 11.5, "paragraphStarts": [0, 7.04, 9.0], "measured": true});});

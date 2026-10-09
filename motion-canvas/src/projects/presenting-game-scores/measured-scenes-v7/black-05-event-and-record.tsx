import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanationMeasuredV7} from '../measured-score-explanation-v7';
// Selected measured explanation input; silent render, all final pixel gates pending.
export default makeScene2D(function* (view) {yield* scoreExplanationMeasuredV7(view,"05-events-and-total",{"durationSeconds": 7.0, "paragraphStarts": [0, 0.15, 4.3], "measured": true});});

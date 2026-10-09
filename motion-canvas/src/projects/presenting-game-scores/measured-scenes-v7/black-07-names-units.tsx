import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanationMeasuredV7} from '../measured-score-explanation-v7';
// Selected measured explanation input; silent render, all final pixel gates pending.
export default makeScene2D(function* (view) {yield* scoreExplanationMeasuredV7(view,"07-name-and-unit",{"durationSeconds": 13.45, "paragraphStarts": [0, 0.2, 6.985], "measured": true});});

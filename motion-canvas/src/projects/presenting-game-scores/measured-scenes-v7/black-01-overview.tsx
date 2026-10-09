import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanationMeasuredV7} from '../measured-score-explanation-v7';
// Selected measured explanation input; silent render, all final pixel gates pending.
export default makeScene2D(function* (view) {yield* scoreExplanationMeasuredV7(view,"01-overview",{"durationSeconds": 16.966666666666665, "paragraphStarts": [0, 3.395, 10.67], "measured": true});});

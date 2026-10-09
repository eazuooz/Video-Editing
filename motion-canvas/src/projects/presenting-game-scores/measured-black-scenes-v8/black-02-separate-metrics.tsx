import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanationMeasuredV8} from '../measured-score-explanation-frame-exact-v8';
export default makeScene2D(function* (view) {yield* scoreExplanationMeasuredV8(view,"02-score-and-lines",{"durationSeconds": 7.0, "paragraphStarts": [0, 0.35, 2.2], "measured": true});});

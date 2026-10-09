import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanationMeasuredV8} from '../measured-score-explanation-frame-exact-v8';
export default makeScene2D(function* (view) {yield* scoreExplanationMeasuredV8(view,"04-evaluation-weights",{"durationSeconds": 7.5, "paragraphStarts": [0, 0.3, 2.0], "measured": true});});

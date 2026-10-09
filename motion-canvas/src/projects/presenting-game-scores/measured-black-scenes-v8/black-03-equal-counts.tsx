import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanationMeasuredV8} from '../measured-score-explanation-frame-exact-v8';
export default makeScene2D(function* (view) {yield* scoreExplanationMeasuredV8(view,"03-same-count",{"durationSeconds": 7.0, "paragraphStarts": [0, 0.2, 2.4], "measured": true});});

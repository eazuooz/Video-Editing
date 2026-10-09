import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanationMeasuredV8} from '../measured-score-explanation-frame-exact-v8';
export default makeScene2D(function* (view) {yield* scoreExplanationMeasuredV8(view,"08-scoring-feedback",{"durationSeconds": 4.0, "paragraphStarts": [0, 0.5, 3.3], "measured": true});});

import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanationBalatroRevisionV2} from '../revision-spatial-score-explanation-v2';
export default makeScene2D(function* (view) {yield* scoreExplanationBalatroRevisionV2(view,"08-scoring-feedback",{"durationSeconds": 4.0, "paragraphStarts": [0, 0.5, 3.3], "measured": true});});

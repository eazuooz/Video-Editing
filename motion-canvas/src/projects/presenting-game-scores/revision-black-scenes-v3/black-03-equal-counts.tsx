import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanationBalatroRevisionV2} from '../revision-spatial-score-explanation-v2';
export default makeScene2D(function* (view) {yield* scoreExplanationBalatroRevisionV2(view,"03-same-count",{"durationSeconds": 7.0, "paragraphStarts": [0, 0.2, 2.4], "measured": true});});

import {makeScene2D} from '@motion-canvas/2d';
import {customizationExplanation} from '../spatial-explanation-fixes-v2';
import timings from '../current-voice-timing-v1.json';
export default makeScene2D(function*(view){yield* customizationExplanation(view,'05-manageable-choice',timings.rows[4]);});

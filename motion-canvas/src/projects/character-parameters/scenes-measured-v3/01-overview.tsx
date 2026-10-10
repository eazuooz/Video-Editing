import {makeScene2D} from '@motion-canvas/2d';
import {characterExplanationMeasured} from '../spatial-character-explanation-measured-v3';
export default makeScene2D(function* (view){yield* characterExplanationMeasured(view,"01-overview",{"durationSeconds":15.9,"paragraphStarts":[0.0,3.89,10.19],"measured":true,"blackIntervals":[{"startFrame":0,"frames":234}]});});

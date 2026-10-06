import {makeScene2D} from '@motion-canvas/2d';
import {guideExplanation} from '../guide-explanation';
// Lookdev only. Measured voiced length and every final cue remain pending.
export default makeScene2D(function* (view) {yield* guideExplanation(view,'14',600,true);});

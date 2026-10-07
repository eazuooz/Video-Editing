import {makeScene2D} from '@motion-canvas/2d';
import {depthExplanation} from '../depth-explanations-v1';
export default makeScene2D(function*(view){yield*depthExplanation(view,'13-3-white-comparison',450);});

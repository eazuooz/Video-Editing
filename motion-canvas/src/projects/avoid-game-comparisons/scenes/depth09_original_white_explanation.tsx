import {makeScene2D} from '@motion-canvas/2d';
import {depthExplanation} from '../depth-explanations-v1';
export default makeScene2D(function*(view){yield*depthExplanation(view,'09-original-white-explanation',2098);});

import {makeScene2D} from '@motion-canvas/2d';
import {explainScene} from './concepts';
export default makeScene2D(function*(view){yield* explainScene(view,'11');});

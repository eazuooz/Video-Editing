import {makeScene2D} from '@motion-canvas/2d';
import {actualScene} from './actual-scene';
export default makeScene2D(function*(view){yield* actualScene(view,'16');});

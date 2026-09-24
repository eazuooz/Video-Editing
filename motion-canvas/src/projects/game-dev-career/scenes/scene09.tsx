import {makeScene2D} from '@motion-canvas/2d';
import {finalScene} from '../final-scene';
export default makeScene2D(function*(view){yield* finalScene(view,8);});

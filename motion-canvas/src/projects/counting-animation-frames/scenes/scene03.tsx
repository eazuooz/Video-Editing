import {makeScene2D} from '@motion-canvas/2d';
import {bodyScene} from '../body-scene';
export default makeScene2D(function*(view){yield* bodyScene(view,2);});

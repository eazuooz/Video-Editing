import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from '../../scene-kit';
export default makeScene2D(function*(view){yield* lesson(view,25);});

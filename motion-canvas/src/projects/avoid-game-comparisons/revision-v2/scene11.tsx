import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,'shared',{duration:10});});

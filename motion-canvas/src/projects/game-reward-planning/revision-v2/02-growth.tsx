import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './lesson-visuals';
import timing from './visual-timing.json';
export default makeScene2D(function*(view){yield* lesson(view,'growth',timing.growth);});

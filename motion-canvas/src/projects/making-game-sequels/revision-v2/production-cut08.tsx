import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,"layers",{"duration": 14.0, "cues": [0, 0, 0, 1, 2]});});

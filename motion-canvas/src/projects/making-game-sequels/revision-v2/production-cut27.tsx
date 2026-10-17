import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,"value",{"duration": 15.35, "cues": [0, 0.7, 1.4, 2.1, 8.71999999999997]});});

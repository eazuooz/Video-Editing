import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,"test",{"duration": 20.15, "cues": [0, 0.6, 1.2, 3, 5]});});

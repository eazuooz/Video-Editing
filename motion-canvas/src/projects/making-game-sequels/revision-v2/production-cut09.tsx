import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,"work",{"duration": 27.333333333333332, "cues": [0, 2, 7.859999999999999, 10.86, 18.0]});});

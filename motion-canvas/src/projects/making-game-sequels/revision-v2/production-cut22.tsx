import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,"oatchi",{"duration": 7.233333333333333, "cues": [0, 0.7, 1.4, 2.2, 3]});});

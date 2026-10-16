import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './lesson-visuals';
export default makeScene2D(function*(view){yield* lesson(view,"training",{"duration": 18.783333333333335, "cues": [0, 0.8, 2.88, 8.66, 15]});});

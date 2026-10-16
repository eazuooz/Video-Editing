import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './lesson-visuals';
export default makeScene2D(function*(view){yield* lesson(view,"worksheet",{"duration": 40.31666666666667, "cues": [2.34, 14.3, 16.7, 19, 22.42]});});

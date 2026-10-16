import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './lesson-visuals';
export default makeScene2D(function*(view){yield* lesson(view,"unlock",{"duration": 10.6, "cues": [0, 4.14, 7.2, 4.14, 9]});});

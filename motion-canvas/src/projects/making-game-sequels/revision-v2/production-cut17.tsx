import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,"experience",{"duration": 14.2, "cues": [0, 0.6, 1.2, 2, 5.339999999999975]});});

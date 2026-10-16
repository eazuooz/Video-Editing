import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './lesson-visuals';
export default makeScene2D(function*(view){yield* lesson(view,"powerLoss",{"duration": 18.616666666666667, "cues": [0, 7.34, 10.0, 12.8, 16]});});

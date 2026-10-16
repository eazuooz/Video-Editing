import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './lesson-visuals';
export default makeScene2D(function*(view){yield* lesson(view,"trophyCost",{"duration": 27.983333333333334, "cues": [0, 2, 11.56, 16.0, 20]});});

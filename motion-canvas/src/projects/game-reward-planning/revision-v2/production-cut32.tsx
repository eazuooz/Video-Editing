import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './lesson-visuals';
export default makeScene2D(function*(view){yield* lesson(view,"progress",{"duration": 34.53333333333333, "cues": [0, 10.0, 24.0, 26.5, 29]});});

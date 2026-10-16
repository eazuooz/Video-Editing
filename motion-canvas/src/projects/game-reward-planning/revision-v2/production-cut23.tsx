import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './lesson-visuals';
export default makeScene2D(function*(view){yield* lesson(view,"coins",{"duration": 33.18333333333333, "cues": [0, 8.38, 15.62, 20.56, 29.44]});});

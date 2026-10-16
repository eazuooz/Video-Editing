import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './lesson-visuals';
export default makeScene2D(function*(view){yield* lesson(view,"growth",{"duration": 28.9, "cues": [0, 13, 16.38, 21.04, 25.72]});});

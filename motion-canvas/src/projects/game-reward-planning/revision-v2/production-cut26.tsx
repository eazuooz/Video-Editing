import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './lesson-visuals';
export default makeScene2D(function*(view){yield* lesson(view,"music",{"duration": 46.1, "cues": [0, 5.4, 9.58, 15.56, 21.58]});});

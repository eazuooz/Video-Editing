import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './lesson-visuals';
export default makeScene2D(function*(view){yield* lesson(view,"checklist",{"duration": 31.283333333333335, "cues": [0, 7.82, 11.42, 14.58, 19.3]});});

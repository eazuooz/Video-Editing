import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './lesson-visuals';
export default makeScene2D(function*(view){yield* lesson(view,"spiritRules",{"duration": 17.15, "cues": [0, 8.54, 12.2, 14.0, 15]});});

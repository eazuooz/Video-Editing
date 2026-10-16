import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './lesson-visuals';
export default makeScene2D(function*(view){yield* lesson(view,"overview",{"duration": 23.5, "cues": [0, 7.12, 15.4, 18.5, 21]});});

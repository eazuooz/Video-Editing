import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './lesson-visuals';
export default makeScene2D(function*(view){yield* lesson(view,"checklist",{"duration": 19.316666666666666, "cues": [0, 13.84, 15.7, 17.1, 18]});});

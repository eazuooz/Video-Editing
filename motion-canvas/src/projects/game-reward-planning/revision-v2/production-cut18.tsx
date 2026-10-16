import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './lesson-visuals';
export default makeScene2D(function*(view){yield* lesson(view,"stickers",{"duration": 20.483333333333334, "cues": [0, 4.44, 10, 7.3, 17]});});

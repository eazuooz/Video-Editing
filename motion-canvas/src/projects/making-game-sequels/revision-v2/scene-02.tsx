import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,"foundation",{duration:12,cues:[0,1.5,3.5,5.5,7.5]});});

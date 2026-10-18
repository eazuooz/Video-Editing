import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
// Look development only; final production uses measured speech cues.
export default makeScene2D(function*(view){yield* lesson(view,"standard",{duration:119/60,cues:[0,.1,.2,.3,.4,.5],credit:'실제 게임 화면·출처는 제작 설계표에 기록'});});

import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,{duration:6,cues:[0,1.5,3],title:'시각 설명 · 내부 사전 점검',mode:'flow',labels:['정보','판단','행동']});});

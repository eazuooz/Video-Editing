import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,"auto",{"duration": 3.9875, "cues": [0.0, 0.8, 1.6, 2.4000000000000004], "credit": "설명 화면 내부 시안 · 실제 출처는 제작 설계표"});});

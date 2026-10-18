import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,"overview",{"duration": 3.9875, "cues": [0.0, 1.0666666666666667, 2.1333333333333333], "credit": "설명 화면 내부 시안 · 실제 출처는 제작 설계표"});});

import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view) {yield* lesson(view, {"kind": "puzzle", "title": "같은 큰 규칙, 다른 구체적인 표현", "duration": 16.383333333333333, "currentPicture": "해설용 도식 · 실제 화면 인용", "cueTimes": [0.05, 1.8, 4]});});

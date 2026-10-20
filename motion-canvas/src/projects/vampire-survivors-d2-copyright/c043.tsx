import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view) {yield* lesson(view, {"kind": "permissions", "title": "무료라는 말과 허락은 다릅니다", "duration": 11.783333333333333, "currentPicture": "해설용 도식 · 실제 화면 인용", "cueTimes": [0.05, 1.8, 4]});});

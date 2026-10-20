import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view) {yield* lesson(view, {"kind": "court", "title": "개별 요소뿐 아니라 결합도 봅니다", "duration": 12.2, "currentPicture": "해설용 도식 · 실제 화면 인용", "cueTimes": [0.05, 1.8, 4]});});

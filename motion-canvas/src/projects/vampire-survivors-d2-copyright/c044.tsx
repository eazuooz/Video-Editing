import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view) {yield* lesson(view, {"kind": "files", "title": "파일은 어디에서 읽을까?", "duration": 9.866666666666667, "currentPicture": "해설용 도식 · 실제 화면 인용", "cueTimes": [0.05, 1.8, 4]});});

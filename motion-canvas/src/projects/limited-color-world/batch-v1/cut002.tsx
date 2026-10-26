import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,{"mode": "color", "title": "같은 색을 찾는 순간", "labels": ["종류 A", "종류 B", "같은 모양"], "summary": "색 차이가 줄면, 종류를 알려 주던 단서도 줄어듭니다", "images": ["/@fs/D:/Github/VideoEditing/projects/limited-color-world/production/local/batch-v1/visual-assets/puyo.jpg"], "duration": 2.45, "cues": [-7.370000000000001, -5.250000000000002, -2.450000000000003]});});

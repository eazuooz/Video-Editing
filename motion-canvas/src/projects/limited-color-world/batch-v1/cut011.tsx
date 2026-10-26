import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,{"mode": "lightness", "title": "밝기와 모양을 함께", "labels": ["어두움", "밝음", "배경"], "summary": "명도 차이가 남으면 경계를 찾기 쉽습니다", "images": ["/@fs/D:/Github/VideoEditing/projects/limited-color-world/production/local/batch-v1/visual-assets/puyo.jpg"], "duration": 4.266666666666667, "cues": [0.28666666666666174, 2.4266666666666623, 5.36666666666666]});});

import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,{"mode": "background", "title": "밝기와 모양을 함께", "labels": ["어두운 블록", "밝은 블록", "어두운 배경"], "summary": "블록끼리 + 배경에서의 분리를 함께 봅니다", "images": ["/@fs/D:/Github/VideoEditing/projects/limited-color-world/production/local/batch-v1/visual-assets/puyo.jpg"], "duration": 4.033333333333333, "cues": [0.0033333333333303017, 2.423333333333332, 5.483333333333334]});});

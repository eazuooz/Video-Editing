import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,{"mode": "grayscale", "title": "색을 빼면 보이는 위계", "labels": ["같은 화면", "색을 빼기", "명도 배치"], "summary": "같은 화면에서 색만 뺀 비교입니다", "images": ["/@fs/D:/Github/VideoEditing/projects/limited-color-world/production/local/batch-v1/visual-assets/mario.jpg", "/@fs/D:/Github/VideoEditing/projects/limited-color-world/production/local/batch-v1/visual-assets/mario-gray.jpg"], "duration": 9.5, "cues": [0.1633333333333269, 4.48333333333332, 6.963333333333338]});});

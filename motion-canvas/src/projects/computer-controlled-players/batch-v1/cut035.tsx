import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,{"mode": "controls", "title": "반응할 시간과 실수", "labels": ["조작 방향 반전", "잠깐의 혼란", "상태에 적응"], "summary": "짧은 혼란 뒤 회복 · 끝없는 추락으로 이어지지 않게", "images": ["/@fs/D:/Github/VideoEditing/projects/computer-controlled-players/production/local/batch-v1/visual-assets/smash.jpg"], "duration": 11.8, "cues": [-0.006666666666689025, 5.1133333333333155, 8.113333333333316]});});

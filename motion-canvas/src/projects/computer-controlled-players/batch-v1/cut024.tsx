import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,{"mode": "range", "title": "거리 하나가 행동을 바꾸기", "labels": ["공격 2칸", "상대 3칸", "한 칸 접근"], "summary": "한 칸 접근 → 공격이 닿는 거리", "images": ["/@fs/D:/Github/VideoEditing/projects/computer-controlled-players/production/local/batch-v1/visual-assets/smash.jpg"], "duration": 12.1, "cues": [0.326666666666668, 2.7666666666666657, 5.266666666666666, 7.846666666666678]});});

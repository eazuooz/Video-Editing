import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,{"mode": "priority", "title": "움직임과 사람다운 판단", "labels": ["상황 없는 공격", "위험으로 이동", "상황을 읽는 판단"], "summary": "움직이는 것과, 상황을 읽는 것은 다릅니다", "images": ["/@fs/D:/Github/VideoEditing/projects/computer-controlled-players/production/local/batch-v1/visual-assets/smash.jpg"], "duration": 14.2, "cues": [1.3533333333333353, 4.653333333333336, 9.173333333333336]});});

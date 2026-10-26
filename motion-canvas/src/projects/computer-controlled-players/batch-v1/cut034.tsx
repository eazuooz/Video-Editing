import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,{"mode": "delay", "title": "반응할 시간과 실수", "labels": ["알아챈 시점", "행동 시점", "12 ÷ 60 = 0.2초"], "summary": "설명 모형의 수치 · 실제 CP 지연 측정값이 아닙니다", "images": ["/@fs/D:/Github/VideoEditing/projects/computer-controlled-players/production/local/batch-v1/visual-assets/smash.jpg"], "duration": 10.7, "cues": [-0.006666666666660603, 2.5933333333333337, 6.2733333333333405]});});

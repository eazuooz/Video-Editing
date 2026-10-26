import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view){yield* lesson(view,{"mode": "priority", "title": "변하는 상태와 겹치는 판단", "labels": ["다가가 공격", "위험해 후퇴", "우선순위 선택"], "summary": "언제 행동을 바꿀지도 정합니다", "images": ["/@fs/D:/Github/VideoEditing/projects/computer-controlled-players/production/local/batch-v1/visual-assets/smash.jpg"], "duration": 14.283333333333333, "cues": [0.0033333333333303017, 1.8433333333333337, 5.8233333333333235, 9.883333333333326]});});

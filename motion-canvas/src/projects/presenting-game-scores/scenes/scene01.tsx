import {makeScene2D} from '@motion-canvas/2d';
import {paperScene} from './paper-scene';
import {SCENE_DURATIONS} from '../timing';
export default makeScene2D(function* (view) {
  yield* paperScene(view,0,'점수는 무엇을 말해 줄까? 이름·단위·비교 기준으로 읽는 게임 성과','이번 영상에서 답할 질문',SCENE_DURATIONS[0]);
});

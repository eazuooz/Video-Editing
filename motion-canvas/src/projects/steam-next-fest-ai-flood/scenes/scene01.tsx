import {makeScene2D} from '@motion-canvas/2d';
import {paperScene} from './paper-scene';
import {SCENE_DURATIONS} from '../timing';
export default makeScene2D(function* (view) {
  yield* paperScene(view,0,'스팀 데모 8,000개, 좋은 게임 찾기가 왜 복권이 됐을까?','이번 영상에서 답할 질문',SCENE_DURATIONS[0]);
});

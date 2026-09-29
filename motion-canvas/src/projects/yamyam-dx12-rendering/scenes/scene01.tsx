import {makeScene2D} from '@motion-canvas/2d';
import {paperScene} from './paper-scene';
import {SCENE_DURATIONS} from '../timing';
export default makeScene2D(function* (view) {
  yield* paperScene(view,0,'화면 하나 제대로 띄우기까지 | 얌얌엔진 DX12 개발기','이번 영상에서 답할 질문',SCENE_DURATIONS[0]);
});

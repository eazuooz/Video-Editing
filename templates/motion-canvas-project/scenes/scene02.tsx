import {makeScene2D} from '@motion-canvas/2d';
import {paperScene} from './paper-scene';
import {SCENE_DURATIONS} from '../timing';
export default makeScene2D(function* (view) {
  yield* paperScene(view,1,'핵심 원리','개념 → 시각적 예시 → 직접 적용',SCENE_DURATIONS[1]);
});

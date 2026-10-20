import {makeScene2D} from '@motion-canvas/2d';
import {paperScene} from './paper-scene';
import {SCENE_DURATIONS} from '../timing';
export default makeScene2D(function* (view) {
  yield* paperScene(view,2,'정리','오늘 기억할 핵심 한 가지',SCENE_DURATIONS[2]);
});

import {makeScene2D} from '@motion-canvas/2d';
import {paperScene} from './paper-scene';
import {SCENE_DURATIONS} from '../timing';
export default makeScene2D(function* (view) {
  yield* paperScene(view,5,SCENE_DURATIONS[5]);
});

import {makeScene2D} from '@motion-canvas/2d';
import {dioramaScene as paperScene} from './diorama-scene';
import {SCENE_DURATIONS} from '../timing';
export default makeScene2D(function* (view) {
  yield* paperScene(view,1,SCENE_DURATIONS[1]);
});

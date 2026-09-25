import {makeScene2D} from '@motion-canvas/2d';
import {windowScene} from './window-scene';
export default makeScene2D(function* (view) {yield* windowScene(view,4);});

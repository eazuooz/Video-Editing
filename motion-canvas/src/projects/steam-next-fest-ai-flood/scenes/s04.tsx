import {makeScene2D} from '@motion-canvas/2d';
import {overlayScene} from '../overlay';
export default makeScene2D(function* (view) { yield* overlayScene(view, '04'); });

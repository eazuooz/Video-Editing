import {makeScene2D} from '@motion-canvas/2d';
import {showcaseScene} from './showcase-scene';
export default makeScene2D(function* (view) { yield* showcaseScene(view, 8); });

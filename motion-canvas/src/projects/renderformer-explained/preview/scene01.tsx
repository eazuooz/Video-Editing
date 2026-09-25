import {makeScene2D} from '@motion-canvas/2d';
import {slide} from './slide';
export default makeScene2D(function*(view){yield* slide(view,0);});

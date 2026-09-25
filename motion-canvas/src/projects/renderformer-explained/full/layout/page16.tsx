import {makeScene2D} from '@motion-canvas/2d';
import {lectureSlide} from '../slide';
import timing from '../layout.generated.json';
export default makeScene2D(function* (view) {yield* lectureSlide(view,timing.scenes[15],false);});

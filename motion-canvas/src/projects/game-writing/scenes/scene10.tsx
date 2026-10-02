import {makeScene2D} from '@motion-canvas/2d';
import {narrativeConcept} from './narrative-concept';
export default makeScene2D(function*(view){yield* narrativeConcept(view,4,45.06666666666667);});

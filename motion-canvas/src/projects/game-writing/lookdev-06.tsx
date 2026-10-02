import {makeScene2D} from '@motion-canvas/2d';
import {narrativeConcept} from './scenes/narrative-concept';
export default makeScene2D(function*(view){yield* narrativeConcept(view,2,8);});

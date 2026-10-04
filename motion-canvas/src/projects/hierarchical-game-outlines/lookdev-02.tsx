import {makeScene2D} from '@motion-canvas/2d';
import {outlineConcept} from './scenes/outline-concepts';
export default makeScene2D(function*(view){yield* outlineConcept(view,0,8);});

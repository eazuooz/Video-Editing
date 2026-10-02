import {makeScene2D} from '@motion-canvas/2d';
import {spectatorConcept} from './spectator-concepts';
export default makeScene2D(function*(view){yield* spectatorConcept(view,3,39.68333333333333);});

import {makeScene2D} from '@motion-canvas/2d';
import {cameraConcept} from './scenes/camera-concepts';
export default makeScene2D(function*(view){yield* cameraConcept(view,0,8);});

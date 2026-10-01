import {makeScene2D} from '@motion-canvas/2d';
import {diagramScene} from './diagram';
export default makeScene2D(function*(view){yield* diagramScene(view,0,10);});

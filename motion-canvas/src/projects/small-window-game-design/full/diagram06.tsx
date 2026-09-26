import {makeScene2D} from '@motion-canvas/2d';
import {diagramScene} from './diagram';
import plan from './plan.json';
export default makeScene2D(function*(view){yield* diagramScene(view,5,plan.scenes[5].diagramSeconds);});

import {makeScene2D} from '@motion-canvas/2d';
import {diagramScene} from '../diagram';
import plan from '../production-plan.json';
export default makeScene2D(function*(view){yield* diagramScene(view,2,plan.scenes[2].diagramSeconds);});

import {makeScene2D} from '@motion-canvas/2d';
import {measuredWhiteDiagram} from '../timed-white-diagram-v4';
import plan from '../timed-white-reel-plan-v4.json';
export default makeScene2D(function*(view){const s=plan.rows[3];yield*measuredWhiteDiagram(view,s.sceneId,s.frames);});

import {makeScene2D} from '@motion-canvas/2d';
import {conceptDiagram} from './concept-diagrams';
import {cueDiagram} from './cue-diagrams';
import plan from '../timed-white-reel-plan-v6.json';
export default makeScene2D(function*(view){const s=plan.rows[9];yield*cueDiagram(view,'10-4',s.seconds);});

import {makeScene2D} from '@motion-canvas/2d';
import {conceptDiagram} from './concept-diagrams';
import {cueDiagram} from './cue-diagrams';
import plan from '../timed-white-reel-plan-v6.json';
export default makeScene2D(function*(view){const s=plan.rows[1];yield*conceptDiagram(view,'03',s.seconds,s.paragraphEnds);});

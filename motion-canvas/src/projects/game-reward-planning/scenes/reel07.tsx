import {makeScene2D} from '@motion-canvas/2d';
import {rewardConcept} from './reward-concepts';
import plan from '../measured-reel-plan.json';
export default makeScene2D(function*(view){const s=plan.scenes.find(s=>s.id==='07')!;yield*rewardConcept(view,3,s.seconds,s.paragraphEnds);});

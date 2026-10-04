import {makeScene2D} from '@motion-canvas/2d';
import plan from '../production-plan.json';
import {rewardConcept} from './reward-concepts';
export function explanationScene(id:string,index:number){return makeScene2D(function*(view){
 const scene=plan.scenes.find(s=>s.id===id);
 if(!plan.currentFinalTimingApproved||!scene?.seconds||!scene.paragraphEnds.length)throw Error(`Scene${id}: current narration and reviewed paragraph timing required`);
 yield*rewardConcept(view,index,scene.seconds,scene.paragraphEnds);
});}

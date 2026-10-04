import {makeScene2D} from '@motion-canvas/2d';
import plan from '../production-plan.json';
import {outlineConcept} from './outline-concepts';
export function explanationScene(id:string,index:number) {
  return makeScene2D(function*(view) {
    const scene=plan.scenes.find(s=>s.id===id);
    if(!plan.currentFinalTimingApproved||!scene?.seconds||scene.paragraphEnds.length!==4)throw Error(`Scene${id}: current narration/paragraph timing required`);
    yield* outlineConcept(view,index,scene.seconds,scene.paragraphEnds);
  });
}

import {makeScene2D} from '@motion-canvas/2d';
import plan from '../production-plan.json';
import {conceptDiagram} from './concept-diagrams';
export function explanationScene(id:string){return makeScene2D(function*(view){
  const scene=plan.scenes.find(s=>s.id===id);
  if(!plan.currentFinalTimingApproved||!scene||scene.role!=='explanation'||!scene.frames||scene.paragraphEnds.length!==scene.paragraphs){
    throw Error(`Scene${id}: reviewed measured paragraph boundaries required; silent lookdev is separate`);
  }
  yield*conceptDiagram(view,id,scene.seconds,scene.paragraphEnds);
});}

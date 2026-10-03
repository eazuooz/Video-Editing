import {makeScene2D} from '@motion-canvas/2d';
import plan from '../production-plan.json';
import {cameraConcept} from './camera-concepts';

export function explanationScene(id: string, index: number) {
  return makeScene2D(function* (view) {
    const scene = plan.scenes.find(scene => scene.id === id);
    if (!plan.currentFinalTimingApproved || !scene?.seconds || scene.paragraphEnds.length !== 4) {
      throw new Error(`Scene ${id}: current narration/paragraph timing required`);
    }
    yield* cameraConcept(view, index, scene.seconds, scene.paragraphEnds);
  });
}

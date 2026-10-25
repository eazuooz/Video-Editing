import {makeScene2D} from '@motion-canvas/2d';
import {lesson, type LessonKind} from './visuals';

/** Revised internal mechanism sample only:3 modes ×4s=720frames@60fps. */
export default makeScene2D(function* (view) {
  const modes: LessonKind[] = ['complete', 'purpose', 'appeals'];
  for (const mode of modes) {
    view.removeChildren();
    yield* lesson(view, mode, {duration: 4, cues: [0, .8, 1.65, 2.5], preflight: true, imagePaths: {"drgs": "/@fs/D:/Github/VideoEditing/projects/similar-game-design/production/local/reference-preserving-v2/visual-assets/drgs.png", "mm2": "/@fs/D:/Github/VideoEditing/projects/similar-game-design/production/local/reference-preserving-v2/visual-assets/mm2.png", "social": "/@fs/D:/Github/VideoEditing/projects/similar-game-design/production/local/reference-preserving-v2/visual-assets/social.png"}});
  }
});

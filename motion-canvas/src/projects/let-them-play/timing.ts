// Generated measured chapter timing; historic reel keeps the default segment length.
import plan from '../../../../projects/let-them-play/planning/scenes.json';
import manifest from '../../../../projects/let-them-play/project.json';
import timeline from './timeline.generated.json';
export const NARRATION_FPS=manifest.video.fps;
export const SEGMENT_SECONDS=manifest.editing.exampleSeconds;
export const SEGMENT_DURATIONS=timeline.scenes.map(s=>s.segmentFrames/NARRATION_FPS);
export const SCENE_DURATIONS=timeline.scenes.map(s=>s.frames/NARRATION_FPS);
export const SCENE_STARTS=timeline.scenes.map(s=>s.startFrame/NARRATION_FPS);
export const SCENE_TITLES=plan.scenes.map(s=>s.title);
export const TOTAL_DURATION=SCENE_DURATIONS.reduce((a,b)=>a+b,0);
export const TOTAL_FRAMES=TOTAL_DURATION*NARRATION_FPS;

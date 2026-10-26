import {makeScene2D} from '@motion-canvas/2d';
import {cutsceneDiagram,CutsceneTiming} from './visuals';
import data from './motion-data.json';
export default makeScene2D(function*(view) {
  if(data.status!=='measured-ready') throw new Error('Measured voice-bound explanation data is required.');
  for(const beat of data.segments as CutsceneTiming[]) yield* cutsceneDiagram(view,beat);
});

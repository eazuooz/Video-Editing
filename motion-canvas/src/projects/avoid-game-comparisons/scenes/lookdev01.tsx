import {makeScene2D} from '@motion-canvas/2d';
import {conceptDiagram} from './concept-diagrams';
import {addCaptionClearanceGuide} from './lookdev-caption-guide';
export default makeScene2D(function*(view){
  // Explicit silent lookdev only: these provisional20s are not production timing.
  const duration=20,ends=Array.from({length:4},(_,i)=>duration*(i+1)/4);
  const diagram=conceptDiagram(view,'01',duration,ends,true);
  addCaptionClearanceGuide(view);
  yield*diagram;
});

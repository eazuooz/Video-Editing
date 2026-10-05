import {makeScene2D} from '@motion-canvas/2d';
import {cueDiagram} from './cue-diagrams';
import {addCaptionClearanceGuide} from './lookdev-caption-guide';
export default makeScene2D(function*(view){
  addCaptionClearanceGuide(view);
  yield*cueDiagram(view,'06-2',4);
});

import {makeScene2D} from '@motion-canvas/2d';
import {conceptDiagram} from './concept-diagrams';
import {addCaptionClearanceGuide} from './lookdev-caption-guide';
export default makeScene2D(function*(view){
  const duration=8;
  addCaptionClearanceGuide(view);
  yield*conceptDiagram(view,'13',duration,[duration],true);
});

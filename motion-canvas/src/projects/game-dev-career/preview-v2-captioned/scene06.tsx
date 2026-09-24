import {makeScene2D} from '@motion-canvas/2d';
import {previewScene} from '../preview/preview-scene';
import timing from '../preview-v2/timing.generated.json';
export default makeScene2D(function*(view){yield* previewScene(view,5,timing,true);});

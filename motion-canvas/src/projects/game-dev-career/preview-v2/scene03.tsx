import {makeScene2D} from '@motion-canvas/2d';
import {previewScene} from '../preview/preview-scene';
import timing from './timing.generated.json';
export default makeScene2D(function*(view){yield* previewScene(view,2,timing);});

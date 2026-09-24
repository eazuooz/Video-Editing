import {makeScene2D} from '@motion-canvas/2d';
import {previewScene} from './preview-scene';
export default makeScene2D(function*(view){yield* previewScene(view,2);});

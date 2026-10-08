import {makeScene2D} from '@motion-canvas/2d';
import {customizationExplanation} from '../spatial-explanation-v1';
import timings from '../authoring-timing-v1.json';
export default makeScene2D(function*(view){yield* customizationExplanation(view,'06-quick-trial',{...timings.rows[5],measured:false});});

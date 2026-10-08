import {makeScene2D} from '@motion-canvas/2d';
import {customizationExplanation} from '../spatial-explanation-v1';
import timings from '../authoring-timing-v1.json';
export default makeScene2D(function*(view){yield* customizationExplanation(view,'02-visible-effects',{...timings.rows[1],measured:false});});

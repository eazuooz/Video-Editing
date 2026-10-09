import {makeScene2D} from '@motion-canvas/2d';
import {similarExplanation} from '../spatial-explanation-v1';
import timing from '../authoring-timing-v1.json';
export default makeScene2D(function*(view){yield* similarExplanation(view,'07-purpose-combination',{...timing.rows[6],measured:false});});

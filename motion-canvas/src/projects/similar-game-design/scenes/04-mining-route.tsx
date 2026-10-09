import {makeScene2D} from '@motion-canvas/2d';
import {similarExplanation} from '../spatial-explanation-v1';
import timing from '../authoring-timing-v1.json';
export default makeScene2D(function*(view){yield* similarExplanation(view,'04-mining-route',{...timing.rows[3],measured:false});});

import {makeScene2D} from '@motion-canvas/2d';
import {similarExplanation} from '../spatial-explanation-v1';
import timing from '../authoring-timing-v1.json';
export default makeScene2D(function*(view){yield* similarExplanation(view,'10-playing-together',{...timing.rows[9],measured:false});});

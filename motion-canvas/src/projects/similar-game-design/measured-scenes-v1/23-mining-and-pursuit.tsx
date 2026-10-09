import {makeScene2D} from '@motion-canvas/2d';
import {similarExplanation} from '../spatial-explanation-measured-v1';
import timing from '../measured-timing-v1.json';
export default makeScene2D(function*(view){yield* similarExplanation(view,'23-mining-and-pursuit',timing.full[4]);});

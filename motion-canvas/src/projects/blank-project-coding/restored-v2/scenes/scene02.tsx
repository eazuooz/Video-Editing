import {makeScene2D} from '@motion-canvas/2d';
import {explain} from '../explain';
export default makeScene2D(function*(view){yield*explain(view,'02');});

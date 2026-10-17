import {makeScene2D} from '@motion-canvas/2d';
import {screenshots} from './visuals';
export default makeScene2D(function*(view){yield* screenshots(view,"conditions",{"duration": 24.95, "cues": [0, 0.5, 3.0, 9.460000000000036, 17.680000000000007]});});

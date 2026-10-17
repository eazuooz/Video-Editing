import {makeScene2D} from '@motion-canvas/2d';
import {screenshots} from './visuals';
export default makeScene2D(function*(view){yield* screenshots(view,"pitch",{"duration": 20.533333333333335, "cues": [0, 4.399999999999999, 10.119999999999997, 16.259999999999998, 20.740000000000002]});});

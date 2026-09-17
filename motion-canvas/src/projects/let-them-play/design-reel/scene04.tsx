import {makeScene2D} from '@motion-canvas/2d';
import {comparisonScene} from '../scenes/design-comparison';
export default makeScene2D(function*(view){yield* comparisonScene(view,3);});

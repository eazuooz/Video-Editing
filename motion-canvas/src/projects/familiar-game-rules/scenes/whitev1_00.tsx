import {makeScene2D} from '@motion-canvas/2d';
import {timedWhiteInput} from '../timed-white-diagram-v1';
export default makeScene2D(function*(view){yield*timedWhiteInput(view,'01',1460);});

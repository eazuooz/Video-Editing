import {makeScene2D} from '@motion-canvas/2d';
import {conceptCard} from './paper-scene';
export default makeScene2D(function* (view){yield* conceptCard(view,6);});

import {makeScene2D} from '@motion-canvas/2d';
import {fullScene} from './runner';
import clip from '../assets/game-05.mp4';
export default makeScene2D(function*(view){yield* fullScene(view,4,clip);});

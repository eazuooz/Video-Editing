import {makeScene2D} from '@motion-canvas/2d';
import {playScene} from './play-clip';
import clip from '../assets/08.mp4';
export default makeScene2D(function*(view) {yield* playScene(view,clip,'08');});

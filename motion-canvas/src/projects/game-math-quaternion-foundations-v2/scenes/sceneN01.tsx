import {makeScene2D} from '@motion-canvas/2d';
import clip from '../assets/N01.mp4';
import {playScene} from './play-clip';
export default makeScene2D(function* (view){yield* playScene(view,clip,'N01');});

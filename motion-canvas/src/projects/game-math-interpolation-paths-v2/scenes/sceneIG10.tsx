import {makeScene2D} from '@motion-canvas/2d';
import clip from '../assets/IG10.mp4';
import {playScene} from './play-clip';
export default makeScene2D(function* (view){yield* playScene(view,clip,'IG10');});

import {makeScene2D} from '@motion-canvas/2d';
import media from '../assets/05.mp4';
import {playScene} from './play-clip';
// Independent 05 scene; rendered Manim or reviewed existing-game footage.
export default makeScene2D(function*(view){yield* playScene(view,media,'05');});


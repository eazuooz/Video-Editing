import {makeScene2D} from '@motion-canvas/2d';
import {episodeScene} from '../episode-scene';
export default makeScene2D(function*(view){yield* episodeScene(view,1,true);});

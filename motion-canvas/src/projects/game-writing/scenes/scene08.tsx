import {makeScene2D} from '@motion-canvas/2d';
import {narrativeConcept} from './narrative-concept';
import {SCENE_DURATIONS} from '../timing';
export default makeScene2D(function*(view){yield* narrativeConcept(view,3,SCENE_DURATIONS[7]);});

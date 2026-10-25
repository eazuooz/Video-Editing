import {makeProject} from '@motion-canvas/core';
import preflight from './preflight-scene?scene';

// Does not start a renderer or change the shared project registry.
export default makeProject({scenes: [preflight]});

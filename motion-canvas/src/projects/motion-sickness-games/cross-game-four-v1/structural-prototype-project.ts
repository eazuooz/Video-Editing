import {makeProject} from '@motion-canvas/core';
import portal from './portal-comparison?scene';
import arrival from './arrival-comparison?scene';
import transfer from './four-game-transfer?scene';
// Silent structural prototypes only; no measured narration or final cue approval.
export default makeProject({scenes:[portal,arrival,transfer]});

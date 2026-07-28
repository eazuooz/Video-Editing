import {makeProject} from '@motion-canvas/core';

import basic from './scenes/jumpPhysics/basic?scene';
import celeste from './scenes/jumpPhysics/celeste?scene';
import ghosts from './scenes/jumpPhysics/ghosts?scene';
import jumpKing from './scenes/jumpPhysics/jumpKing?scene';
import mario from './scenes/jumpPhysics/mario?scene';
import megaman from './scenes/jumpPhysics/megaman?scene';
import metroid from './scenes/jumpPhysics/metroid?scene';
import sf2 from './scenes/jumpPhysics/sf2?scene';
import smashSquat from './scenes/jumpPhysics/smashSquat?scene';
import smashUltimate from './scenes/jumpPhysics/smashUltimate?scene';

export default makeProject({
  scenes: [
    basic,
    mario,
    metroid,
    ghosts,
    sf2,
    smashSquat,
    smashUltimate,
    jumpKing,
    celeste,
    megaman,
  ],
});

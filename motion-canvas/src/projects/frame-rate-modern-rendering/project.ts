import {makeProject} from '@motion-canvas/core';

// Shared with the final MP4: narration, source audio, and background music.
// Regenerate with scripts/mix-frame-rate-audio.ps1 when audio inputs change.
import finalMix from './assets/final-mix.m4a';
import scene01 from './scenes/scene01?scene';
import scene02 from './scenes/scene02?scene';
import scene03 from './scenes/scene03?scene';
import scene04 from './scenes/scene04?scene';
import scene05 from './scenes/scene05?scene';
import scene06 from './scenes/scene06?scene';
import scene07 from './scenes/scene07?scene';
import scene08 from './scenes/scene08?scene';
import scene09 from './scenes/scene09?scene';
import scene10 from './scenes/scene10?scene';
import scene11 from './scenes/scene11?scene';
import scene12 from './scenes/scene12?scene';
import scene13 from './scenes/scene13?scene';
import scene14 from './scenes/scene14?scene';
import scene15 from './scenes/scene15?scene';
import scene16 from './scenes/scene16?scene';
import scene17 from './scenes/scene17?scene';
import scene18 from './scenes/scene18?scene';
import scene19 from './scenes/scene19?scene';
import scene20 from './scenes/scene20?scene';

export default makeProject({
  name: 'frame-rate-modern-rendering',
  audio: finalMix,
  scenes: [
    scene01,
    scene02,
    scene03,
    scene04,
    scene05,
    scene06,
    scene07,
    scene08,
    scene09,
    scene10,
    scene11,
    scene12,
    scene13,
    scene14,
    scene15,
    scene16,
    scene17,
    scene18,
    scene19,
    scene20,
  ],
});

import {makeProject} from '@motion-canvas/core';

// Same narrated mix as the review MP4, decoded to PCM for editor compatibility.
// Third-party source publication permissions remain pending.
import finalMix from './assets/final-mix.wav';
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

export default makeProject({
  name: 'gpt-astra-showcase',
  audio: finalMix,
  scenes: [scene01, scene02, scene03, scene04, scene05, scene06, scene07, scene08, scene09, scene10],
});

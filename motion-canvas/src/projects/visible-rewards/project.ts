import {makeProject} from '@motion-canvas/core';

// Same full mix as final MP4. PCM supports both desktop and VS Code webviews.
import finalMix from './assets/final-mix.wav';
import scene01 from './scenes/scene01?scene';
import scene02 from './scenes/scene02?scene';
import scene03 from './scenes/scene03?scene';
import scene04 from './scenes/scene04?scene';
import scene05 from './scenes/scene05?scene';
import scene06 from './scenes/scene06?scene';
import scene07 from './scenes/scene07?scene';
import scene08 from './scenes/scene08?scene';

export default makeProject({
  name: 'visible-rewards',
  audio: finalMix,
  scenes: [scene01, scene02, scene03, scene04, scene05, scene06, scene07, scene08],
});

import {makeProject} from '@motion-canvas/core';

import narration from './assets/narration.wav';
import scene01 from './scenes/scene01?scene';
import scene02 from './scenes/scene02?scene';
import scene03 from './scenes/scene03?scene';

export default makeProject({
  name: '{{SLUG}}',
  audio: narration,
  scenes: [scene01, scene02, scene03],
});

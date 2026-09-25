// Korean boxed-caption version (boxed-white-forest-v1). Same scenes, timing and audio as project.ts.
import {makeProject} from '@motion-canvas/core';
import {captionMode} from './caption-mode';

// Final mix: narration + quiet Odyssey sound + continuous Discovery (scripts/mix-play-first-audio.cjs).
import narration from './assets/final-mix.wav';
import scene01 from './scenes/scene01?scene';
import scene02 from './scenes/scene02?scene';
import scene03 from './scenes/scene03?scene';
import scene04 from './scenes/scene04?scene';
import scene05 from './scenes/scene05?scene';
import membershipOutro from './scenes/membership-outro?scene';

captionMode.on = true;

export default makeProject({
  name: 'play-first-captioned',
  audio: narration,
  scenes: [scene01, scene02, scene03, scene04, scene05, membershipOutro],
});

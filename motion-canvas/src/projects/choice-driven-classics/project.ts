import {makeProject} from '@motion-canvas/core';

// BGM-only review, not the final narration mix. Voice approval is still pending.
import reviewAudio from './assets/bgm-review-v2.wav';
import scene01 from './scenes/scene01?scene';
import scene02 from './scenes/scene02?scene';
import scene03 from './scenes/scene03?scene';
import scene04 from './scenes/scene04?scene';
import scene05 from './scenes/scene05?scene';
import scene06 from './scenes/scene06?scene';

export default makeProject({
  name: 'choice-driven-classics',
  audio: reviewAudio,
  scenes: [scene01, scene02, scene03, scene04, scene05, scene06],
});

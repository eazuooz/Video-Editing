import {makeProject} from '@motion-canvas/core';

// The mixer connects a validated PCM WAV for VS Code / Chromium playback.
// The AAC sibling is reserved for the MP4 mux. Per-video audio stays muted.
import narration from './editor-audio.generated';
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

export default makeProject({
  name: 'ai-era-cs-fundamentals',
  audio: narration,
  scenes: [scene01, scene02, scene03, scene04, scene05, scene06, scene07, scene08, scene09, scene10, scene11, scene12],
});

import {makeProject} from '@motion-canvas/core';
import scene13 from './scenes/lookdev13?scene';
import scene14 from './scenes/lookdev14?scene';
import cue062 from './scenes/lookdev-cue062?scene';
import cue064 from './scenes/lookdev-cue064?scene';
import cue102 from './scenes/lookdev-cue102?scene';
import cue104 from './scenes/lookdev-cue104?scene';
import cue122 from './scenes/lookdev-cue122?scene';
import cue153 from './scenes/lookdev-cue153?scene';
// Separate silent layout review; production factories retain their final gates.
export default makeProject({name:'avoid-game-comparisons-new-diagram-lookdev',
  scenes:[scene13,scene14,cue062,cue064,cue102,cue104,cue122,cue153]});

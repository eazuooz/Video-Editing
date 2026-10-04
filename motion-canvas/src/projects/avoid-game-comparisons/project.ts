import {makeProject} from '@motion-canvas/core';
import intro from './scenes/branding-intro?scene';
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
import scene15 from './scenes/scene15?scene';
import scene13 from './scenes/scene13?scene';
import scene14 from './scenes/scene14?scene';
import outro from './scenes/membership-outro?scene';
// Final playback is guarded by measured scene/cut approval. The mix and
// burned narration captions will be attached only after current-audio QA.
export default makeProject({name:'avoid-game-comparisons',scenes:[intro,scene01,scene02,scene03,scene04,scene05,scene06,scene07,scene13,scene08,scene09,scene10,scene11,scene14,scene15,scene12,outro]});

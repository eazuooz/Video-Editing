import {makeProject} from '@motion-canvas/core';
// PCM decoded from the final AAC master: narration + quiet source + continuous BGM.
import finalMix from './assets/final-mix.wav';
import scene01 from './scenes/scene01?scene';
import scene02 from './scenes/scene02?scene';
import scene03 from './scenes/scene03?scene';
import scene04 from './scenes/scene04?scene';
import scene05 from './scenes/scene05?scene';
import scene06 from './scenes/scene06?scene';
import scene07 from './scenes/scene07?scene';
import scene08 from './scenes/scene08?scene';
export default makeProject({name:'let-them-play — 야숨 + 2.5D + 전체 오디오',audio:finalMix,scenes:[scene01,scene02,scene03,scene04,scene05,scene06,scene07,scene08]});

import {makeProject} from '@motion-canvas/core';
import audio from './assets/final-mix.wav';
import intro from './scenes/brand-intro?scene';
import s01 from './scenes/scene01?scene';
import s02 from './scenes/scene02?scene';
import s03 from './scenes/scene03?scene';
import s04 from './scenes/scene04?scene';
import s05 from './scenes/scene05?scene';
import s06 from './scenes/scene06?scene';
import s07 from './scenes/scene07?scene';
import outro from './scenes/membership-outro?scene';
export default makeProject({name:'game-math-polar-sample',audio,scenes:[intro,s01,s02,s03,s04,s05,s06,s07,outro]});


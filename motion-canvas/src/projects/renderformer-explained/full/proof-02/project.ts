import {makeProject} from '@motion-canvas/core';
import audio from './narration.wav';
import page01 from './page01?scene';
import page02 from './page02?scene';
export default makeProject({name:'RenderFormer — 본편 음성 검토', audio, scenes:[page01,page02]});

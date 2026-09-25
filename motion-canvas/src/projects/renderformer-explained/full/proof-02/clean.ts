import {makeProject} from '@motion-canvas/core';
import audio from './narration.wav';
import page01 from './page01-clean?scene';
import page02 from './page02-clean?scene';
export default makeProject({name:'RenderFormer — 무자막 본편 검토', audio, scenes:[page01,page02]});

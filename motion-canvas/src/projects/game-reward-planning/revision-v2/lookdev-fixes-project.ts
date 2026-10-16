import {makeProject} from '@motion-canvas/core';
import training from './03-training?scene';
import trophyCost from './05-trophyCost?scene';
import stickers from './06-stickers?scene';
import spiritRules from './06-spiritRules?scene';
import coins from './07-coins?scene';
import music from './08-music?scene';
import checklist from './09-checklist?scene';
// Only the seven changed layouts; retained other lookdev evidence stays valid.
export default makeProject({name:'game-reward-planning-v2-lesson-layout-fixes',scenes:[training,trophyCost,stickers,spiritRules,coins,music,checklist]});

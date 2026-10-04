import {makeScene2D} from '@motion-canvas/2d';
import {rewardConcept} from './reward-concepts';
export default makeScene2D(function*(view){yield*rewardConcept(view,1,8);});

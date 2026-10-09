import {makeScene2D} from '@motion-canvas/2d';
import {similarExplanation} from '../spatial-explanation-v1';
import timing from '../authoring-timing-v1.json';
export default makeScene2D(function*(view){const row=timing.rows.find(x=>x.id==='18-target-and-effects');if(!row)throw Error('Guide timing missing');yield* similarExplanation(view,'18-target-and-effects',{...row,measured:false});});

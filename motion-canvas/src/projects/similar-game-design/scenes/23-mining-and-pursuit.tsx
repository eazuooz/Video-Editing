import {makeScene2D} from '@motion-canvas/2d';
import {similarExplanation} from '../spatial-explanation-v1';
import timing from '../authoring-timing-v1.json';
export default makeScene2D(function*(view){const row=timing.rows.find(x=>x.id==='23-mining-and-pursuit');if(!row)throw Error('Guide timing missing');yield* similarExplanation(view,'23-mining-and-pursuit',{...row,measured:false});});

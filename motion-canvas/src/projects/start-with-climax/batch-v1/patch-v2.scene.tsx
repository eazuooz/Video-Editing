import {makeScene2D} from '@motion-canvas/2d';
import {openingDiagram,OpeningTiming} from './visuals';
import data from './patch-v2-data.json';
export default makeScene2D(function*(view) {
 if(data.status!=='measured-ready') throw new Error('Measured patch data required');
 for(const beat of data.segments as OpeningTiming[]) yield* openingDiagram(view,beat);
});

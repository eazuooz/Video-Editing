import {makeScene2D,Video} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import plan from '../production-plan.json';
export function actualScene(id:string){return makeScene2D(function*(view){const s=plan.scenes.find(s=>s.id===id);if(!s?.actualMediaVerified)throw new Error('Verified current actual scene required');view.add(<Video src={'/@fs/D:/Github/Video-Editing/'+s.actualVideo} width={1920} height={1080} play={true}/>);yield* waitFor(s.seconds);});}

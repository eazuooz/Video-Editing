import {makeScene2D,Video,Txt,View2D} from '@motion-canvas/2d';
import {createRef,waitFor} from '@motion-canvas/core';
import plan from '../production-plan.json';
export function* actualScene(view:View2D,id:string){const s=plan.scenes.find(s=>s.id===id)!;const video=createRef<Video>();view.add(<Video ref={video} src={'/@fs/D:/Github/Video-Editing/'+s.actualVideo} width={1920} height={1080}/>);(video() as any).video().muted=true;video().play();yield*waitFor(s.seconds);video().pause();}

import {makeScene2D,Video} from '@motion-canvas/2d';
import {createRef,usePlayback} from '@motion-canvas/core';
import plan from '../production-plan.json';
import {conceptDiagram} from './concept-diagrams';
type MixedScene={id:string;role:string;frames:number;actualFrames?:number;diagramFrames?:number;actualVideo?:string;actualMediaVerified?:boolean;actualAudioStreams?:number;};
export function mixedAdditiveScene(id:string){return makeScene2D(function*(view){
  const scene=plan.scenes.find(s=>s.id===id) as MixedScene|undefined;
  if(!plan.currentFinalTimingApproved||scene?.role!=='mixed-actual-explanation'||!scene.actualMediaVerified||scene.actualAudioStreams!==0||!scene.actualVideo||!scene.actualFrames||!scene.diagramFrames||scene.actualFrames+scene.diagramFrames!==scene.frames){
    throw Error(`Scene${id}: measured source/caption boundaries and classified diagram timing required`);
  }
  const video=createRef<Video>();
  view.add(<Video ref={video} src={'/@fs/D:/Github/Video-Editing/'+scene.actualVideo} width={1920} height={1080} play={true}/>);
  const playback=usePlayback(),start=playback.frame;
  while(playback.frame-start<scene.actualFrames)yield;
  video().pause();video().remove();
  const duration=scene.diagramFrames/playback.fps;
  yield*conceptDiagram(view,id,duration,[duration]);
});}

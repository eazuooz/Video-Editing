import {makeScene2D,Video} from '@motion-canvas/2d';
import {createRef,usePlayback} from '@motion-canvas/core';
import plan from '../production-plan.json';
export function actualScene(id:string){return makeScene2D(function*(view){
  const scene=plan.scenes.find(s=>s.id===id);
  const segments=scene?.segments;
  if(!plan.currentFinalTimingApproved||!scene?.actualMediaVerified||scene.actualAudioStreams!==0||!scene.frames||!segments?.length||segments.reduce((n,s)=>n+s.frames,0)!==scene.frames||segments.some(s=>s.role!=='actual-existing-game'||!s.video||!s.mediaVerified||s.audioStreams!==0)){
    throw Error(`Scene${id}: compiled unique official cuts and measured timing required`);
  }
  const playback=usePlayback();
  for(const segment of segments){
    view.removeChildren();const video=createRef<Video>();
    view.add(<Video ref={video} src={'/@fs/D:/Github/Video-Editing/'+segment.video} width={1920} height={1080} play={true}/>);
    const start=playback.frame;while(playback.frame-start<segment.frames)yield;
    video().pause();
  }
});}

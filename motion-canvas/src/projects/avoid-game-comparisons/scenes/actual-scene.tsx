import {makeScene2D,Video} from '@motion-canvas/2d';
import {createRef,usePlayback} from '@motion-canvas/core';
import plan from '../production-plan.json';
export function actualScene(id:string){return makeScene2D(function*(view){
  const scene=plan.scenes.find(s=>s.id===id);
  if(!plan.currentFinalTimingApproved||!scene?.actualMediaVerified||scene.actualAudioStreams!==0||!scene.actualVideo||!scene.frames){
    throw Error(`Scene${id}: compiled unique official cuts and measured timing required`);
  }
  const video=createRef<Video>();
  view.add(<Video ref={video} src={'/@fs/D:/Github/Video-Editing/'+scene.actualVideo} width={1920} height={1080} play={true}/>);
  const playback=usePlayback(),start=playback.frame;
  while(playback.frame-start<scene.frames)yield;
  video().pause();
});}

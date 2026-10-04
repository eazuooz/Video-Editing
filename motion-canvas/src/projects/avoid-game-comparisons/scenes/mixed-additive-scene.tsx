import {makeScene2D,Video,Txt} from '@motion-canvas/2d';
import {createRef,usePlayback} from '@motion-canvas/core';
import plan from '../production-plan.json';
import {conceptDiagram} from './concept-diagrams';
import {cueDiagram} from './cue-diagrams';
type Segment={role:'actual-existing-game'|'explanation';frames:number;video?:string;mediaVerified?:boolean;audioStreams?:number;diagramId?:string;diagramPixelsReviewed?:boolean;contextLabel?:string;};
type MixedScene={id:string;role:string;frames:number;segments?:Segment[];};
export function mixedAdditiveScene(id:string){return makeScene2D(function*(view){
  const scene=plan.scenes.find(s=>s.id===id) as MixedScene|undefined;
  if(!plan.currentFinalTimingApproved||scene?.role!=='mixed-actual-explanation'||!scene.segments?.length||scene.segments.reduce((n,s)=>n+s.frames,0)!==scene.frames||scene.segments.some(s=>!Number.isInteger(s.frames)||s.frames<=0|| (s.role==='actual-existing-game'?(!s.video||!s.mediaVerified||s.audioStreams!==0):(!s.diagramId||!s.diagramPixelsReviewed)))){
    throw Error(`Scene${id}: measured source/caption boundaries and classified diagram timing required`);
  }
  const playback=usePlayback();
  for(const segment of scene.segments){
    view.removeChildren();
    if(segment.role==='actual-existing-game'){
      const video=createRef<Video>();view.fill('#000000');
      view.add(<Video ref={video} src={'/@fs/D:/Github/Video-Editing/'+segment.video} width={1920} height={1080} play={true}/>);
      if(segment.contextLabel)view.add(<Txt x={-880} y={-480} offset={[-1,0]} text={segment.contextLabel} fontFamily={'Noto Sans KR'} fontSize={27} fill={'white'} stroke={'#111111'} lineWidth={4} strokeFirst/>);
      const start=playback.frame;while(playback.frame-start<segment.frames)yield;
      video().pause();
    }else{
      const duration=segment.frames/playback.fps;
      if(segment.diagramId==='13'||segment.diagramId==='14')yield*conceptDiagram(view,segment.diagramId,duration,[duration]);
      else yield*cueDiagram(view,segment.diagramId!,duration);
    }
  }
});}

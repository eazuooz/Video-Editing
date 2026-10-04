import {makeScene2D,Video} from '@motion-canvas/2d';
import {createRef,waitFor} from '@motion-canvas/core';
import plan from '../production-plan.json';
export function actualScene(id:string) {
  return makeScene2D(function*(view) {
    const scene=plan.scenes.find(s=>s.id===id);
    if(!plan.currentFinalTimingApproved||!plan.captionReviewComplete||!scene?.actualMediaVerified||scene.actualAudioStreams!==0||!scene.actualVideo||!scene.seconds)throw Error(`Scene${id}: current voice-fit cuts/captions required`);
    const video=createRef<Video>();
    view.add(<Video ref={video} src={'/@fs/D:/Github/Video-Editing/'+scene.actualVideo} width={1920} height={1080} play={true}/>);
    yield* waitFor(scene.seconds);video().pause();
  });
}

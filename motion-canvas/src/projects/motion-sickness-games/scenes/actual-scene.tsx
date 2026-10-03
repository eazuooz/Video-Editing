import {makeScene2D, Video} from '@motion-canvas/2d';
import {createRef, waitFor} from '@motion-canvas/core';
import plan from '../production-plan.json';

export function actualScene(id: string) {
  return makeScene2D(function* (view) {
    const scene = plan.scenes.find(scene => scene.id === id);
    if (!plan.currentFinalTimingApproved || !scene?.actualMediaVerified || !scene.actualVideo || !scene.seconds || scene.actualAudioStreams !== 0) {
      throw new Error(`Scene ${id}: current measured footage/caption review required before final playback`);
    }
    // Chapter cut MP4s must be encoded without source audio. The project mix
    // is the only soundtrack, including editor playback.
    const video = createRef<Video>();
    view.add(<Video ref={video} src={'/@fs/D:/Github/Video-Editing/' + scene.actualVideo} width={1920} height={1080} play={true}/>);
    yield* waitFor(scene.seconds);
    video().pause();
  });
}

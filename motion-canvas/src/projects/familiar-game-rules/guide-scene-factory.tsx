import {makeScene2D, Video} from '@motion-canvas/2d';
import {createRef, waitFor} from '@motion-canvas/core';
import plan from './guide-scene-plan.json';

/** Independent actual-game guide entries become renderable only after measured source review. */
export function observationGuideScene(id:string) {
  return makeScene2D(function* (view) {
    const guide=plan.guides.find(g=>g.id===id);
    if (!guide || !plan.finalTimingApproved || !plan.allSourceSegmentPixelsReviewed ||
        !plan.allFinalCaptionPixelsReviewed || guide.durationFrames<=0 ||
        !Number.isInteger(guide.durationFrames)) {
      throw new Error(`Guide ${id}: measured timing and every source/fixed-caption pixel remain pending.`);
    }
    const segments=guide.segments as {frames:number; mediaUrl:string; mediaPixelsReviewed:boolean; sourceAudioStreams:number}[];
    if (!segments.length || segments.reduce((n,s)=>n+s.frames,0)!==guide.durationFrames) {
      throw new Error(`Guide ${id}: continuous measured frames required.`);
    }
    for (const segment of segments) {
      if (!Number.isInteger(segment.frames) || segment.frames<=0 || !segment.mediaPixelsReviewed ||
          !segment.mediaUrl || segment.sourceAudioStreams!==0) throw new Error('Reviewed silent existing-game interval required.');
      view.removeChildren();
      const video=createRef<Video>();
      view.add(<Video ref={video} src={segment.mediaUrl} width={1920} height={1080}/>);
      video().play(); yield* waitFor(segment.frames/60); video().pause();
    }
  });
}

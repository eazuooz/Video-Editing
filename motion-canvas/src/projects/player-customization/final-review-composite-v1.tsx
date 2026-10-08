import {makeScene2D, Video} from '@motion-canvas/2d';
import {createRef} from '@motion-canvas/core';
import silentVisual from '../../../../projects/player-customization/production/final-v1/current.silent.mp4';

// Review the measured interleaved timeline with the same master mix as the MP4.
// Original editable spatial explanation scenes remain in their authoring projects.
export function finalReviewScene(startFrame: number, frames: number) {
  return makeScene2D(function* (view) {
    view.fill('#ffffff');
    const video = createRef<Video>();
    view.add(<Video ref={video} src={silentVisual} width={1920} height={1080}/>);
    video().seek(startFrame / 60);
    video().play();
    // Advance integer ticks so fractional-second accumulation cannot lose frames.
    for (let frame = 0; frame < frames; frame++) yield;
    video().pause();
  });
}

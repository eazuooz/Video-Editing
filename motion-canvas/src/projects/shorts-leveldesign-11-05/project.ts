import {makeProject} from '@motion-canvas/core';
import solutionPathOverlays from './solution-path-overlays?scene';

/** Source only. Default cannot render using invented durations or captions. */
export default makeProject({
  name: 'shorts-leveldesign-11-05-source-bound-overlays-v1',
  scenes: [solutionPathOverlays],
  variables: {
    timingMode: 'unbound-preparation',
    totalFrames: 0,
    segmentStartFrame: -1,
    fps: 60,
    narrationSHA256: '8a35438d9b12131a60a1ec817aaa11d2f4df21b59c2f645dfd69143a71d92a53',
    voiceEvidenceSHA256: '',
    rawAsrReviewSHA256: '',
    timelineSHA256: '',
    frameCues: [],
  },
});

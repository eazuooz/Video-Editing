import {makeProject} from '@motion-canvas/core';
import rewardDiagrams from './reward-diagrams?scene';

/** Preparation only: these logical durations must be replaced by actual ASR cues. */
export default makeProject({
  name: 'shorts-leveldesign-07-04-reward-diagrams-draft',
  scenes: [rewardDiagrams],
  variables: {
    segment: 'all', // 'p2' | 'p6' | 'p7' for separately aligned content clips.
    p2Seconds: 20,
    p6Seconds: 24,
    p7Seconds: 24,
    timingStatus: 'draft-logical-duration; not speech-aligned',
    contentWidth: 1080,
    contentHeight: 900,
  },
});

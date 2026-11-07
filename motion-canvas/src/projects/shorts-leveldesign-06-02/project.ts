import {makeProject} from '@motion-canvas/core';
import refugeRelationships from './refuge-relationships?scene';

/** Source preparation only. Future exact ASR-bound frame cues enable rendering. */
export default makeProject({
  name: 'shorts-leveldesign-06-02-relationship-source',
  scenes: [refugeRelationships],
  variables: {
    segment: 'p04', // 'p04' | 'p25'; never run both with a fabricated shared clock.
    timingMode: 'unbound-source-preparation',
    segmentFrames: 0,
    phaseFrameMap: [],
    contentWidth: 1080,
    contentHeight: 900,
  },
});

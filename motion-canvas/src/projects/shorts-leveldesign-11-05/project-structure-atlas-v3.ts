import {makeProject} from '@motion-canvas/core';
import structureAtlas from './solution-path-structure-atlas-v3?scene';

export default makeProject({
  scenes: [structureAtlas],
  variables: {renderMode: 'unbound-preparation', jobFingerprint: '', sourcePackets: []},
});

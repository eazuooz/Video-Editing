// CPU-only in-memory tests. No production timing, media, server or GPU is created.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const Module = require('node:module');
const ts = require('../../../node_modules/typescript');
const file = path.join(__dirname, 'model.ts');
const compiled = new Module(file, module);
compiled.filename = file;
compiled._compile(ts.transpileModule(fs.readFileSync(file, 'utf8'), {
  compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020},
}).outputText, file);
const {validateProductionInput: validate, visualAt, sectionAt, focusAt, SECTIONS} = compiled.exports;
const timing = {revision: 'surface-ink-v1', fps: 60, frames: 420, previewOnly: false,
  voiceDurationSeconds: 6, timingInputs: {voiceSha256: 'a'.repeat(64)}, sections: [], events: {},
  gameplayWindows: [{cut: 'floor', startFrame: 0, endFrame: 12}, {cut: 'wall', startFrame: 12, endFrame: 24}]};
const counts = [2, 3, 3, 4, 4, 2, 3];
for (let paragraph = 0; paragraph < 7; paragraph++) {
  timing.sections.push({id: SECTIONS[paragraph], startFrame: paragraph * 60, endFrame: (paragraph + 1) * 60});
  for (let cue = 0; cue < counts[paragraph]; cue++) timing.events[`p${paragraph + 1}-${cue + 1}`] = {
    startFrame: paragraph * 60 + cue * 6, endFrame: paragraph * 60 + (cue + 1) * 6};
}
const root = '/@fs/D:/Github/VideoEditing/projects/shorts-splatoon-surface-ink/production/local/test-only/';
const config = {revision: 'surface-ink-v1', framesPrepared: true, frameRoot: root,
  unityImagePlacement: {size: [648, 1152], center: [540, 860], preserveAspect: true},
  gameplayCuts: {
    floor: {directory: 'floor', frameCount: 234, sourceStartSeconds: 62.4, sourceEndSeconds: 66.3,
      sourceSha256: '0c9bcb99f0344e7023d82446fe82012239a97b1aa40a03348781a096c7b57ccd',
      nativeDimensions: [1920, 1080], fps: 60, inspected: true},
    wall: {directory: 'wall', frameCount: 180, sourceStartSeconds: 68.5, sourceEndSeconds: 71.5,
      sourceSha256: '164a876b17ae78c4fbcbe0c3321d7ff7ae752fa806c68b62c22f9350288baa75',
      nativeDimensions: [1920, 1080], fps: 60, inspected: true},
  },
  unityFrames: {root, width: 1080, height: 1920, fps: 60, captured: true, voiceSha256: 'a'.repeat(64),
    sequences: [{directory: 'sheet', startFrame: 24, endFrame: 420, firstFrame: 100, indexBasis: 'sequence-relative'}]},
  compositing: {anchorsReviewed: true, anchors: {sheet: [540, 610], wall: [566, 900], floor: [418, 1147], impact: [566, 900], seam: [540, 610]},
    uvReadout: {u: .5, v: .5, runtimeVerified: true, evidencePath: 'in-memory-test-only-not-media'}}};
assert.equal(validate(timing, config).timing.frames, 420);
assert.equal(Object.keys(timing.events).length, 21);
assert.equal(visualAt(timing, config, 11).index, 11);
assert.equal(visualAt(timing, config, 12).cut, 'wall');
assert.equal(visualAt(timing, config, 12).index, 0);
assert.equal(visualAt(timing, config, 24).kind, 'unity');
assert.equal(visualAt(timing, config, 24).index, 100);
assert.equal(visualAt(timing, config, 60).index, 136);
const absolute = structuredClone(config);
absolute.unityFrames.sequences[0].indexBasis = 'absolute-final-frame';
assert.equal(visualAt(timing, absolute, 60).index, 60);
assert.equal(sectionAt(timing, 60).id, 'sheet');
assert.throws(() => sectionAt(timing, 420));
assert.equal(focusAt([{time: 0, x: 100, y: 200, radiusX: 20, radiusY: 30},
  {time: 1, x: 200, y: 400, radiusX: 40, radiusY: 50}], .5).x, 150);
assert.equal(focusAt([{time: 1, x: 100, y: 200, radiusX: 20, radiusY: 30}], 0), undefined);
assert.throws(() => validate(undefined, config));
assert.throws(() => validate({...timing, previewOnly: true}, config));
assert.throws(() => validate({...timing, timingInputs: {voiceSha256: ''}}, config));
assert.throws(() => validate(timing, {...config, framesPrepared: false}));
for (const mutate of [
  (t, c) => {delete t.events['p7-3'];},
  (t, c) => {t.sections[2].startFrame++;},
  (t, c) => {c.unityFrames.sequences[0].startFrame++;},
  (t, c) => {c.unityFrames.voiceSha256 = 'b'.repeat(64);},
  (t, c) => {c.gameplayCuts.floor.nativeDimensions = [1280, 720];},
  (t, c) => {c.gameplayCuts.wall.sourceSha256 = 'b'.repeat(64);},
  (t, c) => {c.compositing.uvReadout.runtimeVerified = false;},
  (t, c) => {c.compositing.uvReadout.u = .48;},
  (t, c) => {c.compositing.anchorsReviewed = false;},
  (t, c) => {t.gameplayWindows[1].sourceFrameOffset = 179;},
]) {
  const t = structuredClone(timing), c = structuredClone(config);
  mutate(t, c); assert.throws(() => validate(t, c));
}
console.log(JSON.stringify({status: 'passed', events: 21, sections: 7,
  absoluteAndPerClipIndexMapping: true, inputGuard: 'passed-in-memory-only',
  sourceLoopOrHold: false, syntheticProductionFilesWritten: false, mediaJobsStarted: 0}));

// CPU-only invariants; no browser, dev server, GPU, TTS or media output.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const Module = require('node:module');
const ts = require('../../../node_modules/typescript');
const filename = path.join(__dirname, 'model.ts');
const javascript = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
  compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020},
}).outputText;
const compiled = new Module(filename, module);
compiled.filename = filename;
compiled.paths = module.paths;
compiled._compile(javascript, filename);
const {sampleAt, poseHoldLengths, recentThreeFrames} = compiled.exports;

// One-second60Hz presentation of24Hz samples holds for2or3frames, never2.5.
const holds = poseHoldLengths(24);
assert.equal(holds.length, 24);
assert.equal(holds.reduce((a, b) => a + b, 0), 60);
assert(holds.every(n => n === 2 || n === 3));
assert.equal(holds.filter(n => n === 2).length, 12);
assert.equal(holds.filter(n => n === 3).length, 12);
assert.deepEqual(Array.from({length: 6}, (_, n) => sampleAt(n).position), [0, 4, 8, 12, 16, 20]);
assert.deepEqual(Array.from({length: 6}, (_, n) => sampleAt(n).poseKey), ['A', 'A', 'A', 'B', 'B', 'C']);
assert.deepEqual(Array.from({length: 6}, (_, n) => sampleAt(n, 24, 24).position), [0, 0, 0, 10, 10, 20]);

// One-variable comparisons: changing artwork sampling cannot move the marker;
// changing position sampling cannot change the pose index at the same time.
for (let n = 0; n <= 60; n++) {
  assert.equal(sampleAt(n, 60, 60).position, sampleAt(n, 24, 60).position);
  assert.equal(sampleAt(n, 24, 60).poseSample, sampleAt(n, 24, 24).poseSample);
}
assert.equal(sampleAt(0, 24, 24).position, 0);
assert.equal(sampleAt(60, 24, 24).position, 240);
assert.equal(sampleAt(60, 24, 60).position, 240);
assert.deepEqual(recentThreeFrames(0), [0, 1, 2]);
assert.deepEqual(recentThreeFrames(5), [3, 4, 5]);
assert.throws(() => sampleAt(-1));
assert.throws(() => sampleAt(0.5));

// Extract the pure input validator through the TS AST. Vite glob calls and
// media modules are never evaluated, and no fake timing file is written.
const inputFile = path.join(__dirname, 'production-input.ts');
const inputAst = ts.createSourceFile(inputFile, fs.readFileSync(inputFile, 'utf8'), ts.ScriptTarget.ES2020, true);
const printer = ts.createPrinter();
const selectedStatements = inputAst.statements.filter(s =>
  ts.isFunctionDeclaration(s) && s.name?.text === 'validateProductionInput' ||
  ts.isVariableStatement(s) && s.declarationList.declarations.some(d =>
    ts.isIdentifier(d.name) && ['SECTION_IDS', 'CUE_IDS'].includes(d.name.text)));
const pureValidatorText = selectedStatements.map(s => printer.printNode(ts.EmitHint.Unspecified, s, inputAst)).join('\n');
const validatedModule = new Module(inputFile, module);
validatedModule.filename = inputFile;
validatedModule._compile(ts.transpileModule(pureValidatorText, {
  compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020},
}).outputText, inputFile);
const validate = validatedModule.exports.validateProductionInput;
const sectionIds = ['game', 'frames', 'source-rates', 'pose24', 'position24', 'close'];
const cueCounts = [2, 4, 2, 4, 4, 3];
const t = {revision: 'animation-tick-v1', fps: 60, frames: 360, previewOnly: false,
  timingInputs: {voiceSha256: 'a'.repeat(64)}, sections: [], events: {}};
for (let i = 0; i < sectionIds.length; i++) {
  t.sections.push({id: sectionIds[i], startFrame: i * 60, endFrame: (i + 1) * 60});
  for (let j = 0; j < cueCounts[i]; j++)
    t.events[`p${i + 1}-${j + 1}`] = {startFrame: i * 60 + j * 10, endFrame: i * 60 + (j + 1) * 10};
}
const c = {game: 'Cuphead', framesPrepared: true, frameRoot: '/test-only-never-loaded/',
  poseImages: {A: 'A', B: 'B', C: 'C'}, cuts: {game: {frameDirectory: 'game', maxDuration: 1}}};
assert.throws(() => validate(undefined, undefined));
assert.throws(() => validate({...t, previewOnly: true}, c));
assert.throws(() => validate({...t, timingInputs: {voiceSha256: ''}}, c));
assert.throws(() => validate({...t, sections: t.sections.slice(1)}, c));
assert.throws(() => validate(t, {...c, cuts: {}}));
assert.throws(() => validate(t, {...c, framesPrepared: false}));
assert.equal(validate(t, c).timing.frames, 360);
const badCue = structuredClone(t);
badCue.events['p2-1'].startFrame = 10;
assert.throws(() => validate(badCue, c));
console.log(JSON.stringify({status: 'passed', samples: 61, twoFrameHolds: 12, threeFrameHolds: 12,
  actualInputGuard: 'passed-in-memory-only', sourceMeasurement: false, syntheticProductionFilesWritten: false}));

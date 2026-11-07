/* Pure Node contract tests. Never invokes main, Vite, browser or FFmpeg. */
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const crypto = require('node:crypto');
const w = require('./render-prospect-refuge-diagrams.cjs');
const root = path.resolve(__dirname, '../../..');
const source = path.join(root, 'motion-canvas/src/projects/shorts-leveldesign-06-02');
const attempt = 'C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-06-02/mc-render-attempts/synthetic-cpu-fixture-not-created';
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const font = 'C:/Windows/Fonts/NotoSansKR-VF.ttf';
const stagedSources = ['project.ts', 'refuge-relationships.tsx'].map(name => ({name,path:path.join(source,name)}));
const inputPins = [...stagedSources.map(s => s.path),font].map(p => ({path:p,sha256:sha(p)}));
const base = {schemaVersion:'06-02-mc-render-job-v1',topicId:'06.02',segment:'p04',attempt,
 contract:{width:1080,height:900,fps:60,frames:100,audio:false,alpha:false},
 output:path.join(attempt,'p04.silent.mp4'),fingerprint:'a'.repeat(64),stagedSources,inputPins,font:{path:font},versions:{core:'3.17.2',two:'3.17.2'},
 variables:{segment:'p04',timingMode:'authored-cue-frames',segmentFrames:100,phaseFrameMap:[{frame:0,phase:0},{frame:10,phase:.06},{frame:25,phase:.25},{frame:60,phase:.65},{frame:80,phase:.82},{frame:99,phase:1}]},
 lifecycle:{protocol:'architectural111-06-02-mc-crop-v1',owner:'architectural-111-06-02-mc-crop',token:'synthetic',parent:{pid:10,createTime:100}},cueFrames:[]};
const clone = () => structuredClone(base), jobPath=path.join(attempt,'job.json');
assert.equal(w.validateJob(base,jobPath),base);
let bad=clone();bad.contract.fps=30;assert.throws(()=>w.validateJob(bad,jobPath));
bad=clone();bad.segment='p2';assert.throws(()=>w.validateJob(bad,jobPath));
bad=clone();bad.inputPins[0].sha256='0'.repeat(64);assert.throws(()=>w.validateJob(bad,jobPath));
bad=clone();bad.stagedSources[1].path=path.join(root,'motion-canvas/src/projects/shorts-leveldesign-07-04/reward-diagrams.tsx');assert.throws(()=>w.validateJob(bad,jobPath));
bad=clone();bad.variables.phaseFrameMap[0].phase=.01;assert.throws(()=>w.validateJob(bad,jobPath));
const page=w.workerPage(base);assert.match(page,/new Renderer\(project\)/);assert.match(page,/audio:undefined/);assert.match(page,/new Vector2\(1080,900\)/);assert.ok(!page.includes('@motion-canvas/ui'));
const lease={protocol:base.lifecycle.protocol,owner:base.lifecycle.owner,token:'synthetic',pid:10,createTime:100,fingerprint:base.fingerprint,output:attempt};assert.equal(w.leaseMatches(base,lease),true);assert.equal(w.leaseMatches(base,{...lease,owner:'foreign'}),false);
assert.equal(w.leaseMatches(base,{...lease,createTime:101}),false);assert.equal(w.leaseMatches(base,{...lease,output:root}),false);
const png=Buffer.alloc(24);Buffer.from('89504e470d0a1a0a','hex').copy(png);png.write('IHDR',12);png.writeUInt32BE(1080,16);png.writeUInt32BE(900,20);assert.equal(w.pngDimensions(png).width,1080);assert.throws(()=>w.pngDimensions(Buffer.alloc(24)));
console.log('10 pure Node checks PASS; no browser/server/model/media process');

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {spawnSync}=require('node:child_process');
const {isMedia,root}=require('./media-policy.cjs');
const blocked=['clip.mp4','clip.Mp4','music.MP3','voice.wav','voice.m4a','capture.webm','video.mp4.part','video.mp4.zip','shared/media-archives/p/part-001.gz','shared/media-archives/p/file.gz.001','archive.7z','voice.flac','sound.ogg'];
const allowed=['scene.ts','scene.tsx','clip.mp4.render.json','voice.wav.json','captions.ko.srt','captions.en.srt','captions.ass','manifest.json','license.txt','project.json','engine.uasset'];
const raster=['image.png','image.JPG','image.JpEg','image.webp','image.gif','image.bmp','image.TIFF'];
for(const f of blocked)assert.equal(isMedia(f),true,f);
for(const f of allowed)assert.equal(isMedia(f),false,f);
for(const f of raster)assert.equal(isMedia(f),false,'raster is reviewed separately: '+f);
for(const f of blocked){const r=spawnSync('git',['check-ignore','--no-index','--stdin'],{cwd:root,input:f+'\n',encoding:'utf8',windowsHide:true});assert.equal(r.status,0,'not ignored: '+f);}
for(const f of allowed){const r=spawnSync('git',['check-ignore','--no-index','--stdin'],{cwd:root,input:'projects/p/'+f+'\n',encoding:'utf8',windowsHide:true});assert.equal(r.status,1,'metadata ignored: '+f);}
for(const f of raster){const r=spawnSync('git',['check-ignore','--no-index','--stdin'],{cwd:root,input:'projects/p/'+f+'\n',encoding:'utf8',windowsHide:true});assert.equal(r.status,0,'new raster must default to local: '+f);}
if(process.argv.includes('--rules-only')) {console.log('OK: media/ignore rules, metadata preservation and new raster defaults.');process.exit(0);}
const index=JSON.parse(fs.readFileSync(path.join(root,'projects/rebuild-index.json'),'utf8'));
for(const p of index.projects){
  const m=JSON.parse(fs.readFileSync(path.join(root,p.manifest),'utf8'));
  assert.equal(m.slug,p.slug);assert.equal(m.schemaVersion,1);
  assert.equal(m.counts.referencedMediaFiles,m.mediaAssets.length);
  assert.equal(m.counts.clipRecords,m.clipRecords.length);
  assert.equal(m.rebuild.automatic,false);
  assert.ok(m.rebuild.gaps.length);
  for(const key of ['video','editing','audio','approvals','membershipOutro','publishReady'])assert.deepEqual(m.projectSettings[key],JSON.parse(fs.readFileSync(path.join(root,`projects/${p.slug}/project.json`),'utf8').replace(/^\uFEFF/,''))[key]);
}
const load=s=>JSON.parse(fs.readFileSync(path.join(root,`projects/${s}/rebuild.json`),'utf8'));
assert.equal(load('small-window-game-design').sceneLayout.length,7);
assert.equal(load('small-window-game-design').sceneLayout[0].id,'intro-cats-v2');
assert.equal(load('frame-rate-modern-rendering').clipRecords.length,20);
assert.equal(load('choice-driven-classics').sceneLayout.length,6);
assert.equal(load('visible-rewards').counts.clipRecords,14);
console.log(`OK: media/ignore rules, metadata preservation, all ${index.projects.length} manifests and canonical timeline counts.`);

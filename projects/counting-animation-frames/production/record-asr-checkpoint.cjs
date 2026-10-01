// Record only reviewed current hashes; preserve later render/upload checkpoints.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),read=f=>JSON.parse(fs.readFileSync(f,'utf8')),file=path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
const m=read(path.join(path.dirname(__dirname),'project.json')),report=read(path.join(root,m.tts.outputDir,m.tts.filenameStem+'.asr-review.json')),review=read(path.join(__dirname,'narration-scene-review.json'));
for(const scene of review.scenes){const actual=report.scenes.find(s=>s.scene===scene.scene);if(!actual||actual.audio_sha256!==scene.audioSha256)throw Error('Reviewed chunk superseded or missing: '+scene.scene);}
const q=read(file),item=q.items.find(i=>i.slug==='counting-animation-frames');
item.localProgress.narrationScenesAsrReviewed=review.scenes.filter(s=>s.result==='passed-content-and-ending').map(s=>s.scene);
item.localProgress.narrationReview='projects/counting-animation-frames/production/narration-scene-review.json';
if(!item.checkpoints.render){const all=item.localProgress.narrationScenesAsrReviewed.length===read(path.join(root,m.paths.script)).scenes.length;item.localProgress.narrationSceneFindings=all?'All current scene hashes inspected; no missing/repeated phrase. Exact repaired02 numerical exception is documented. Full assembled ASR and final QA still required. Human listening pending.':'Partial current-hash review only; continue recorded live jobs and inspect remaining scenes.';item.localProgress.narration=item.localProgress.narrationSceneFindings;}
item.updatedAt=new Date().toISOString();q.updatedAt=item.updatedAt;fs.writeFileSync(file,JSON.stringify(q,null,2)+'\n');
console.log('Recorded actual current-hash scene review without resetting later completion.');

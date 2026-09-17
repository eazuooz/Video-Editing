// Cross-machine, read-only verification. Requires Node; no TTS models or raw footage.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),manifest=require('../projects/visible-rewards/project.json'),delivery=require('../projects/visible-rewards/publishing/delivery-v3.json');
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,file))).digest('hex');
for(const f of delivery.files){assert.equal(fs.statSync(path.join(root,f.file)).size,f.bytes,f.file);assert.equal(sha(f.file),f.sha256,f.file);}
for(const [file,hash] of Object.entries(delivery.protectedInputs))assert.equal(sha(file),hash,file);
const ms=s=>{const [h,m,secs,frac]=s.split(/[:,]/).map(Number);return ((h*60+m)*60+secs)*1000+frac;};
function srt(file){
 const blocks=fs.readFileSync(path.join(root,file),'utf8').trim().split(/\r?\n\s*\r?\n/);
 let previous=0;
 return blocks.map((block,i)=>{
  const lines=block.split(/\r?\n/);assert.equal(Number(lines[0]),i+1);
  const match=lines[1].match(/^(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})$/);assert.ok(match);
  const start=ms(match[1]),end=ms(match[2]);assert.ok(start>=previous&&end>start&&end<=delivery.seconds*1000);assert.ok(lines.slice(2).join('').trim());previous=end;return [start,end];
 });
}
const ko=srt(manifest.paths.deliveryCaptionsKo),en=srt(manifest.paths.deliveryCaptionsEn);
assert.equal(ko.length,94);assert.deepEqual(en,ko);assert.equal(sha(manifest.paths.captionsKo),sha(manifest.paths.deliveryCaptionsKo));assert.equal(sha(manifest.paths.captionsEn),sha(manifest.paths.deliveryCaptionsEn));
assert.equal(manifest.revision.version,3);assert.equal(manifest.editing.exampleFullFrame,true);assert.equal(manifest.editing.explanatoryFooters,false);
assert.equal(manifest.paths.videoClean,delivery.files[0].file);
for(let i=1;i<=8;i++)assert.ok(fs.existsSync(path.join(root,`motion-canvas/src/projects/visible-rewards/assets/gameplay-v3/scene${String(i).padStart(2,'0')}.mp4`)));
assert.ok(fs.existsSync(path.join(root,manifest.paths.editorAudioMix)));
console.log(JSON.stringify({passed:true,frames:delivery.frames,seconds:delivery.seconds,koCues:ko.length,enCues:en.length,lastCaptionMs:ko.at(-1)[1],fileHashes:'matched',protectedInputs:'unchanged',gameplayClips:8}));

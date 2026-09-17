import fs from 'node:fs';
import assert from 'node:assert/strict';
const root=new URL('../',import.meta.url);
const read=p=>fs.readFileSync(new URL(p,root),'utf8').replace(/^\uFEFF/,'');
const load=p=>JSON.parse(read('projects/let-them-play/'+p));
const m=load('project.json'),p=load('planning/scenes.json'),n=load('script/narration.ko.json');
const review=read('projects/let-them-play/script/review.ko.md');
const order=['gameplay','design','application'];
const measured=JSON.parse(read('motion-canvas/src/projects/let-them-play/timeline.generated.json'));
if(measured.voiceAligned){
 assert.equal(measured.scenes.length,8);assert.equal(measured.creditsFrames,0);
 let cursor=0;const totals={gameplay:0,design:0,application:0};
 measured.scenes.forEach((s,i)=>{
  assert.equal(s.id,n.scenes[i].id);assert.equal(s.startFrame,cursor);
  assert.equal(s.frames,s.segmentFrames*3);assert.equal(s.segmentFrames,Math.round(s.segmentFrames));
  cursor+=s.frames;order.forEach(k=>totals[k]+=s.segmentFrames/measured.fps);
 });
 assert.equal(cursor,measured.totalFrames);assert.equal(cursor,measured.contentFrames);
 assert.equal(totals.gameplay,totals.design);assert.equal(totals.design,totals.application);
 const timing=JSON.parse(read(m.tts.outputDir+'/'+m.tts.filenameStem+'.timing.json'));
 assert.equal(timing.entries.length,n.scenes.reduce((a,s)=>a+s.lines.length,0));
 assert.equal(timing.narration_placement,'continuous-across-all-three-segments');
 assert.ok(Math.abs(timing.duration_seconds-cursor/measured.fps)<.001);
 console.log(JSON.stringify({status:'PASS',scenes:8,segments:24,seconds:cursor/measured.fps,frames:cursor,totals,voiceAligned:true,paragraphTransitionOffsets:measured.scenes.map(s=>s.paragraphTransitionOffsetsSeconds),publishReady:m.publishReady},null,2));
 process.exit(0);
}
assert.deepEqual(m.editing.segmentOrder,order);
assert.deepEqual(m.editing.ratio,{gameplay:1,design:1,application:1});
assert.equal(p.scenes.length,8);assert.equal(n.scenes.length,8);
let totals={gameplay:0,design:0,application:0};
p.scenes.forEach((s,i)=>{
 assert.equal(s.id,n.scenes[i].id);assert.equal(s.title,n.scenes[i].title);
 assert.equal(s.seconds,m.editing.exampleSeconds*3);
 assert.deepEqual(s.segments.map(x=>x.kind),order);
 assert.deepEqual(n.scenes[i].segments.map(x=>x.kind),order);
 let line=0;
 s.segments.forEach((seg,k)=>{
  assert.equal(seg.seconds,m.editing.exampleSeconds);
  assert.equal(seg.offsetSeconds,k*m.editing.exampleSeconds);
  assert.equal(seg.seconds*m.video.fps,Math.round(seg.seconds*m.video.fps));
  totals[seg.kind]+=seg.seconds;
  const speech=n.scenes[i].segments[k];assert.equal(speech.lineStart,line);assert.ok(speech.lineCount>0);line+=speech.lineCount;
 });
 assert.equal(line,n.scenes[i].lines.length);
 n.scenes[i].lines.forEach(text=>assert.ok(review.includes(text)));
 assert.ok(fs.existsSync(new URL('motion-canvas/src/projects/let-them-play/scenes/scene'+s.id+'.tsx',root)));
 assert.ok(s.application.kind);
});
const total=Object.values(totals).reduce((a,b)=>a+b,0);
assert.equal(totals.gameplay,totals.design);assert.equal(totals.design,totals.application);
assert.equal(total,p.estimatedSeconds);assert.equal(total,m.video.estimatedDurationSeconds);
assert.equal(m.publishReady,false);
const cues=read('projects/let-them-play/planning/edit-cues.csv').trim().split(/\r?\n/).slice(1);
assert.equal(cues.length,24);let end=0;
cues.forEach(row=>{const c=row.split(',');assert.equal(Number(c[1]),end);assert.equal(Number(c[2])-end,m.editing.exampleSeconds);end=Number(c[2]);});
assert.equal(end,total);
console.log(JSON.stringify({status:'PASS',scenes:8,segments:24,seconds:total,frames:total*m.video.fps,totals,voiceAligned:false,publishReady:false},null,2));

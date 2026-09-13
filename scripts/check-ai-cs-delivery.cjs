// Read-only consistency checks for the v6+ continuous-narration deliverables.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),project='projects/ai-era-cs-fundamentals';
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const json=p=>JSON.parse(read(p)),m=json(`${project}/project.json`);
const t=json(`${m.tts.outputDir}/${m.tts.filenameStem}.timing.json`);
const compact=s=>s.replace(/\s+/g,'');
const seconds=s=>{const [h,min,sec,ms]=s.split(/[:,]/).map(Number);return 3600*h+60*min+sec+ms/1000;};
const parse=p=>read(p).trim().split(/\r?\n\s*\r?\n/).map((block,i)=>{
 const [n,time,...lines]=block.split(/\r?\n/),times=time.split(' --> ').map(seconds);
 assert.equal(+n,i+1);assert.ok(lines.length>0&&lines.length<=2);
 assert.ok(times[1]>times[0]&&times[0]>=0&&times[1]<=m.video.durationSeconds);
 return {number:+n,time,start:times[0],end:times[1],text:lines.join(' ')};
});
const ko=parse(m.paths.captionsKo),en=parse(m.paths.captionsEn);
assert.deepEqual(ko.map(c=>c.time),en.map(c=>c.time),'KO/EN cue times differ');
for(const [lang,cues]of [['ko',ko],['en',en]]){
 const script=json(`${project}/script/narration.${lang}.json`);
 assert.equal(compact(cues.map(c=>c.text).join(' ')),compact(script.scenes.flatMap(s=>s.lines).join(' ')),`${lang} script text missing or changed`);
 cues.forEach((c,i)=>assert.ok(!i||c.start>=cues[i-1].end,`${lang} overlap ${c.number}`));
 const maxCps=Math.max(...cues.map(c=>c.text.length/(c.end-c.start)));
 console.log(`${lang}: ${cues.length} matching cues, complete approved text, <=2 lines, max ${maxCps.toFixed(1)} characters/second`);
}
assert.equal(t.narration_placement,m.editing.narrationPlacement);
assert.equal(t.example_seconds,m.editing.exampleSeconds);
assert.equal(t.entries.length,86);assert.equal(new Set(t.entries.map(e=>e.scene_id)).size,12);
const report=json(m.paths.audioMixReport);
assert.ok(Math.abs(report.duration-m.video.durationSeconds)<.002);
assert.equal(report.editorMix,m.paths.editorAudioMix);assert.equal(report.mix,m.paths.audioMix);
assert.equal(report.scenes.length,12);
assert.ok(report.scenes.every(s=>Number.isFinite(s.exampleVoiceLufs)&&Number.isFinite(s.sourceLufs)&&Number.isFinite(s.exampleBgmLufs)&&Number.isFinite(s.explanationBgmLufs)));
assert.ok(+report.measurement.input_tp<=m.audio.truePeakDbtp+.1);
if(m.audio.backgroundMusic.previewUseOnly){assert.equal(report.musicRightsVerified,false);assert.equal(report.publishReady,false);}
console.log(`PASS: ${report.duration.toFixed(3)}s, 12 chapter voice/source/music checks, true peak ${report.measurement.input_tp} dBTP; listening approval remains separate`);

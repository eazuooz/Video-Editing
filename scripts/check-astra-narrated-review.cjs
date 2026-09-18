// Technical verification only. Does not grant publication or human listening approval.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),slug='gpt-astra-showcase',base=path.join(root,'projects',slug);
const m=JSON.parse(fs.readFileSync(path.join(base,'project.json'),'utf8'));
const plan=JSON.parse(fs.readFileSync(path.join(root,m.editing.plan),'utf8'));
const out=path.join(root,m.tts.outputDir),stem=m.tts.filenameStem;
function assert(ok,msg){if(!ok)throw Error(msg);}
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:8e6});assert(r.status===0,r.stderr||String(r.error));return r.stdout.trim();}
function packetHash(file,stream){return run('ffmpeg',['-v','error','-i',path.join(root,file),'-map',stream,'-c','copy','-f','hash','-hash','sha256','-']);}
const time=s=>{const [h,min,sec,ms]=s.split(/[:,]/).map(Number);return h*3600+min*60+sec+ms/1000;};
function captions(file){let last=0;return fs.readFileSync(path.join(root,file),'utf8').trim().split(/\r?\n\r?\n/).map((s,i)=>{const lines=s.split(/\r?\n/),[a,b]=lines[1].split(' --> ').map(time);assert(+lines[0]===i+1&&a>=last-.001&&b>a&&b<=plan.durationSeconds+.01,'Bad caption '+file+' '+(i+1));assert(lines.length<=4,'Caption exceeds two lines');last=b;return {index:i+1,start:a,end:b,text:lines.slice(2).join(' ')};});}
const ko=captions(m.paths.captionsKo),en=captions(m.paths.captionsEn);
assert(ko.length===en.length,'Caption language count mismatch');
assert(ko.every((c,i)=>c.start===en[i].start&&c.end===en[i].end),'Caption languages have different timing');
const timing=JSON.parse(fs.readFileSync(path.join(out,stem+'.timing.json'),'utf8'));
const script=JSON.parse(fs.readFileSync(path.join(root,m.paths.script),'utf8'));
assert(timing.entries.length===script.scenes.reduce((n,s)=>n+s.lines.length,0),'Paragraph count mismatch');
assert(timing.duration_seconds===plan.durationSeconds,'Narration timing duration mismatch');
const voiceHash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
assert(voiceHash(path.join(out,'chunks/03-scene.wav'))===voiceHash(path.join(root,m.paths.voiceSample)),'Approved train take changed');
const asr=JSON.parse(fs.readFileSync(path.join(out,stem+'.asr-review.json'),'utf8'));
assert(asr.complete&&asr.sceneCount===plan.scenes.length,'Incomplete ASR');
const alignment=JSON.parse(fs.readFileSync(path.join(out,stem+'.alignment-review.json'),'utf8'));
for(const s of alignment)assert(s.matchingCharacterCoverage>=.93,'Low ASR alignment coverage: '+s.scene);
const pictureHash=packetHash(m.paths.pictureReview,'0:v:0'),videoHash=packetHash(m.paths.videoClean,'0:v:0');
assert(pictureHash===videoHash,'Final picture stream differs from reviewed picture');
const aacHash=packetHash(m.paths.audioMix,'0:a:0'),videoAudioHash=packetHash(m.paths.videoClean,'0:a:0');
assert(aacHash===videoAudioHash,'Editor AAC and MP4 audio packets differ');
const mix=JSON.parse(fs.readFileSync(path.join(base,`review/audio-v${plan.version}/mix-report.json`),'utf8'));
assert(+mix.finalLevels.input_tp<=m.audio.truePeakDbtp,'True peak ceiling exceeded');
assert(mix.levels.length===20&&mix.continuousBgm,'Incomplete scene layer QA');
assert(m.publishReady===false,'Unverified source rights must not be marked publish-ready');
const editor=JSON.parse(fs.readFileSync(path.join(base,`review/qa-v${plan.version}-narrated/report.json`),'utf8'));
assert(editor.errors.length===0&&editor.audio.src.includes(path.basename(m.paths.editorAudioMix))&&!editor.audio.muted&&editor.audio.volume>0,'Editor audio QA failed');
let frame=0,maxBoundaryError=0;
for(const [i,s] of plan.scenes.entries()){
 const real=editor.timing.scenes[i];maxBoundaryError=Math.max(maxBoundaryError,Math.abs(real.start-frame),Math.abs(real.end-(frame+s.duration*plan.fps)));frame+=s.duration*plan.fps;
}
assert(maxBoundaryError<=1,'Editor scene differs from fixed edit by more than a frame');
const report={status:'technical-checks-passed-human-review-and-source-permission-pending',duration:plan.durationSeconds,captionCount:ko.length,lastCaptionEnd:ko.at(-1).end,approvedSamplePreserved:true,asrScenes:asr.sceneCount,minAsrCharacterCoverage:Math.min(...alignment.map(s=>s.matchingCharacterCoverage)),pictureHash,aacHash,maxEditorBoundaryErrorFrames:maxBoundaryError,finalLufs:+mix.finalLevels.input_i,truePeakDbtp:+mix.finalLevels.input_tp,music:mix.music,continuousBgm:true,musicFallbackScenes:mix.musicFallbackScenes,publishReady:false};
if(m.editing.middleSummarySlides===false){
 assert(plan.scenes.filter(s=>s.cuts.length).every(s=>Math.abs(s.duration-s.cuts.reduce((n,c)=>n+c.out-c.in,0))<1e-6),'Middle summary time remains');
 const previous=JSON.parse(fs.readFileSync(path.join(base,'revisions/v2/project.json'),'utf8'));
 for(const s of plan.scenes)assert(voiceHash(path.join(out,`chunks/${s.id}-scene.wav`))===voiceHash(path.join(root,previous.tts.outputDir,`chunks/${s.id}-scene.wav`)),'An approved voice take changed: '+s.id);
 report.allTenVoiceTakesPreserved=true;report.removedMiddleSummarySeconds=24;
}
fs.writeFileSync(path.join(base,`review/technical-check-v${plan.version}.json`),JSON.stringify(report,null,2)+'\n');
const csv=v=>'"'+String(v).replaceAll('"','""')+'"';
const clock=s=>`${String(Math.floor(s/60)).padStart(2,'0')}:${(s%60).toFixed(3).padStart(6,'0')}`;
const rows=[['scene','start','end','segment_type','visual','source','source_audio','bgm','narration','status']];
let start=0;
for(const s of plan.scenes){
 const ex=s.cuts.reduce((n,c)=>n+c.out-c.in,0),voiceEnd=Math.max(...timing.entries.filter(e=>e.scene_id===s.id).map(e=>e.end));
 if(ex)rows.push([s.id,clock(start),clock(start+ex),'real-example',s.title,s.post,mix.musicFallbackScenes.includes(s.id)?'silent-source-bgm-fallback':'normalized--31-LUFS-plus-ducking','Discovery-continuous',`from ${clock(start)} to ${clock(voiceEnd)}`,'local-narrated-review-rights-pending']);
 if(s.duration>ex)rows.push([s.id,clock(start+ex),clock(start+s.duration),'channel-summary',s.takeaway,'original','none','Discovery-continuous',ex?'speech-finished-viewing-pause':`to ${clock(voiceEnd)}`,'human-full-review-pending']);start+=s.duration;
}
fs.writeFileSync(path.join(base,'planning/edit-cues.csv'),rows.map(r=>r.map(csv).join(',')).join('\n')+'\n');
console.log(JSON.stringify(report,null,2));

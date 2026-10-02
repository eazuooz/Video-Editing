// Called only after direct inspection of complete current-hash readbacks and focused ambiguities.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base=path.join(__dirname,'..'),read=p=>JSON.parse(fs.readFileSync(p,'utf8')),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
const m=read(path.join(base,'project.json')),add=read(path.join(base,'observations-manifest.json')),initial=read(path.join(__dirname,'base-voice-review-initial.json')),repair=read(path.join(__dirname,'repair-voice.json')),focused=read(path.join(__dirname,'focused-asr-repair1.json'));
if(repair.status!=='finished'||focused.findings.length!==2)throw Error('Actual repair/focused evidence incomplete');
const dir=path.join(__dirname,'approved-asr'),scenes=[];
for(const manifest of [m,add]){
 const out=path.join(root,manifest.tts.outputDir),report=read(path.join(out,manifest.tts.filenameStem+'.asr-review.json'));
 if(!report.complete)throw Error('Complete current read-back required');
 for(const s of report.scenes){const file=path.join(out,'chunks',s.scene+'-scene.wav');if(hash(file)!==s.audio_sha256||!s.acousticChecks.endingHeuristicPassed)throw Error('Audio changed or incomplete ending '+s.scene);
 const rawFile=path.join(out,'asr',s.scene+'.json'),raw=read(rawFile);let finding='All paragraph content present; no omitted/repeated claim or extra spoken greeting. Punctuation/spacing and equivalent liaison variations retained. Human listening remains pending.';
 if(s.scene==='01')finding='All seven paragraphs retained. Recognized 마를 is the normal liaison of 말을; original and focused evidence saved.';
 if(s.scene==='07'||s.scene==='10'){const f=focused.findings.find(f=>f.scene===s.scene);if(f.sourceSha256!==s.audio_sha256)throw Error('Focused reread stale');finding=s.scene==='07'?'Opening clearly reads 도망가기. Focused12–36s reread accurately recognizes 우회/우회하면/우회경로, resolving whole-scene spelling errors without inventing voice approval.':'Clear same-meaning opening retained. Focused13–26s reread recognizes 잃을 rather than whole-scene 이룰; important meaning is present.';}
 if(s.scene==='11')finding='Clear new own-game opening and all seven complete paragraphs. Minor spelling 덮어져지지 retains the spoken negative; no missing/duplicated condition. Human articulation and comprehension remain pending.';
 if(s.scene==='09'){
  const removed=raw.words.filter(w=>w.timestamp[0]>=56.9);if(removed.length!==12||removed.some(w=>(w.timestamp[1]??56.94)-w.timestamp[0]>.021))throw Error('Unexpected tail; do not filter unreviewed speech');
  raw.words=raw.words.filter(w=>w.timestamp[0]<56.9);raw.text=raw.words.map(w=>w.text).join('');raw.derivation={rawAsr:path.relative(root,rawFile).replaceAll('\\','/'),excludedImpossibleTail:removed,evidence:'projects/game-writing/production/focused-asr.json',reason:'20ms/zero-duration fabricated credit tokens after a fully spoken ending; focused reread contains expected text only and final80ms RMS/peak is nearly silent.'};finding='All seven paragraphs present. Only the proven impossible ASR credit tail is excluded from timing; source PCM and raw ASR remain unchanged.';
 }
 const dest=path.join(dir,s.scene+'.json');write(dest,raw);
 scenes.push({id:s.scene,wav:path.relative(root,file).replaceAll('\\','/'),audioSha256:s.audio_sha256,approvedAsr:path.relative(root,dest).replaceAll('\\','/'),decision:'technical-content-and-ending-reviewed',finding,acousticChecks:s.acousticChecks,similarity:s.similarity,humanListening:'pending'});
 }
}
if(scenes.length!==16)throw Error('All original and added scenes required');
for(const s of initial.scenes.filter(s=>!['07','10','11'].includes(s.id)))if(scenes.find(a=>a.id===s.id).audioSha256!==s.audioSha256)throw Error('Preserved original voice changed');
write(path.join(__dirname,'voice-approval.json'),{reviewedAt:new Date().toISOString(),allCurrentScenesTechnicallyReviewed:true,scenes:scenes.sort((a,b)=>a.id.localeCompare(b.id)),originalParagraphs:72,addedParagraphs:8,allExplanationClaimsPreserved:true,humanListening:'pending',kind:'Direct ASR/acoustic technical review, not an asserted human listening session',sourceRights:'pending',finalRenderApproved:false});
console.log('All16 current scene voices/80 paragraphs technically reviewed; human listening remains pending.');

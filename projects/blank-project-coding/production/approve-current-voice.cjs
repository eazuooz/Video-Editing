// Technical content/ending review only. This does not claim human listening.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict'),root=path.resolve(__dirname,'../../..'),read=p=>JSON.parse(fs.readFileSync(p,'utf8')),m=read(path.join(__dirname,'../project.json')),out=path.join(root,m.tts.outputDir),script=read(path.join(root,m.paths.script)),r=read(path.join(out,m.tts.filenameStem+'.asr-review.json'));
assert(r.complete&&r.sceneCount===34);const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const notes={
 '02':'Number spelling 1/2 only.', '05':'ASR adds a harmless opening 자; every intended sentence remains complete.',
 '07':'Digits and Korean number spellings only.','08':'Digits and Korean number spellings only.',
 '09':'Repaired and independently recognized 10/15/20 correctly; 앞/압 final consonant spelling and numeric normalization only.',
 '11':'Node English spelling and a minor 에/해 adjacent-syllable difference; node/scope question unchanged.',
 '12':'Focused unprompted recognition confirms correct 테트리스 opening; full-scene ASR adds initial 스. 2차원 numeral normalization.',
 '14':'Four spelled 4; same block cells.',
 '16':'Repaired opening clearly says 이동 함수. Minor 옆 이동에 썼던/옆 이동했었던 readback difference; intended reuse of collision check remains intelligible in context.',
 '18':'쌓/싸 final consonant and four/4 spelling; boundary rule complete.',
 '19':'의/에 pronunciation variants only.','21':'에/의 adjacent-syllable readback; empty/nonempty and tail traversal complete.',
 '24':'백/100, numbers 10/30/2 normalization; blank-project and time examples complete.',
 '25':'Focused unprompted recognition confirms 아무 코드나, overriding erroneous full-scene 암흑. Particle differences do not alter debugger rule.',
 '27':'맡/맞 final-consonant homophone; request for limited help unchanged.',
 '29':'1/2 and 3/4 numeric spelling only.','32':'패들을/패드를 reduced-syllable readback; same visible paddle and center/edge collision example.',
 '34':'의/에 pronunciation only; complete concluding call to independently implement.'
};
const scenes=r.scenes.map(s=>{const wav=path.join(out,'chunks',s.scene+'-scene.wav'),a=read(path.join(out,'asr',s.scene+'.json'));assert.equal(hash(wav),s.audio_sha256);assert.equal(a.audio_sha256,s.audio_sha256);assert.equal(s.expected,script.scenes.find(v=>v.id===s.scene).lines.join(' '));assert(s.acousticChecks.endingHeuristicPassed);assert(!s.differences.length||notes[s.scene]);return{id:s.scene,audioSha256:s.audio_sha256,wav:path.relative(root,wav).replaceAll('\\','/'),approvedAsr:path.relative(root,path.join(out,'asr',s.scene+'.json')).replaceAll('\\','/'),notes:notes[s.scene]||'All intended words independently recognized without differences; complete ending.',acousticChecks:s.acousticChecks,asrDifferences:s.differences};});
for(const sid of ['12','25']){const f=read(path.join(__dirname,'focused-asr-remaining.json')).find(s=>s.scene===sid);assert.equal(f.sourceSha256,scenes.find(s=>s.id===sid).audioSha256);}
fs.writeFileSync(path.join(__dirname,'voice-approval.json'),JSON.stringify({reviewedAt:new Date().toISOString(),allCurrentScenesTechnicallyReviewed:true,scope:'All current scene audio hashes, full-scene independent ASR, explicit difference review and ending measurements; targeted unprompted ASR for ambiguous words; corrected scenes09/16/20 independently reviewed.',humanListening:'pending',paragraphCount:script.scenes.reduce((n,s)=>n+s.lines.length,0),scenes},null,2)+'\n');console.log('34 current scenes technically reviewed; human listening remains pending.');

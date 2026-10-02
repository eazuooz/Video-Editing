// Run only after inspecting the complete current ASR report. Human listening is separate.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict'),W=__dirname,R=path.resolve(W,'../../../..'),read=p=>JSON.parse(fs.readFileSync(p,'utf8')),m=read(path.join(W,'voice.manifest.json')),out=path.join(R,m.tts.outputDir),s=read(path.join(W,'narration.tts.ko.json')),r=read(path.join(out,m.tts.filenameStem+'.asr-review.json'));
assert(r.complete&&r.sceneCount===56,'Finish all current scene ASR first');const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const reviewed={
 '02':{diff:[['replace','에','의']],note:'Particle 에/의 readback only; the hiring question is intact.'},
 '03':{diff:[['replace','람인','라민'],['replace','씨플러스플러스','c']],note:'사람인 liaison/spelling and C++ conventional transcription; claim and qualifications retained.'},
 '04':{diff:[['replace','씨플러스플러스','c'],['replace','씨플러스플러스','c'],['replace','난은','나는']],note:'C++ spelling and 취업난은 liaison; the explicit warning against inferring easy junior hiring remains complete.'},
 '05':{diff:[['replace','씨플러스플러스','c']],note:'C++ conventional transcription only.'},
 '08':{diff:[['replace','넥스트','next']],note:'Next is transcribed in English; all pointer and deletion questions retained.'},
 '11':{diff:[['replace','씨플러스플러스','c']],note:'C++ conventional transcription only.'},
 '35':{diff:[['replace','부터','붙어']],note:'부터 and 붙어 share the same spoken consonant sequence; the quoted question and getting-stuck statement are complete.'},
 '36':{diff:[['insert','','자']],note:'Full-scene ASR has a zero-duration opening 자. Require separate unprompted short-window ASR showing the actual Tetris opening.'},
 '37':{diff:[['replace','에','의']],note:'Particle 에/의 readback; the learner must answer the design questions, not the instructor.'},
 '44':{diff:[['replace','에','의']],note:'Particle 에/의 readback in 이 질문에; all six design questions and the learner-answering requirement are intact.'},
 '45':{diff:[['replace','깃허브','github']],note:'GitHub transcribed with its original English spelling; Recognition is now correctly recognized in the repaired take.'},
 '47':{diff:[['replace','1000','천'],['replace','10','열'],['replace','10','열']],note:'Identical numbers1000 and10 spelled in Korean; no quantity or claim change.'},
 '49':{diff:[['replace','두','2']],note:'두 시간 and 2시간 denote the identical two-hour debugging example; surrounding original words are intact.'},
 '52':{diff:[['replace','삼사','34']],note:'The repaired spoken three and four are both independently recognized as3 and4. Korean numeral spelling differs from digit transcription only.'}
};
const scenes=r.scenes.map(v=>{const wav=path.join(out,'chunks',v.scene+'-scene.wav'),a=read(path.join(out,'asr',v.scene+'.json'));assert.equal(hash(wav),v.audio_sha256);assert.equal(a.audio_sha256,v.audio_sha256);assert.equal(v.expected,s.scenes.find(x=>x.id===v.scene).lines.join(' '));assert(v.acousticChecks.endingHeuristicPassed,'Review ending '+v.scene);if(v.differences.length){assert(reviewed[v.scene],'Unreviewed difference '+v.scene);assert.deepEqual(v.differences.map(d=>[d.kind,d.expected,d.recognized]),reviewed[v.scene].diff,'Changed differences '+v.scene);}if(v.scene==='36'&&v.differences.length){const f=read(path.join(W,'focused-asr-36.json'))[0];assert.equal(f.sourceSha256,v.audio_sha256);assert(f.text.trim().startsWith('테트리스를'),'Review opening36');}
return{id:v.scene,audioSha256:v.audio_sha256,wav:path.relative(R,wav).replaceAll('\\','/'),approvedAsr:path.relative(R,path.join(out,'asr',v.scene+'.json')).replaceAll('\\','/'),notes:v.differences.length?reviewed[v.scene].note:'All intended words recognized with complete ending; spacing/punctuation normalized.',acousticChecks:v.acousticChecks,asrDifferences:v.differences};});
fs.copyFileSync(path.join(out,m.tts.filenameStem+'.asr-review.json'),path.join(W,'asr-final-review.json'));fs.copyFileSync(path.join(out,m.tts.filenameStem+'.asr-review.txt'),path.join(W,'asr-final-review.txt'));
fs.writeFileSync(path.join(W,'voice-approval.json'),JSON.stringify({reviewedAt:new Date().toISOString(),allCurrentScenesTechnicallyReviewed:true,scope:'56 current WAV hashes, full independent ASR, explicit difference inspection and ending measurements. Scenes10/14 re-recorded for code pronunciation;13/21/33/34 ending repairs preserved previous takes.',humanListening:'pending',paragraphCount:118,scenes},null,2)+'\n');console.log('56 current scenes technically reviewed; human listening pending.');

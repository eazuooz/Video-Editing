// Direct transcript review record; never substitutes for human listening.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v2');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const manifest=read(path.join(work,'tts-manifest.json')),output=path.join(root,manifest.tts.outputDir),report=read(path.join(output,manifest.tts.filenameStem+'.asr-review.json'));
if(!report.complete||report.sceneCount!==6)throw Error('Complete six-scene current ASR is required');
const repairing=process.argv.includes('--repair-04');
if(repairing){
 fs.writeFileSync(path.join(work,'rejected-initial-asr.json'),JSON.stringify(report,null,2)+'\n');
 const file=path.join(work,'additions.ko.json'),script=read(file);
 script.scenes[3].lines[4]='앞의 자체 점프 테스트에서는 발판의 너비나 재시도 대기 시간 중 하나만 바꿨습니다.';
 fs.writeFileSync(file,JSON.stringify(script,null,2)+'\n');
}
const scenes=report.scenes.map(s=>{
 const audio=path.join(output,'chunks',s.scene+'-scene.wav');
 if(hash(audio)!==s.audio_sha256)throw Error('Stale ASR '+s.scene);
 const rejected=repairing&&s.scene==='04';
 return {scene:s.scene,audioSha256:s.audio_sha256,status:rejected?'rejected':'accepted',duration:s.acousticChecks.duration,contentReview:rejected?'Ambiguous ASR 발판 포기나 for 발판 폭이나: rewrite as 발판의 너비나 재시도 대기 시간 중 하나만 and regenerate only this addition.':'All nine lines present in order, complete ending, no repeated word strings or missing statements. FTL recognized as English abbreviation; Into the Breach loanword recognized as 브리지/브릿지/Into the bridge. Captions use actual title and human pronunciation review stays pending.',acousticChecks:s.acousticChecks,humanListening:'pending'};
});
fs.writeFileSync(path.join(work,'addition-asr-direct-review.json'),JSON.stringify({reviewedAt:new Date().toISOString(),method:'Read every complete actual scene transcript against all54 new KO lines, with current WAV hash and tail evidence',allCurrentChunksReviewed:!repairing,scenes,humanListening:'pending; ASR is not human listening'},null,2)+'\n');
console.log(repairing?'Only scene04 rejected for clearer technical wording; other five current chunks retained.':'Direct current-hash addition review recorded.');

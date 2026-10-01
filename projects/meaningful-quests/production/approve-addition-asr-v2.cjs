// This records the direct comparison of all 54 complete actual transcript lines.
// ASR spelling uncertainties remain explicit; this is not human listening approval.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v2');
const m=JSON.parse(fs.readFileSync(path.join(work,'tts-manifest.json'),'utf8'));
const dir=path.join(root,m.tts.outputDir),review=JSON.parse(fs.readFileSync(path.join(dir,m.tts.filenameStem+'.asr-review.json'),'utf8'));
const notes={
 '01':'All nine statements and the complete closing statement occur once in order. A Short Hike is recognized in English; the spoken Korean game name is retained in the script.',
 '02':'All nine statements occur once in order with a complete ending. ASR writes 맥퀘스트 for 내 퀘스트, 절벽으로 for 절벽을 and 바닥에 for 바닥의. Pronunciation uncertainty remains for human listening; no clause is omitted or repeated.',
 '03':'All nine statements occur once in order and the complete ending is present. Spiritfarer spacing and 앞의/앞에 are recognition variants. No missing acquisition/use distinction.',
 '04':'All nine statements occur once in order. The script explicitly distinguishes this commercial montage from the original controlled bridge comparison. Complete ending; 앞의/앞에 recognition variant only.',
 '05':'All nine statements occur once in order and the complete ending is present. ASR writes 귀한 for 귀환 and 새의 적 for 새 적. These are recorded as pronunciation uncertainties for human listening, not silently marked human-approved.',
 '06':'All nine statements occur once in order, including the distinction between observed action and human understanding. Complete ending; 사이의/사이에 recognition variant only.'
};
if(!review.complete||review.scenes.length!==6)throw Error('Incomplete actual ASR');
const scenes=review.scenes.map(s=>{
 const hash=crypto.createHash('sha256').update(fs.readFileSync(path.join(dir,'chunks',s.scene+'-scene.wav'))).digest('hex');
 if(hash!==s.audio_sha256||!s.acousticChecks.endingHeuristicPassed)throw Error('Stale hash or failed acoustic ending '+s.scene);
 return {scene:s.scene,audioSha256:hash,status:'accepted',duration:s.acousticChecks.duration,contentReview:notes[s.scene],acousticChecks:s.acousticChecks,humanListening:'pending',actualTranscript:s.recognized,expectedTranscript:s.expected};
});
fs.writeFileSync(path.join(work,'addition-asr-direct-review.json'),JSON.stringify({reviewedAt:new Date().toISOString(),method:'Directly read each complete actual current-hash transcript against all nine authored lines per chapter; compare content order, missing clauses, repeats and full ending with measured acoustic evidence.',allCurrentChunksReviewed:true,scenes,humanListening:'pending'},null,2)+'\n');
console.log('54 actual additional statements reviewed; current hashes/tails match, human listening remains pending.');

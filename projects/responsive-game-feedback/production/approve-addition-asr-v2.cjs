// Execute only after directly reading all six complete current-hash transcripts.
const fs=require('node:fs'),crypto=require('node:crypto');
if(!process.argv.includes('--confirmed-direct-review'))throw Error('Direct review of current speech required');
const work='projects/responsive-game-feedback/production/final-v2',dir='shared/output/narration/responsive-game-feedback/qwen3-1.7b-additions-v2';
const r=JSON.parse(fs.readFileSync(dir+'/responsive-game-feedback-additions-v2.asr-review.json','utf8'));
const script=JSON.parse(fs.readFileSync(work+'/additions.ko.json','utf8'));
const notes={
 '01':'Nine clauses occur once in order with complete ending. 패널 안의/안에 and 앞의/앞에 remain recognition variants for human listening.',
 '02':'Current rewritten ending and every nine-clause observation directly compared; no unauthored sign-off may be accepted.',
 '03':'All nine clauses occur once. 산소 미포함 is recognized as 산소 및 포함; terminology pronunciation remains pending human listening. No unsupported keyboard action asserted.',
 '04':'All nine clauses occur once in order. 세 캐릭터 is recognized as 새 캐릭터, acoustically ambiguous; exact visual three-worker state and caption preserved. Human listening pending.',
 '05':'All nine current clauses, including the new work-marker/character/terrain observation, directly compared. Previous production-process wording must be absent.',
 '06':'Nine clauses including Cancel Tool and context-specific response ending occur once. 범례/범내 and Korean particles vary in recognition; human listening pending.'
};
const scenes=r.scenes.map(s=>{
 const wav=dir+'/chunks/'+s.scene+'-scene.wav',hash=crypto.createHash('sha256').update(fs.readFileSync(wav)).digest('hex');
 const expected=script.scenes.find(x=>x.id===s.scene)?.lines.join(' ');
 if(hash!==s.audio_sha256||expected!==s.expected||!s.acousticChecks.endingHeuristicPassed||s.similarity<.97)throw Error('Stale/failed speech '+s.scene);
 if(/다음\s*영상에서\s*만나요/.test(s.recognized))throw Error('Unauthored ending still recognized');
 if(s.scene==='05'&&s.recognized.includes('속도를 낮추어'))throw Error('Old production-process sentence persists');
 return {scene:s.scene,audioSha256:hash,status:'accepted',duration:s.acousticChecks.duration,contentReview:notes[s.scene],acousticChecks:s.acousticChecks,expectedTranscript:s.expected,actualTranscript:s.recognized,humanListening:'pending'};
});
if(scenes.length!==6)throw Error('All six current chunks required');
fs.writeFileSync(work+'/addition-asr-direct-review.json',JSON.stringify({reviewedAt:new Date().toISOString(),method:'Direct reading of every54 authored clause against complete current-hash ASR, checking order, omission, repetition, unauthorized ending and acoustic tail; same approved model/reference with only02/05 generated on CPU after verified owned GPU stop.',allCurrentChunksReviewed:true,scenes,humanListening:'pending'},null,2)+'\n');
console.log('Current added speech reviewed; human listening remains pending.');

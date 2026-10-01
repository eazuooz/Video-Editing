// Directly read all six complete current transcripts before writing this record.
const fs=require('node:fs'),crypto=require('node:crypto');
const work='projects/praise-player/production/final-v2',dir='shared/output/narration/praise-player/qwen3-1.7b-additions-v2';
const r=JSON.parse(fs.readFileSync(dir+'/praise-player-additions-v2.asr-review.json','utf8'));
const notes={
 '01':'All nine statements occur once in order; complete ending. ASR writes 맞췄 for 마쳤 and 앞에 for 앞의. Human pronunciation review remains pending.',
 '02':'All nine statements and the full closing distinction between instruction and praise occur once. 러시/러쉬, 굿/굳 and 앞의/앞에 are recorded recognition variants; human listening pending.',
 '03':'All nine statements occur once in order, including the difference between input guidance and a performed hit. 그 뒤의/그 뒤에 and 내 게임의/내 게임에 are recognition variants; human listening pending.',
 '04':'All nine complete statements occur once, including the explicit distinction from the original controlled comparison. ASR writes 이어진 선 for 이어진 성과; this uncertain noun phrase is flagged for human listening rather than silently treated as human-approved.',
 '05':'All nine statements occur once in order, including the limited scope of a single Perfect and the prohibition on inventing unseen failures/completion. Complete ending; 러시/러쉬 and 앞의/앞에 variants remain for human listening.',
 '06':'All nine statements occur once in order, including the human-understanding limitation and the five original design criteria. Complete ending; human listening pending.'
};
const scenes=r.scenes.map(s=>{
 const f=dir+'/chunks/'+s.scene+'-scene.wav',h=crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
 if(h!==s.audio_sha256||!s.acousticChecks.endingHeuristicPassed||s.similarity<.97)throw Error('Stale/failed ASR or acoustic check '+s.scene);
 return {scene:s.scene,audioSha256:h,status:'accepted',duration:s.acousticChecks.duration,contentReview:notes[s.scene],acousticChecks:s.acousticChecks,humanListening:'pending',actualTranscript:s.recognized,expectedTranscript:s.expected};
});
if(scenes.length!==6)throw Error('All six current chunks required');
fs.writeFileSync(work+'/addition-asr-direct-review.json',JSON.stringify({reviewedAt:new Date().toISOString(),method:'Directly read all 54 authored lines against the six complete current-hash ASR transcripts, checking clause order, repeats, omissions and acoustic ending evidence; uncertain pronunciation stays pending.',allCurrentChunksReviewed:true,scenes,humanListening:'pending'},null,2)+'\n');
console.log('Six current chunks directly reviewed; human listening remains pending.');

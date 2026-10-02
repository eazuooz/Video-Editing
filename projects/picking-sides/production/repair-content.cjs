// Repair only the two new actual-example chapters; preserve the six explanations.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const base=path.resolve(__dirname,'..'),read=p=>JSON.parse(fs.readFileSync(path.join(base,p),'utf8'));
const draft=read('script/draft-bilingual.json');
const backup=path.join(base,'script/draft-before-asr-repair.json');
if(!fs.existsSync(backup))fs.writeFileSync(backup,JSON.stringify(draft,null,2)+'\n');
const original=JSON.parse(fs.readFileSync(backup,'utf8'));
const s=id=>draft.scenes.find(x=>x.id===id);
s('03').lines[3][0]=s('03').lines[3][0].replace('앞선 경주를 되감은 장면은 아닙니다.','앞선 실행을 다시 재생한 것은 아닙니다.');
s('09').lines[0][0]=s('09').lines[0][0].replace('모자를 쓴 토끼 한 마리','뿔이 있는 양 한 마리');
s('09').lines[0][1]=s('09').lines[0][1].replace('the rabbit wearing a hat','the horned sheep');
s('09').lines[2][0]=s('09').lines[2][0].replace('같은 토끼','같은 양');
s('09').lines[2][1]=s('09').lines[2][1].replace('that rabbit','that sheep');
s('09').lines[4][0]=s('09').lines[4][0].replace('컷마다 동작을 관찰하되','각 장면의 동작을 관찰하되');
for(const id of ['02','04','06','08','10','12'])if(JSON.stringify(s(id))!==JSON.stringify(original.scenes.find(x=>x.id===id)))throw Error('Explanation changed '+id);
draft.status='source-and-asr-repair-03-09';
fs.writeFileSync(path.join(base,'script/draft-bilingual.json'),JSON.stringify(draft,null,2)+'\n');
// Keep the prior action-source rewrite reproducible rather than restoring the rejected target.
const p=path.join(__dirname,'finalize-action-script.cjs');let source=fs.readFileSync(p,'utf8');
source=source.replaceAll('모자를 쓴 토끼 한 마리','뿔이 있는 양 한 마리').replaceAll('the rabbit wearing a hat','the horned sheep').replaceAll('같은 토끼','같은 양').replaceAll('that rabbit','that sheep').replaceAll('컷마다 동작을 관찰하되','각 장면의 동작을 관찰하되');
fs.writeFileSync(p,source);
const report=read('../../shared/output/narration/picking-sides/qwen3-1.7b-balanced-v1/picking-sides-qwen3-1.7b-balanced-v1.asr-review.json');
const notes={
 '01':'All seven paragraphs recovered. 세/새 and 의/에 are homophonic recognition differences; no missing clause, repetition or added greeting.',
 '02':'All five paragraphs and final 확인해 보겠습니다 recovered. 이 세→이세 spacing; Whisper end timestamp warning is not by itself missing speech. Acoustic ending evidence retained.',
 '03':'Seven paragraphs recovered but 되감은→대감은 is ambiguous pronunciation. Replace only that phrase and regenerate this scene; 잎/입 and 세/새 are expected homophones.',
 '04':'All five paragraphs recovered. 평소에→평소의 particle difference is minor; no claim omitted, repeated or invented.',
 '05':'All seven paragraphs including selection-only behavior recovered. 잎/입, 세/새 are homophones; no duplication or missing ending.',
 '06':'All five paragraphs including no financial reward and separate human enjoyment evaluation recovered.',
 '07':'All seven paragraphs including distinction between attempts recovered. Commas and 의/에 differences do not change the claim.',
 '08':'All five paragraphs including warning about unfinished matches recovered. 이세관계 is whitespace; full final 마세요 recognized despite timestamp warning.',
 '09':'All seven paragraphs recovered; 컷마다→컵마다 ambiguous. More importantly direct source crops show the rabbit static/dead while the horned sheep actively flies. Correct target and phrase, resynthesize.',
 '10':'All five paragraphs including human evidence distinction recovered; no missing/repeated speech.',
 '11':'All seven paragraphs and the exact observed finishing order recovered (잎 recognized 입). Ending 만들어 보세요 recovered despite timestamp warning.',
 '12':'All five paragraphs including four questions and final claim recovered; no invented greeting or repetition.'
};
fs.writeFileSync(path.join(__dirname,'asr-direct-review-initial.json'),JSON.stringify({reviewedAt:new Date().toISOString(),method:'Direct comparison of all twelve complete ASR transcripts with all 72 Korean paragraphs, not a similarity-score-only pass',humanListening:'pending',finalMixReview:false,scenes:report.scenes.map(x=>({scene:x.scene,audioSha256:x.audio_sha256,decision:['03','09'].includes(x.scene)?'repair-required':'content-readback-pass',notes:notes[x.scene],acousticChecks:x.acousticChecks})),repairScenes:['03','09']},null,2)+'\n');
console.log('Preserved six explanation chapters. Scene03 phrase and scene09 visible target corrected; only03/09 require resynthesis.');

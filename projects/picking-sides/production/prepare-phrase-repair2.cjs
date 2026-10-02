// Prepare only the two rejected candidates; keep the accepted05 candidate and original PCM.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base=path.join(root,'projects/picking-sides'),work=path.join(__dirname,'existing-game-replan/phrase-repair2');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,'')),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
if(fs.existsSync(path.join(work,'request.json')))throw Error('Already prepared; use the existing frozen request.');
const out1=path.join(root,'shared/output/narration/picking-sides/qwen3-1.7b-balanced-v2-phrase-repair1');
const report=read(path.join(out1,'picking-sides-phrase-repair1.asr-review.json'));
for(const s of report.scenes)if(hash(path.join(out1,'chunks',s.scene+'-scene.wav'))!==s.audio_sha256)throw Error('Stale candidate '+s.scene);
const review={reviewedAt:new Date().toISOString(),humanListening:'pending',scenes:report.scenes.map(s=>({...s,decision:s.scene==='05'?'content-readback-pass':'rejected-pending-new-wording',reason:s.scene==='02'?'지금부터 is again absent in actual recognized content; clean ending does not approve the omission.':s.scene==='07'?'닭 still repeatedly recognized as 닷; use the visible white character to avoid ambiguous pronunciation.':'All three sentences read exactly; no invented prefix, complete ending. Keep this candidate for the later preserved-PCM splice.'}))};
write(path.join(__dirname,'existing-game-replan/phrase-repair1/direct-review.json'),review);
for(const f of ['script/draft-bilingual.json','script/narration.ko.json','script/narration.en.json','production/script-source-review.json']){const dest=path.join(work,'baseline',f);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.copyFileSync(path.join(base,f),dest);}
const draftPath=path.join(base,'script/draft-bilingual.json'),draft=read(draftPath),before=JSON.parse(JSON.stringify(draft));
draft.scenes.find(s=>s.id==='02').lines[4]=[
 '두 게임의 실제 플레이를 보겠습니다. 대상을 찾고, 마음속으로 선택하고, 위험과 결과를 읽는 순서로 하나씩 확인해 보겠습니다.',
 'Let us watch the two games in action, finding a participant, choosing whom to root for, and reading the risk and outcome.'
];
draft.scenes.find(s=>s.id==='07').lines[2]=[
 '얼티밋 치킨 호스의 초기 플레이 자료로 옮겨보죠. 움직이는 톱날과 흰색 캐릭터가 점프하는 모습을 함께 봅니다. 출발한 곳과 착지할 발판 사이에 위험이 있습니다.',
 'Switch to early Ultimate Chicken Horse gameplay. Watch the moving saw and the white character jumping. The danger lies between takeoff and the next platform.'
];
draft.scenes.find(s=>s.id==='07').lines[3]=[
 '뒤의 다른 시도에서는 말이 움직입니다. 컷이 바뀌었으니 앞서 본 흰색 캐릭터의 행동이 이어진 결과로 보아서는 안 됩니다.',
 'The horse moves in a different attempt. The cut should not make its outcome look like a continuation of the white character’s earlier action.'
];
for(const s of draft.scenes.filter(s=>Number(s.id)%2===0))if(s.id!=='02'&&JSON.stringify(s.lines)!==JSON.stringify(before.scenes.find(x=>x.id===s.id).lines))throw Error('Preserved explanation changed');
if(JSON.stringify(draft.scenes.find(s=>s.id==='02').lines.slice(0,4))!==JSON.stringify(before.scenes.find(s=>s.id==='02').lines.slice(0,4)))throw Error('Original02 prefix changed');
write(draftPath,draft);const prep=spawnSync(process.execPath,[path.join(__dirname,'prepare-script.cjs')],{cwd:root,encoding:'utf8',windowsHide:true});if(prep.status!==0)throw Error(prep.stderr);
const selected=[['02',[4]],['07',[2,3]]];
for(const [lang,col] of [['ko',0],['en',1]])write(path.join(work,'patch.'+lang+'.json'),{title:read(path.join(base,'project.json')).titles[lang],status:'reviewed-targeted-pronunciation-repair2-candidates-only',scenes:selected.map(([id,indices])=>({id,title:'Targeted replacement '+id,lines:indices.map(i=>draft.scenes.find(s=>s.id===id).lines[i][col])}))});
const manifest=read(path.join(base,'project.json'));manifest.paths.script=path.relative(root,path.join(work,'patch.ko.json')).replaceAll('\\','/');manifest.paths.scriptEn=path.relative(root,path.join(work,'patch.en.json')).replaceAll('\\','/');manifest.tts.outputDir='shared/output/narration/picking-sides/qwen3-1.7b-balanced-v2-phrase-repair2';manifest.tts.filenameStem='picking-sides-phrase-repair2';write(path.join(work,'manifest.json'),manifest);
const gate=read(path.join(__dirname,'script-source-review.json'));Object.assign(gate,{updatedAt:new Date().toISOString(),draftSha256:hash(draftPath),koSha256:hash(path.join(base,'script/narration.ko.json')),enSha256:hash(path.join(base,'script/narration.en.json')),targetedPhraseRepair:{request:'projects/picking-sides/production/existing-game-replan/phrase-repair2/request.json',changes:['02 transition rephrased with all concept steps preserved; original four explanation paragraphs unchanged.','07 uses visible white character to avoid unresolved chicken-word pronunciation.'],originalExplanationParagraphsPreserved:29,currentPcmApproved:false}});write(path.join(__dirname,'script-source-review.json'),gate);
write(path.join(work,'request.json'),{createdAt:new Date().toISOString(),status:'ready-to-synthesize-candidates-only',selected,accepted05:'projects/picking-sides/production/existing-game-replan/phrase-repair1/direct-review.json',originalExplanationParagraphsPreserved:29,allOldPcmPreserved:true,sourcePlanUnchanged:true,application:'Directly review both candidates before preserved-PCM composites and current-hash full ASR.',humanListening:'pending'});
const oldState=read(path.join(__dirname,'repair-v2-phrases.json'));Object.assign(oldState,{status:'candidates-reviewed-two-rejected-one-accepted',reconciledAt:new Date().toISOString(),runnerExited:true,checkpointError:'Transient UNKNOWN queue write after successful CPU-ASR; children completed with exit0. No synthesis rerun.',directReview:'projects/picking-sides/production/existing-game-replan/phrase-repair1/direct-review.json'});write(path.join(__dirname,'repair-v2-phrases.json'),oldState);
console.log('Prepared02/07 only; accepted05 and original29 explanation paragraphs preserved.');

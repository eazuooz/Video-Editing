// One-time editorial pronunciation repair; retain all explanation text and PCM.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base=path.join(root,'projects/picking-sides');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const work=path.join(__dirname,'existing-game-replan/phrase-repair1');
if(fs.existsSync(path.join(work,'request.json')))throw Error('Already prepared; inspect current request instead of rerunning.');
const parent=read(path.join(__dirname,'resource-v2-runner.json'));
if(parent.status!=='tts-asr-ready-for-direct-review')throw Error('Original v2 parent must finish first');
const bridge=read(path.join(__dirname,'repair-v2-bridge02.json'));
if(bridge.status!=='superseded-by-targeted-phrase-repair-before-any-child')throw Error('Single bridge candidate runner must be safely superseded');
const originals=['project.json','script/draft-bilingual.json','script/narration.ko.json','script/narration.en.json','production/script-source-review.json','production/voice-approval.json'];
for(const f of originals){const out=path.join(work,'baseline',f);fs.mkdirSync(path.dirname(out),{recursive:true});fs.copyFileSync(path.join(base,f),out);}
const draftPath=path.join(base,'script/draft-bilingual.json'),draft=read(draftPath);
const before=JSON.parse(JSON.stringify(draft));
draft.scenes.find(s=>s.id==='05').lines[0]=[
 '이번에는 창문 청소용 발판입니다. 빨간 캐릭터와 노란 캐릭터 중 한 명을 골라 보세요. 지금 발판 위에 있는 쪽과 아래에 매달린 쪽의 다음 행동은 다릅니다.',
 'Now watch the window-cleaning platforms. Choose red or yellow. Standing on the platform and hanging below it lead to different immediate actions.'
];
draft.scenes.find(s=>s.id==='07').lines[2]=[
 '얼티밋 치킨 호스의 초기 플레이 자료로 옮겨보죠. 움직이는 톱날과 닭 캐릭터가 점프하는 모습을 함께 봅니다. 출발한 곳과 착지할 발판 사이에 위험이 있습니다.',
 'Switch to early Ultimate Chicken Horse gameplay. Watch the moving saw and the chicken character jumping. The danger lies between takeoff and the next platform.'
];
draft.scenes.find(s=>s.id==='07').lines[3]=[
 '뒤의 다른 시도에서는 말이 움직입니다. 컷이 바뀌었으니 앞서 본 닭 캐릭터의 행동이 이어진 결과로 보아서는 안 됩니다.',
 'The horse moves in a different attempt. The cut should not make its outcome look like a continuation of the chicken character’s earlier action.'
];
for(const s of draft.scenes.filter(s=>Number(s.id)%2===0))if(JSON.stringify(s.lines)!==JSON.stringify(before.scenes.find(x=>x.id===s.id).lines))throw Error('Explanation changed');
write(draftPath,draft);
const prep=spawnSync(process.execPath,[path.join(__dirname,'prepare-script.cjs')],{cwd:root,encoding:'utf8',windowsHide:true});if(prep.status!==0)throw Error(prep.stderr);
const selected=[['02',[4]],['05',[0]],['07',[2,3]]];
for(const [lang,col] of [['ko',0],['en',1]])write(path.join(work,'patch.'+lang+'.json'),{
 title:read(path.join(base,'project.json')).titles[lang],status:'reviewed-targeted-pronunciation-repair-candidates-only',
 scenes:selected.map(([id,indices])=>({id,title:'Targeted replacement '+id,lines:indices.map(i=>draft.scenes.find(s=>s.id===id).lines[i][col])}))
});
const manifest=read(path.join(base,'project.json'));manifest.paths.script=path.relative(root,path.join(work,'patch.ko.json')).replaceAll('\\','/');manifest.paths.scriptEn=path.relative(root,path.join(work,'patch.en.json')).replaceAll('\\','/');
manifest.tts.outputDir='shared/output/narration/picking-sides/qwen3-1.7b-balanced-v2-phrase-repair1';manifest.tts.filenameStem='picking-sides-phrase-repair1';write(path.join(work,'manifest.json'),manifest);
const review=read(path.join(__dirname,'script-source-review.json'));
review.updatedAt=new Date().toISOString();review.status='same-reviewed-actions-targeted-pronunciation-wording-repair';
review.draftSha256=hash(draftPath);review.koSha256=hash(path.join(base,'script/narration.ko.json'));review.enSha256=hash(path.join(base,'script/narration.en.json'));
review.targetedPhraseRepair={request:'projects/picking-sides/production/existing-game-replan/phrase-repair1/request.json',changes:['05paragraph1 removes an unneeded repeated spoken game name; game/footage identity remains unchanged.','07paragraph3/4 explicitly say chicken character to avoid 닭의→달걀 ambiguity.'],explanationsUnchanged:true,currentPcmApproved:false};write(path.join(__dirname,'script-source-review.json'),review);
write(path.join(work,'request.json'),{createdAt:new Date().toISOString(),status:'ready-to-synthesize-candidates-only',selected,
 reasons:{'02':'지금부터 omitted in three direct read-backs.','05':'Unscripted 가스캥/바스킹 before spoken game name.','07':'닭의 점프 repeatedly recognized as 달걀/달개; make chicken character explicit.'},
 allSixExplanationsUnchanged:true,unchangedExplanationParagraphs:29,oldWavesPreserved:true,
 application:'No automatic replacement. Directly review candidate speech, splice at inspected silent boundaries, preserve unaffected PCM, then regenerate assembly/fullASR/timing/mix/bilingual captions.',humanListening:'pending'});
console.log(prep.stdout+'Prepared four targeted paragraphs across02/05/07; no original explanation re-synthesis.');

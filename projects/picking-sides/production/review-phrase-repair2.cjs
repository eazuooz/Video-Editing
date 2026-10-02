// Direct comparison decisions made after reading complete current candidate ASRs.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),folder='shared/output/narration/picking-sides/qwen3-1.7b-balanced-v2-phrase-repair2';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const report=read(`${folder}/picking-sides-phrase-repair2.asr-review.json`);
const reasons={
 '02':'Both complete sentences, including the first 두 게임의 and final 확인해 보겠습니다, are present. No invented prefix, repetition or omission in the complete current-hash ASR.',
 '07':'Both paragraphs and all six sentences are present. 흰색 캐릭터 is now clearly recognized twice; horse is explicitly a separate attempt. 뒤의/뒤에 is a minor particle difference without a changed claim. Complete final 안 됩니다 is present.'
};
for(const s of report.scenes){
 const wave=path.join(root,folder,'chunks',`${s.scene}-scene.wav`);
 if(crypto.createHash('sha256').update(fs.readFileSync(wave)).digest('hex')!==s.audio_sha256)throw Error('Current candidate hash mismatch');
 if(!reasons[s.scene])throw Error('Unreviewed scene');
 s.decision='content-readback-pass';s.reason=reasons[s.scene];
}
fs.writeFileSync(path.join(__dirname,'existing-game-replan/phrase-repair2/direct-review.json'),JSON.stringify({reviewedAt:new Date().toISOString(),kind:'direct-complete-current-candidate-ASR-comparison',humanListening:'pending',automaticallyApproved:false,scenes:report.scenes},null,2)+'\n');
const statePath=path.join(__dirname,'repair-v2-phrases2.json'),state=JSON.parse(fs.readFileSync(statePath,'utf8'));
state.status='candidates-directly-reviewed-awaiting-preserved-PCM-composite';state.directReview='projects/picking-sides/production/existing-game-replan/phrase-repair2/direct-review.json';state.updatedAt=new Date().toISOString();fs.writeFileSync(statePath,JSON.stringify(state,null,2)+'\n');
const qp=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),queue=JSON.parse(fs.readFileSync(qp,'utf8')),item=queue.items.find(x=>x.slug==='picking-sides');
item.execution.phraseRepair2={...state,state:'projects/picking-sides/production/repair-v2-phrases2.json',toolSessionId:72096};item.stage='v3-preserved-PCM-composite-and-full-ASR';item.nextAction='Compose separately reviewed02/05/07 candidates into preserved PCM v3; review all12 current-hash ASRs and splice boundaries before final timing.';fs.writeFileSync(qp,JSON.stringify(queue,null,2)+'\n');
console.log('02/07 complete candidate ASRs directly accepted; human listening remains pending. No final render approval.');

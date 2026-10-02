const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='shared/output/narration/picking-sides/qwen3-1.7b-balanced-v3';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const report=read(`${base}/picking-sides-qwen3-1.7b-balanced-v3.asr-review.json`);
if(!report.complete||report.sceneCount!==12)throw Error('Full current report missing');
const reasons={
 '01':'All seven paragraphs and all game/early-version caveats are present without additions or omissions.',
 '02':'Four unchanged explanations and both new bridge sentences are complete. First 두 게임의 and last 확인해 보겠습니다 are present after the29.175s preserved PCM splice.',
 '03':'All seven identity, body/hand, position-memory and no-controlled-experiment paragraphs are present. 정해/정에 is a minor consonant ambiguity; human listening remains pending.',
 '04':'All five preserved explanation paragraphs are present. 평소에/평소의 is a minor particle difference without a changed claim.',
 '05':'New first paragraph and all six retained suffix paragraphs are complete across the candidate/suffix splice. No invented game-name prefix remains. 트럭 위의/위에 is a minor particle difference.',
 '06':'All five preserved reasons-for-rooting and human-enjoyment distinction paragraphs are complete.',
 '07':'All seven paragraphs are complete across both splices. 흰색 캐릭터 is recognized twice, later horse remains a separate attempt, no chicken/egg confusion. 뒤의/뒤에 and 앞의/앞에 are minor particles.',
 '08':'All five preserved relation/camera/unfinished-match explanations and final 마세요 are complete.',
 '09':'All seven moving-animal, flames, rocks, separate-attempt and camera-formula-limit paragraphs are present. 얼티밋/얼티미 remains a minor final-consonant recognition ambiguity; human listening pending.',
 '10':'All five preserved choice/observation/human-enjoyment-evidence paragraphs are complete.',
 '11':'All seven truck/scaffold/hand/drop/result/limited-winner-evidence paragraphs are complete. 위의/위에 and 쪽의/쪽에 are minor particles.',
 '12':'All five preserved concluding questions, camera/identity and actual-human-reaction explanations are complete.'
};
const scenes=report.scenes.map(s=>{const wav=`${base}/chunks/${s.scene}-scene.wav`;if(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,wav))).digest('hex')!==s.audio_sha256)throw Error('Current hash mismatch');return {id:s.scene,decision:'content-readback-pass',reason:reasons[s.scene],wav,audioSha256:s.audio_sha256,approvedAsr:`${base}/asr/${s.scene}.json`,expected:s.expected,recognized:s.recognized,differences:s.differences,acousticChecks:s.acousticChecks};});
const approval='projects/picking-sides/production/voice-approval.json',historical='projects/picking-sides/production/existing-game-replan/voice-approval-before-v3.json';if(!fs.existsSync(path.join(root,historical)))fs.copyFileSync(path.join(root,approval),path.join(root,historical));
write(approval,{reviewedAt:new Date().toISOString(),kind:'v3-all12-current-hash-complete-ASR-directly-reviewed',allCurrentScenesTechnicallyReviewed:true,humanListening:'pending',editorialApproval:true,finalMixApproved:false,paragraphCount:72,originalExplanationParagraphsPreserved:29,compositeProof:'projects/picking-sides/production/existing-game-replan/v3-composite-proof.json',scenes});
const proof=read('projects/picking-sides/production/existing-game-replan/v3-composite-proof.json');proof.scenes.forEach(s=>s.wholeCompositeAsrReviewed=true);proof.status='all12-current-hash-ASR-direct-review-pass-human-listening-pending';write('projects/picking-sides/production/existing-game-replan/v3-composite-proof.json',proof);
const qpath='production/batches/sakurai-planning-game-design/queue.json',q=read(qpath),i=q.items.find(x=>x.slug==='picking-sides');i.execution.v3FullAsr.status='finished-directly-reviewed';i.execution.v3FullAsr.exitCode=0;i.execution.currentAudioApproved=true;i.stage='final-timeline-and-existing-game-cut-review';i.nextAction='Measure exact12scene timing and bilingual cues, select existing-game actions, directly inspect every source boundary and caption before media rendering.';write(qpath,q);
console.log('All12 current-hash scene ASRs /72paragraphs directly reviewed; original29 explanation paragraphs and PCM retained. Human listening remains pending.');

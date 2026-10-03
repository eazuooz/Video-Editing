// Authored decisions after direct whole-scene and independent contextual review.
// Hash/completeness checks are evidence guards, not automated content approval.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/motion-sickness-games';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n','utf8');
const dir='shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v2';
const reportPath=`${dir}/motion-sickness-games-qwen3-1.7b-balanced-v2.asr-review.json`;
const report=read(reportPath),contextPath=`${base}/production/v2-end-context/asr.json`,context=read(contextPath);
if(!report.complete||report.sceneCount!==12||!context.complete||context.results.length!==4)throw Error('Incomplete ASR evidence');
const script=read(`${base}/script/narration.ko.json`),baseline=read(`${base}/production/repair1/baseline/script/narration.ko.json`);
let unchanged=0;for(const s of script.scenes){const b=baseline.scenes.find(v=>v.id===s.id);unchanged+=s.lines.filter((v,i)=>v===b.lines[i]).length;}
if(unchanged!==53)throw Error(`Original unchanged paragraph count ${unchanged}`);
const notes={
 '01':'All6 paragraphs present; 2022 and 이천이십이 are numerical normalization. Byte-identical v1 already independently reviewed.',
 '02':'All4 paragraphs and closing design question match. Byte-identical approved v1.',
 '03':'All6 paragraphs exact after replacement; source PCM before/after p4 remains byte-identical. Both seam-adjacent sentences and ending complete.',
 '04':'All4 paragraphs exact, including complete 조절값도 따로 둘 수 있죠 and 뜻밖에. Both replacements and all adjacent retained clauses read in full. Candidate04a ending heuristic false remains historical evidence; whole composite closing pass does not erase it.',
 '05':'All6 paragraphs and both p4 seams complete. Independent full-final-paragraph and short-tail ASRs contain only the requested final statement. Whole-ASR extra gratitude text consists of12 zero-duration words at55.70, after final 합니다55.34–55.62, in a55.72-second wave. This terminal ASR hallucination has no supported speech interval. Preserved original suffix and initial readback also exclude extra speech. 아니므로/아님으로 is transcription spelling of the connecting phrase; comparison limitation is retained.',
 '06':'All4 paragraphs including restored reset/recommended-value conclusion complete. 입력에/입력의 and 앞의/앞에 are /e/ transcription variants in retained PCM; role distinctions and disclaimer unchanged.',
 '07':'All6 paragraphs complete. Independent p3 context explicitly recognizes 읽지는 마세요; whole-scene 익 is Korean liaison transcription, not omitted instruction. 투/2 numeric normalization; connecting spelling 컷이므로/컷임으로 keeps the separate-cut prohibition. Replacement landmarks/direction and both seams complete.',
 '08':'All4 paragraphs exact, including explanation-only diagram disclaimer and immediate stop/reset. Byte-identical v1.',
 '09':'All6 paragraphs exact; actual tool/surface observation and no measurement of body state disclaimers retained. Byte-identical v1.',
 '10':'All4 paragraphs present including p2 replacement. Independent complete final paragraph confirms individual feedback and prohibition on tolerating discomfort; 다르므로/다름으로 transcription spelling does not alter it.',
 '11':'All6 paragraphs present, byte-identical approved v1. Prior independent context explicitly recognizes 에임 모드; whole-scene A is language normalization. Closing question complete.',
 '12':'All4 paragraphs including coaching-link ending complete. 의/에 normal /e/ realization; byte-identical v1.'
};
const proofPath=`${base}/production/repair2/v2-composite-proof.json`,proof=read(proofPath);
const scenes=script.scenes.map(s=>{
 const wav=`${dir}/chunks/${s.id}-scene.wav`,asrPath=`${dir}/asr/${s.id}.json`,asr=read(asrPath);
 const digest=sha(wav),r=report.scenes.find(v=>v.scene===s.id),p=proof.scenes.find(v=>v.scene===s.id);
 if(digest!==asr.audio_sha256||digest!==p.compositeSha256||r.audio_sha256!==digest)throw Error(`Stale wave ${s.id}`);
 return {id:s.id,wav,audioSha256:digest,approvedAsr:asrPath,asrSha256:sha(asrPath),
   expected:r.expected,recognized:r.recognized,differences:r.differences,acousticChecks:r.acousticChecks,
   paragraphs:s.lines.map((text,i)=>({paragraph:i+1,text,directlyCompared:true})),
   decision:'content-readback-pass',notes:notes[s.id],allParagraphsDirectlyCompared:true,
   allReplacementSeamsDirectlyCompared:true,humanListening:'pending'};
});
for(const r of context.results)if(sha(r.source)!==r.sourceSha256)throw Error('Stale context');
const approval={kind:'v2-composite-all12-current-hash-full-ASR-direct-review',status:'technical-content-readback-pass-human-listening-pending',
 reviewedAt:new Date().toISOString(),allCurrentScenesTechnicallyReviewed:true,sceneCount:12,paragraphCount:60,
 unchangedOriginalParagraphs:53,retainedOriginalPcmVerified:true,fullReport:reportPath,fullReportSha256:sha(reportPath),
 contextReport:contextPath,contextReportSha256:sha(contextPath),compositionProof:proofPath,
 scriptInputs:['ko','en'].map(l=>({path:`${base}/script/narration.${l}.json`,sha256:sha(`${base}/script/narration.${l}.json`)})),
 scenes,humanListening:'pending',sourceRights:'pending',finalRenderingApproved:false,
 timestampAlignmentExclusions:[{scene:'05',fromWordIndex:read(`${dir}/asr/05.json`).words.length-12,count:12,
  reason:'Unsupported zero-duration terminal ASR insertion; two independent context readbacks and byte-preserved original suffix exclude an audible appended greeting. Preserve raw ASR evidence.'}]};
write(`${base}/production/voice-approval.json`,approval);
proof.status='retained-PCM-verified-whole-current-hash-ASR-directly-reviewed';
for(const s of proof.scenes)s.wholeCompositeAsrReviewed=true;
proof.wholeReview=`${base}/production/voice-approval.json`;proof.humanListening='pending';write(proofPath,proof);
const queuePath='production/batches/sakurai-planning-game-design/queue.json',q=read(queuePath),item=q.items.find(x=>x.slug==='motion-sickness-games');
item.checkpoints.narration=true;item.stage='voice-reviewed-measured-source-cut-planning';
Object.assign(item.execution,{phase:'v2-voice-technically-reviewed-source-fit-next',status:'current12-scene60-paragraph-content-readback-pass',
 sessionId:null,pid:null,workerPid:null,alive:false,activeTasks:[],voiceApproval:`${base}/production/voice-approval.json`,
 updatedAt:approval.reviewedAt,nextAction:'Measure source/caption timeline, allocate fresh existing-game action without overlap, directly review all final cuts and fixed-bottom captions. Human full listening and final render/upload pending.'});
item.execution.mixedComposer.wholeSceneReviewComplete=true;
q.updatedAt=approval.reviewedAt;write(queuePath,q);
console.log(JSON.stringify({voice:'current12-scene-content-pass',paragraphs:60,unchanged:53,humanListening:'pending',finalRender:false}));

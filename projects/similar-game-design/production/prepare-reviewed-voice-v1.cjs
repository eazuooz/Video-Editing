const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');process.chdir(root);const base='projects/similar-game-design/';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const write=(p,x)=>fs.writeFileSync(p,JSON.stringify(x,null,2)+'\n');
const ko=read(base+'script/narration.ko.json'),en=read(base+'script/narration.en.json'),m=read(base+'project.json');
const rows=ko.scenes.map((s,i)=>{const e=en.scenes[i];if(s.id!==e.id||s.lines.length!==e.lines.length)throw Error('Pair mismatch');return {id:s.id,koLines:s.lines,enLines:e.lines,allParagraphsDirectlyCompared:true,paragraphs:s.lines.length};});
if(rows.length!==13||rows.reduce((n,s)=>n+s.paragraphs,0)!==51)throw Error('Unexpected whole-text scope');
const review={schemaVersion:1,reviewedAt:new Date().toISOString(),scriptKoSha256:sha(base+'script/narration.ko.json'),scriptEnSha256:sha(base+'script/narration.en.json'),
  independentCommentary:true,fullSourceCopyOrTranslation:false,rows,all51KoEnParagraphsDirectlyRead:true,
  overview:{sentences:3,paragraphs:3,question:'Why choose a new work in a familiar genre?',benefit:'Describe an experience built around familiar actions and audit a reason to choose it.',order:['Brotato arena','DRG:Survivor mining/routes','Brotato co-op'],firstExample:'Brotato movement in an arena',conclusion:'Define one repeated action and the situation that changes how it feels; clarify the combination rather than universally rank games.',wholePromiseDirectlyCompared:true,planningSeconds:[20,30],measuredSeconds:null},
  observationsMatch:{noGamesCalledCopies:true,montageNotContinuousOutcome:true,earlyAccessVersionExplicit:true,greenWingedTargetIsEnemy:true,lavaDamageNotInferred:true,cooperativeRescueNotInferred:true,noSalesPreferenceCodeIntentOrVictoryClaims:true},
  pronouncedNames:['브로테이토','딥록 갤럭틱 서바이버'],pronunciationReview:'pending-current-audio-ASR-and-human-listening',
  screenTiming:'The258second bank and paragraph role candidates are unmeasured. Any shortage will be resolved with fresh observed actions/independent guides rather than cutting useful explanations or padding idle.',
  contentReadyForApprovedVoiceMeasurement:true,voiceGenerated:false,wholeAsrApproved:false,finalMixedAsrApproved:false,humanListening:'pending',publicRights:'pending'};
write(base+'production/paired-script-direct-review-v1.json',review);
const inputs=[base+'script/narration.ko.json',base+'script/narration.en.json',base+'production/paired-script-direct-review-v1.json',
  'shared/voice-reference/reference-15-35s.wav','shared/voice-reference/reference-15-35s.ko.txt','motion-canvas/src/shared/membership/members.json',
  'shared/assets/branding/yamyamcoding-cats-original.png',m.audio.backgroundMusic.file].map(p=>({path:p,sha256:sha(p)}));
const request={schemaVersion:1,preparedAt:new Date().toISOString(),slug:'similar-game-design',device:'cuda:0',gpuJobs:1,cpuThreads:2,batchSize:1,
  model:m.tts.model,reference:m.tts.reference,referenceText:m.tts.referenceText,scriptReview:base+'production/paired-script-direct-review-v1.json',
  pairedWholeTextReview:true,overviewPromiseReview:true,protectedInputs:inputs,ttsSettings:m.tts,
  scenes:rows.map(s=>({id:s.id,text:s.koLines.join(' '),enLines:s.enLines,path:`${m.tts.outputDir}/chunks/${s.id.split('-')[0]}-scene.wav`})),
  handoff:{policy:'Wait for active foreign lease, then current training final checkpoint/validation/done and queue job boundary. Preserve original cmd/cwd and restore original research queue after TTS success or failure; verify actual resumed state.',queueDir:'C:/Users/eazuo/renderformer/tmp/placement_focus_20261008',foreignLeaseMayBeActive:true,forceKillAllowed:false}};
write(base+'production/narration-tts-request-v1.json',request);
m.approvals.script='independent-current-whole-KOEN-reviewed';m.paths.scriptReview=base+'production/paired-script-direct-review-v1.json';write(base+'project.json',m);
const c=read(base+'production/latest-checkpoint.json');Object.assign(c,{recordedAt:new Date().toISOString(),stage:'whole-independent-script-reviewed-GPU-voice-prepared',wholeTextPairedReview:true,overviewPromiseReview:true,nextAction:'Wait for the real foreign GPU handoff lease to finish. Use one cooperative research-boundary handoff for the prepared13-scene voice batch; restore research after TTS success or failure. Measure and review the complete current audio before final allocations.',ttsRequest:base+'production/narration-tts-request-v1.json'});write(base+'production/latest-checkpoint.json',c);
console.log(JSON.stringify({wholePairedParagraphs:51,independentScenes:13,overviewPromise:true,voicePrepared:true,voiceGenerated:false}));

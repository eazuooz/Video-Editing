// Prepare only this video's reviewed metadata and explicit delivery paths.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),batch='production/batches/sakurai-planning-game-design',proof=batch+'/proof-avoid-game-comparisons',project='projects/avoid-game-comparisons';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const now=new Date().toISOString(),bank=proof+'/source-research/source-action-bank-v4.json';
function refresh(c){
 c.updatedAt=now;
 if(c.sourceActionBank&&!c.sourceActionBankBeforeAdditiveVoice)c.sourceActionBankBeforeAdditiveVoice=c.sourceActionBank;
 c.sourceActionBank={path:bank,sha256:sha(bank),planningIntervals:98,planningUniqueSeconds:310.54745,projectAssignedIntervals:88,projectAssignedSeconds:300.24745,sourceAudioUsed:false,selfCreatedGames:0,measuredRatioApproved:false,finalCutAndCaptionApproval:false};
 if(c.independentPlan)c.independentPlan.candidateActualSeconds=300.24745;
 if(c.independentScript){c.independentScript.scenes=14;c.independentScript.paragraphs=56;c.independentScript.voiceAsrReviewed=true;c.independentScript.finalPixelsReviewed=false;}
 if(c.independentContextReadback){c.independentContextReadback.historicalPreRepairNarrationApproved=c.independentContextReadback.narrationApproved;c.independentContextReadback.status='original10-contexts-preserved-two-clarity-repairs-and-three-new-contexts-reviewed';c.independentContextReadback.narrationApproved=true;c.independentContextReadback.approvalScope='Current hash technical direct ASR review only; human pronunciation/listening and final mix pending.';}
 c.nextAction='Resolve measured14-scene paragraph/native action alignment and explanation roles, then current exact body60:40 and new white13/14 pixel review. Preserve all current PCM and completed sources. Final mix/captions/render/QA/output/private upload pending.';
 c.finalMixComplete=false;c.renderComplete=false;c.qaComplete=false;c.collected=false;c.privateUploadSaved=false;c.completedVideoDelivery=false;
 return c;
}
for(const p of [project+'/production/latest-checkpoint.json',proof+'/latest-checkpoint.json'])write(p,refresh(read(p)));
const q=read(batch+'/queue.json');
function visit(o){if(!o||typeof o!=='object')return;if(o.slug==='avoid-game-comparisons'&&o.sourceActionBank)refresh(o);for(const v of Object.values(o))if(v&&typeof v==='object')Array.isArray(v)?v.forEach(visit):visit(v);}
visit(q);write(batch+'/queue.json',q);
const direct=[
 'motion-canvas/src/projects/avoid-game-comparisons/production-plan.json',
 'motion-canvas/src/projects/avoid-game-comparisons/project.ts',
 'motion-canvas/src/projects/avoid-game-comparisons/scenes/concept-diagrams.tsx',
 'motion-canvas/src/projects/avoid-game-comparisons/scenes/mixed-additive-scene.tsx',
 'motion-canvas/src/projects/avoid-game-comparisons/scenes/scene13.tsx',
 'motion-canvas/src/projects/avoid-game-comparisons/scenes/scene14.tsx',
 'production/batches/private-review-expansion/README.md',batch+'/README.md',batch+'/queue.json',
 proof+'/latest-checkpoint.json',proof+'/repaired-source-evidence-git-verification.json',bank,
 project+'/README.md',project+'/planning/chapter-plan.json',project+'/planning/outline.md',
 project+'/project.json',project+'/rebuild.json',project+'/script/narration.en.json',project+'/script/narration.ko.json',
 project+'/sources/action-map.json',project+'/sources/game-candidates.json'
];
const production=[
 'independent-scene-design.json','latest-checkpoint.json','script-source-review.json',
 'action-map-v2-preserved.json','additive-context-asr-execution.json','additive-context-asr-session.json',
 'additive-context-readback-request.json','additive-mine-script-review.json','additive-narration-direct-review.json',
 'additive-narration-request.json','additive-narration-tts-execution.json','additive-narration-tts-session.json',
 'additive-whole-asr-execution.json','additive-whole-asr-session.json','chapter-plan-v2-preserved.json',
 'expanded-visual-role-plan.json','measure-reviewed-paragraphs.py','measured-paragraphs-expanded14.json',
 'measured-paragraphs-original12.json','narration-expanded-index.json','narration-script-en-v2.json',
 'narration-script-ko-v2.json','plan-additive-mine-narration.py','record-additive-voice-review.py',
 'render-additive-narration.py','review-additive-narration.py','save-expanded-voice-checkpoint.py',
 'script-source-review-v2.json','additive-context-asr-local/13-conditions.json',
 'additive-context-asr-local/13-end-join.json','additive-context-asr-local/14-result-and-join.json',
 'additive-whole-asr-local/13.json','additive-whole-asr-local/14.json'
];
const selected=[...direct,...production.map(p=>project+'/production/'+p),batch+'/prepare-expanded-voice-delivery.cjs',batch+'/deliver-expanded-voice-progress.cjs',batch+'/expanded-voice-delivery-paths.json',proof+'/expanded-voice-pre-delivery-checks.json'];
if(selected.length!==new Set(selected).size)throw Error('Duplicate explicit path');
write(batch+'/expanded-voice-delivery-paths.json',selected);
let runner=fs.readFileSync(path.join(root,batch+'/deliver-repaired-source-progress.cjs'),'utf8');
runner=runner.replaceAll('repaired-source-pre-delivery-checks','expanded-voice-pre-delivery-checks').replaceAll('repaired-source-delivery-paths','expanded-voice-delivery-paths').replaceAll("'.git','repaired-source-'","'.git','expanded-voice-'").replaceAll('repaired-source-git-verification','expanded-voice-git-verification').replaceAll('repairedSourceProgressCommit','expandedVoiceProgressCommit').replaceAll('current12SceneTechnicalAsrApproved','current14SceneTechnicalAsrApproved').replace('Review repaired game-pitch narration and unique official Mine action sources','Review additive game-pitch narration and mixed actual-action explanation scenes');
runner=runner.replace("node(['scripts/build-rebuild-manifests.cjs','avoid-game-comparisons','--check']);", "node(['scripts/build-rebuild-manifests.cjs','avoid-game-comparisons','--check']);node(['motion-canvas/node_modules/typescript/bin/tsc','-p','motion-canvas/tsconfig.avoid-game-comparisons.json','--pretty','false']);");
runner=runner.replace('current narration review are progress','current14 narration review and proposed mixed visual roles are progress');
fs.writeFileSync(path.join(root,batch+'/deliver-expanded-voice-progress.cjs'),runner);
console.log(JSON.stringify({explicitPaths:selected.length,current14Scenes:true,completedVideoDelivery:false,newImages:0}));

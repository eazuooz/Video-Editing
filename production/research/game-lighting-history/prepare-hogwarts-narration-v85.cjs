// Bind six inspected observation paragraphs without approving final cuts or quota.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const ref=p=>({path:p,sha256:sha(p)});
const write=(p,j)=>{const file=path.join(root,p);if(fs.existsSync(file))throw Error('Preserve existing '+p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(j,null,2)+'\n');};
const source='projects/game-lighting-history-04/script/physical-part3-hogwarts-observation.koen.v81.json';
const draft=read(source),originalRequest=read(base+'part3-guided-actions-tts-request-v69.json');
if(draft.scenes.length!==6||sha(source)!=='d6129a726f67e0bf150ff80a699b906524046e025104748135dbd1bb29f3643e')throw Error('Read changed paired paragraphs first');
for(const x of originalRequest.protectedInputs)if(sha(x.path)!==x.sha256)throw Error('Protected input changed '+x.path);
const sourceReview=base+'hogwarts-official-source-direct-review-v80.json';
if(!read(sourceReview).allEightBoardsDirectlyRead)throw Error('Native source boards required');
cp.execFileSync(process.execPath,['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json','--check'],{cwd:root,stdio:'inherit'});
const publicReview=base+'hogwarts-bounded-public-motion-review-v85.json';
write(publicReview,{schemaVersion:1,reviewedAt:new Date().toISOString(),source:ref(draft.scenes[0].sourcePath),nativeBoardReview:ref(sourceReview),publicUrl:'https://www.youtube.com/watch?v=OKOgcdvFIAg',publisher:'Harry Potter verified',uploadDate:'20221111',browserTab:'51',observations:[
 {sourceSeconds:1050.94472,rate:1,visible:'Player climbs stairs below bright windows; yellow robe and other figure upstairs.'},
 {sourceSeconds:1066.924456,rate:1,visible:'Courtyard arches and sky; robe and background figures remain distinguishable.'},
 {sourceSeconds:1101.883091,rate:1,visible:'Near stone balustrade, distant landscape and NPC at left; character/camera turn.'},
 {sourceSeconds:1119.851514,rate:1,visible:'Character turns beside flaming brazier; flame and stone floor are separate regions.'},
 {sourceSeconds:1176.498627,rate:1,visible:'Backlit character by bright stained glass, carved surround, original map and spell icons.'},
 {sourceSeconds:1214.193767,rate:1,visible:'Character crosses leafy courtyard; two background figures by arches and target figure at left.'},
 {sourceSeconds:1221.677921,rate:1,paused:true,visible:'Player approaches Nellie Oggspire under tree; Talk prompt above NPC, original minimap and spells visible.'}
 ],excluded:[{sourceSeconds:1204.956026,reason:'Presenter interview; do not assign to action footage.'},{sourceSeconds:1235.703995,reason:'Dialogue closeup outside the downloaded window.'},{sourceSeconds:1261.748811,reason:'Dialogue after window; do not use as evidence of a selected cut.'}],boundedNormalSpeedSamplesDirectlyRead:true,fullContinuousWindowReview:false,exactPublicToNativeOffsetApproved:false,sourcePhysicsOrDlssImplementationProved:false,finalAnnotationsReviewed:false,allFinalPixelsReviewed:false,sourceAudio:false,newGitImages:0});
const ko='projects/game-lighting-history-04/script/hogwarts-observation.ko.v85.json',en='projects/game-lighting-history-04/script/hogwarts-observation.en.v85.json';
write(ko,{title:'최종 화면의 비교 대상을 정하는 호그와트 관찰',scenes:draft.scenes.map(s=>({id:s.id,title:s.id,lines:[s.ko],screenRole:s.role}))});
write(en,{title:'Establishing a surface and camera reference in Hogwarts',scenes:draft.scenes.map(s=>({id:s.id,title:s.id,lines:[s.en],screenRole:s.role}))});
const review=base+'hogwarts-observation-script-review-v85.json';
write(review,{schemaVersion:1,reviewedAt:new Date().toISOString(),pairedSource:ref(source),ko:ref(ko),en:ref(en),nativeReview:ref(sourceReview),boundedPublicReview:ref(publicReview),allSixCompleteKoEnParagraphsDirectlyRead:true,meaningAndOrderMatched:true,comparison:'The six paragraphs establish clothing/window/stone/flame/camera/UI observation targets after the four-game appearance comparison. They identify the2022 preview and do not attribute an observed surface to DLSS5, ray tracing, physical units, quest success, or a measured exposure toggle. Original111/current37 and five framing PCM are unchanged.',insertAfter:'appearance-nba',insertBefore:'appearance-to-controls',finalCutsAwaitMeasuredNarration:true,finalSourceMovingPixelsReviewed:false,publicRightsApproved:false,ttsTextReviewApproved:true});
const originalManifest=read(originalRequest.manifestOverride),audio='shared/output/narration/game-lighting-history-04/qwen3-1.7b-hogwarts-observation-v85',stem='game-lighting-history-04-hogwarts-observation-v85';
const manifest={...originalManifest,paths:{...originalManifest.paths,script:ko,scriptEn:en,narration:audio+'/'+stem+'.wav',captionsKo:audio+'/'+stem+'.srt',captionsEn:audio+'/'+stem+'.en.srt'},tts:{...originalManifest.tts,outputDir:audio,filenameStem:stem,maxRenderAttempts:3,maxNewTokens:1536,maxNewTokensReason:'Six new complete source-observation paragraphs only; preserve all prior PCM and source files.'}};
const mf=base+'hogwarts-observation-manifest-v85.json',request=base+'hogwarts-observation-tts-request-v85.json';write(mf,manifest);
write(request,{schemaVersion:1,preparedAt:new Date().toISOString(),slug:'game-lighting-history-04',manifestOverride:mf,scriptReview:ref(review),protectedInputs:[...originalRequest.protectedInputs,ref(source),ref(sourceReview),ref(publicReview),ref(ko),ref(en),ref(review),ref(mf),ref(draft.scenes[0].sourcePath)],scenes:draft.scenes.map(s=>({id:s.id,path:audio+'/chunks/'+s.id+'-scene.wav'})),cpuThreads:2,gpuJobs:1,batchSize:1,thresholdChanged:false,originalPcmRegenerated:false,wholeAndIndependentAsrRequired:true,finalSourceUseApproved:false,ttsStarted:false});
console.log(JSON.stringify({request,paragraphs:6,ttsStarted:false,allFinalPixelsReviewed:false}));

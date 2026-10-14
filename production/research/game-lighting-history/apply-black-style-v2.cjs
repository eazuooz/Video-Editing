/* Explicit current-series palette revision. Never synthesizes or renders. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const rel = p => path.relative(root,p).replace(/\\/g,'/');
const write = (p,j) => {const t=p+'.tmp-'+process.pid;fs.writeFileSync(t,JSON.stringify(j,null,2)+'\n');fs.renameSync(t,p);};
const reference = 'C:/Users/eazuo/AppData/Local/Temp/codex-clipboard-85becf26-1c98-41e1-b2c2-b4ffd68392e3.png';
const recordPath = path.join(__dirname,'black-style-revision-v2.json');
if (fs.existsSync(recordPath)) throw Error('Revision already recorded; inspect current checkpoint instead of overwriting history.');
const now = new Date().toISOString();
const slugs=[1,2,3,4].map(n=>'game-lighting-history-0'+n);
const before=slugs.map(slug=>{
 const p=path.join(root,'projects',slug,'project.json'),m=read(p);
 return {slug,manifestSha256:sha(p),previousStyle:m.visualStyle,
   narration:{path:m.paths.narration,sha256:sha(path.join(root,m.paths.narration))},
   koScript:{path:m.paths.script,sha256:sha(path.join(root,m.paths.script))},
   enScript:{path:m.paths.scriptEn,sha256:sha(path.join(root,m.paths.scriptEn))}};
});
fs.mkdirSync(path.join(__dirname,'local'),{recursive:true});
const localRef=path.join(__dirname,'local/black-style-reference-v2.png');
fs.copyFileSync(reference,localRef);
const revision={schemaVersion:2,requestedAt:now,styleId:'research-black-v1',
 userEvidence:'피피티 배경검은색에 글시를 흰색으로 해서 이걸로해주고 영상 제작규칙에 추가해줘',
 scope:slugs,explicitExistingSeriesOverride:true,otherAlreadyStartedProjectsChanged:false,
 reference:{originalPath:reference,localPath:rel(localRef),sha256:sha(reference),
   titleVisible:'Arrows Inside a Determinant',directlyViewed:true,gitImageAdded:false},
 palette:{background:'#000000',body:'#f5f5f5',heading:'#e8cf83',secondary:'#b8b8b8',
   vectorX:'#ef8585',vectorY:'#a4c6a0',vectorZ:'#73c7c2',focal:'#f39a4b'},
 geometry:'projected top/front/side faces, spatial relationships, occlusion and narration-timed motion',
 captions:'boxed-white-forest-v1; fixed960,970 / MC0,430; separate from white explanation text',
 preserve:{generatedNarration:true,historicalWhiteRenders:true,actualFootageColors:true,
   brandingAndMembership:true,illustratedThumbnailStyle:true},
 currentBlackAnimatedPixelsReviewed:false,finalVideoProduced:false,uploaded:false,before};
const policyPath=path.join(root,'shared/publishing/explanation-style-policy.json');
const policy=read(policyPath);policy.explicitSeriesRevisions??=[];policy.explicitSeriesRevisions.push({
 recordedAt:now,styleId:revision.styleId,slugs,reference:revision.reference,
 userEvidence:revision.userEvidence,record:rel(recordPath),
 overrides:'Earlier already-started palette preservation only for these four episodes.'});
write(policyPath,policy);
for(const b of before){
 const p=path.join(root,'projects',b.slug,'project.json'),m=read(p);
 m.visualStyle='research-black-v1';m.editing.explanationGeometry=m.editing.explanationStyle;
 m.editing.explanationStyle='research-black-v1';m.editing.explanationStyleSource='motion-canvas/src/styles/research-dark.ts';
 m.editing.explanationStyleRevision=rel(recordPath);
 m.productionGates.currentDistinct=false;m.productionGates.allAnimated25dPixelsReviewed=false;
 m.productionGates.allEncodedPixelsReviewed=false;
 m.productionState.explanationPaletteRevision={record:rel(recordPath),requestedAt:now,
   explicitCurrentSeriesRevision:true,previousStyle:b.previousStyle,blackPixelsApproved:false};
 write(p,m);
 if(sha(path.join(root,m.paths.narration))!==b.narration.sha256||sha(path.join(root,m.paths.script))!==b.koScript.sha256||sha(path.join(root,m.paths.scriptEn))!==b.enScript.sha256)
  throw Error('Palette change altered narration/script bytes.');
}
const seriesPath=path.join(__dirname,'series-plan.json'),series=read(seriesPath);
series.visualStyle='research-black-v1';series.explanationStyleRevision=rel(recordPath);
series.episodes.forEach(e=>e.visualStyle='research-black-v1');series.updatedAt=now;write(seriesPath,series);
const checkpointPath=path.join(__dirname,'checkpoint.json'),checkpoint=read(checkpointPath);
checkpoint.updatedAt=now;checkpoint.explanationPaletteRevision={record:rel(recordPath),styleId:'research-black-v1',
 explicitCurrentSeriesRevision:true,blackAnimatedPixelsReviewed:false};
checkpoint.latestUserVideoRequest='영상계속 제작해줘 마무리 지어줘; 현재 시리즈 설명을 첨부 검정/흰색 기준으로 수정';
checkpoint.next='Review current voice/word timing, black projected explanations and concept-matched native footage; preserve generated WAVs and original research queue.';
write(checkpointPath,checkpoint);
// Keep the historical white module untouched; create the current dark variant.
const oldModels=path.join(root,'motion-canvas/src/projects/game-lighting-history-01/final/models.tsx');
let source=fs.readFileSync(oldModels,'utf8');
source=source.replace("{PAPER as P} from '../../../styles/research-paper'","{DARK as P} from '../../../styles/research-dark'")
 .replace("'../../../shared/depth-diagrams'","'../../game-lighting-history-shared/depth-space'");
const faces={'#e5eaf1':'#34454b','#7791b5':'#3d6675','#f3df9b':'#62583d','#acb6b0':'#374640',
 '#f3e7b6':'#5c573e','#d3e5d9':'#30463b','#e5a77a':'#805640','#a8b5c5':'#40515b',
 '#eef2f4':'#26343b','#aebbb7':'#35483f','#e1e5dc':'#4b5748','#bec9c6':'#3b4c46',
 '#81968d':'#2b3c33','#f5f3d7':'#636349','#dfe8df':'#3a493e','#aab4aa':'#68796f',
 '#a3afae':'#263b3e','#b3b9a5':'#414934','#9d6860':'#87554d','#d9e2ed':'#3a4d60',
 '#f1d4b6':'#80654e','#52704c':'#42653c','#b8c4a1':'#485c3b','#e9eff2':'#33444d',
 '#aebac4':'#425460','#a9c6e9':'#547a96','#91a4bf':'#42627d','#8098b5':'#3d607b',
 '#b8cce5':'#43647d','#c98246':'#ad793e','#8c9b9d':'#48595b','#71877b':'#394c41',
 '#b8ceb0':'#44673d','#9caab5':'#3f515c'};
source=source.replace(/#[0-9a-f]{6,8}/g,c=>(faces[c.slice(0,7)]??c.slice(0,7))+c.slice(7));
const newModels=path.join(root,'motion-canvas/src/projects/game-lighting-history-01/final/black-models-v2.tsx');
fs.writeFileSync(newModels,source);
const runtimePath=path.join(root,'motion-canvas/src/projects/game-lighting-history-01/final/runtime.tsx');
const oldRuntime=fs.readFileSync(runtimePath,'utf8');
fs.writeFileSync(runtimePath,oldRuntime.replace("{PAPER as P} from '../../../styles/research-paper'","{DARK as P} from '../../../styles/research-dark'")
 .replace("'../../../shared/depth-diagrams'","'../../game-lighting-history-shared/depth-space'")
 .replace("from './models'","from './black-models-v2'"));
revision.sourceRevision={historicalWhiteModels:{path:rel(oldModels),sha256:sha(oldModels)},
 blackModels:{path:rel(newModels),sha256:sha(newModels)},
 previousFinalRuntimeSha256:crypto.createHash('sha256').update(oldRuntime).digest('hex'),
 currentFinalRuntime:{path:rel(runtimePath),sha256:sha(runtimePath)}};
write(recordPath,revision);
console.log(JSON.stringify({styleId:revision.styleId,episodes:4,narrationAndScriptHashesPreserved:true,
 existingWhiteModelsPreserved:true,newRasterGitAdded:0,blackPixelsApproved:false}));

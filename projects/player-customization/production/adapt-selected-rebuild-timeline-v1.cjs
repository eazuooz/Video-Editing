// Usage: node projects/player-customization/production/adapt-selected-rebuild-timeline-v1.cjs
// Metadata only: expose the sealed current 16-scene/139-cut timeline to the shared rebuild reader.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/player-customization';
const planPath=base+'/production/final-v1/plan.json';
const adapterPath=base+'/production/final-v1/rebuild-timeline-v1.json';
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8'));
const planBytes=fs.readFileSync(path.join(root,planPath));
const plan=JSON.parse(planBytes),seal=read(base+'/production/final-v1/final-pixel-direct-review-v1.json');
const digest=crypto.createHash('sha256').update(planBytes).digest('hex');
if(digest!==seal.planSha256||!seal.allFinalPixelsReviewed)throw Error('The current final plan must match the actual pixel seal');
if(plan.sceneStarts.length!==16||plan.cuts.length!==139)throw Error('Unexpected selected timeline');
let cursor=120;
const scenes=plan.sceneStarts.map(s=>{
 if(s.startFrame!==cursor)throw Error('Scene gap or overlap '+s.id);
 const cuts=plan.cuts.filter(c=>c.scene===s.id);
 let cutCursor=s.startFrame;
 for(const c of cuts){if(c.outputStartFrame!==cutCursor||c.frames!==c.sourceOutFrame-c.sourceInFrame)throw Error('Cut timing differs '+s.id);cutCursor+=c.frames;}
 if(cutCursor!==s.endFrame)throw Error('Cuts do not cover '+s.id);
 cursor=s.endFrame;
 return {...s,durationFrames:s.endFrame-s.startFrame,cuts};
});
if(cursor+plan.membership.frames!==plan.finalFrames||plan.intro.frames!==120||plan.membership.frames!==600)throw Error('Original intro/outro timing differs');
const adapter={schemaVersion:1,slug:'player-customization',status:'selected-current-sealed-timeline-metadata',fps:60,sourcePlan:planPath,sourcePlanSha256:digest,finalPixelSeal:base+'/production/final-v1/final-pixel-direct-review-v1.json',note:'Cut objects retain the original input-stage flags. The separate current final pixel seal is authoritative for encoded review. This adapter changes no media, samples, source offsets or timing.',scenes,intro:{...plan.intro,startFrame:0,endFrame:120},membership:{...plan.membership,startFrame:cursor,endFrame:plan.finalFrames},measuredTotals:{actualFrames:plan.actualFrames,explanationFrames:plan.explanationFrames,bodyFrames:plan.bodyFrames,finalFrames:plan.finalFrames,bodyRatioErrorFrames:plan.body60_40ErrorFrames}};
fs.writeFileSync(path.join(root,adapterPath),JSON.stringify(adapter,null,2)+'\n');
const projectPath=base+'/project.json',project=read(projectPath);
project.paths.timeline=adapterPath;
fs.writeFileSync(path.join(root,projectPath),JSON.stringify(project,null,2)+'\n');
if(!fs.readFileSync(path.join(root,planPath)).equals(planBytes))throw Error('The source final plan changed concurrently');
console.log(JSON.stringify({metadataOnly:true,sceneCount:scenes.length,bodyCutCount:plan.cuts.length,mediaChanged:false,planSha256:digest}));

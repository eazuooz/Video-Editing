const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='production/research/game-lighting-history',project='projects/game-lighting-history-03';
const sha=x=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,x))).digest('hex');
const input=base+'/local/native-action-support-v15-lumen-action-gaps/execution.json',a=JSON.parse(fs.readFileSync(path.join(root,input),'utf8'));
const out=project+'/production/native-lumen-action-gap-direct-review-v15.json';
if(fs.existsSync(path.join(root,out)))throw Error('Preserve completed review');
if(a.status!=='action-sequences-ready')throw Error('Completed extraction required');
const notes=[
 '181–182 lit opening with selected rock;183–186 outlined large rock moves over the opening and changes its shading;187–189 closer nearly unchanged view. Geometry edit is visible; controlled latency is not measured.',
 '190 rock moves away and opening returns;191–192 camera reframes;193–198 prolonged opening-view hold. Do not fill actual-footage time with the hold.',
 '199–202 same opening view remains; exclude prolonged static tail.',
 '284 Show/Visualize menu has GlobalDistanceField checked;285 gray transition;286 lit world with editor icons;287 Show menu;288 LumenScene highlight;289–292 coarser world appearance. Highlight alone is not proof of a selected cache mode.',
 '293–298 nearly identical coarse lit world;299 small camera change;300 camera shift;301 returns to another framing. Exclude293–298 hold.',
 '302–303 differently rendered/material-lit rocky view;304 coarse world/icons return;305–308 prolonged nearly identical view;309 moves away;310 camera turns toward dark passage. This is world-view/result context, not SurfaceCache capture proof.',
 '311–314 active camera movement into dark rocky space with editor light/actor icons. No cache-coverage or update-time measurement is displayed.',
 '336–338 camera traverses lit opening toward darker arch;339–341 passage changes;342–344 camera looks up at ornate stonework and lit opening.',
 '345 nearly unchanged;346 moves toward arch;347 passes dark near occluder;348–349 emerge/reframe;350–353 prolonged far-wall hold. Stop traversal candidate at350.',
 '354 far-wall hold continues; exclude tail.',
 '529–531 nearly fixed warm rocky exterior;532–537 transform gizmo appears, with no substantial geometry or light change visible. Exclude long hold.',
 '538–546 same warm exterior and selected transform gizmo; exclude entire prolonged hold.',
 '547–553 same selected exterior;554 slight camera reframe only. The final small movement does not justify using the preceding25-second hold.',
 '602–608 near-static orange-lit cave wall;609–610 small camera movement. Exclude602–608 hold.',
 '611–613 nearly identical cave wall;614 save dialog;615–617 title slide;618–619 presenter panel. Save/title/presenters do not qualify as actual action examples.',
 '620–624 presenter panel continues; exclude.'
];
let i=0;const reviewed=a.completed.map(r=>({...r,boards:r.boards.map(b=>{
 if(sha(b.path)!==b.sha256)throw Error('Changed board');for(const s of b.samples)if(sha(s.path)!==s.sha256)throw Error('Changed sample');
 return {...b,directlyViewed:true,note:notes[i++]};
})}));if(i!==16||i!==notes.length)throw Error('Direct count mismatch');
const record={schemaVersion:1,reviewedAt:new Date().toISOString(),input:{path:input,sha256:sha(input)},reviewed,
 boardCount:16,temporalSampleCount:121,allBoardsDirectlyViewed:true,allTemporalSamplesDirectlyViewed:true,
 candidateRanges:[{source:'lumen-content-examples-2021',ranges:[[181,187],[190,193],[299,305],[309,315],[336,345],[346,350],[609,611]],role:'Unique geometry edit and separate camera/world-result context. Provisional exact boundaries; no SurfaceCache or controlled latency claim.'}],
 excludedRanges:[{source:'lumen-content-examples-2021',ranges:[[193,203],[293,299],[305,309],[350,355],[529,554],[602,609],[611,625]],reason:'Prolonged holds, save UI, slides or presenters; never actual-footage quota.'}],
 sourceCrop:'crop=1280:720:0:20',surfaceCacheObserved:false,menuSelectionContinuousReviewPending:true,
 fullContinuousMotionReviewed:false,finalUseApproved:false,allFinalCaptionPixelsReviewed:false,rightsApproved:false,sourceAudioUsed:false,newGitRasterCount:0,localOnly:true};
fs.writeFileSync(path.join(root,out),JSON.stringify(record,null,2)+'\n');
const cp=path.join(root,base,'checkpoint.json'),c=JSON.parse(fs.readFileSync(cp,'utf8'));c.updatedAt=new Date().toISOString();
c.episode03LumenActionGapReview={path:out,sha256:sha(out),boards:16,temporalSamples:121,allBoardsDirectlyViewed:true,fullContinuousMotionReviewed:false,finalUseApproved:false};
fs.writeFileSync(cp,JSON.stringify(c,null,2)+'\n');
console.log(JSON.stringify({review:out,boards:16,samples:121,originalPcmChanged:false,finalUseApproved:false}));

const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const rel='projects/game-lighting-history-04/production/native-process-review-v4.json';
if(fs.existsSync(path.join(root,rel)))throw Error('Preserve the completed direct observation record');
const executionPath='production/research/game-lighting-history/local/episode04-process-v3/execution.json';
const execution=read(executionPath);
if(execution.status!=='all-window-samples-ready'||execution.current||execution.completed.length!==8)throw Error('Extraction is not complete');
for(const source of Object.values(execution.sources))if(hash(source.file)!==source.sha256)throw Error('Original source changed');
const observations={
 'hair-debug':{boards:4,visible:'Groom preview and UV/attribute visualizations; intervening Geometry Parameters slide around598–606; returns to moving world character.',candidates:[[562,596],[609,626]],reject:[[598,606]],focus:'Name the strand attribute/debug display before interpreting its colors.'},
 'hair-material':{boards:6,visible:'World fur close-up, Hair Attributes/material graph, then material instance controls with visible fur color changes; Skinning slide around842.',candidates:[[650,678],[692,715],[770,800],[808,838]],reject:[[842,860]],focus:'Separate editable strand material appearance from a proof of transparency algorithm or performance.'},
 'hair-physics':{boards:4,visible:'Simulation slide around1012–1024; guide visualization, Niagara solver and bend/stretch settings afterward.',candidates:[[1034,1057],[1058,1084],[1130,1139]],reject:[[1012,1024]],focus:'Guide/solver controls describe deformation; they do not establish a light-transport result.'},
 'hair-lod':{boards:8,visible:'LOD method slides around1390–1398; rabbit groom LOD controls, Cards selection and card-like artifacts, material/texture preview; later full-screen play.',candidates:[[1411,1458],[1482,1539],[1580,1619],[1621,1645],[1744,1765]],reject:[[1390,1398]],focus:'Record the visible representation and LOD field. Do not infer an assigned card mesh from a Cards dropdown with None fields.'},
 'post-exposure':{boards:6,visible:'Desktop at1380; Auto-Exposure scene; camera and min/max brightness/exposure-bias controls; HDR histogram visualization; desktop again1720.',candidates:[[1570,1618],[1621,1715]],reject:[[1380,1388],[1720,1728]],focus:'Track lighting scene, post-process volume controls and histogram separately. Exposure-bias values are source settings, not our measured pixel intensity.'},
 'post-bloom-film':{boards:5,visible:'Bloom controls then a browser outline at1759–1767; color-grading/tonemapper controls and resulting colored scene; desktop around1919; LUT preview after1927.',candidates:[[1735,1755],[1783,1853],[1855,1911],[1927,1969]],reject:[[1759,1768],[1918,1925]],focus:'Only actual editor changes belong to action footage. The tone curve is different from direct or indirect lighting.'},
 'post-dof-before':{boards:5,visible:'Desktop around2058 and documentation pages around2082–2114/2178–2250; actual editor around2122–2170 shows blurred distant cubes and a sharp near cube.',candidates:[[2122,2174]],reject:[[2058,2063],[2082,2118],[2178,2252]],focus:'This interval mainly establishes the initial depth/focus state; controls that do not change are not a full before/action/after example.'},
 'post-dof-after':{boards:5,visible:'Depth-of-field layer debug colors, focal-distance change250→about1259, visualization toggle and blurred foreground; documentation around2417–2461; returns to real editor2465 onward.',candidates:[[2325,2411],[2465,2538]],reject:[[2416,2461]],focus:'Use the debug legend blue far/green near/black focus. A changed focus setting must be connected to the same visible cube arrangement.'},
};
// Board labels are exploratory sample times. tile output and output -t allowed
// overshoot in the original extraction; a later code fix does not repair them.
const reviewed=execution.completed.map(window=>{
 const note=observations[window.id];
 if(!note||window.boards.length!==note.boards||window.actualExit!==0)throw Error('Unexpected recorded window');
 const boards=window.boards.map(b=>{if(hash(b.path)!==b.sha256)throw Error('Board changed after direct read');return {...b,directlyRead:true};});
 return {...window,boards,directRead:note,allBoardsDirectlyRead:true,exactBoundedCutApproved:false};
});
if(reviewed.reduce((n,w)=>n+w.boards.length,0)!==43)throw Error('Expected43 reviewed boards');
const now=new Date().toISOString();
const record={schemaVersion:1,reviewedAt:now,scope:'Direct exploratory source/process review; does not approve final encoded pixels or bounded source cuts.',execution:{path:executionPath,sha256:hash(executionPath),actualExit:0,session:4507,sessionClosedObserved:true,status:execution.status,parentPid:execution.parentPid,completedAt:execution.completedAt},windows:reviewed,
 all43BoardsDirectlyRead:true,allFinalMotionApproved:false,
 samplingLimitations:{labels:'Relative fps sample times plus source start, approximate; exact cut frames require original playback.',overshoot:true,examples:['hair-debug board004 includes638–650 beyond nominal635','hair-material board006 includes842–860 beyond835','hair-lod includes1766 beyond1755'],futureProducerFix:'Input trim and setpts precede fps/tile; existing43 boards were not regenerated.',allSamplesWithinRequestedWindows:false},
 additionalDirectPlayback:[
  {source:'strand-hair-editor-ue426-2021',requestedLocalRange:[1400,1558],speed:1,muted:true,observed:[{time:1473.876,visible:'Rabbit groom editor; LOD0/LOD1 both Strands with changed decimation parameters.'},{time:1558.190,visible:'Cards tab, imported/procedural mesh None fields; clumped card-like rabbit appearance.'}],fullMotionApproved:false},
  {source:'strand-hair-editor-ue426-2021',requestedLocalRange:[808,837],speed:1,muted:true,observed:[{time:816.620,visible:'Mongoose fur and MelaninMainColor material-instance controls.'},{time:837.209,visible:'MelaninMainColor0.842857, secondary0.3, redness0.4, roughness0.25; darkened fur at the observed end.'}],fullMotionApproved:false},
  {source:'epic-postprocess-2017',requestedLocalRange:[1570,1618],speed:1,muted:true,observed:[{time:1618.132,visible:'Auto-Exposure scene, MinBrightness0.03/MaxBrightness2.0 and ExposureBias-1.0.'}],fullMotionApproved:false},
  {source:'epic-postprocess-2017',requestedLocalRange:[2140,2174],speed:1,muted:true,observed:[{time:2140,visible:'Sharp near cube and blurred farther cubes; the settings panel is scrolling.'},{time:2174.002,visible:'BokehDOF, FocalDistance250, FocalRegion917.431213, Scale0.2. Initial state chiefly holds.'}],fullMotionApproved:false}
 ],
 rights:{checkedAt:now,epicPrimary:'https://legal.epicgames.com/epicgames/fan-art-policy',epicScope:'Policy1.4 has an individual-ad-monetized-web-video exception;1.3 preserves third-party rights;1.10 requires the non-endorsement disclaimer. This does not grant blanket third-party model or source-music permission.',nvidiaPrimary:'https://www.nvidia.com/en-eu/about-nvidia/terms-of-service/',nvidiaScope:'Website materials personal/non-commercial unless accompanying license differs. An official technology link does not itself establish video redistribution permission.',publicRightsApproved:false,sourceMusicUsed:false},
 original87ParagraphsPreserved:true,newTtsProduced:false,newFinalRenderProduced:false,newRasterAddedToGit:0,allFinalUseApproved:false,next:'Finish exact source playback/crops and recent-use comparison, then independent source-specific guides and current distinct before cooperative TTS.'};
fs.writeFileSync(path.join(root,rel),JSON.stringify(record,null,2)+'\n');
const candidatesPath='projects/game-lighting-history-04/sources/game-candidates.json',candidates=read(candidatesPath);
if(candidates.candidates.some(c=>c.id==='epic-post-processing-2017'))throw Error('Preserve prior post-process candidate');
candidates.candidates.push({id:'epic-post-processing-2017',url:'https://www.youtube.com/watch?v=DFT7hFz_DpE',title:'Post Processing in UE4 | Live Training | Unreal Engine',publisher:'Unreal Engine',historicalDate:'2017-07-06 broadcast;2017-07-11 upload',engineScope:'UE4.16.2 actual exposure/color-grading/depth-of-field editor process; not a current-engine benchmark.',localFile:execution.sources.post.file,sha256:execution.sources.post.sha256,chapters:['22p','22rb'],viewerFocus:'Follow the same cube arrangement from post-process parameter change to the visible result.',diagramConnection:'Retained exposure→tone-curve→display and distinct near/focus/far planes.',insertionPoint:'Between22p retained paragraphs, with a causal result reference in22rb.',candidateRanges:reviewed.filter(w=>w.source==='post').flatMap(w=>w.directRead.candidates),nativeAcquired:true,allSampleBoardsDirectlyRead:true,fullMotionReviewed:false,rightsApproved:false,recentUseCheckPassed:false,finalUseApproved:false,evidence:rel});
for(const candidate of candidates.candidates){
 const source=(read('projects/game-lighting-history-04/production/native-direct-progress-v3.json').sources||[]).find(s=>s.id===candidate.id);
 if(source){candidate.currentAcquisitionEvidence={record:'projects/game-lighting-history-04/production/native-direct-progress-v3.json',media:source.media,sha256:source.sha256};candidate.nativeAcquired=true;}
}
candidates.candidateReview.currentProcessReview={record:rel,reviewedAt:now,all43BoardsDirectlyRead:true,allFinalUseApproved:false};
fs.writeFileSync(path.join(root,candidatesPath),JSON.stringify(candidates,null,2)+'\n');
const cpPath='production/research/game-lighting-history/checkpoint.json',cp=read(cpPath);
cp.updatedAt=now;cp.episode04ProcessDirectReview=rel;cp.ownedJobsRunning=[];cp.ownedGpuJobs=0;cp.nextAction=record.next;
fs.writeFileSync(path.join(root,cpPath),JSON.stringify(cp,null,2)+'\n');
console.log(JSON.stringify({record:rel,reviewedBoards:43,extractionComplete:true,newTtsProduced:false,allFinalUseApproved:false}));

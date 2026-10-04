const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../../..'),base=path.join(root,'production/batches/sakurai-planning-game-design/proof-game-reward-planning/source-research');
const read=p=>JSON.parse(fs.readFileSync(path.join(base,p),'utf8')),write=(p,x)=>fs.writeFileSync(path.join(base,p),JSON.stringify(x,null,2)+'\n');
if(fs.existsSync(path.join(base,'action-bank-v14.json')))throw Error('Preserve existing source-fit inspection.');
const index=read('frames/native-bank-v13/index.json');if(index.frameCount!==80||index.uniqueFrameCount!==70||index.sheets.length!==4)throw Error('Unexpected inspected evidence.');
write('direct-source-fit-review-v13.json',{reviewedAt:new Date().toISOString(),all4SheetsDirectlyRead:true,frameRoles:80,uniqueFrames:70,sourceId:'ZTV0rPQ0_ik',v12:{validInspection:false,reason:'Four requests but missing source metadata produced zero frames. Preserved; not treated as a content pass.'},observations:[
 {from:99,to:104.5,visible:'Dark forest combat and a subsequent snowy/watery combat shot with players, targets, projectiles and circular effects.',decision:'Candidate only; verify exact transition before the real office shot at105.'},
 {from:105,to:107,visible:'Real office/developer/presenter/monitors.',decision:'Exclude from game quota and this independent commentary.'},
 {from:107.5,to:116,visible:'Save/new-game and numerical difficulty/custom settings.',decision:'Exclude from actual quota; no current narration about difficulty settings.'},
 {from:116.5,to:120.5,visible:'Office/keyboard/programmer and AMANDA END Engineer presenter.',decision:'Exclude from this game example.'},
 {from:121,to:122.5,visible:'Dark forest combat, moving wizard and target.',decision:'Candidate only; tighten both real-presenter and base-shot boundaries.'},
 {from:123,to:126,visible:'Player movement at FIRE RESEARCH STATION, LIGHTNING FURNACE, EVAPORATOR; interaction/inventory near workstations.',decision:'Potential production-function comparison only; no inferred unlock, costs or obtained reward.'},
 {from:126.5,to:128,visible:'A different base GENERAL LIBRARY and player movement.',decision:'Hold unless independently connected to an existing claim.'},
 {from:128.5,to:131,visible:'Library grid then Welcome To The Tower text page.',decision:'Exclude from actual quota for this commentary.'}
],finalCaptionApproval:false,finalRatioApproval:false});
const source=read('action-bank-v13.json').sources;
const windows=[['coop-fit-combat-01',99,104.83333333333333,'Moving players, enemy targets and projectiles in distinct forest and snowy combat cuts.'],['coop-fit-combat-02',120.83333333333333,122.83333333333333,'Moving wizard and target in dark forest combat; confirm adjacent office/base boundaries.'],['coop-fit-base-01',122.83333333333333,126.33333333333333,'Workstation names and player movement/interaction in the base; functional contrast only.']];
write('action-bank-v14.json',{schemaVersion:1,status:'tight-positive-action-candidates-awaiting-direct-native-boundaries',createdAt:new Date().toISOString(),sources:source,cuts:windows.map(([id,a,z,visibleAction])=>({id,sourceId:'ZTV0rPQ0_ik',sourceInSeconds:a,sourceOutSeconds:z,durationSeconds:z-a,visibleAction,classification:'unreviewed-candidate',speed:1,sourceAudio:'exclude-all',finalApproved:false})),finalApproval:false});
console.log('Recorded all80 v13 roles; three tighter actual-action candidates require exact native review.');

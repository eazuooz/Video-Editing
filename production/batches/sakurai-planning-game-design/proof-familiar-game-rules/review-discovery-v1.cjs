const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),stamp=new Date().toISOString();
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const write=(p,d)=>fs.writeFileSync(path.join(root,p),JSON.stringify(d,null,2)+'\n');
const base=path.relative(root,__dirname).replaceAll('\\','/');
const notes={
 '7kJo0miz08g':{decision:'native-action-review-required',observed:'Nominal 0–35s cinematic poker/hallway; 40–70s first-person movement, kick, door and shooting montage; 75s title and 80s cinematic. Exclude all cinematic/title material. Exact in/out pending.',claims:'No observed current key binding, learning-speed result, or remapping UI.'},
 'zdqK0zC53CE':{decision:'native-action-review-required',observed:'Platform movement, umbrella in air, lifts and shooting/combat. Nominal 10s dialogue and 55–60s title excluded; independently verify action and umbrella results, not a still-frame inference.',claims:'Historical pre-release showcase; no current control/device claims.'},
 'BW0uTZ6-dsM':{decision:'native-action-and-cross-source-repeat-review-required',observed:'Nominal 20–40s platform/train movement and combat, 55s boss. Nominal 0–15s conversation/cinematic, 45s repair menu, 50s NPC dialogue, 60–65s dialogue and 70s title excluded. Compare overlapping Gunbrella shots before adopting unique segments.',claims:'No claim that a menu selection proves action effects or current keys.'},
 'm2CN7zy2nA4':{decision:'rejected-for-final-footage',observed:'All 51 coarse frames inspected. Presenter overlay at bottom left, large banana streamer graphic top right and publisher/HUD graphics at bottom right persist throughout gameplay. Variable wide letterboxing makes a consistent crop preserve neither action nor HUD. Presenter, repeated tutorial dialogue/idle, race, restart and black pause excluded.',claims:'Historical 2016 build prompts are research only, not current input mappings. Retain downloaded original/SHA/decode evidence locally; acquire clean official Pedro footage instead.'}
};
const boards=read(base+'/discovery-boards-v1.json');
if(boards.boardCount!==18||boards.frameCount!==96)throw Error('Unexpected discovery manifest');
for(const b of boards.boards){b.directlyRead=true;b.reviewedAt=stamp;b.notes=notes[path.basename(b.board).slice(0,11)].observed;}
boards.allDiscoveryBoardsDirectlyRead=true;boards.reviewedAt=stamp;boards.directActionReview=false;boards.actualCutApproval=false;
write(base+'/discovery-boards-v1.json',boards);
const sources=read('projects/familiar-game-rules/sources/game-candidates.json');
const decoded=read(base+'/decode-execution-v1.json');
for(const c of sources.candidates){const actual=decoded.results.find(x=>x.videoId===c.videoId);Object.assign(c,{actualDownload:actual,discoveryReview:notes[c.videoId],cutSelected:false,sourceIn:null,sourceOut:null});}
sources.stage='discovery-read-clean-pedro-replacement-native-review-pending';sources.reviewedAt=stamp;sources.allFourSourceFullDecode=true;sources.all96DiscoveryFramesDirectlyRead=true;sources.actualCutApproval=false;
sources.rejected.push({game:'My Friend Pedro',sourceId:'m2CN7zy2nA4',reason:notes.m2CN7zy2nA4.observed,localOriginalPreserved:true,replacement:'Clean publisher-owned Full Throttle Trailer YIVtT7SJrMM; acquisition/native review pending.'});
write('projects/familiar-game-rules/sources/game-candidates.json',sources);
write(base+'/discovery-direct-review-v1.json',{schemaVersion:1,slug:'familiar-game-rules',reviewedAt:stamp,all18BoardsAnd96FramesDirectlyRead:true,notes,exactNativeIntervalsApproved:false,independentNarrationCreated:false,sourceAudioForFinal:'exclude-all',imagesGitPolicy:'local-only'});
console.log(JSON.stringify({boards:18,frames:96,directlyRead:true,finalPedroStreamRejected:true,exactCutsApproved:false}));

// Records the direct visual review; extracted frames alone are never cut approval.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const here=__dirname,root=path.resolve(here,'../../../../..');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const state=JSON.parse(fs.readFileSync(path.join(here,'native-review-v1.json'),'utf8'));
if(state.status!=='native-samples-extracted-awaiting-direct-review')throw Error('Native extraction incomplete');
const observations={
 wl7MCdFifH8:{
  observed:['5–7 close sword strikes;7.5–14 movement/fighting beside green wall spray in the narrow corridor.','20–29 blue chain lightning on stairs/floor-trap route;35–41 purple staff fighting.','49–51 elevated Priestess view,51.5–62 a different higher wide view of the fortified battle area.','69–75 close sword action;82–88 wide Knight combat and88.5 another close view.'],
  boundaries:['Native scene candidates at72.033/74.733 seconds are attack flashes, not necessarily camera edits.','The detector missed view changes visible between41/41.5,42/42.5,51/51.5 and88/88.5 seconds. Exact native frame inspection is required before assigning continuous clips.'],
  limitations:['Do not join separately edited shots as one uninterrupted player action.','Equipment/guardian titles, internal code reuse, standard damage values and player enjoyment are not established by these frames.'],
  next:'Inspect only the missed internal boundaries; keep the completed104 action samples and15 triplets.'
 },
 MXxOg1xuWcI:{
  observed:['420–425 Acid Sprayer preview and wall row placement;425.5–426 red invalid preview;433–434.5 crossbow/staff combat.','571–577 advancing orc group and shots on the bridge;579–587 stairs/corridor combat near wall spray;587.5–602 bridge lightning/combat;604–607 wall-spray fight.','619.5–621 spike-floor placement;622–632 nearby large green enemy, installed floor row and rotating Spring Trap previews;633–639 staff combat.','833–835 fighting;835.5–837 Spike Trap placement,837.5–838.5 Spring Trap rotation,839–840.5 Floor Scorcher preview/placement;842.5–852 combat, with Ogre explicitly visible in the HUD at847.5.','1061.5 spike placement;1063.5–1064 blocked Floor Scorcher preview;1064.5–1068.5 wall-spray placement;1069–1076 rotated Barricade preview/placement/blocked state;1077–1085 rotated Floor Scorcher placements;1087–1089 spike preview/placement/blocked state.'],
  boundaries:['Menu→game is native16948 (564.933333 seconds); candidate565 begins after it.','433.8/581.033/590.733/605.5/629.333/839.733/845.533 candidates show attack flashes, placement or preview changes rather than observed edit cuts. All18 before/at/after triplets were directly read.'],
  excluded:['427–432 empty traversal,565–570 pre-wave traversal,852.5–855 empty stairs, other idle/menus are held rather than counted as filler.'],
  limitations:['Nightmare2014 recording is historical/difficulty-specific.','Observed currency drops or blocked previews do not establish universal trap costs, optimal balance or internal sequel production reuse.','Native UI/caption crop and exact chosen action start/end are still pending.'],
  next:'Select bounded placement/combat candidates and verify underlying framing at fixed bottom-center captions.'
 },
 kzZI_mbp0HY:{
  observed:['Local432–447 (original1272–1287): Ready Up Wave1, blue spectral routes, floor/spike preview and installation with changing currency.','Local454.5–461 (original1294.5–1301): more floor/spike placement and Sell Trap prompts.','Local466.5–472 (original1306.5–1312): placement of three hanging objects and currency changes5000→3800→2600→1400.','Local482–485 (original1322–1325): looking at hanging objects, another placement leaving200 and Sell Trap prompt.'],
  boundaries:['All58 detector/window-edge before/at/after triplets were directly read. The reviewed changes are placement flashes/camera movement; no hard edit was observed within those triplets.','The last three boards show continuous turns/jumps over the installed floor rows, still Ready Up, and native29100 at485 seconds still looking at a hanging object.'],
  excluded:['Local448–454 and472.5–481.5 empty traversal/looking are held. Blue spectral route markers are not invading enemies.','No trap activation, cannon firing, enemy battle or victory is established in this acquired840–1440 section.'],
  limitations:['Presenter face at lower right requires a separately verified crop.','Do not guess the hanging trap name, universal costs, sell action from a prompt alone, or current release/patch behaviour.'],
  next:'Use only meaningful setup if needed and review the separately acquired nonoverlapping1440–1800 combat section.'
 }
};
const sources=state.sources.map(s=>{
 const boards=[...s.actionSheets,...s.boundarySheets];
 for(const b of boards)if(sha(b.path)!==b.sha256)throw Error('Board changed '+b.path);
 return{videoId:s.videoId,source:s.source,sourceSha256:s.sourceSha256,sourceOffsetSeconds:s.sourceOffsetSeconds,nativeFrameRate:s.nativeFrameRate,decodeScope:s.decodeScope,candidateWindowsSeconds:s.candidateWindowsSeconds,actionSamples:s.actionSamples,boundarySamples:s.boundarySamples,candidateBoundaryFrames:s.candidateBoundaryFrames,contactSheets:boards.map(b=>({...b,directlyRead:true,localOnly:true})),...observations[s.videoId],allActionAndBoundaryTilesDirectlyRead:true,wholeHumanViewing:false,exactSelectedIntervalsApproved:false,finalCaptionPixelsApproved:false};
});
const record={schemaVersion:1,slug:'making-game-sequels',reviewedAt:new Date().toISOString(),method:'Directly read all50 native contact sheets:478 action samples and91 before/at/after boundary triplets. Scene scores are candidates only. Preserve missed cuts and false detector boundaries.',worker:{pid:state.pid,sessionId:state.sessionId,exitCode:0,endedAt:state.endedAt},nativeStateSha256:sha(path.relative(root,path.join(here,'native-review-v1.json')).replaceAll('\\','/')),sources,sourceCount:3,totalActionSamples:478,totalBoundaryTriplets:91,totalContactSheets:50,approvedIntervals:[],approvedActualSeconds:0,sourceAudioUsed:false,selfCreatedGames:0,loops:0,slowdown:0,newGitImages:0,finalCutApproval:false,nextAction:'Resolve missed OMD3 exact native boundaries, inspect additional Deathtrap combat, then select concept-matched intervals and verify fixed-caption framing before independent narration.'};
fs.writeFileSync(path.join(here,'direct-native-review-v1.json'),JSON.stringify(record,null,2)+'\n');
console.log(JSON.stringify({directlyRead:true,actionSamples:478,boundaryTriplets:91,boards:50,finalCutApproved:false,newGitImages:0}));

const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/game-writing';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const queue=read('production/batches/sakurai-planning-game-design/queue.json'),item=queue.items.find(i=>i.slug==='game-writing');
const records=item.sourceDownloads.map(r=>{const meta=read(r.path.replace(/\.mp4$/,'.info.json'));return{...r,title:meta.title,channel:meta.channel,channelId:meta.channel_id,uploadDate:meta.upload_date,durationSeconds:meta.duration,width:1920,height:1080,fps:30,originalInfoJsonLocalOnly:true,originalAudioUse:false};});
write(`${base}/sources/source-files.json`,{reviewedAt:new Date().toISOString(),files:records});
const recent=['Super Meat Boy','Hollow Knight','Portal','Into the Breach','Noita','FTL','A Short Hike','Spiritfarer','Mega Man 11','Monster Hunter Rise','Street Fighter 6','Guilty Gear Strive','Nintendo Switch Sports','Ring Fit Adventure','Hi-Fi Rush','Aperture Desk Job','Half-Life: Alyx','Oxygen Not Included'];
const history={searchedPaths:['projects/*/sources','projects/*/project.json','projects/*/production/final-v2/plan.json','projects/*/production/final-v3/plan.json','shared/assets'],matchingHistoryForDOS2:[],recentUsedFamilies:recent,method:'Full project JSON/Markdown text search and current five original/expanded project sources; active final scripts included. No DOS2/BG3 prior match found.',allSourceSegmentsNew:true};
write(`${base}/sources/game-candidates.json`,{
 generatedAt:new Date().toISOString(),topic:'Narrative facts, conditional dialogue, current item owner and branch convergence',history,
 selected:[
  {game:'Divinity: Original Sin 2',sourceIds:records.map(r=>r.sourceVideoId),priorUse:false,reason:'Fresh official visible character dialogue, actionable choice/vignette editing and item creation fit the chapter.',visibleActions:['character addressed by name','different displayed answers','question/choice editing','rename/create inventory item'],limitations:'GM is a human-directed authoring mode; footage does not prove automatic narrative-condition implementation.',rights:{urls:['https://larian.com/fan-content-policy','https://larian.com/support/faqs/intellectual-property-ip-usage-by-content-creators-for-streaming-recording-and-original-content_67'],status:'policy-reviewed-private-production; final public scope pending',conditions:['free viewing/ad use conditions reviewed','no implied endorsement or added Larian logo','preserve source IP/legal notices','source audio muted; no actor clone or ML training','do not generate Larian IP'],notAutomaticLicenseFromOfficialUploader:true}},
  {game:'The Harbor Seal / 항구의 봉인',kind:'original-playable-prototype',priorUse:false,reason:'Own executable story directly demonstrates knowledge transfer, actual owner/access, retained route consequences and recovered essential facts.',rights:'Own code/art/story. No Larian characters, lines, audio or visual assets.',classification:'Dominant playable-world actions count actual; state tables/graphs/log explanations count PPT.',evidence:[`${base}/production/playtest-state-proof.json`,`${base}/production/playtest-ui-proof.json`]}
 ],
 rejected:[
  {game:'Baldur’s Gate 3',priorUse:false,reason:'Separate BG3/Wizards terms and third-party component conditions; available initial official cinematic does not demonstrate the required state transitions. Do not assume DOS2 policy covers BG3.',policyUrls:['https://baldursgate3.game/bg3-fan-content-terms/','https://company.wizards.com/en/legal/fancontentpolicy/']},
  {game:'Divinity: Original Sin 2',sourceVideoId:'SNxDMZhiGtU',reason:'Long official live GM session includes multiple outside performers; clean suitable 1080p action track not established. Official tutorial chosen instead.',downloaded:false},
  {game:'Divinity: Original Sin 2',sourceVideoIds:['bTWTFX8qzPI','jXiT9Shrw5k','ga6uJaGyrEk'],reason:'Short cinematic/story trailer or combat spotlight, not the narrative fact/ownership action being explained.',downloaded:false},
  {game:'Divinity: Original Sin 2',sourceVideoId:'vJ4SVSm1ARQ',reason:'PlayStation duplicate of the same overview; no fresh action segment.',downloaded:false},
  {game:'Divinity: Original Sin 2',sourceVideoIds:['4X8SS5cysHI','nsIwseI94m4','dxWRY9N_xRE','k9dA1vQZG9M'],reason:'Third-party recording permission not confirmed; use selected developer sources and own test instead.',downloaded:false},
  {game:'Pentiment',priorUse:false,reason:'Concept fit considered. Search found outside full walkthroughs; suitable extended official recording and all required reuse conditions not confirmed. Not downloaded or relied on.',downloaded:false},
  {game:'Recent ONI/Desk Job/Alyx/SF6/Hi-Fi/Nintendo examples',priorUse:true,reason:'Already used in recent videos and better fit other concepts. Do not recycle their clips for this topic.'}
 ]
});
write(`${base}/sources/native-review.json`,{
 reviewedAt:new Date().toISOString(),kind:'Editorial source screening, not final all-cut QA',
 proofDirectory:'production/batches/sakurai-planning-game-design/preflight/proof-game-writing-refresh',
 reviewedSheets:['gm-tutorial-coarse-01.jpg','gm-tutorial-coarse-02.jpg','gm-tutorial-coarse-03.jpg','gm-tutorial-coarse-04.jpg','gameplay-overview-coarse-01.jpg','gameplay-overview-coarse-02.jpg','detail-map-1.jpg','detail-vignette-1.jpg','detail-vignette-2.jpg','detail-story-item-1.jpg','detail-players-1.jpg','detail-players-2.jpg','detail-dialogue-1.jpg'],
 nativeFrames:[{file:'native-vignette-484.png',observation:'Question and attack/feed/run options are being edited; chest illustration still precedes its replacement.'},{file:'native-story-item-1263.png',observation:'Renamed unique ring exists in GM inventory with changed description.'},{file:'native-dialogue-48.png',observation:'Caryl names Ifan; multiple responses including acting confused and a coin-purse gesture are displayed.'}],
 excludedIntervals:[{source:'gm-tutorial',in:1790,out:1880,reason:'Long pause/resume/explanation over mostly unchanged world; not sufficient meaningful narrative action to fill footage quota.'},{source:'gameplay-overview',in:135,out:206,reason:'Mostly combat/arena/cinematic/preorder montage; not the current narrative fact chapter.'}],
 requireBeforeFinal:['selected intervals at native first/middle/end and transition review','normal playback/no duplicated source range','caption placement avoids lower native dialogue and GM options','full source decode','current voice measured timeline','actual whole-video 60:40 classification']
});
item.playtest={stateProof:`${base}/production/playtest-state-proof.json`,stateCases:11,reachableStates:2209,optionsChecked:1424,uiProof:`${base}/production/playtest-ui-proof.json`,uiCases:5,uiActions:52,uiPageErrors:0,humanNarrativeReview:'pending',finalFootageCapture:'pending-current-narration-timing'};
item.sources={candidates:`${base}/sources/game-candidates.json`,files:`${base}/sources/source-files.json`,nativeScreening:`${base}/sources/native-review.json`,finalFootageApproved:false};
write('production/batches/sakurai-planning-game-design/queue.json',queue);
console.log('Source history, observed actions, rights and actual UI/state proof recorded. Final footage QA remains pending.');

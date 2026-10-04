const fs=require('fs'),path=require('path');
const out=path.join(__dirname,'action-bank-v6.json');
if(fs.existsSync(out))throw Error('Preserve native bank history.');
const old=JSON.parse(fs.readFileSync(path.join(__dirname,'action-bank-v5.json'),'utf8'));
const cuts=old.cuts.map(c=>({...c}));
for(const c of cuts){
 if(c.id==='wool-03'){c.sourceOutSeconds=321.3;c.revisionReason='Stop before the next snowy combat shot begins around321.5.';}
 if(c.id==='wool-07'){c.sourceInSeconds=366;c.revisionReason='Start after the dialogue visible at365.5; the next blue snowy battle is visible by366.';}
 c.durationSeconds=c.sourceOutSeconds-c.sourceInSeconds;
 c.scriptScene='12';c.nativeBoundaryReview='pending-v6-direct-review';
}
const sources=[...old.sources];
for(const name of ['bounty','improved']){
 const a=JSON.parse(fs.readFileSync(path.join(__dirname,'acquisition-'+name+'.json'),'utf8'));
 if(a.status!=='acquired-decoded-awaiting-direct-action-review'||a.results.some(s=>s.fullDecode.exitCode||s.fullDecode.diagnostics))throw Error('Source decode not complete.');
 for(const s of a.results){const v=s.streams.find(x=>x.codec_type==='video');sources.push({...s,fps:Number(v.r_frame_rate.split('/')[0])/Number(v.r_frame_rate.split('/')[1])});}
}
function add(id,sourceId,a,z,scene,action,focus){
 cuts.push({id,sourceId,sourceInSeconds:a,sourceOutSeconds:z,durationSeconds:z-a,scriptScene:scene,group:scene==='04'?'prerequisites':scene==='08'?'appearance-vs-function':scene==='06'?'limits':scene==='10'?'production':'review-contexts',visibleAction:action,focus,speed:1,sourceAudio:'exclude-all',classification:'candidate-existing-game-action',nativeBoundaryReview:'pending-v6-direct-review',fixedCaptionSafety:'pending-final-cues-and-render',intervalApprovedForIndependentPlanning:false,finalApproved:false});
}
const b='-jkxOq-vyu4';
const f='Observe moving targets, attacks and overlapping effects. No controlled numerical comparison, earned upgrade or balance defect is inferred.';
for(const [id,a,z,scene,action] of [
 ['bounty-01',2.5,4.3,'06','A player attacks a large moving enemy amid a red circular ground effect.'],
 ['bounty-02',4.5,6.8,'06','The player fires at an enemy while a purple circular field appears.'],
 ['bounty-03',8.4,9.8,'06','Several outward projectiles and a green circular effect occupy the same combat area.'],
 ['bounty-04',10,11.4,'10','A bright cyan projectile travels across a dark combat area toward a target.'],
 ['bounty-05',11.55,13.3,'10','Fire and pale-blue effects appear around a character in an arena.'],
 ['bounty-06',20.5,22.3,'12','A purple projectile is fired through a ruined forest combat space.'],
 ['bounty-07',22.55,24.25,'12','A player fires while moving through a snowy area near a tall crystal structure.'],
 ['bounty-08',26.35,27.3,'04','A snowy combat shot includes an Arcane Tome pickup and a small visible bounty indicator.'],
 ['bounty-09',27.5,28.3,'04','A separate edited shot shows an Imperium Bounty pickup near an Imperial Linen prompt.'],
 ['bounty-10',28.5,30.5,'04','A player approaches and interacts with the Bounty Mechana; dialogue begins.'],
 ['bounty-11',31.5,34.3,'04','A separate Bounty Mechana scene is followed by a dropped Hand Cannon pickup prompt.'],
 ['bounty-12',36,39.8,'06','Several small enemies surround players, with red ground markings and moving attacks.'],
 ['bounty-13',40,41.3,'06','A different enemy encounter shows a red projectile/impact in a brown terrain area.'],
 ['bounty-14',41.55,42.8,'10','An orange projectile or explosion appears in a red-brown ruin area.'],
 ['bounty-15',45.75,46.8,'10','A large purple glowing projectile travels toward a target in a dark combat area.'],
 ['bounty-16',47,48.2,'10','Fire and purple impacts overlap around characters and multiple enemies.'],
 ['bounty-17',48.4,49.3,'10','Pale-blue and green circular effects overlap in a combat shot.'],
 ['bounty-18',49.55,51.8,'10','Multiple players and enemies move through overlapping yellow, green and pale-blue combat effects.']
])add(id,b,a,z,scene,action,scene==='04'?'The official description connects completed bounties to claiming new weapons. Distinguish that stated rule from separate edited pickup/interaction shots; do not infer exact normal acquisition costs.':f);
add('appearance-01','mRkJ2uWFWYw',27,31.25,'08','The actual customization interface changes hats and masks on a character preview.','Observe the changed appearance. This does not verify an earned condition or numerical/statistical equality; active selection rather than a static title is shown.');
add('appearance-02','mRkJ2uWFWYw',33.5,34.4,'08','A character with changed headwear moves after a separate sewing-interface edit.','The character appearance is visible in actual play, while acquisition rules and numerical equality remain unverified.');
add('appearance-03','mRkJ2uWFWYw',41.7,45.75,'08','Different dressed characters move together in snowy terrain and a heart effect appears between them.','Appearance and visible interaction are different observations; do not claim the clothing caused healing or equal statistics.');
const rec={schemaVersion:1,createdAt:new Date().toISOString(),status:'supplemental-native-boundary-review-pending',sources,cuts,cutCount:cuts.length,candidateSeconds:cuts.reduce((n,c)=>n+c.durationSeconds,0),previousBank:'action-bank-v5.json',rejectedInternalRanges:[...old.rejectedInternalRanges,{cut:'wool-03',range:[321.3,322],reason:'Internal cut to another snowy battle'},{cut:'wool-07',range:[365.5,366],reason:'Dialogue before actual attack shot'}],discoveryEvidence:{bounty:'frames/-jkxOq-vyu4-native-discovery/index.json',bountyFramesDirectlyRead:120,bountySheetsDirectlyRead:5,improved:'frames/mRkJ2uWFWYw-native-discovery/index.json',improvedFramesDirectlyRead:113,improvedSheetsDirectlyRead:5},additionalRejectedCandidates:[{source:'JziX-60OyCc',ranges:[[10,21],[63,72]],reason:'Dense extra discovery includes title cards, short ambiguous animal interaction, menus, quiet camera travel and animated closeups. No additional clean interval selected simply to fill runtime.'},{source:'mRkJ2uWFWYw',ranges:[[0,5.5],[15,19],[19,25],[25,27],[50.5,56.24]],reason:'Titles, static map and long inventory panels held. No unseen station use inferred from the description.'},{source:'-jkxOq-vyu4',ranges:[[0,2.5],[7,8.3],[13.4,15],[15.8,16.9],[17.8,18.4],[24.4,26.3],[34.4,35.9],[43,44],[51.9,59.92]],reason:'Title/announcement cards and full wanted-board panels excluded from actual-action quota.'}],sourceIntervalsApproved:false,sourceAudioForFinal:'exclude-all',agentCreatedGames:0,finalApproval:false};
fs.writeFileSync(out,JSON.stringify(rec,null,2)+'\n');console.log(JSON.stringify({cuts:rec.cutCount,candidateSeconds:rec.candidateSeconds,existingPlanningSeconds:194.2,totalAvailableCandidateSeconds:194.2+rec.candidateSeconds}));

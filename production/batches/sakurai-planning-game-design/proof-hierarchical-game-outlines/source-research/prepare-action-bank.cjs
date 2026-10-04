// Source actions precede independent narration. This is a research bank, not final timing.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const base = __dirname;
if (fs.existsSync(path.join(base,'action-bank.json'))) throw Error('Preserve and review the existing bank; this first-pass research builder cannot overwrite later direct-review decisions.');
const acquire = JSON.parse(fs.readFileSync(path.join(base,'acquisition.json'),'utf8'));
if (acquire.status !== 'acquired-decoded-awaiting-direct-action-review') throw Error('Verified acquisition required');
const source = acquire.results.find(s=>s.videoId==='I-ccSZ5J1Bo');
const reviewed = [
  ['01',2616,2628,'levels','A selected track-end preview bends into a different shape.'],
  ['02',2635,2640,'overview','Camera moves from a wide station view toward the edited coaster.'],
  ['03',2654,2668,'levels','The next track preview grows/turns around the nearby drop attraction.'],
  ['04',2692,2700,'levels','Camera approaches the selected endpoint and support handle.'],
  ['05',2704,2714,'levels','Selected track preview changes its curve and support position.'],
  ['06',2716,2724,'fold','Camera inspects the station and connected track from another angle.'],
  ['07',2726,2745,'fold','Successive visible curve adjustments extend the selected track.'],
  ['08',2746,2768,'fold','A loop preview changes its height/tilt while the camera exposes its relation to the station.'],
  ['09',2769,2778,'move','The support/segment is selected and the visible loop shape shifts.'],
  ['10',2779,2788,'move','A selected red track preview tilts near the ground and changes its footprint.'],
  ['11',2789,2804,'move','Camera and endpoint changes show multiple track sections and their support points.'],
  ['12',2806,2824,'move','The camera moves to inspect the adjoining loops and selected support.'],
  ['13',3001,3012,'exceptions','Different curve previews appear against already existing rails.'],
  ['14',3014,3031,'exceptions','A selected curve changes shape and stretches over existing track; outline placement is still a preview.'],
  ['15',3047,3054,'exceptions','The selected red curve and support move relative to neighboring loops.'],
  ['16',3056,3064,'exceptions','A further track preview adjustment is shown; no claim of a successfully finished ride.'],
  ['17',3070,3078,'exceptions','Camera moves to another support/loop with the edit controls still active.'],
  ['18',3142,3159,'move','Changing support settings visibly changes the nearby curved segment.'],
  ['19',3160,3186,'review','Camera follows the built rails around the loop and station; inspect the complete object rather than one setting.'],
  ['20',3192,3204,'review','The view returns to the coaster and selects a different support for editing.'],
  ['21',3210,3224,'review','Support adjustment changes a loop while neighboring sections remain in view.'],
  ['22',3224,3238,'review','Track preview alternates between different positions/shapes as it is adjusted.'],
  ['23',3238,3258,'review','A selected loop is reshaped beside an existing loop; do not equate a green confirmation indicator with all conditions verified.'],
  ['24',3260,3272,'review','Another selected support changes the shape of the loop.'],
  ['25',3272,3284,'review','Camera inspects the resulting loop arrangement and a track overview is selected.'],
  ['26',2179,2193,'overview','A drop-ride placement preview moves between locations and valid/invalid indicators. This does not show a completed newly operating ride.'],
  ['27',2194,2202,'overview','The same placement preview is moved around other attractions before leaving the build action.'],
  ['28',4601,4612,'overview','A circular attraction is positioned and the build controls close before the camera approaches it.'],
  ['29',4612,4622,'overview','Camera inspects the circular attraction and its entrance/queue; no claim of a new pathway being built here.'],
  ['30',4624,4630,'exceptions','The view approaches the existing entrance and queue. Movement is inspection, not evidence of constructing an extension.'],
  ['31',4670,4682,'exceptions','A golden balloon decoration preview is repositioned beside the circular attraction.'],
  ['32',4688,4694,'exceptions','Camera rotates around the decoration and attraction; do not claim a measured visitor effect.'],
  ['33',4724,4738,'exceptions','A fence/prop preview is moved around the entrance and changes placement validity.'],
  ['34',3528,3554,'overview','A selected mascot walks outdoors and past visitors inside an exhibit room. No claim of an efficiency/happiness change.'],
];
const groups = [
  {key:'overview',claim:'A useful parent describes the player-facing experience; organize concrete observations underneath it.',diagram:'Flat mixed notes → goal / functions / concrete checks.',focus:'Separate the attraction, its entrance, decoration and moving visitors; these are different kinds of notes.',insert:'Opening actual examples, followed by explanation01.'},
  {key:'levels',claim:'Keep sibling items at comparable levels of detail and put adjustable properties under the feature they describe.',diagram:'Attraction placement / track design / access, with height and tilt under track design.',focus:'Changing one curve property is different from the whole attraction being complete.',insert:'After explanation01 and before explanation02.'},
  {key:'fold',claim:'Folding hides detail for an overview without deleting it; expand the branch needed for the current question.',diagram:'Collapse track properties, retain three headings, then expand the track branch.',focus:'Read the relationship between station, rails and adjustable details as the camera changes viewpoint.',insert:'After explanation02 and before explanation03.'},
  {key:'move',claim:'Move a parent together with its children and review whether its new parent still describes the contents.',diagram:'Move a branch with children; show a stranded child as a rejected comparison.',focus:'A track section and its support belong together in our notes even though individual properties can change.',insert:'After explanation03 and before explanation04.'},
  {key:'exceptions',claim:'Hierarchy is an organizing choice; relationships across branches need references instead of duplicated facts.',diagram:'Entrance and decoration branches with a separate cross-reference; distinguish contains from depends on.',focus:'Placement and access are separate concerns; a prop preview does not prove the queue works.',insert:'After explanation04 and before explanation05.'},
  {key:'review',claim:'Validate an outline by whether a reader can find a concrete condition and connect it to the parent goal.',diagram:'Top-level review → leaf check → return to parent; show unanswered questions explicitly.',focus:'Inspect the whole track after editing one support, and distinguish a preview from a verified result.',insert:'After explanation05 and before explanation06 / coaching conclusion.'},
];
const cuts = reviewed.map(([id,start,end,group,action])=>({id:'museum-'+id,sourceId:source.videoId,sourceInSeconds:start,sourceOutSeconds:end,durationSeconds:end-start,group,visibleAction:action,focus:groups.find(g=>g.key===group).focus,crop:[0,id==='34'?160:0,1376,774],speed:1,sourceAudio:'exclude',classification:'candidate-existing-game-action',evidence:'1/2-second source research; cropped native first/middle/last review pending',finalApproved:false}));
const ordered=[...cuts].sort((a,b)=>a.sourceInSeconds-b.sourceInSeconds);
for(let i=1;i<ordered.length;i++)if(ordered[i].sourceInSeconds<ordered[i-1].sourceOutSeconds)throw Error('Source overlap '+ordered[i].id);
const result={schemaVersion:1,preparedAt:new Date().toISOString(),source:{videoId:source.videoId,fileSha256:source.fileSha256,fileBytes:source.fileBytes,localMediaPath:source.localMediaPath,title:source.title,channel:source.channel,uploadDate:source.uploadDate,versionLabel:'Two Point Museum · Two Point Studios · 2026 public Update12 demonstration / DLC preview'},status:'candidate-bank-awaiting-native-crop-and-action-review',uniqueCandidateSeconds:cuts.reduce((n,c)=>n+c.durationSeconds,0),groups,cuts,boundaries:['All proposed outlines are our analysis, not the developers original planning documents.','Separate excerpts are not presented as one uninterrupted play session.','Source footage is normal speed. No replay loops, countdown, static discussion or promotional time-lapse filling the body.','Do not infer a completed successful ride, happiness change, queue construction or productivity effect from an unconfirmed preview.','Final60:40, narration fit, every caption cue and encoded boundary remain pending.'],narrationWritten:false,final60_40Measured:false,captionCueApproval:false,finalPublicRights:'pending'};
const output=path.join(base,'action-bank.json');
fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({cutCount:cuts.length,uniqueCandidateSeconds:result.uniqueCandidateSeconds,sha256:crypto.createHash('sha256').update(fs.readFileSync(output)).digest('hex'),finalApproval:false}));

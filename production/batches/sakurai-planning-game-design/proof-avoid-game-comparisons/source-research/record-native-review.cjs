// Record the direct image review already performed; this script does not inspect images itself.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '../../../../..');
const rel = p => path.relative(root, p).replaceAll('\\', '/');
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const read = n => JSON.parse(fs.readFileSync(path.join(__dirname, n), 'utf8'));
const now = new Date().toISOString();
const write = (n, d) => fs.writeFileSync(path.join(__dirname, n), JSON.stringify(d, null, 2) + '\n');
const states = ['native-review-v1.json', 'native-review-rocket-v1.json'].map(read);
if (states.some(s => s.status !== 'native-samples-extracted-awaiting-direct-review')) throw Error('Extraction not complete');
const observations = {
  z4utn4Sm6SY: {
    hard: {
      122:'Branding to close-up',142:'Close-up to cave action',182:'Cave to bramble corridor',256:'Corridor to loop cave',306:'Edited camera/time jump within cave',332:'Cave to vertical columns',387:'Columns to water/island',427:'Edited jump within water/island sequence',469:'Water to lava',521:'Lava to launch column',554:'Column to hanging yellow terrain',592:'Hanging terrain to rock ring',633:'Ring to boss staging',659:'Boss staging edited close-up',697:'Boss staging to lava fight',740:'Lava to gun close-up',778:'Gun close-up to wide explosion',803:'Explosion to cauldron',838:'Cauldron to cart/saw chain',1123:'Sea to large machine close-up',1150:'Machine close-up to wide action',1205:'Machine to saw tunnel',1245:'Saw tunnel to vertical lava',1279:'Lava to separated terrain islands',1339:'Island gaps to blue grapple',1409:'Grapple to circular red attacker',1463:'Attacker to barrel cannon',1529:'Cannon to exploding columns',1556:'Columns to purple boss attack'
    },
    effects: {765:'Gun flash, same shot',768:'Gun flash, same shot',1539:'Column explosion flash, same shot',1607:'Boss flash within the same action; not a cut'},
    other: {150:'Manual window point within cave',900:'Manual point with marketing text',1140:'Manual point within machine close-up',1615:'White transition flash after boss action',1616:'Green title background begins',1617:'Title logo appears',1620:'Manual point within title'},
    sequences: ['Yellow burrowing curves and exits to air across distinct terrain; no unseen button mapping claimed.', 'Water/island traversal, lava launch, gun/cart, large machine, grapple and cannon are different visible actions; split at editorial jumps.', 'Boss staging, marketing text and title transitions are excluded.'],
  },
  '4c-3gbC5mc4': {
    hard: {175:'New horizontal bramble corridor',221:'Red boss shot repeated from z4',266:'Vertical column shot repeated from z4',325:'Black wipe to promotional section',517:'Rope bridge walking',555:'Edited zoom/drop within bridge',598:'Water/idle after bridge',683:'New bramble wall gap',748:'Green fortress gun',796:'Blue/red machine appearance',835:'Cannon/rope aerial chain',893:'Snow trucks',959:'Snow/ice aerial traversal',1044:'World map',1366:'Exploding launch column repeated from z4',1440:'Cauldron repeated from z4',1497:'Purple elastic polygon',1578:'Second polygon over water',1626:'Options menu begins'},
    effects: {1367:'Explosion flash in same launch-column shot'},
    other: {150:'Manual loop-cave point; potential z4 repeat',330:'Manual point inside black wipe',540:'Manual point within bridge',600:'Manual water/idle point',690:'Manual point within bramble action',1050:'Manual map point',1380:'Manual repeated launch-column point',1650:'Manual options point'},
    sequences: ['Bridge, bramble wall, fortress gun, aerial cannon, snow/ice and elastic polygon candidates are distinct.', 'Matching boss/column/cauldron shots across trailers are held here and represented only once by z4.', 'Options begin at native frame1626=54.2s; the earlier rough55s candidate is superseded. 0.7/0.6 speed demonstration is excluded.'],
  },
  WFIvd2HrMNY: {
    hard: {827:'Music page to book jump',961:'Jump to word/block scene',1163:'World map begins',1746:'Boss to city',1882:'City to boat combat',1983:'Boat to night/day word scene',2156:'Day scene to ball minigame',2322:'Ball to boss arena',2501:'Boss to green book portal',2589:'Portal transition to a different castle-page shot',3123:'Castle-page shot to river/star portal',3305:'River/star portal to purple boss',3460:'Boss to virtual desk flag path',3777:'Mode/menu segment'},
    effects: {2095:'Continuous visible night-to-day change, not an editorial cut'},
    other: {720:'Manual music-page point',1200:'Manual map point',1800:'Manual city point',3360:'Manual boss point',3480:'Manual flag-path point',3720:'Camera whip; stop candidate before this'},
    sequences: ['Word/block change and NIGHT/DAYTIME are visible; do not claim an unseen input sequence.', 'Book-to-3D desk portal at41.683–43.15 is continuous; the following castle shot is a hard edit.', 'Castle blue/red printed doors, avatar transition and key glow are visible; no completed key acquisition/unlock claimed.', 'Virtual game desk is distinct from launch-trailer physical advertising.'],
  },
  JdNZo7E_hXU: {
    hard: {146:'Title to music-page action',234:'Music to paint scene',372:'Paint to book jump',486:'Jump to path fight',650:'Path to pond fight',790:'New-game menu',846:'Mode menu',970:'Industrial combat',1148:'Mode menu',1224:'Mode menu zoom',1308:'Silhouette cave',1498:'Goblin platforms',1652:'Options menu',3178:'ShowHiddenPortals ON context to portal scene',3702:'Portal scene to combat/assist demonstration',4360:'Ruler walking after assist context',4762:'Post-it to short paper portal',4942:'Paper portal to different3D shot',5458:'Dialogue to city portal',5604:'City portal to pond fight',5700:'Pond to night fight',5776:'Night to drained-moat scene',5906:'Moat to stairs',6002:'Stairs to fanned pages',6098:'Pages to castle shot repeated in WFI',6146:'Castle to celebration',6196:'Celebration zoom',6240:'Release card'},
    effects: {},
    other: {180:'Manual music point',840:'Manual menu point',1020:'Manual industrial point',1200:'Manual menu point',1320:'Manual cave point',1680:'Manual menu point',3180:'Manual portal point after assist ON',3720:'Manual combat point in assist demonstration',4380:'Manual ruler point after assist context',4620:'Manual dialogue point',4800:'Manual portal point',4920:'Portal dialogue already begins near82s; hold window pending exact onset',5460:'Manual city-portal point'},
    sequences: ['Path/pond fights, industrial combat, cave/platform actions and fanned paper path are observable candidates.', 'The initial music and book-jump shots duplicate WFI; rating overlay on paint scene is held.', 'ShowHiddenPortals ON precedes53–62s; default portal visibility is not established. Invincibility/OneHitKill is not base difficulty evidence.', 'The79–82s portal includes dialogue before the old rough endpoint; held. Celebration/menus are excluded.'],
  },
  'h27ZF-hKKYM': {
    hard: {7775:'Cylinder ground shooting to an edited later airborne shooting shot',8431:'Edited jump to different airborne cylinder-combat viewpoint',10087:'Small-cup portal close-up is an editorial camera jump'},
    effects: {5384:'Portal glow during continuous3D-to-flat-wall entry'},
    other: {840:'Manual window edge still under opening fade; select from14.5s',1920:'Manual edge before cup dialogue; select through31.5s',3060:'Manual point before leaving cup; dialogue already over',3480:'Close-up after exit, hold at57.5s before dialogue',4140:'Dialogue/rocket-climb dissolve; exclude69–69.5s',6420:'Dialogue after dissolve from mug flight; stop before106s',6780:'Dialogue ends near113s; select from113.5s',7200:'Cylinder dialogue begins; stop at119.5s',7560:'Dialogue/ground-combat dissolve; select from127s',10380:'Cup dialogue; duplicate earlier cup-entry sequence held'},
    sequences: ['Desk combat14.5–26.5; cup-portal approach/entry27–31.5; departure51.5–57.5.', 'Dissolves around69,71.5,79,100.5,106.5,126 and154.5 are not caught by the scene-score threshold. Use conservative interior intervals and do not narrate them as continuous action.', '72–78.5 and79.5–89.5 rocket traversal on spools/card ledges; fuel icons below may conflict with fixed captions, so final framing/cues must resolve this.', '90–100 flat blue-wall jumping/striking;101–105.5 mug descent/collection/rise;113.5–119.5 cylinder portal entry.', '127–129.5 cylinder ground movement;130–140.5 airborne shooting;141–148.5 further shooting;149–154.5 countdown/GO/anomaly overlay held;155–166.5 desk combat and rocket takeoff.', '167–173 repeats the first small-cup portal approach: hold this second sequence. All dialogue, rocket assembly/cinematic standing and end cards excluded.'],
  },
};
const sourceReviews = states.flatMap(state => state.sources.map(s => {
  const o = observations[s.videoId];
  if (!o) throw Error('Missing direct review: ' + s.videoId);
  const sheets = [...s.actionSheets, ...s.boundarySheets];
  for (const f of sheets) if (sha(path.join(root, f.path)) !== f.sha256) throw Error('Sheet hash changed: ' + f.path);
  const boundaryDecisions = s.candidateBoundaryFrames.map(frame => {
    const kind = o.hard[frame] ? 'editorial-cut-or-menu-transition' : o.effects[frame] ? 'continuous-action-effect' : 'manual-edge-or-transition';
    const observation = o.hard[frame] || o.effects[frame] || o.other[frame];
    if (!observation) throw Error('Unreviewed boundary ' + s.videoId + ':' + frame);
    return {frame, seconds:frame/s.nativeFps, kind, observation};
  });
  return {videoId:s.videoId, sourceSha256:s.sourceSha256, nativeFps:s.nativeFps, actionFramesDirectlyRead:s.actionSamples.length, boundaryTripletsDirectlyRead:boundaryDecisions.length, boundaryTiles:s.candidateBoundaryFrames.length*3, sheetsDirectlyRead:sheets, boundaryDecisions, sequences:o.sequences};
}));
const review = {
  schemaVersion:1, slug:'avoid-game-comparisons', reviewedAt:now,
  status:'all-native-sheets-directly-read-candidate-bank-selected',
  method:'Direct visual reading of every half-second native action sample and all before/at/after native boundary triplets in the listed sheets. Original-source decoding is separate technical evidence. This is not full human audiovisual playback or final-caption QA.',
  inputStates:['native-review-v1.json','native-review-rocket-v1.json'].map(n=>({path:rel(path.join(__dirname,n)),sha256:sha(path.join(__dirname,n))})),
  sourceReviews,
  totals:{actionFrames:sourceReviews.reduce((a,s)=>a+s.actionFramesDirectlyRead,0),boundaryTriplets:sourceReviews.reduce((a,s)=>a+s.boundaryTripletsDirectlyRead,0),boundaryTiles:sourceReviews.reduce((a,s)=>a+s.boundaryTiles,0),sheets:sourceReviews.reduce((a,s)=>a+s.sheetsDirectlyRead.length,0)},
  corrections:['WFI world map begins at1163/60=19.383333s, earlier rough20s candidate superseded.', '4c options menu begins1626/30=54.2s, earlier rough55s candidate superseded.', 'Jd menus begin790/60=13.166667s and1148/60=19.133333s; old14/20s windows not action throughout.', 'z4 boss flash1607 is within action;1615 white/1616 green/1617 title transition excludes subsequent frames.', 'Rocket has several dissolves below scene-score threshold; candidate interiors avoid them.'],
  duplicateShotDecisions:[{keep:'z4utn4Sm6SY',hold:'4c-3gbC5mc4',shots:['loop cave potential repeat','red boss','vertical launch columns','cauldron']},{keep:'WFIvd2HrMNY',hold:'JdNZo7E_hXU',shots:['music page','book jump','castle blue/red printed doors']},{keep:'h27ZF-hKKYM27–31.5',hold:'h27ZF-hKKYM167–173',shots:['second approach to same small-cup portal']}],
  sourceAudioUsed:false,selfCreatedGameExamples:0,actualCutApproval:false,bodyRatioApproved:false,humanFullPlayback:'pending',finalPublicRights:'pending',localOnlyRaster:true,
};
write('direct-native-review-v1.json',review);
const disc=read('discovery-rocket-ride.json');
const ds=disc.sources[0];
const discReview={schemaVersion:1,reviewedAt:now,videoId:'h27ZF-hKKYM',input:{path:rel(path.join(__dirname,'discovery-rocket-ride.json')),sha256:sha(path.join(__dirname,'discovery-rocket-ride.json'))},allDiscoverySheetsDirectlyRead:true,frames:204,sheets:ds.contactSheets||ds.sheets,observations:observations['h27ZF-hKKYM'].sequences,excluded:['0–14 intro/title/cinematic','32–51 cup dialogue','58–69 dialogue','107–113 dialogue','120–126 cylinder dialogue','167–173 repeated portal approach','173–181 dialogue','182–188 rocket assembly/standing','189–197 dialogue','198–203 end card'],nativeReview:rel(path.join(__dirname,'direct-native-review-v1.json')),sourceAudioUsed:false,humanFullPlayback:'pending',actualCutApproval:false};
write('direct-rocket-discovery-review.json',discReview);
// Conservative, unique action intervals for planning. Final cue/crop/ratio approval is a later gate.
const bank=[];
function add(id,start,end,action,claim,focus,diagram,insertion,caution='Describe only the observed action; do not infer exact button mapping, success or a complete game rule.') {
  const s=sourceReviews.find(x=>x.videoId===id); const fps=s.nativeFps;
  const a=Math.round(start*fps),b=Math.round(end*fps);
  if(b<=a) throw Error('Empty interval');
  bank.push({id:`action-${String(bank.length+1).padStart(2,'0')}`,sourceVideoId:id,sourceUrl:`https://www.youtube.com/watch?v=${id}`,sourceSha256:s.sourceSha256,nativeFps:fps,startFrame:a,endFrameExclusive:b,inSeconds:a/fps,outSeconds:b/fps,seconds:(b-a)/fps,visibleAction:action,planningClaim:claim,viewerFocus:focus,diagramConnection:diagram,insertionPoint:insertion,caution,status:'selected-for-independent-planning',finalCaptionFramingApproved:false});
}
const p='z4utn4Sm6SY',f='4c-3gbC5mc4',w='WFIvd2HrMNY',j='JdNZo7E_hXU',r='h27ZF-hKKYM';
const verb='A familiar genre/name alone omits the visible action.';
const chain='A pitch can state action, affected surface, constraint and visible result.';
const distinction='Separate a presentation change from the action performed within it.';
const limit='Specific observed constraints make two apparently similar descriptions distinguishable.';
const audience='Let the listener restate the action and ask a concrete unresolved question.';
for(const [a,b,action] of [[5,6,'Curve through yellow cave and exit into air'],[6.5,8.5,'Burrow through yellow corridor between brambles'],[9,10,'Travel around yellow cave loop'],[11.5,12.5,'Move between yellow columns and blue pins'],[13,14,'Swim and traverse water/island'],[14.5,15.5,'Strike floating green attacker over water'],[16,17,'Launch upward above lava'],[17.5,18,'Launch along blue-arrow column'],[18.5,19.5,'Traverse hanging yellow bulb'],[20,21,'Move around rotating rock ring'],[23.5,24.5,'Attack amid lava projectiles'],[25,25.5,'Gun action in close-up'],[26,26.5,'Wide gun projectiles/explosion'],[27,27.5,'Cauldron/lava weapon action'],[28,29,'Cart and saw chain above lava'],[38.5,40,'Large machine airborne movement and projectiles'],[40.5,41,'Drill through saw-lined terrain'],[41.5,42.5,'Traverse vertical lava region'],[43,44.5,'Exit one yellow island and travel toward another'],[45,46.5,'Grapple a blue hook between brambles'],[47,48.5,'Strike circular red attacker'],[49,50.5,'Barrel-cannon travel between terrain and balloons'],[51.5,51.8,'Explosions on vertical terrain'],[52,53.5,'Attack purple boss']]) add(p,a,b,action,verb,'Follow the avatar path and terrain boundary','Name label → visible verb/surface/result','Before/after first explanation');
for(const [a,b,action] of [[6,7,'Horizontal yellow burrowing corridor'],[17.5,18.5,'Walk across rope bridge before the edited zoom'],[18.6,19.8,'Drop/traverse bridge section after the edited zoom'],[23,24.5,'Burrow into bramble wall gap'],[25,26.5,'Fire within green fortress'],[28,29.5,'Cannon/rope aerial chain'],[30,31.5,'Move between snow trucks'],[32,34.5,'Aerial/snow-ice burrowing traversal'],[50,52.5,'Enter and launch from purple elastic polygon'],[53,54,'Traverse a second elastic polygon above water']]) add(f,a,b,action,chain,'Track entry, exit and next landing point','Action → surface → next visible state','Around action-chain explanation');
for(const [a,b,action] of [[12,13.5,'Walk on yellow music page'],[14,16,'Jump across book gap'],[16.5,19,'Stair/block interaction with visible text/state change'],[30,31,'Walk through city page'],[31.5,33,'Boat combat'],[33.5,35.5,'Visible NIGHT/DAYTIME word and lighting change'],[36,38.5,'Match colored balls'],[39,41.5,'Boss-arena combat'],[42,43,'Pass from flat book page to3D desk through green portal'],[43.5,51.5,'Move between desk and blue/red printed-door page'],[52.5,55,'River/star portal movement'],[58,61.5,'Walk along virtual desk flag/string path']]) add(w,a,b,action,distinction,'Distinguish the avatar location from the camera/view and object appearance','Before/after surfaces plus arrows indicating actual avatar transition','Around presentation-versus-mechanic explanation', 'Visible transitions only; key glow is not proof of completed acquisition or unlock. No developer-internal design-document claim.');
for(const [a,b,action] of [[8.5,10.5,'Fight along page path'],[11,13,'Fight by page pond'],[17,19,'Combat among industrial page structures'],[22,24.5,'Silhouette cave combat'],[25,27,'Traverse goblin platforms'],[73,76.5,'Walk ruler/post-it path on virtual desk'],[91,93,'Exit city-page portal into3D surroundings'],[93.5,95,'Pond fight'],[95.5,96,'Night page combat'],[96.5,98,'Move through visibly drained moat page'],[98.5,100,'Climb silhouette stairs'],[100.5,101.5,'Traverse fanned paper path while boulders move']]) add(j,a,b,action,limit,'Observe path shape, obstacle and state shown in this exact excerpt','Constraint/result boxes attached to the visible path','Around limits and unresolved-questions explanation','This official accessibility demo includes assists elsewhere. Do not infer default portal visibility, base difficulty or unseen controls.');
for(const [a,b,action] of [[14.5,26.5,'Move, strike desk enemies and throw an explosive object'],[27,31.5,'Approach cup portal and enter its flat printed surface'],[51.5,57.5,'Leave cup surface and appear on3D desk with rocket pack'],[70,71,'Rocket climb along card ledges between dissolves'],[72,78.5,'Fly between spool tops/card ledges and strike enemies'],[79.5,89.5,'Strike ledge enemy, rocket upward, approach blue-wall portal'],[90,100,'Jump/strike enemies on flat blue printed wall'],[101,105.5,'Rocket up, descend inside mug, collect a light and rise'],[113.5,119.5,'Approach large cylinder portal and enter printed surface'],[127,129.5,'Move and shoot on printed cylinder ground'],[130,140.5,'Airborne shooting against visible incoming attackers'],[141,148.5,'Continue airborne cylinder shooting after editorial jump'],[155,166.5,'Strike desk enemies then rocket upward']]) add(r,a,b,action,audience,'Follow avatar transition, movement direction and landing/attack result','Three-sentence pitch linked to two distinct action sequences','Around concrete pitch and listener-restate explanation','Exclude dialogue/dissolves/countdown overlays; fuel icons near the bottom require final framing/cue review with captions fixed at960,970. Do not assert exact fuel rule, unlimited flight or complete victory.');
const grouped={}; for(const c of bank) grouped[c.sourceVideoId]=(grouped[c.sourceVideoId]||0)+c.seconds;
const actionBank={schemaVersion:1,slug:'avoid-game-comparisons',createdAt:now,status:'conservative-source-action-bank-for-planning',directReview:rel(path.join(__dirname,'direct-native-review-v1.json')),intervalConvention:'Native frame start inclusive, end exclusive. Conservative interiors avoid known editorial cuts, fades/dialogue and duplicate shots.',clips:bank,uniqueSourceSeconds:bank.reduce((a,c)=>a+c.seconds,0),bySourceSeconds:grouped,rightsEvidence:'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/source-candidates-and-usage-review.json',sourceAudioUsed:false,selfCreatedGameExamples:0,bodyRatioApproved:false,finalCutAndCaptionApproval:false,measuredNarration:false,nextAction:'Review claim/clip connections and each selected interval endpoint; create independent whole-video overview/body plan only after current distinct gate. Measure approved TTS before allocating final60:40; acquire further relevant action if needed.'};
// No overlapping source-time intervals inside this candidate bank.
for(const c of bank) for(const other of bank) if(c.id<other.id&&c.sourceVideoId===other.sourceVideoId&&c.startFrame<other.endFrameExclusive&&other.startFrame<c.endFrameExclusive) throw Error('Source overlap: '+c.id+' '+other.id);
write('source-action-bank-v1.json',actionBank);
const candidateFile=path.join(__dirname,'../source-candidates-and-usage-review.json');
const candidates=JSON.parse(fs.readFileSync(candidateFile,'utf8'));
candidates.historicalNativeApproval={approvedIntervals:candidates.approvedIntervals,status:candidates.status,updatedAt:candidates.updatedAt};
candidates.status='native-sheets-read-conservative-action-bank-selected';
candidates.updatedAt=now;
candidates.approvedIntervals=[];
candidates.selectedPlanningIntervals=bank.map(c=>({id:c.id,sourceVideoId:c.sourceVideoId,inSeconds:c.inSeconds,outSeconds:c.outSeconds,seconds:c.seconds}));
candidates.selectedPlanningSeconds=actionBank.uniqueSourceSeconds;
candidates.sourceActionBank=rel(path.join(__dirname,'source-action-bank-v1.json'));
candidates.directNativeReview=rel(path.join(__dirname,'direct-native-review-v1.json'));
candidates.additionalAcquisition={rocket:rel(path.join(__dirname,'acquisition-rocket-ride.json')),pestHeld:rel(path.join(__dirname,'acquisition-pest-control.json')),pestReason:'Normal acquisition failedHTTP403; partial local files/log retained. No retry/cookie/account bypass. Different verified official Rocket Ride source successfully acquired and decoded.'};
candidates.candidates.slice(0,2).forEach(c=>c.status='selected-for-independent-action-planning');
candidates.nextAction=actionBank.nextAction;
candidates.limitations=['Selected source intervals support planning; current audio, final60:40, all final cues/crops and public-rights/human-listening approval remain incomplete.', 'No new project/script/TTS/Motion Canvas has been created.', 'All discovery/native JPEGs remain local-only; no new raster is part of Git delivery.'];
fs.writeFileSync(candidateFile,JSON.stringify(candidates,null,2)+'\n');
console.log(JSON.stringify({review:review.totals,clips:bank.length,candidateSeconds:actionBank.uniqueSourceSeconds,bySourceSeconds:grouped}));

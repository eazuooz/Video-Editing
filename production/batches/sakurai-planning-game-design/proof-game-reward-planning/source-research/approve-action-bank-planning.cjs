const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../../../..');
const relative=f=>path.relative(root,f).replace(/\\/g,'/');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const target=path.join(__dirname,'action-bank-planning-v1.json');
if(fs.existsSync(target))throw Error('Preserve the reviewed planning bank.');
const input=path.join(__dirname,'action-bank-v3.json'),bank=read(input);
const native=read(path.join(__dirname,'frames/native-bank-v3/index.json'));
const state=read(path.join(__dirname,'native-bank-inspection-v3.json'));
if(state.status!=='finished-awaiting-direct-native-bank-review'||native.bankSha256!==hash(input))throw Error('Native review input mismatch.');
const rejected={
 'ranch-01':'The native middle frame is a non-action animal presentation/animated transition. Exclude the whole short menu/variant montage from the actual-action bank; do not infer cosmetic-only rewards.',
 'ammo-07':'The native middle frame is the Fast Traveler recipe heading over a quiet transition. The later ammo-11 already demonstrates a meaningful gap-crossing action; exclude this four-second proposal.',
 'coop-07':'The later battle shots show enormous pickup/damage counters in the promotional build. They are unnecessary for our catalogue argument and unsafe as normal acquisition/balance evidence; exclude the whole eight-second proposal.'
};
bank.rejectedCuts.push(...bank.cuts.filter(c=>rejected[c.id]).map(c=>({...c,rejectionReason:rejected[c.id]})));
bank.cuts=bank.cuts.filter(c=>!rejected[c.id]);
for(const c of bank.cuts){
 c.nativeBoundaryReview='directly-read-v3-first-middle-last-and-adjacent';
 c.intervalApprovedForIndependentPlanning=true;
 c.finalApproved=false;c.fixedCaptionSafety='pending-final-cues-and-render';
 if(c.id==='ranch-02')c.visibleAction='Separate in-game shots show petting/heart feedback, milking a cow and a further night interaction; do not describe the whole montage as shearing or assume one continuous collection session.';
 if(c.id==='ammo-11')c.visibleAction='Separate combat/ground-creation and character movement shots include crossing a gap on generated ground. No controlled numerical damage comparison is demonstrated.';
}
bank.preparedAt=new Date().toISOString();bank.status='native-action-intervals-reviewed-for-independent-planning';
bank.cutCount=bank.cuts.length;bank.uniqueCandidateSeconds=Number(bank.cuts.reduce((n,c)=>n+c.durationSeconds,0).toFixed(6));
bank.sourceIntervalsApproved=true;bank.previousBank={path:relative(input),sha256:hash(input),cutCount:39,candidateSeconds:209.2};
bank.final60_40Measured=false;bank.captionCueApproval=false;bank.narrationWritten=false;
bank.boundaries.push('ranch-01, ammo-07 and coop-07 rejected after v3 native reading; this bank approval permits planning only, not final footage/caption/ratio approval.');
write(target,bank);
const review={schemaVersion:1,slug:'game-reward-planning',reviewedAt:bank.preparedAt,status:'direct-native-action-review-complete-for-planning',
 previousReview:relative(path.join(__dirname,'direct-source-review-v2.json')),
 discovery:{sourceCount:7,framesDirectlyRead:875,sheetsDirectlyRead:40},
 v2Dense:{input:'action-bank-v2.json',index:'frames/native-bank-v2/index.json',rolesDirectlyRead:616,uniqueFramesDirectlyRead:543,sheetsDirectlyRead:31,internalStepSeconds:0.5},
 v3Native:{input:relative(input),sha256:hash(input),index:relative(path.join(__dirname,'frames/native-bank-v3/index.json')),rolesDirectlyRead:195,uniqueFramesDirectlyRead:161,sheetsDirectlyRead:10,pid:2540,sessionId:72511,startedAt:state.startedAt,endedAt:state.endedAt,exitCode:0},
 fullSizeRead:['frames/native-bank-v3/n8wJDqZanbM/frame-0013.jpg','frames/native-bank-v3/xNUn4fn4br8/frame-0018.jpg','frames/native-bank-v3/3nIAR1g8RAU/frame-0030.jpg'],
 readableFacts:['Life Bullet description says it heals living/organic targets and damages undead. Do not copy exact numerical values or call all bullets stronger damage upgrades.','Potion and Ground research interfaces show selected/completed nodes AND missing-ingredient warnings. These edited promotional shots do not prove successful normal payment, earned acquisition or actual resource deduction.','ranch feeding changes Feed Berry/Feed Grass. Wide graphic80/5 cost panels are not our verified acquisition-rule evidence.','Gap crossing in ammo-11 and freeze/shatter in ammo-01 are different visible capabilities. Separate edits are not a controlled comparison.'],
 rejectedCuts:rejected,selectedBank:relative(target),selectedBankSha256:hash(target),selectedCutCount:bank.cutCount,selectedCandidateSeconds:bank.uniqueCandidateSeconds,
 sourceAudioForFinal:'exclude-all',agentCreatedGames:0,final60_40Measured:false,finalCaptionApproval:false,finalPublicRights:'pending',humanWholeListening:'pending',
 nextAction:'Create the current-distinct project, record the independent overview and claim/action/diagram links, write matching KO/EN narration. Measure useful explanation and secure additional related action when needed; never shorten it to fit the bank.'};
write(path.join(__dirname,'direct-source-review-v3.json'),review);
write(path.join(__dirname,'native-bank-launch-v3.json'),{schemaVersion:1,pid:state.pid,sessionId:72511,startedAt:state.startedAt,endedAt:state.endedAt,status:'finished',exitCode:0,command:'python inspect-bank-native.py --version v3',gpuJobs:0});
const oldResearch=path.join(__dirname,'../source-research.json'),research=read(oldResearch);
research.historicalInitialResearch={observedAt:research.observedAt,status:research.status,footageSecured:research.footageSecured,sourceIntervalsApproved:research.sourceIntervalsApproved};
research.observedAt=bank.preparedAt;research.status='official-native-actions-reviewed-for-independent-planning';research.footageSecured=true;research.sourceIntervalsApproved=true;
research.selectedBank={path:relative(target),sha256:hash(target),cutCount:bank.cutCount,candidateSeconds:bank.uniqueCandidateSeconds,finalRatioApproval:false};
research.directActionReview=relative(path.join(__dirname,'direct-source-review-v3.json'));
research.acquiredSources=bank.sources.map(s=>({...s,selectedForPlanning:bank.cuts.some(c=>c.sourceId===s.videoId),approvedPlanningIntervals:bank.cuts.filter(c=>c.sourceId===s.videoId).map(c=>({id:c.id,in:c.sourceInSeconds,out:c.sourceOutSeconds,action:c.visibleAction})),finalPublicRights:'pending'}));
for(const c of research.candidates){if(c.game==='Cult of the Lamb'){c.status='selected-official-ranch-actions-for-planning';c.selected=true;c.directActionReview=research.directActionReview;c.approvedIntervals=research.acquiredSources.find(s=>s.videoId==='JziX-60OyCc').approvedPlanningIntervals;}}
research.candidates.push({game:'Wizard with a Gun',status:'selected-official-ammo-research-placement-and-test-context-for-planning',selected:true,primaryPages:['https://influencers.devolverdigital.com/wizard-with-a-gun','https://canipostandmonetizevideosofdevolvergames.com/'],usageConditions:'Publisher creator page links the observed personalized posting/monetization permission for this public channel. Retain internal permission evidence; exclude source audio and hold final public-rights review.',recentUse:'Repository-wide recent source/game-candidates search found no earlier Wizard with a Gun selection.',directActionReview:research.directActionReview});
research.nextAction=review.nextAction;research.gpuJobs=0;research.newNarrationWritten=false;research.ttsStarted=false;research.scenesCreated=false;
write(oldResearch,research);process.stdout.write(JSON.stringify({cutCount:bank.cutCount,seconds:bank.uniqueCandidateSeconds,bank:relative(target)})+'\n');

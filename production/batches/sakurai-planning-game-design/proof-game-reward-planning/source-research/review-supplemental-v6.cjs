const fs=require('fs'),path=require('path'),crypto=require('crypto');
const base=__dirname,root=path.resolve(base,'../../../../..');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const write=(p,x)=>fs.writeFileSync(p,JSON.stringify(x,null,2)+'\n');
if(fs.existsSync(path.join(base,'action-bank-v7.json')))throw Error('Preserve existing review and native boundary extraction.');
const bank=read(path.join(base,'action-bank-v6.json'));
const index=read(path.join(base,'frames/native-bank-v6/index.json'));
const revisions={
 'wool-03':[318,321,'The snowy next shot is already visible at321.2. Retain the red-ground combat through320.933; prior321.3 estimate was wrong.'],
 'wool-07':[366,372.5,'Preserve the visible boss attack wind-up and moving red projectile pattern; inspect the extended endpoint before accepting it.'],
 'bounty-02':[4.5,6.5,'Announcement card is visible at6.75 and6.783; end on the reviewed combat frame instead.'],
 'bounty-05':[11.55,13.1,'Combat is visible at13.05; announcement card is already visible at13.283.'],
 'bounty-07':[22.55,24.1,'Snowy combat remains visible at24.05; announcement card is visible at24.233.'],
 'bounty-10':[28.5,29.9,'Keep approach and machine transformation; exclude the held dialogue beginning around30.0.'],
 'bounty-11':[32.5,34+16/60,'Exclude held Talk prompt; keep character movement, item prompts and the Hand Cannon prompt through34.25, before the card at34.283.'],
 'bounty-18':[49.55,51.6,'Actual combat remains visible at51.55; illustrated character overlay appears by51.783.'],
 'appearance-01':[27,31.1,'Keep changing masks/hats; exclude the separately edited Sewing Mechana interface seen at31.233.']
};
const notes=[
 'All18 contact sheets were directly read, covering353 role frames/351 unique native images. This is source/planning review only; final caption safety remains pending.',
 'wool-01 and wool-04 contain internal cuts between genuine moving combat shots. Final compilation must retain native cut boundaries in its QA and not claim a continuous encounter.',
 'Bounty08 shows Metal Scrap pickup, followed by a separately edited Imperium Bounty prompt. Prior Arcane Tome label is corrected, not carried into narration.',
 'Bounty09 includes Imperial Linen and an Imperium Bounty inventory increment. Bounty11 displays The Rotten Log and The Hand Cannon prompts. No uninterrupted earned weapon acquisition or cost is inferred.',
 'Several Bounty combat intervals contain internal edits. Repeat arena settings are different visible gameplay states; do not loop or replay frames to fill the quota.',
 'Appearance03 includes differently dressed characters, movement and heart/emote interaction. Clothing is not claimed to cause healing or equal statistics.',
 'Appearance02 is rejected: most of its interval is a held character view followed by a communication wheel, rather than the claimed headwear walking action.'
];
const review={schemaVersion:1,reviewedAt:new Date().toISOString(),bankSha256:sha(path.join(base,'action-bank-v6.json')),indexSha256:sha(path.join(base,'frames/native-bank-v6/index.json')),framesDirectlyRead:index.frameCount,uniqueFramesDirectlyRead:index.uniqueFrameCount,sheetsDirectlyRead:index.sheets,notes,revisions,rejectedCuts:[{id:'appearance-02',reason:notes.at(-1)}],finalApproval:false,fixedCaptionSafety:'pending-final-cues-and-render',wholeSourceRightsApproval:'pending-final-public-review'};
write(path.join(base,'direct-supplemental-review-v6.json'),review);
const v7={...bank,createdAt:new Date().toISOString(),previousBank:'action-bank-v6.json',status:'changed-boundaries-awaiting-native-direct-review',cuts:bank.cuts.filter(c=>revisions[c.id]).map(c=>{const [a,z,reason]=revisions[c.id];return {...c,previousInterval:{in:c.sourceInSeconds,out:c.sourceOutSeconds},sourceInSeconds:a,sourceOutSeconds:z,durationSeconds:z-a,revisionReason:reason,nativeBoundaryReview:'pending-v7-direct-review'};}),directReviewEvidence:'direct-supplemental-review-v6.json',sourceIntervalsApproved:false,finalApproval:false};
v7.cutCount=v7.cuts.length;v7.candidateSeconds=v7.cuts.reduce((s,c)=>s+c.durationSeconds,0);
write(path.join(base,'action-bank-v7.json'),v7);
console.log(JSON.stringify({reviewedFrames:index.frameCount,sheets:index.sheets.length,changedBoundaryCuts:v7.cutCount,sourceAudioForFinal:0,finalApproval:false}));
